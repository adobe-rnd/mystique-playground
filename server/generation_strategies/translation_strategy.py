import asyncio

from server.generation_strategies.base_strategy import AbstractGenerationStrategy, StrategyCapability
from server.llm import LlmClient, ModelType, parse_markdown_output
from server.scraper import WebScraper


class TranslationStrategy(AbstractGenerationStrategy):
    def id(self):
        return "content-translation"

    def name(self):
        return "Content Translation"

    def capabilities(self):
        return [StrategyCapability.GENERATOR]

    async def generate(self, url, selector, prompt):
        scraper = WebScraper()

        self.send_progress(f"Fetching HTML content from {url}...")
        html, _ = await scraper.get_html_and_screenshot(url, selector, with_styles=False, wait_time=60000)

        system_prompt = f"""
            You are a professional translator.
            You translate HTML content from one language to another.
            You must output the translated HTML only.
        """

        llm = LlmClient(ModelType.GPT_4_OMNI, system_prompt=system_prompt)

        prompt = f"""
            Translate all text in the following HTML to {prompt or 'French'}.
            
            {html}
        """

        self.send_progress("Translating HTML content...")
        llm_response = llm.get_completions(prompt)

        translated_html = parse_markdown_output(llm_response, lang='html')

        self.replace_html(selector, translated_html)

    def __init__(self):
        super().__init__()
