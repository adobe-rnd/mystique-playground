from io import BytesIO

from PIL import Image
from bs4 import BeautifulSoup

from server.shared.image import crop_and_downscale_image
from server.shared.llm import LlmClient, ModelType, parse_markdown_output
from server.shared.scraper import WebScraper


def get_cleaned_buttons_and_links_with_essential_attributes(html_content):
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


async def fetch_html_and_screenshot(website_url: str, job_folder: str) -> tuple[str, bytes]:
    scraper = WebScraper()
    html = await scraper.get_html(website_url)

    print("Compressing HTML for LLM...")
    compressed_html = '\n'.join(get_cleaned_buttons_and_links_with_essential_attributes(html))

    print("Identifying consent button...")
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
    print(f"Identified consent button selector: {consent_button_selector}")

    original_screenshot = await scraper.get_screenshot(website_url, consent_popup_button_selector=consent_button_selector)
    screenshot = crop_and_downscale_image(original_screenshot, crop=True)

    # save screenshot to job folder
    screenshot_path = f'{job_folder}/website_screenshot.png'
    with open(screenshot_path, 'wb') as f:
        f.write(screenshot)

    return html, screenshot
