import asyncio

from server.generation_strategies.base_strategy import AbstractGenerationStrategy, StrategyCategory
from server.shared.llm import LlmClient, ModelType, parse_markdown_output
from server.shared.scraper import WebScraper


class TranscreationStrategy(AbstractGenerationStrategy):
    def id(self):
        return "transcreation"

    def name(self):
        return "Transcreation (VT)"

    def category(self):
        return StrategyCategory.STABLE

    async def generate(self, url, selector, prompt):
        scraper = WebScraper()

        self.send_progress(f"Fetching HTML content from {url}...")
        html, _ = await scraper.get_html_and_screenshot(url, selector, with_styles=False)

        system_prompt = f"""
            You are a professional copywriter and translator.
            You need to rewrite the provided HTML content to make it more engaging for a given audience.
            You must output the modified HTML only.
        """

        llm = LlmClient(ModelType.GPT_4_OMNI, system_prompt=system_prompt)

        prompt = f"""
            Rewrite the text content in the following HTML to make it more engaging for a {prompt} audience.
            
            {html}
        """

        self.send_progress("Rewriting content...")
        llm_response = llm.get_completions(prompt)

        translated_html = parse_markdown_output(llm_response, lang='html')

        self.replace_html(selector, translated_html)

    def __init__(self):
        super().__init__()
