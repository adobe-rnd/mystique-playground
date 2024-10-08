import os

from server.generation_strategies.base_strategy import AbstractGenerationStrategy, StrategyCategory
from server.shared.llm import create_prompt_from_template, parse_markdown_output, LlmClient
from server.shared.scraper import WebScraper


class CssGenerationStrategy(AbstractGenerationStrategy):
    def id(self):
        return "css-generation"

    def name(self):
        return "CSS Generation (VT)"

    async def generate(self, url, selector, prompt):

        scraper = WebScraper()
        llm = LlmClient()

        self.send_progress('Getting the HTML and screenshot of the original page...')
        original_html, original_screenshot = await scraper.get_html_and_screenshot(url, selector, with_styles=True)

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
        instructions = llm.get_completions(assessment_prompt, [original_screenshot])

        self.send_progress('Generating CSS variation...')
        generation_prompt = create_prompt_from_template(
            os.path.dirname(__file__) + "/prompts/generation.txt",
            instructions=instructions,
            html=original_html.strip()
        )
        raw_output = llm.get_completions(generation_prompt, [original_screenshot])
        generated_css = parse_markdown_output(raw_output, lang='css')

        self.add_css(generated_css)

    def __init__(self):
        super().__init__()
