import os

from server.generation_strategies.base_strategy import AbstractGenerationStrategy
from server.llm import create_prompt_from_template, parse_markdown_output, parse_css, LlmClient
from server.scraper import WebScraper


class AKGenerationStrategy(AbstractGenerationStrategy):
    def id(self):
        return "ak-user-generation"

    def name(self):
        return "AK User Generation"

    async def generate(self, url, selector, user_prompt=''):
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
        full_page_screenshot = await scraper.get_full_page_screenshot_highlight(url, selector)

        self.send_progress('Running the assessment...')

        master_prompt = create_prompt_from_template(
            os.path.dirname(__file__) + "/prompts/user_instructions.txt",
            user_prompt=user_prompt,
            block_css=block_css,
            root_css_vars=root_css_vars,
            extracted_html=extracted_html
        )

        self.send_progress('Generating CSS variation...')

        raw_output = llm.get_completions(master_prompt, [full_page_screenshot])
        generated_css = parse_css(raw_output)[0]
        # print(generated_css)

        # Save the generated css
        with open('generated_styles.css', 'w') as f:
            f.write(generated_css)

        self.add_css(generated_css)

    def __init__(self):
        super().__init__()
