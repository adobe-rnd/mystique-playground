import os

from server.generation_recipes.create_page_brief import create_page_brief
from server.generation_recipes.create_page_data_model import create_page_data_model
from server.generation_recipes.create_page_narrative import create_page_narrative
from server.generation_recipes.generate_image_captions import generate_image_captions
from server.generation_recipes.load_images_from_files import load_images_from_files
from server.generation_recipes.save_page import save_page
from server.job_manager import JobStatus, Job
from server.generation_recipes.extract_markdown_and_images import extract_markdown_and_images
from server.generation_recipes.fetch_html_and_screenshot import fetch_html_and_screenshot
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

            self.set_status(JobStatus.PROCESSING, 'Creating page brief...')
            page_brief = create_page_brief(markdown_content, self.user_intent)
            self.set_status(JobStatus.PROCESSING, 'Page brief created.')

            print(page_brief)

            self.set_status(JobStatus.PROCESSING, 'Creating page narrative...')
            page_narrative = create_page_narrative(markdown_content, page_brief, self.user_intent)
            self.set_status(JobStatus.PROCESSING, 'Page narrative created.')

            print(page_narrative)

            self.set_status(JobStatus.PROCESSING, 'Capturing screenshot of the website...')
            html, screenshot = await fetch_html_and_screenshot(self.website_url)
            self.set_status(JobStatus.PROCESSING, 'Screenshot captured.')

            self.set_status(JobStatus.PROCESSING, 'Inferring CSS variables...')
            inferred_css_vars = infer_css_vars(screenshot)
            self.set_status(JobStatus.PROCESSING, 'CSS variables inferred.')

            print(inferred_css_vars)

            self.set_status(JobStatus.PROCESSING, 'Generating page data model...')
            page_data_model = create_page_data_model(self.job_id, markdown_content, screenshot, page_brief, page_narrative, self.user_intent, all_images)
            self.set_status(JobStatus.PROCESSING, 'Page data model generated.')

            print(page_data_model)

            self.set_status(JobStatus.PROCESSING, 'Saving page...')
            save_page(self.job_id, page_data_model, inferred_css_vars, all_images)
            self.set_status(JobStatus.COMPLETED, 'Page saved.')
        except Exception as e:
            print(e)
            self.set_status(JobStatus.ERROR, error=str(e))

