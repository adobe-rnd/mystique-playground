from dataclasses import dataclass

from server.pipeline_step import PipelineStep
from server.shared.scraper import WebScraper

@dataclass
class HtmlResult:
    html: str

class FetchHtmlStep(PipelineStep):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)

    @staticmethod
    def get_unique_id() -> str:
        return "fetch_html"

    @staticmethod
    def get_name() -> str:
        return "Fetch HTML"

    @staticmethod
    def get_description() -> str:
        return "Fetch HTML content from a website."

    async def process(self, website_url: str, **kwargs) -> HtmlResult:
        self.push_update("Starting HTML fetching process...")

        scraper = WebScraper()
        self.push_update(f"Fetching HTML content from {website_url}...")

        html = await scraper.get_html(website_url)

        self.push_update("HTML content fetched successfully.")
        return HtmlResult(html=html)
