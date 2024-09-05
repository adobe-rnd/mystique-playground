from dataclasses import dataclass

from bs4 import BeautifulSoup

from server.pipeline_step import PipelineStep
from server.shared.image import crop_and_downscale_image
from server.shared.llm import LlmClient, ModelType, parse_markdown_output
from server.shared.scraper import WebScraper


@dataclass
class ScreenshotResult:
    screenshot: bytes


def get_buttons_and_links_with_essential_attributes(html_content: str) -> list[str]:
    soup = BeautifulSoup(html_content, "html.parser")

    # Find all <a> and <button> elements
    elements = soup.find_all(['a', 'button'])

    cleaned_html_list = []

    for element in elements:
        # Remove all inner tags, keeping only the textual content
        for inner_tag in element.find_all(True):
            inner_tag.unwrap()  # Removes the tag while preserving its content

        # Retain essential attributes: href (for <a>), type and aria-label (for <button>), and class/id
        if element.name == 'a':
            # Keep 'href', 'class', and 'id' attributes
            element.attrs = {
                'href': element.get('href'),
                'class': element.get('class'),
                'id': element.get('id')
            }
        elif element.name == 'button':
            # Keep 'type', 'aria-label', 'class', and 'id' attributes
            element.attrs = {
                'type': element.get('type'),
                'aria-label': element.get('aria-label'),
                'class': element.get('class'),
                'id': element.get('id')
            }

        # Clean None values from attributes
        element.attrs = {k: v for k, v in element.attrs.items() if v is not None}

        # Append the cleaned outer HTML
        cleaned_html_list.append(str(element))

    return cleaned_html_list


class FetchScreenshotStep(PipelineStep):
    def __init__(self, job_folder: str, max_width: int = 1024, max_height: int = 1024, **kwargs):
        super().__init__(**kwargs)
        print(f"max_width: {max_width}, max_height: {max_height}")
        print(f"max_width: {type(max_width)}, max_height: {type(max_height)}")
        self.max_width = max_width
        self.max_height = max_height
        self.job_folder = job_folder

    @staticmethod
    def get_type() -> str:
        return "fetch_screenshot"

    @staticmethod
    def get_name() -> str:
        return "Capture Screenshot"

    @staticmethod
    def get_description() -> str:
        return "Capture a screenshot of the webpage."

    async def process(self, website_url: str, **kwargs) -> ScreenshotResult:
        self.push_update("Starting screenshot capture process...")

        scraper = WebScraper()

        self.push_update(f"Fetching HTML content from {website_url}...")
        html_content = await scraper.get_html(website_url)

        self.push_update("Cleaning HTML content for LLM processing...")
        compressed_html = '\n'.join(get_buttons_and_links_with_essential_attributes(html_content))

        self.push_update("Identifying consent button using LLM...")
        llm = LlmClient(model=ModelType.GPT_4_OMNI)

        prompt = f"""
        Identify the CSS selector for the consent button in the following HTML code.
        
        The button usually performs actions like:
        - Accepting cookies
        - Agreeing to terms or conditions
        - Closing privacy pop-ups
        
        It might include text such as:
        - "Accept"
        - "Agree"
        - "Consent"
        - "OK"
        - Similar terms
        
        **Output**: Provide only the CSS selector as plain text.
        
        ### HTML Code ###
        {compressed_html}
        """

        llm_response = llm.get_completions(prompt, temperature=0.0)
        consent_button_selector = parse_markdown_output(llm_response, lang='css')
        self.push_update(f"Identified consent button selector: {consent_button_selector}")

        self.push_update("Taking screenshot and cropping the image...")
        original_screenshot = await scraper.get_screenshot(website_url, consent_popup_button_selector=consent_button_selector)

        self.push_update(f"Resizing the image to a maximum of {self.max_width}x{self.max_height}...")
        screenshot = crop_and_downscale_image(original_screenshot, max_width=self.max_width, max_height=self.max_height, crop=True)

        screenshot_path = f'{self.job_folder}/website_screenshot.png'
        with open(screenshot_path, 'wb') as f:
            f.write(screenshot)

        self.push_update("Screenshot saved and process completed.")
        return ScreenshotResult(screenshot=screenshot)
