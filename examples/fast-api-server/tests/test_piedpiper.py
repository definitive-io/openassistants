import pytest
from fast_api_server.main import hooli_assistant
from openassistants.eval.base import PatternValidation, json_schema
from openassistants.eval.checks.function_infilling import FunctionInfillingCheck
from openassistants.eval.checks.function_selection import FunctionSelectionCheck
from openassistants.eval.interaction import FunctionInteraction

core_interaction = FunctionInteraction(
    message="Show me some recent purchases",
    library="piedpiper",
    function="show_recent_purchases",
    summarization_assertions=[
        "it mentions that purchases were made",
    ],
    children=[
        FunctionInteraction(
            message="send the first person an email about their recent purchase",
            library="piedpiper",
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

entity_resolution_interaction = FunctionInteraction(
    message="what is richard's email address?",
    library="piedpiper",
    function="find_email",
    arg_schema=json_schema(
        {"name": PatternValidation(r"Richard Hendricks")},
        ["name"],
    ),
    sample_args={"name": "Richard Hendricks"},
    summarization_assertions=["it mentions richard's email address"],
)


core_checks = [
    FunctionSelectionCheck(),
    FunctionInfillingCheck(),
]


@pytest.mark.asyncio
async def test_interaction():
    response = await core_interaction.run(hooli_assistant, [])
    report = await response.run_checks(core_checks)
    print(report.pretty_repr())


@pytest.mark.asyncio
async def test_entity_resolution():
    response = await entity_resolution_interaction.run(hooli_assistant, [])
    report = await response.run_checks(core_checks)
    print(report.pretty_repr())
