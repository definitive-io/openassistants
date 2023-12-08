import asyncio
from typing import Any, Dict, List, Optional, Tuple

from langchain.chat_models.base import BaseChatModel
from langchain.chat_models.openai import ChatOpenAI

from openassistants.data_models.chat_messages import (
    OpasAssistantMessage,
    OpasFunctionMessage,
    OpasMessage,
    OpasUserMessage,
)
from openassistants.data_models.function_input import FunctionCall, FunctionInputRequest
from openassistants.functions.base import BaseFunction, FunctionExecutionDependency
from openassistants.functions.crud import FunctionCRUD, LocalCRUD
from openassistants.llm_function_calling.infilling import (
    generate_argument_decisions,
    generate_arguments,
)
from openassistants.llm_function_calling.selection import select_function
from openassistants.utils.async_utils import AsyncStreamVersion


class Assistant:
    function_identification: BaseChatModel
    function_infilling: BaseChatModel
    function_summarization: BaseChatModel
    function_libraries: List[FunctionCRUD]

    _cached_all_functions: List[BaseFunction]

    def __init__(
        self,
        libraries: List[str | FunctionCRUD],
        function_identification: BaseChatModel = ChatOpenAI(model="gpt-3.5-turbo-16k"),
        function_infilling: BaseChatModel = ChatOpenAI(model="gpt-3.5-turbo-16k"),
        function_summarization: BaseChatModel = ChatOpenAI(model="gpt-3.5-turbo-16k"),
    ):
        self.function_identification = function_identification
        self.function_infilling = function_infilling
        self.function_summarization = function_summarization
        self.function_libraries = [
            library if isinstance(library, FunctionCRUD) else LocalCRUD(library)
            for library in libraries
        ]
        self._cached_all_functions = []

    async def get_all_functions(self) -> List[BaseFunction]:
        if not self._cached_all_functions:
            functions = []
            for library in self.function_libraries:
                functions.extend(await library.aread_all())
            self._cached_all_functions = functions
        return self._cached_all_functions

    async def execute_function(
        self,
        function: BaseFunction,
        func_args: Dict[str, Any],
        dependencies: Dict[str, Any],
    ):
        deps = FunctionExecutionDependency(
            arguments=func_args,
            **dependencies,
        )

        function_call_invocation = OpasAssistantMessage(
            content="",
            function_call=FunctionCall(name=function.id, arguments=func_args),
        )

        yield [function_call_invocation]

        async for version in function.execute(deps):
            yield [
                function_call_invocation,
                OpasFunctionMessage(name=function.id, outputs=list(version)),
            ]

    async def do_infilling(
        self,
        dependencies: dict,
        message: OpasUserMessage,
        selected_function: BaseFunction,
        args_json_schema: dict,
    ) -> Tuple[bool, dict]:
        # Perform infilling and generate argument decisions in parallel
        arguments_future = asyncio.create_task(
            generate_arguments(
                selected_function,
                self.function_infilling,
                message.content,
                dependencies.get("chat_history"),
            )
        )
        argument_decisions_future = asyncio.create_task(
            generate_argument_decisions(
                selected_function,
                self.function_infilling,
                message.content,
                dependencies.get("chat_history"),
            )
        )
        arguments = await arguments_future
        argument_decisions = await argument_decisions_future
        # Filter arguments that are not needed or cannot be inferred
        arguments = {
            arg_name: arg_value
            for arg_name, arg_value in arguments.items()
            if arg_name in argument_decisions
            and argument_decisions[arg_name]["can_be_found"]
            and argument_decisions[arg_name]["needed"]
        }
        # Find if any of the arguments are needed but cannot be inferred
        arguments_needed_but_cannot_be_inferred = [
            arg_name
            for arg_name, arg_decision in argument_decisions.items()
            if arg_decision["needed"] and not arg_decision["can_be_found"]
        ]
        # Check if any of the arguments that are required are missing
        required_arguments_missing = [
            arg_name
            for arg_name, arg_property in args_json_schema["properties"].items()
            if arg_name in args_json_schema["required"] and arg_name not in arguments
        ]

        complete = (
            len(arguments_needed_but_cannot_be_inferred) == 0
            and len(required_arguments_missing) == 0
        )

        return complete, arguments

    async def handle_user_plaintext(
        self,
        message: OpasUserMessage,
        all_functions: List[BaseFunction],
        dependencies: Dict[str, Any],
        autorun: bool,
        force_select_function: Optional[str],
    ) -> AsyncStreamVersion[List[OpasMessage]]:
        selected_function: Optional[BaseFunction] = None

        # Perform function selection
        if force_select_function is not None:
            filtered = [f for f in all_functions if f.id == force_select_function]
            if len(filtered) == 0:
                raise ValueError("function not found")
            selected_function = filtered[0]

        if selected_function is None:
            function_selection = await select_function(
                self.function_identification, all_functions, message.content
            )

            if function_selection.function:
                selected_function = function_selection.function
            elif function_selection.suggested_functions:
                suggested_functions_names = ", ".join(
                    [
                        f.get_function_name()
                        for f in function_selection.suggested_functions
                    ]
                )
                yield [
                    OpasAssistantMessage(
                        content=(
                            f"No function matching that question was found. "
                            f"Did you mean: {suggested_functions_names}?"
                        )
                    )
                ]
                return
            else:
                yield [
                    OpasAssistantMessage(
                        content="No function matching that question was found."
                    )
                ]
                return

        selected_function_arg_json_schema = (
            await selected_function.get_parameters_json_schema()
        )

        # perform argument infilling
        if len(selected_function_arg_json_schema["properties"]) > 0:
            complete, arguments = await self.do_infilling(
                dependencies,
                message,
                selected_function,
                selected_function_arg_json_schema,
            )
        else:
            complete, arguments = True, {}

        can_autorun = autorun  # and selected_function.can_autoru

        if can_autorun and complete:
            # execute
            async for version in self.execute_function(
                selected_function, arguments, dependencies
            ):
                yield version
            return
        else:
            # request input
            request_user_input = OpasAssistantMessage(
                content=f"""\
    I found the function *{selected_function.display_name or selected_function.id}*.
    Please fill in the following parameters and I'll run it.
    """,
                input_request=FunctionInputRequest(
                    name=selected_function.id,
                    json_schema=selected_function_arg_json_schema,
                    arguments=arguments,
                ),
            )
            yield [request_user_input]
            return

    async def handle_user_input(
        self,
        message: OpasUserMessage,
        all_functions: List[BaseFunction],
        dependencies: Dict[str, Any],
    ) -> AsyncStreamVersion[List[OpasMessage]]:
        if message.input_response is None:
            raise ValueError("message must have input_response")

        selected_function: Optional[BaseFunction] = None

        for f in all_functions:
            if f.id == message.input_response.name:
                selected_function = f

        if selected_function is None:
            raise ValueError("function not found")

        async for version in self.execute_function(
            selected_function, message.input_response.arguments, dependencies
        ):
            yield version

    async def run_chat(
        self,
        messages: List[OpasMessage],
        autorun: bool = True,
        force_select_function: Optional[str] = None,
    ) -> AsyncStreamVersion[List[OpasMessage]]:
        last_message = messages[-1]

        dependencies = {
            "chat_history": messages,
            "summarization_chat_model": self.function_summarization,
        }

        if not isinstance(last_message, OpasUserMessage):
            raise ValueError("last message must be a user message")

        if last_message.input_response is not None:
            async for version in self.handle_user_input(
                last_message, await self.get_all_functions(), dependencies
            ):
                yield version
        else:
            async for version in self.handle_user_plaintext(
                last_message,
                await self.get_all_functions(),
                dependencies,
                autorun,
                force_select_function,
            ):
                yield version
