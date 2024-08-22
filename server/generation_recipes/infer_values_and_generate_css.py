import json

from server.generation_recipes.generate_css_vars import generate_css_vars, css_variables
from server.shared.llm import parse_markdown_output, LlmClient, ModelType


def infer_css_vars(screenshot: bytes) -> str:
    infer_values_prompt = f"""
        You are a professional web developer tasked with inferring the CSS variables from a provided screenshot.
        Extract the primary colors, font family, font size, and dimensions such as header height, footer height, sidebar width, padding, and margin.
        Use the extracted values to populate the following variables:

        {', '.join(css_variables.keys())}

        Return the values in a JSON format. Here is an example format for the JSON response:

        {json.dumps(css_variables, indent=4)}

        Provide the JSON response with the inferred values.
    """
    print(infer_values_prompt)
    client = LlmClient(model=ModelType.GPT_4_OMNI)
    inferred_values_response = client.get_completions(infer_values_prompt, temperature=0.0, json_output=True, image_list=[screenshot])
    print(inferred_values_response)

    inferred_values = json.loads(parse_markdown_output(inferred_values_response, lang='json'))

    return generate_css_vars(inferred_values)
