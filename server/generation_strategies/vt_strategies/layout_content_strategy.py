import os

from server.generation_strategies.base_strategy import AbstractGenerationStrategy, StrategyCategory
from server.shared.llm import LlmClient, ModelType, parse_markdown_output
from server.shared.scraper import WebScraper


class LayoutAndContentEnhancementStrategy(AbstractGenerationStrategy):
    def id(self):
        return "layout-and-content-enhancement"

    def name(self):
        return "Layout and Content Enhancement (VT)"

    def category(self):
        return StrategyCategory.STABLE

    async def generate(self, url, selector, prompt):
        scraper = WebScraper()

        self.send_progress(f"Fetching HTML content from {url}...")
        html, screenshot = await scraper.get_html_and_screenshot(url, selector, with_styles=False)

        system_prompt = f"""
            You are a professional web developer, designer, or content creator.
            You are tasked with enhancing the style, layout and content of the following HTML content.
            You MUST never change or create new images or URLs.
            You MUST think in steps.
            You MUST not use gradients for background colors.
        """

        llm = LlmClient(ModelType.GPT_4_OMNI, system_prompt=system_prompt)

        analysis_prompt = f"""
            Analyze the provided HTML content to identify its current layout structure.
            Based on your analysis, suggest modifications to alter the layout and improve its appearance.
            Ensure your recommendations are focused on design concepts rather than specific code changes.
            
            ```Tasks:```
            - Propose the changes needed to enhance the style, layout, and content of the HTML.
            - Make sure to use contrasting colors and appropriate text sizes.
            - You MUST not propose to change images or URLs.
            
            ```Prompt for Analysis:```
            {prompt}

            ```HTML Content:```
            {html}
        """

        self.send_progress("Analyzing layout and content...")
        proposed_changes = llm.get_completions(analysis_prompt, [screenshot], temperature=0.0)

        prompt = f"""
        You are required to output only the modified HTML content with inline CSS and updated text content.
        Use style attributes exclusively to adjust the layout.
        
        Instructions:
        - Apply the proposed changes specified below.
        - Generate a new layout and update the text content for the provided HTML.
        - Maintain good contrast between text and background colors.
        - Add decorations like borders, shadows, and hover effects to enhance the design. 
        - Do NOT use emojis or any other non-HTML elements.
        - Do NOT change images or URLs.
        
        Proposed Changes:
        {proposed_changes}
        
        Original HTML Content:
        {html}
        """

        self.send_progress("Generating new layout and content...")
        llm_response = llm.get_completions(prompt, [screenshot], temperature=0.0)

        print(llm_response)

        new_html = parse_markdown_output(llm_response, lang='html')
        self.replace_html(selector, new_html)

    def __init__(self):
        super().__init__()
