import pytest
from openassistants.core.assistant import Assistant
from openassistants.eval.base import PatternValidation, json_schema
from openassistants.eval.interaction import FunctionInteraction
from openassistants.eval.run_helpers import run_interaction

core_interaction = FunctionInteraction(
    message="Show me some recent purchases",
    function="show_recent_purchases",
    summarization_assertions=[
        "it mentions that purchases were made",
    ],
    children=[
        FunctionInteraction(
            message="send the first person an email about their recent purchase",
            function="send_purchase_inquiry_email",
            arg_schema=json_schema(
                {"email": PatternValidation(r"richard@piedpiper.com")},
                ["email"],
            ),
            sample_args={"email": "richard@piedpiper.com"},
            summarization_assertions=["it mentions the email has been sent"],
        ),
    ],
)


@pytest.mark.asyncio
async def test_interaction():
    assistant = Assistant(libraries=["piedpiper"])
    await run_interaction(core_interaction, assistant)
