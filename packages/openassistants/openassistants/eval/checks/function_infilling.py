import jsonschema
from openassistants.eval.interaction import (
    BaseResponseChecker,
    FunctionInteractionResponse,
    InteractionCheckError,
)


class FunctionInfillingCheck(BaseResponseChecker):
    async def check(self, response: FunctionInteractionResponse) -> None:
        if response.assistant_infilling.input_request is None:
            raise InteractionCheckError(
                failure_type="Function Infilling",
                comment="Expected input request",
            )

        try:
            jsonschema.validate(
                response.assistant_infilling.input_request.arguments,
                response.interaction.arg_schema,
            )
        except jsonschema.ValidationError as e:
            raise InteractionCheckError(
                failure_type="Function Infilling",
                comment=f"Function call arguments did not match schema: {str(e)}",
            ) from e
