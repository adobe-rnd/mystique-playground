from dataclasses import dataclass
from typing import Dict, Any

from server.pipeline_step import PipelineStep
from server.shared.llm import LlmClient, ModelType, parse_markdown_output


@dataclass
class GeneratedHtml:
    html: str


class GenerateBootstrapPageHtmlStep(PipelineStep):
    def __init__(self, job_folder: str, runs: int = 1, **kwargs: Any):
        super().__init__(**kwargs)
        self.runs = runs
        print(f"Number of runs: {runs}")
        self.job_folder = job_folder

    @staticmethod
    def get_unique_id() -> str:
        return "generate_bootstrap_page_html"

    @staticmethod
    def get_name() -> str:
        return "Bootstrap HTML"

    @staticmethod
    def get_description() -> str:
        return "This step generates a responsive web page using Bootstrap CSS based on the provided content."

    def process(
            self,
            text_content: str,
            images: Dict[str, str],
            captions: Dict[str, str],
            screenshot: bytes,
            **kwargs: Any
    ) -> GeneratedHtml:
        try:
            # Update the job status at the start of processing
            self.push_update("Starting page HTML generation using Bootstrap CSS...")

            # Prepare image captions and hashes for the prompt
            image_info_list = []
            for url_hash, image_url in images.items():
                caption = captions.get(url_hash, "No caption provided")
                image_url = f"/{self.job_folder}/{url_hash}.png"
                image_info_list.append(f"Image URL: {image_url}, Caption: {caption}")

            # Construct the prompt
            prompt = f'''
            Design a responsive web page using the content provided below. The page should be visually appealing, easy to navigate, and styled consistently with the provided design references.
            
            Requirements:
            
            - The output should be in a single HTML file with all styles embedded within <style> tags.
            - Use Bootstrap’s grid system for the layout structure, and include appropriate Bootstrap components such as buttons, cards, alerts, and navigation bars.
            - The design should match the visual style seen in the provided screenshot, including color schemes, fonts, padding, and margins.
            - Ensure the page includes essential web elements (headers, paragraphs, lists, images, buttons, links, etc.).
            - Organize the content into a clean hierarchy with clear section divisions.
            - The page should either be 70% or 100% width, centered on the screen based on best design practices.
            
            CDN Links for Bootstrap:
            
            <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.2/dist/css/bootstrap.min.css" rel="stylesheet">
            <script src="https://cdn.jsdelivr.net/npm/bootstrap@5.3.2/dist/js/bootstrap.bundle.min.js"></script>
            
            Provided Data:
            
            Page Content:
            {text_content}
            
            Image Information (including URLs):
            {'\n'.join(image_info_list)}
            
            Important Notes:
            
            - The layout should be clean, well-organized, and visually balanced.
            - Pay attention to typography (font styles, sizes, and weights) and spacing (padding, margins) to align with the provided design reference.
            - Ensure all links and buttons are styled consistently and are easy to interact with.
            - Follow accessibility best practices, including using proper alt text for images and ARIA attributes where relevant.
            '''

            # Initialize LLM client and get the HTML response
            client = LlmClient(model=ModelType.GPT_4_OMNI)
            llm_response = client.get_completions(prompt, temperature=1.0, image_list=[screenshot])

            # Parse the LLM output for HTML
            html = parse_markdown_output(llm_response, lang='html')
            self.push_update("HTML generation completed successfully.")

            return GeneratedHtml(html=html)

        except Exception as e:
            self.push_update(f"An error occurred during HTML generation: {e}")
            raise e
