import os

import asyncio

from server.generation_strategies.base_strategy import AbstractGenerationStrategy
from server.llm import create_prompt_from_template, get_text_and_image_completions, parse_markdown_output
from server.renderer import get_html_and_screenshot


class DefaultGenerationStrategy(AbstractGenerationStrategy):
    def id(self):
        return "css-v1"

    def name(self):
        return "CSS Generation Strategy (v1)"

    async def generate(self, url, selector):

        self.send_progress('Getting the HTML and screenshot of the original page...')
        original_html, original_screenshot = await get_html_and_screenshot(url, selector)

        self.send_progress('Running the assessment...')
        goals = [
            "Improve conversion rate",
            "Make the styles more consistent with the brand",
            "Improve the overall look and feel of the form"
        ]
        assessment_prompt = create_prompt_from_template(
            os.path.dirname(__file__) + "/prompts/assessment.txt",
            goals=goals,
            html=original_html.strip()
        )
        instructions = get_text_and_image_completions(assessment_prompt, image_data=original_screenshot)

        self.send_progress('Generating CSS variation...')
        generation_prompt = create_prompt_from_template(
            os.path.dirname(__file__) + "/prompts/generation.txt",
            instructions=instructions,
            html=original_html.strip()
        )
        raw_output = get_text_and_image_completions(generation_prompt, image_data=original_screenshot)
        parsed_output = parse_markdown_output(raw_output)

        print(raw_output)
        print(parsed_output['css'])

        self.add_css('\n'.join(parsed_output['css']))

    def __init__(self):
        super().__init__()
