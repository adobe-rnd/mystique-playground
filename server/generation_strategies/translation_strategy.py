import asyncio

from server.generation_strategies.base_strategy import AbstractGenerationStrategy
from server.llm import LlmClient, ModelType, parse_markdown_output
from server.scraper import WebScraper


class TranslationStrategy(AbstractGenerationStrategy):
    def id(self):
        return "content-translation"

    def name(self):
        return "Content Translation"

    async def generate(self, url, selector):
        scraper = WebScraper()

        self.send_progress(f"Fetching HTML content from {url}...")
        html, _ = await scraper.get_html_and_screenshot(url, selector, with_styles=False)

        system_prompt = f"""
            You are a professional translator.
            You translate HTML content from English to French.
            You must output the translated HTML only.
        """

        llm = LlmClient(ModelType.GPT_35_TURBO, system_prompt=system_prompt)

        prompt = f"""
            Translate all text in the following HTML to French:
            
            {html}
        """

        self.send_progress("Translating HTML content...")
        llm_response = llm.get_completions(prompt)

        parsed_response = parse_markdown_output(llm_response)

        if 'html' in parsed_response:

            translated_html = '\n'.join(parsed_response['html'])
            self.replace_html(selector, translated_html)

        else:
            raise Exception("Failed to translate HTML content.")

    def __init__(self):
        super().__init__()
