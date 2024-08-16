import os

from server.generation_recipes.generate_image_captions import generate_image_captions
from server.generation_recipes.load_images_from_files import load_images_from_files
from server.generation_recipes.create_page_structure import create_page_structure
from server.job_manager import JobStatus, Job
from server.generation_recipes.create_page_content import create_page_content
from server.generation_recipes.extract_markdown_and_images import extract_markdown_and_images
from server.generation_recipes.fetch_html_and_screenshot import fetch_html_and_screenshot
from server.generation_recipes.generate_html_layout import generate_html_layout
from server.generation_recipes.infer_values_and_generate_css import infer_css_vars


class StandardGenerationRecipe(Job):
    def __init__(self, job_id, file_paths, user_intent, website_url):
        super().__init__(job_id)
        self.file_paths = file_paths
        self.user_intent = user_intent
        self.website_url = website_url

    async def run(self):
        try:
            self.set_status(JobStatus.PROCESSING, 'Processing uploaded documents...')
            markdown_content, extracted_images = extract_markdown_and_images(self.file_paths)
            self.set_status(JobStatus.PROCESSING, f'Documents converted: {len(markdown_content)}')
            self.set_status(JobStatus.PROCESSING, f'Images extracted: {len(extracted_images)}')

            self.set_status(JobStatus.PROCESSING, 'Processing uploaded images...')
            uploaded_images = load_images_from_files(self.file_paths)
            self.set_status(JobStatus.PROCESSING, f'Images uploaded: {len(uploaded_images)}')

            all_images = extracted_images | uploaded_images

            self.set_status(JobStatus.PROCESSING, 'Generating image captions...')
            image_captions = generate_image_captions(all_images)
            self.set_status(JobStatus.PROCESSING, f'Image captions generated: {len(image_captions)}')

            print(image_captions)

            self.set_status(JobStatus.PROCESSING, 'Generating page content...')
            page_content = create_page_content(markdown_content, self.user_intent)
            self.set_status(JobStatus.PROCESSING, 'Page content generated.')

            self.set_status(JobStatus.PROCESSING, 'Creating page structure...')
            page_structure = create_page_structure(page_content, self.user_intent)
            self.set_status(JobStatus.PROCESSING, 'Page structure created.')

            self.set_status(JobStatus.PROCESSING, 'Capturing screenshot of the website...')
            html, screenshot = await fetch_html_and_screenshot(self.website_url)
            self.set_status(JobStatus.PROCESSING, 'Screenshot captured.')

            self.set_status(JobStatus.PROCESSING, 'Inferring CSS variables...')
            inferred_css_vars = infer_css_vars(screenshot)
            self.set_status(JobStatus.PROCESSING, 'CSS variables inferred.')

            self.set_status(JobStatus.PROCESSING, 'Generating HTML layout...')
            html_output = generate_html_layout(page_structure, page_content, all_images, inferred_css_vars, self.user_intent)
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
            print(e)
            self.set_status(JobStatus.ERROR, error=str(e))

