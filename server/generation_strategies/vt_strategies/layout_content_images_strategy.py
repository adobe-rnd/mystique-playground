import base64
import datetime
import hashlib
import os

from server.dalle import DalleClient
from server.generation_strategies.base_strategy import AbstractGenerationStrategy, StrategyCategory
from server.html_utils import convert_hashes_to_urls
from server.llm import LlmClient, ModelType, parse_markdown_output
from server.scraper import WebScraper


def make_image_generator(dalle, url_mapping):
    def generate_image(prompt):
        """
        description: Generate an image URL based on the provided prompt.
        parameters:
          prompt:
            type: string
            description: The prompt for generating the image.
        returns:
          type: string
          description: THe image URL generated based on the prompt.
        """

        data_url = dalle.generate_image(prompt)

        # Save the image to a file
        os.makedirs('pictures', exist_ok=True)
        header, encoded = data_url.split(",", 1)
        file_extension = header.split("/")[-1].split(";")[0]
        data = base64.b64decode(encoded)
        filename = 'screenshot_{}.{}'.format(datetime.datetime.now().strftime("%Y%m%d_%H%M%S"), file_extension)
        with open(os.path.join('pictures', filename), 'wb') as f:
            f.write(data)

        url_hash = f"hash://{hashlib.md5(data_url.encode()).hexdigest()}"
        url_mapping.update({url_hash: data_url})

        return url_hash

    return generate_image


class LayoutAndContentEnhancementStrategy(AbstractGenerationStrategy):
    def id(self):
        return "layout-content-images"

    def name(self):
        return "Layout and Content + Images Enhancement (VT)"

    def category(self):
        return StrategyCategory.STABLE

    async def generate(self, url, selector, prompt):
        scraper = WebScraper()

        self.send_progress(f"Fetching HTML content from {url}...")
        html, screenshot = await scraper.get_html_and_screenshot(url, selector, with_styles=False)

        system_prompt = f"""
            You are a professional web developer, designer, or content creator.
            You are tasked with enhancing the style, layout, content and images of the following HTML content.
            You MUST not use gradients for background colors.
            You MUST think in steps.
        """

        url_mapping = {}
        generate_image = make_image_generator(DalleClient(), url_mapping)
        llm = LlmClient(ModelType.GPT_4_OMNI, system_prompt=system_prompt)

        analysis_prompt = f"""
            Analyze the provided HTML content to identify its current layout structure.
            Based on your analysis, suggest modifications to alter the layout and improve its appearance.
            Ensure your recommendations are focused on design concepts rather than specific code changes.
            
            ```Tasks:```
            - Propose the changes needed to enhance the style, layout, images and content of the HTML.
            - Make sure to use contrasting colors and appropriate text sizes.
            
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
        - Do NOT use emojis or any other non-HTML elements.
        - Add decorations like borders, shadows, and hover effects to enhance the design. 
        - You MUST replace image URLs with generated image URLs formatted as 'hash://<hash_value>'.
        - Treat all tags of the picture as a single image.
        - Use very detailed and specific instructions for the image generation.
        
        Proposed Changes:
        {proposed_changes}
        
        Original HTML Content:
        {html}
        """

        self.send_progress("Generating new layout and content...")
        llm_response = llm.get_completions(prompt, [screenshot], temperature=0.0, tools=[generate_image])

        print(llm_response)

        new_html = parse_markdown_output(llm_response, lang='html')
        self.replace_html(selector, convert_hashes_to_urls(new_html, url_mapping))

    def __init__(self):
        super().__init__()
