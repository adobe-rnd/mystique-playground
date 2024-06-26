import os

from server.generation_strategies.base_strategy import AbstractGenerationStrategy, StrategyCategory
from server.llm import create_prompt_from_template, parse_markdown_output, parse_css, LlmClient
from server.scraper import WebScraper
from server.image import image_to_bytes


class AKGenerationStrategy(AbstractGenerationStrategy):
    def id(self):
        return "ak-user-generation"

    def name(self):
        return "Layout Enhancement with User Instructions (AK)"

    def category(self):
        return StrategyCategory.STABLE

    async def generate(self, url, selector, prompt):
        scraper = WebScraper()

        system_prompt = f"""
            You are an expert UX designer known for creating stunning, high-impact web designs.
            Based on the provided CSS, CSS variables, HTML and screenshot of a webpage section (highlighted with red 
            rectangle), make bold, creative modifications that will significantly enhance the overall design and visual 
            appeal of the website.
        """
        llm = LlmClient(system_prompt=system_prompt)
        self.send_progress('Getting the HTML, CSS and screenshot of the original page...')
        extracted_html = await scraper.get_block_html(url, selector)

        # Save the extracted html
        with open('extracted_markup.html', 'w') as f:
            f.write(extracted_html)

        block_css, root_css_vars = await scraper.get_raw_css(url, selector)
        # full_page_screenshot = await scraper.get_full_page_screenshot(url)
        full_page_screenshot = await scraper.get_full_page_screenshot_with_highlight(url, selector)

        self.send_progress('Running the assessment...')

        master_prompt = create_prompt_from_template(
            os.path.dirname(__file__) + "/prompts/user_instructions.txt",
            user_prompt=prompt,
            block_css=block_css,
            root_css_vars=root_css_vars,
            extracted_html=extracted_html
        )

        self.send_progress('Generating CSS variation...')

        raw_output = llm.get_completions(master_prompt, [image_to_bytes(full_page_screenshot)])
        generated_css = parse_css(raw_output)[0]
        # print(generated_css)

        # Save the generated css
        with open('generated_styles.css', 'w') as f:
            f.write(generated_css)

        self.add_css(generated_css)

    def __init__(self):
        super().__init__()
