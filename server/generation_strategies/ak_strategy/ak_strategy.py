import os

from server.generation_strategies.base_strategy import AbstractGenerationStrategy
from server.llm import create_prompt_from_template, parse_markdown_output, parse_css, LlmClient
from server.scraper import WebScraper


class AKGenerationStrategy(AbstractGenerationStrategy):
    def id(self):
        return "ak-generation"

    def name(self):
        return "AK Generation"

    async def generate(self, url, selector):
        scraper = WebScraper()
        llm = LlmClient(system_prompt="You are an expert UX designer known for creating stunning, high-impact web designs. Based on the provided CSS, CSS variables and screenshot of a webpage section (highlighted with red rectangle), make bold, creative modifications that will significantly enhance the overall design and visual appeal of the website.")
        self.send_progress('Getting the CSS and screenshot of the original page...')
        # extracted_html, block_screenshot = await scraper.get_html_and_screenshot(url, selector, with_styles=False)

        # Save the extracted html
        # with open('extracted_markup.html', 'w') as f:
        #     f.write(extracted_html)

        block_css, root_css_vars = await scraper.get_raw_css(url, selector)
        # full_page_screenshot = await scraper.get_full_page_screenshot(url)
        full_page_screenshot = await scraper.get_full_page_screenshot_highlight(url, selector)

        self.send_progress('Running the assessment...')

        master_prompt = create_prompt_from_template(
            os.path.dirname(__file__) + "/prompts/on_brand.txt",
            # os.path.dirname(__file__) + "/prompts/off_brand.txt",
            block_css=block_css,
            root_css_vars=root_css_vars
        )

        self.send_progress('Generating CSS variation...')

        raw_output = llm.get_completions(master_prompt, [full_page_screenshot])
        # generated_css = parse_markdown_output(raw_output, lang='css')
        generated_css = parse_css(raw_output)[0]
        # print(generated_css)

        # save the generated css
        with open('generated_styles.css', 'w') as f:
            f.write(generated_css)

        self.add_css(generated_css)

    def __init__(self):
        super().__init__()
