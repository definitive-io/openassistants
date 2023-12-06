from openassistants.core.assistant import Assistant
from openassistants.data_models.function_output import DataFrameOutput, TextOutput
from openassistants.eval.interaction import BaseInteraction, InteractionReport


async def run_interaction(interaction: BaseInteraction, assistant: Assistant):
    result = await interaction.run([], assistant)

    print(result.pretty_repr())
    show_results(result)


def show_results(parsed: InteractionReport):
    def ignore_sentinel(report: InteractionReport) -> bool:
        return report.interaction.type == "sentinel"

    def summary_is_ok(report: InteractionReport) -> bool:
        if (
            report.summary_grading is not None
            and report.summary_grading.pass_fail == "fail"
        ):
            print("--Message--")
            print(report.interaction.message)

            assert report.function_response is not None

            for o in report.function_response.outputs:
                if isinstance(o, DataFrameOutput):
                    print("\n--DF--")
                    print(o.dataframe.to_pd().to_markdown(index=False))
                if isinstance(o, TextOutput):
                    print("\n--Summary--")
                    print(o.text)

            print("\n--Critique--")
            print(report.summary_grading.analysis)
            print("\n\n")
            return False
        else:
            return True

    print(parsed.count_condition(summary_is_ok, ignore_node=ignore_sentinel))
