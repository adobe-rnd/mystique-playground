from server.generation_strategies.base_strategy import AbstractGenerationStrategy
from server.scraper import WebScraper


class ExtractCssStrategy(AbstractGenerationStrategy):
    def id(self):
        return "extract-css-strategy"

    def name(self):
        return "Extract CSS Strategy"

    async def generate(self, url, selector):
        scraper = WebScraper()

        self.send_progress('Extracting CSS styles...')
        block_css, root_css_vars = await scraper.get_raw_css(url, selector)

        # write css to file
        with open('raw_block.css', 'w') as f:
            f.write(block_css)

        with open('style_vars.css', 'w') as f:
            f.write(root_css_vars)

    def __init__(self):
        super().__init__()
