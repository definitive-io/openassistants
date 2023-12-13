from openassistants.eval.interaction import (
    BaseResponseChecker,
    FunctionInteractionResponse,
    InteractionCheckError,
)


class FunctionSelectionCheck(BaseResponseChecker):
    async def check(self, response: FunctionInteractionResponse) -> None:
        if response.assistant_selection.input_request is None:
            raise InteractionCheckError(
                failure_type="Function Selection",
                comment="Expected function selection but got no input request",
            )

        if (
            selected := response.assistant_selection.input_request.name
        ) != response.interaction.function:
            raise InteractionCheckError(
                failure_type="Function Selection",
                comment=f"Expected function {response.interaction.function} but got {selected}",  # noqa: E501
            )
