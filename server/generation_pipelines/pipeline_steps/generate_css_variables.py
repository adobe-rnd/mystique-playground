from dataclasses import dataclass

from server.generation_pipelines.pipeline_steps.generate_css_vars import css_variables, generate_css_vars
from server.pipeline_step import PipelineStep
import json
from server.shared.llm import parse_markdown_output, LlmClient, ModelType


@dataclass
class StepResult:
    css_vars: str


class GenerateCssVariablesStep(PipelineStep):
    @staticmethod
    def get_type() -> str:
        return "generate_css_variables"

    @staticmethod
    def get_name() -> str:
        return "CSS Variables"

    @staticmethod
    def get_description() -> str:
        return "Infers CSS variables from a screenshot and generates CSS variables based on the inferred values."

    async def process(self, screenshot: bytes, **kwargs) -> StepResult:
        self.push_update("Inferring CSS variables from screenshot...")

        try:
            infer_values_prompt = f"""
                You are a professional web developer tasked with inferring the CSS variables from a provided screenshot.
                Extract the primary colors, font family, font size, and dimensions such as header height, footer height, sidebar width, padding, and margin.
                Use the extracted values to populate the following variables:

                {', '.join(css_variables.keys())}

                Return the values in a JSON format. Here is an example format for the JSON response:

                {json.dumps(css_variables, indent=4)}

                Provide the JSON response with the inferred values.
            """
            client = LlmClient(model=ModelType.GPT_4_OMNI)
            inferred_values_response = client.get_completions(infer_values_prompt, temperature=0.0, json_output=True, image_list=[screenshot])
            inferred_values = json.loads(parse_markdown_output(inferred_values_response, lang='json'))

            self.push_update("Generating CSS variables...")

            css_vars = generate_css_vars(inferred_values)

            return StepResult(css_vars)

        except Exception as e:
            self.push_update(f"An error occurred: {e}")
            raise e
