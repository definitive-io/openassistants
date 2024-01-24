import asyncio
from typing import Any, Dict, List, Optional, Tuple

from langchain.chat_models.base import BaseChatModel
from langchain.chat_models.openai import ChatOpenAI
from langchain.embeddings import OpenAIEmbeddings
from langchain.embeddings.base import Embeddings
from openassistants.contrib.index_function import IndexFunction
from openassistants.data_models.chat_messages import (
    OpasAssistantMessage,
    OpasFunctionMessage,
    OpasMessage,
    OpasUserMessage,
)
from openassistants.data_models.function_input import FunctionCall, FunctionInputRequest
from openassistants.functions.base import (
    FunctionExecutionDependency,
    IEntity,
    IFunction,
    IFunctionLibrary,
)
from openassistants.functions.crud import PythonLibrary
from openassistants.llm_function_calling.entity_resolution import resolve_entities
from openassistants.llm_function_calling.fallback import perform_general_qa
from openassistants.llm_function_calling.infilling import (
    generate_argument_decisions,
    generate_arguments,
)
from openassistants.llm_function_calling.selection import (
    SelectFunctionResult,
    select_function,
)
from openassistants.utils.async_utils import AsyncStreamVersion
from openassistants.utils.langchain_util import LangChainCachedEmbeddings
from openassistants.utils.vision import image_url_to_text


class Assistant:
    function_identification: BaseChatModel
    function_infilling: BaseChatModel
    function_summarization: BaseChatModel
    function_fallback: BaseChatModel
    entity_embedding_model: Embeddings
    function_libraries: List[IFunctionLibrary]
    scope_description: str

    _cached_all_functions: List[IFunction]

    def __init__(
        self,
        libraries: List[IFunctionLibrary],
        function_identification: Optional[BaseChatModel] = None,
        function_infilling: Optional[BaseChatModel] = None,
        function_summarization: Optional[BaseChatModel] = None,
        function_fallback: Optional[BaseChatModel] = None,
        vision_model: Optional[BaseChatModel] = None,
        entity_embedding_model: Optional[Embeddings] = None,
        scope_description: str = "General assistant.",
        add_index: bool = True,
    ):
        # instantiate dynamically vs as default args
        self.function_identification = function_identification or ChatOpenAI(
            model="gpt-3.5-turbo-16k", temperature=0.0, max_tokens=128
        )
        self.function_infilling = function_infilling or ChatOpenAI(
            model="gpt-3.5-turbo-16k", temperature=0.0, max_tokens=128
        )
        self.function_summarization = function_summarization or ChatOpenAI(
            model="gpt-3.5-turbo-16k", temperature=0.0, max_tokens=1024
        )
        self.function_fallback = function_fallback or ChatOpenAI(
            model="gpt-4-1106-preview", temperature=0.2, max_tokens=1024
        )
        self.vision_model = vision_model or ChatOpenAI(
            model="gpt-4-vision-preview", temperature=0.2, max_tokens=1024
        )
        self.scope_description = scope_description

        self.entity_embedding_model = (
            entity_embedding_model or LangChainCachedEmbeddings(OpenAIEmbeddings())
        )
        self.function_libraries = libraries

        if add_index:
            index_func: IFunction = IndexFunction(
                id="index",
                display_name="List functions",
                description=(
                    "List the functions available to the assistant. "
                    "This is a list of things you can ask."
                ),
                sample_questions=[
                    "What can you do?",
                    "What can I ask?",
                    "Which functions are defined?",
                ],
                functions=self.get_all_functions,
            )

            self.function_libraries.append(PythonLibrary(functions=[index_func]))

        self._cached_all_functions = []

    async def get_all_functions(self) -> List[IFunction]:
        if not self._cached_all_functions:
            functions: List[IFunction] = []
            for library in self.function_libraries:
                functions.extend(await library.get_all_functions())
            self._cached_all_functions = functions
        return self._cached_all_functions

    async def get_function_by_id(self, function_id: str) -> Optional[IFunction]:
        functions = await self.get_all_functions()
        for function in functions:
            if function.get_id() == function_id:
                return function
        return None

    async def execute_function(
        self,
        function: IFunction,
        func_args: Dict[str, Any],
        dependencies: Dict[str, Any],
    ):
        deps = FunctionExecutionDependency(
            arguments=func_args,
            **dependencies,
        )

        function_call_invocation = OpasAssistantMessage(
            content="",
            function_call=FunctionCall(name=function.get_id(), arguments=func_args),
        )

        yield [function_call_invocation]

        async for version in function.execute(deps):
            yield [
                function_call_invocation,
                OpasFunctionMessage(name=function.get_id(), outputs=list(version)),
            ]

    async def do_infilling(
        self,
        dependencies: dict,
        message: OpasUserMessage,
        selected_function: IFunction,
        args_json_schema: dict,
        entities_info: Dict[str, List[IEntity]],
    ) -> Tuple[bool, dict]:
        # Perform infilling and generate argument decisions in parallel
        chat_history: List[OpasMessage] = dependencies.get("chat_history")  # type: ignore
        arguments_future = asyncio.create_task(
            generate_arguments(
                selected_function,
                self.function_infilling,
                message.content,
                chat_history,
                entities_info,
            )
        )
        argument_decisions_future = asyncio.create_task(
            generate_argument_decisions(
                selected_function,
                self.function_infilling,
                message.content,
                chat_history,
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

    async def run_function_selection(
        self,
        chat_history: List[OpasMessage],
    ) -> SelectFunctionResult:
        all_functions = await self.get_all_functions()

        last_message = chat_history[-1]

        assert isinstance(last_message, OpasUserMessage)
        assert isinstance(last_message.content, str)

        select_function_result = await select_function(
            self.function_identification,
            all_functions,
            last_message.content,
        )

        return select_function_result

    async def handle_user_plaintext(
        self,
        message: OpasUserMessage,
        all_functions: List[IFunction],
        dependencies: Dict[str, Any],
        autorun: bool,
        force_select_function: Optional[str],
    ) -> AsyncStreamVersion[List[OpasMessage]]:
        selected_function: Optional[IFunction] = None
        # perform entity resolution
        chat_history: List[OpasMessage] = dependencies.get("chat_history")  # type: ignore

        # Perform function selection
        if force_select_function is not None:
            filtered = [f for f in all_functions if f.get_id() == force_select_function]
            if len(filtered) == 0:
                raise ValueError("function not found")
            selected_function = filtered[0]

        if selected_function is None:
            function_selection = await self.run_function_selection(
                chat_history=chat_history,
            )

            if function_selection.function:
                selected_function = function_selection.function
            elif function_selection.suggested_functions:
                suggested_functions_names = ", ".join(
                    [f.get_id() for f in function_selection.suggested_functions]
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
                # In case no function was found and no suggested functions were found
                # attempt to directly perform the request requested by the user.
                async for output in perform_general_qa(
                    chat=self.function_fallback,
                    chat_history=dependencies.get("chat_history"),  # type: ignore
                    user_query=message.content,
                    scope_description=self.scope_description,
                ):
                    yield [
                        OpasAssistantMessage(content=output),
                    ]

                return

        selected_function_arg_json_schema = (
            selected_function.get_parameters_json_schema()
        )

        entities_info = await resolve_entities(
            selected_function,
            self.function_infilling,
            self.entity_embedding_model,
            message.content,
            chat_history,
        )

        # perform argument infilling
        if len(selected_function_arg_json_schema["properties"]) > 0:
            complete, arguments = await self.do_infilling(
                dependencies,
                message,
                selected_function,
                selected_function_arg_json_schema,
                entities_info,
            )
        else:
            complete, arguments = True, {}

        can_autorun = autorun
        if selected_function.get_confirm():
            can_autorun = False

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
    I found the function *{selected_function.get_display_name() or selected_function.get_id()}*.
    Please fill in the following parameters and I'll run it.
    """,  # noqa: E501
                input_request=FunctionInputRequest(
                    name=selected_function.get_id(),
                    json_schema=selected_function_arg_json_schema,
                    arguments=arguments,
                ),
            )
            yield [request_user_input]
            return

    async def handle_user_input(
        self,
        message: OpasUserMessage,
        all_functions: List[IFunction],
        dependencies: Dict[str, Any],
    ) -> AsyncStreamVersion[List[OpasMessage]]:
        if message.input_response is None:
            raise ValueError("message must have input_response")

        selected_function: Optional[IFunction] = None

        for f in all_functions:
            if f.get_id() == message.input_response.name:
                selected_function = f

        if selected_function is None:
            raise ValueError("function not found")

        async for version in self.execute_function(
            selected_function, message.input_response.arguments, dependencies
        ):
            yield version

    async def convert_list_message(self, messages, message, idx):
        text_context = " ".join(
            content["text"]
            for content in message.content
            if content.get("type") == "text"
        )
        for i, content in enumerate(message.content):
            if isinstance(content, dict) and content.get("type") == "image_url":
                image_description = "Image described as {}".format(content["filename"])
                if self.vision_model is not None and idx == len(messages) - 1:
                    image_description = image_url_to_text(
                        vision_model=self.vision_model,
                        image_url=content["image_url"],
                        text_context=text_context,
                    )
                message.content[i] = {
                    "type": "text",
                    "text": image_description,
                }
        message.content = " ".join(
            piece["text"] for piece in message.content if piece.get("type") == "text"
        )

    async def pre_process_messages(self, messages):
        tasks = [
            self.convert_list_message(messages, message, idx)
            for idx, message in enumerate(messages)
            if isinstance(message, OpasUserMessage)
            and isinstance(message.content, list)
        ]
        await asyncio.gather(*tasks)
        return messages

    async def run_chat(
        self,
        messages: List[OpasMessage],
        autorun: bool = True,
        force_select_function: Optional[str] = None,
    ) -> AsyncStreamVersion[List[OpasMessage]]:
        last_message = messages[-1]

        messages = await self.pre_process_messages(messages)

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
