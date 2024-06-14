from server.generation_strategies.base_strategy import AbstractGenerationStrategy, StrategyCapability
from server.image import downscale_image
from server.llm import LlmClient, ModelType, parse_markdown_output
from server.scraper import WebScraper


class LayoutGenerationStrategy(AbstractGenerationStrategy):
    def id(self):
        return "layout-generation"

    def name(self):
        return "Layout Generation"

    def capabilities(self):
        return [StrategyCapability.GENERATOR]

    async def generate(self, url, selector):
        scraper = WebScraper()

        self.send_progress(f"Fetching HTML content from {url}...")
        html, screenshot = await scraper.get_html_and_screenshot(url, selector, with_styles=True)

        system_prompt = f"""
            You are a professional web designer.
            You are tasked with improving the layout of the following HTML content.
            You must generate a new layout that looks different from the original.
            You must think in steps.
        """

        llm = LlmClient(ModelType.GPT_4_OMNI, system_prompt=system_prompt)

        analysis_prompt = f"""
            Analyze the following HTML content and identify the type of layout it uses.
            Propose a new layout that is different from the original.
            Write down the changes you would make to the layout to make it look different.
            Do not output any code.
            
            {html}
        """

        self.send_progress("Analyzing layout...")
        proposed_changes = llm.get_completions(analysis_prompt, [screenshot])

        prompt = f"""
            You must output the modified HTML only.
            You must use only style attributes to modify the layout.

            {proposed_changes}

            Generate a new layout for the following HTML content.

            {html}
        """

        self.send_progress("Generating new layout...")
        llm_response = llm.get_completions(prompt, [screenshot])

        new_html = parse_markdown_output(llm_response, lang='html')
        self.replace_html(selector, new_html)

    def __init__(self):
        super().__init__()
