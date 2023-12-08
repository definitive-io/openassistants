import abc
import asyncio
import logging
import textwrap
import traceback
from typing import Annotated, Any, Callable, Dict, List, Literal, Optional, Tuple, Union

import jsonschema
from langchain.chains.openai_functions.base import convert_pydantic_to_openai_function
from langchain.chat_models import ChatOpenAI
from pydantic import BaseModel, Field

from openassistants.core.assistant import Assistant
from openassistants.data_models.chat_messages import (
    OpasAssistantMessage,
    OpasFunctionMessage,
    OpasMessage,
    OpasUserMessage,
)
from openassistants.data_models.function_input import FunctionCall
from openassistants.data_models.function_output import DataFrameOutput, TextOutput
from openassistants.eval.base import extract_assistant_autofill_function
from openassistants.utils.async_utils import last_value

logger = logging.getLogger(__name__)


class GradeSummary(BaseModel):
    """Grade a summary against a data table."""

    analysis: Annotated[
        str,
        Field(description="grading analysis of the summary"),
    ]
    pass_fail: Annotated[
        Literal["pass", "fail"],
        Field(description="does the summary pass or fail"),
    ]

    @staticmethod
    def _remove_key_recursive(d: Any, target_key: str):
        if isinstance(d, dict):
            d.pop(target_key, "")
            for key in d:
                d[key] = GradeSummary._remove_key_recursive(d[key], target_key)
        return d

    @classmethod
    def to_openai_function(cls) -> dict:
        schema = convert_pydantic_to_openai_function(cls)  # type: ignore
        if "description" in schema["parameters"]:
            schema["parameters"].pop("description")
        GradeSummary._remove_key_recursive(schema, "title")
        return schema  # type: ignore


InteractionTypes = Annotated[
    Union["SentinelInteraction", "FunctionInteraction"],
    Field(json_schema_extra={"discriminator": "type"}),
]


class BaseInteraction(abc.ABC, BaseModel):
    type: str
    message: str
    children: List[InteractionTypes] = []

    @abc.abstractmethod
    async def run(
        self, chat_history: List[OpasMessage], assistant: Assistant
    ) -> "InteractionReport":
        pass


class InteractionReport(BaseModel):
    interaction: InteractionTypes
    failures: List[str]
    children: List["InteractionReport"]
    function_response: Optional[OpasFunctionMessage] = None
    summary_grading: Optional[GradeSummary] = None

    @staticmethod
    def cascade_failure(interaction: InteractionTypes, failure: str):
        return InteractionReport(
            interaction=interaction,
            failures=[failure],
            children=[
                InteractionReport.cascade_failure(c, "cascading failure from parent")
                for c in interaction.children
            ],
        )

    def pretty_repr(self) -> str:
        this_status = f"{self.interaction.message} - {self.failures}"
        child_status = "\n".join([child.pretty_repr() for child in self.children])
        child_status = textwrap.indent(child_status, "> ")

        return this_status + "\n" + child_status

    def count_condition(
        self,
        condition: Callable[["InteractionReport"], bool],
        ignore_node: Callable[["InteractionReport"], bool] = lambda x: False,
    ) -> Tuple[int, int]:
        ignored = ignore_node(self)
        total = 1 if not ignored else 0
        pos = 1 if (not ignored) and condition(self) else 0
        for child in self.children:
            child_pos, child_total = child.count_condition(condition)
            pos += child_pos
            total += child_total
        return pos, total


class SentinelInteraction(BaseInteraction):
    type: Literal["sentinel"] = "sentinel"
    message: str = "sentinel"

    async def run(
        self, chat_history: List[OpasMessage], assistant: Assistant
    ) -> "InteractionReport":
        children_result: List[InteractionReport] = await asyncio.gather(
            *[c.run(chat_history, assistant) for c in self.children]
        )

        return InteractionReport(
            interaction=self,
            failures=[],
            children=children_result,
        )


class FunctionInteraction(BaseInteraction):
    type: Literal["function"] = "function"
    function: str
    arg_schema: dict = {"type": "object"}
    sample_args: Dict[str, Any] = {}
    summarization_assertions: List[str] = []

    async def validate_function_call(
        self,
        response_messages: List[OpasMessage],
        interaction_report: InteractionReport,
    ):
        function_call = extract_assistant_autofill_function(response_messages[0])

        if function_call is None:
            interaction_report.failures.append(
                f"Could not extract function call from response {response_messages[0]}"
            )

        elif function_call.name != self.function:
            interaction_report.failures.append(
                f"Expected function {self.function} but got {function_call.name}"
            )

        else:
            try:
                jsonschema.validate(function_call.arguments, self.arg_schema)
            except jsonschema.ValidationError as e:
                interaction_report.failures.append(
                    f"Function call arguments did not match schema: {str(e)}"
                )

    async def validate_function_response(
        self,
        response_messages: List[OpasMessage],
        interaction_report: InteractionReport,
    ):
        assistant_function_call, function_response = response_messages

        if not isinstance(assistant_function_call, OpasAssistantMessage):
            interaction_report.failures.append(
                f"Expected OpasAssistantMessage but got "
                f"{type(assistant_function_call)} as first response message"
            )
            return

        if assistant_function_call.function_call is None:
            interaction_report.failures.append(
                "Expected OpasAssistantMessage to have function_call but got None"
            )
            return

        function_name = assistant_function_call.function_call.name
        function_args = assistant_function_call.function_call.arguments

        if not isinstance(function_response, OpasFunctionMessage):
            interaction_report.failures.append(
                f"Expected OpasFunctionMessage but got "
                f"{type(function_response)} as last response message"
            )
            return

        if function_response.name != self.function:
            interaction_report.failures.append(
                f"Expected function {self.function} but got "
                f"{function_response.name}"
            )
            return

        df = None
        summary_text = None

        for o in function_response.outputs:
            if isinstance(o, DataFrameOutput):
                df = o.dataframe.to_pd()

            if isinstance(o, TextOutput):
                summary_text = o.text

        if df is None:
            return (
                [
                    f"Could not find DataFrameOutput in function response "
                    f"{function_response}"
                ],
                None,
                function_response,
            )

        if summary_text is None:
            return (
                [f"Could not find TextOutput in function response {function_response}"],
                None,
                function_response,
            )

        llm = ChatOpenAI(model="gpt-4-0613", temperature=0.0)

        df_csv = df.to_csv(index=False, date_format="iso")
        func = f"{function_name}({function_args}"
        prompt = f"""\
Based on the following data table that was retrieved from calling the function {func})
```
{df_csv}
```

a junior analyst wrote the summary:
```
{summary_text}
```

Please grade the analysts summary.

Split the analysis in 2 sections:
- inaccuracies on facts that can be derived from the data table
- other inaccuracies

Finally provide a pass / fail:
- only take into account 'inaccuracies on the data table facts'
"""

        grading_functions = [GradeSummary.to_openai_function()]
        llm_result = llm.invoke(
            input=prompt,
            functions=grading_functions,
            function_call={"name": GradeSummary.__name__},
        )

        raw_arg = llm_result.additional_kwargs.get("function_call", {}).get(
            "arguments", {}
        )

        grade: GradeSummary = GradeSummary.model_validate_json(raw_arg)

        interaction_report.summary_grading = grade
        interaction_report.function_response = function_response

        if grade.pass_fail == "fail":
            interaction_report.failures.append("Summary failed grading")

    async def run(
        self, chat_history: List[OpasMessage], assistant: Assistant
    ) -> InteractionReport:
        try:
            report = InteractionReport(interaction=self, failures=[], children=[])

            failures: List[str] = []

            user_message = OpasUserMessage(content=self.message)

            response_messages: List[OpasMessage] = await last_value(
                assistant.run_chat(chat_history + [user_message], True)
            )

            # check assistant message
            await self.validate_function_call(response_messages, report)

            # continue with function call
            user_function_call = OpasUserMessage(
                content="",
                input_response=FunctionCall(
                    name=self.function,
                    arguments=self.sample_args,
                ),
            )

            function_response_messages: List[OpasMessage] = await last_value(
                assistant.run_chat(
                    chat_history
                    + [user_message]
                    + response_messages
                    + [user_function_call],
                )
            )

            await self.validate_function_response(function_response_messages, report)

            failures.extend(failures)

            child_coroutines = [
                child.run(
                    chat_history
                    + [user_message]
                    + response_messages
                    + [user_function_call]
                    + function_response_messages,
                    assistant,
                )
                for child in self.children
            ]

            child_results: List[InteractionReport] = await asyncio.gather(
                *child_coroutines
            )  # type: ignore

            report.children.extend(child_results)

            return report

        except Exception as e:
            traceback.print_exc()
            logger.exception(
                f"Exception while running function interaction: {self.message}"
            )
            return InteractionReport.cascade_failure(
                interaction=self,
                failure=f"Exception: {str(e)}",
            )
