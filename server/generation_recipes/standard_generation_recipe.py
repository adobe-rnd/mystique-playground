import os

from server.job_manager import JobStatus, Job
from server.generation_recipes.create_page_structure import create_page_structure
from server.generation_recipes.extract_markdown_content import extract_markdown_content
from server.generation_recipes.fetch_html_and_screenshot import fetch_html_and_screenshot
from server.generation_recipes.generate_html_layout import generate_html_layout
from server.generation_recipes.infer_values_and_generate_css import infer_css_values


class StandardGenerationRecipe(Job):
    def __init__(self, job_id, file_paths, user_intent, website_url):
        super().__init__(job_id)
        self.file_paths = file_paths
        self.user_intent = user_intent
        self.website_url = website_url

    async def run(self):
        try:
            self.set_status(JobStatus.PROCESSING, 'Reading uploaded files...')
            markdown_content = extract_markdown_content(self.file_paths)
            self.set_status(JobStatus.PROCESSING, 'Files read.')

            self.set_status(JobStatus.PROCESSING, 'Generating page structure...')
            page_content = create_page_structure(markdown_content, self.user_intent)
            self.set_status(JobStatus.PROCESSING, 'Page structure generated.')

            self.set_status(JobStatus.PROCESSING, 'Capturing screenshot of the website...')
            html, screenshot = await fetch_html_and_screenshot(self.website_url)
            self.set_status(JobStatus.PROCESSING, 'Screenshot captured.')

            self.set_status(JobStatus.PROCESSING, 'Inferring CSS variables...')
            inferred_css = infer_css_values(screenshot)
            self.set_status(JobStatus.PROCESSING, 'CSS variables inferred.')

            self.set_status(JobStatus.PROCESSING, 'Generating HTML layout...')
            html_output = generate_html_layout(page_content, inferred_css, self.user_intent)
            self.set_status(JobStatus.PROCESSING, 'HTML layout generated.')

            folder_name = self.job_id
            folder_path = os.path.join('generated', folder_name)
            os.makedirs(folder_path)

            file_name = "markup.html"
            file_path = os.path.join(folder_path, file_name)
            with open(file_path, "w") as file:
                file.write(html_output)

            self.set_status(JobStatus.COMPLETED, 'File saved', folder=folder_name, file=file_name)
        except Exception as e:
            self.set_status(JobStatus.ERROR, error=str(e))

