from server.shared.scraper import WebScraper


async def fetch_html_and_screenshot(website_url: str) -> tuple[str, bytes]:
    scraper = WebScraper()
    return await scraper.get_html_and_screenshot(website_url, selector='body', with_styles=False)
