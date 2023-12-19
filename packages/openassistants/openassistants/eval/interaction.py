import abc
import asyncio
import textwrap
from typing import Any, Dict, List, Literal, Tuple

from openassistants.core.assistant import Assistant
from openassistants.data_models.chat_messages import (
    OpasAssistantMessage,
    OpasFunctionMessage,
    OpasMessage,
    OpasUserMessage,
)
from openassistants.data_models.function_input import FunctionCall
from openassistants.data_models.function_output import DataFrameOutput, TextOutput
from openassistants.functions.base import IBaseFunction
from openassistants.utils.async_utils import last_value
from pydantic import BaseModel, ConfigDict


class InteractionCheckError(Exception):
    def __init__(self, failure_type: str, comment: str):
        super().__init__(f"[{failure_type}] {comment}")
        self.failure_type = failure_type
        self.comment = comment


class BaseResponseChecker(abc.ABC):
    @abc.abstractmethod
    async def check(self, response: "FunctionInteractionResponse") -> None:
        """
        Check the response
        :raises InteractionCheckError: if the check fails
        """
        pass


class FunctionInteractionNode(BaseModel):
    type: Literal["function"] = "function"
    message: str
    library: str
    function: str
    arg_schema: dict = {"type": "object"}
    sample_args: Dict[str, Any] = {}
    summarization_assertions: List[str] = []


class FunctionInteraction(FunctionInteractionNode):
    children: List["FunctionInteraction"] = []

    async def run_function_selection(
        self,
        assistant: Assistant,
        history_with_user_message: List[OpasMessage],
    ) -> OpasAssistantMessage:
        response_messages = await last_value(
            assistant.run_chat(history_with_user_message, False)
        )
        assistant_selection = response_messages[0]
        assert isinstance(assistant_selection, OpasAssistantMessage)
        return assistant_selection

    async def run_function_infilling(
        self,
        assistant: Assistant,
        history_with_user_message: List[OpasMessage],
    ) -> OpasAssistantMessage:
        response_messages = await last_value(
            assistant.run_chat(history_with_user_message, False)
        )
        assistant_infilling = response_messages[0]
        assert isinstance(assistant_infilling, OpasAssistantMessage)
        return assistant_infilling

    async def run_function_invocation(
        self,
        assistant: Assistant,
        history_with_user_message_input_response: List[OpasMessage],
    ):
        response_messages = await last_value(
            assistant.run_chat(history_with_user_message_input_response, True)
        )
        assistant_function_invocation = response_messages[0]
        function_response = response_messages[1]
        assert isinstance(assistant_function_invocation, OpasAssistantMessage)
        assert isinstance(function_response, OpasFunctionMessage)
        return assistant_function_invocation, function_response

    async def get_function(
        self,
        assistant: Assistant,
    ) -> IBaseFunction:
        base_function = await assistant.get_function_by_id(self.function)
        if base_function is None:
            raise ValueError("Function not found")
        return base_function

    async def run(
        self,
        assistant: Assistant,
        ancestor_response: List["FunctionInteractionResponse"],
    ) -> "FunctionInteractionResponse":
        history: List[OpasMessage] = [
            m  # type: ignore
            for interaction_response in ancestor_response
            for m in interaction_response.as_chat_history()
        ]

        user_message = OpasUserMessage(content=self.message)

        user_input_response = OpasUserMessage(
            content="",
            input_response=FunctionCall(
                name=self.function,
                arguments=self.sample_args,
            ),
        )

        (
            assistant_selection,
            # assistant_infilling,
            (assistant_function_invocation, function_response),
            function_spec,
        ) = await asyncio.gather(
            self.run_function_selection(assistant, history + [user_message]),
            # self.run_function_infilling(client, history + [user_message]),
            self.run_function_invocation(
                assistant, history + [user_message, user_input_response]
            ),
            self.get_function(assistant),
        )

        interaction_response = FunctionInteractionResponse(
            interaction=self,
            user_message=user_message,
            assistant_selection=assistant_selection,
            assistant_infilling=assistant_selection,
            user_input_response=user_input_response,
            assistant_function_invocation=assistant_function_invocation,
            function_response=function_response,
            function_spec=function_spec,
            children=[],
        )

        interaction_response.children = await asyncio.gather(
            *[
                c.run(assistant, ancestor_response + [interaction_response])
                for c in self.children
            ]
        )

        return interaction_response


class FunctionInteractionResponseNode(BaseModel):
    interaction: "FunctionInteractionNode"
    user_message: OpasUserMessage
    assistant_selection: OpasAssistantMessage
    assistant_infilling: OpasAssistantMessage
    user_input_response: OpasUserMessage
    assistant_function_invocation: OpasAssistantMessage
    function_response: OpasFunctionMessage
    function_spec: IBaseFunction


class FunctionInteractionResponse(FunctionInteractionResponseNode):
    children: List["FunctionInteractionResponse"] = []

    def as_chat_history(
        self,
    ) -> Tuple[
        OpasUserMessage,
        OpasAssistantMessage,
        OpasUserMessage,
        OpasAssistantMessage,
        OpasFunctionMessage,
    ]:
        return (
            self.user_message,
            self.assistant_infilling,
            self.user_input_response,
            self.assistant_function_invocation,
            self.function_response,
        )

    async def run_checks(
        self,
        response_checkers: List["BaseResponseChecker"],
    ) -> "InteractionReport":
        tasks = []

        for checker in response_checkers:
            task = asyncio.create_task(checker.check(self))
            tasks.append(task)

        errors: List[Exception] = []

        for t in tasks:
            try:
                await t
            except InteractionCheckError as e:
                errors.append(e)

        report = InteractionReport(
            interaction_response=self,
            failures=errors,
        )

        report.children = await asyncio.gather(
            *[c.run_checks(response_checkers) for c in self.children]
        )

        return report


class InteractionReport(BaseModel):
    model_config = ConfigDict(arbitrary_types_allowed=True)

    interaction_response: "FunctionInteractionResponseNode"
    failures: List[Exception] = []
    children: List["InteractionReport"] = []

    def pretty_repr(self, include_summary=True, include_dataframe=True) -> str:
        failures = "\n".join([str(e) for e in self.failures])

        if len(self.failures) == 0:
            failures = "PASSED"

        response_txt = ""
        for o in self.interaction_response.function_response.outputs:
            if include_dataframe and isinstance(o, DataFrameOutput):
                response_txt += f"[DataFrame]\n{o.dataframe.to_pd().to_markdown()}\n"
            if include_summary and isinstance(o, TextOutput):
                response_txt += f"[Text]\n{o.text}\n"

        this_status = f"""
"{self.interaction_response.interaction.message}"
{response_txt.strip()}
{failures}
"""

        child_status = "\n".join([child.pretty_repr() for child in self.children])
        child_status = textwrap.indent(child_status, "|   ")

        return this_status + child_status
