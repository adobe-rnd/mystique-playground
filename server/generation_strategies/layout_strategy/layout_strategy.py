from server.generation_strategies.base_strategy import AbstractGenerationStrategy
from server.image import downscale_image
from server.llm import LlmClient, ModelType, parse_markdown_output
from server.scraper import WebScraper


class LayoutGenerationStrategy(AbstractGenerationStrategy):
    def id(self):
        return "layout-generation"

    def name(self):
        return "Layout Generation"

    async def generate(self, url, selector):
        section_selector = 'div.section.columns-container'
        scraper = WebScraper()

        self.send_progress(f"Fetching HTML content from {url}...")
        html, screenshot = await scraper.get_html_and_screenshot(url, selector, with_styles=True)

        system_prompt = f"""
            You are an expert UX designer known for creating stunning, high-impact web designs.
            Based on the provided HTML and screenshot of a webpage section, make bold, creative modifications that will 
            significantly enhance the overall design and visual appeal of the website.
            You must think in steps.
        """

        llm = LlmClient(ModelType.GPT_4_OMNI, system_prompt=system_prompt)

        analysis_prompt = f"""
            Analyze the following HTML content and identify the type of layout it uses.
            Propose a new layout to create a distinct looking design.
            Write down the changes you would make to the layout to make it look different.
            Do not output any code.
            ---
            {html}
        """

        self.send_progress("Analyzing layout...")
        proposed_changes = llm.get_completions(analysis_prompt, [screenshot])

        prompt = f"""
            You must output the modified HTML only.
            You must use only style attributes to modify the layout.
            ---
            {proposed_changes}
            ---
            Generate a new layout for the following HTML content.
            ---
            {html}
        """

        self.send_progress("Generating new layout...")
        llm_response = llm.get_completions(prompt, [screenshot])

        new_html = parse_markdown_output(llm_response, lang='html')
        self.replace_html(selector, new_html)

    def __init__(self):
        super().__init__()
