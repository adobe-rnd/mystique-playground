import asyncio

from server.generation_recipes.base_recipe import BaseGenerationRecipe
from server.generation_recipes.create_page_brief import create_page_brief
from server.generation_recipes.create_page_from_data_model import create_page_from_data_model
from server.generation_recipes.create_page_narrative import create_page_narrative
from server.generation_recipes.refine_user_intent import refine_user_intent
from server.generation_recipes.generate_image_captions import generate_image_captions
from server.generation_recipes.generate_page_data_model import generate_page_data_model
from server.generation_recipes.load_images_from_files import load_images_from_files
from server.job_manager import JobStatus, Job
from server.generation_recipes.extract_markdown_and_images import extract_markdown_and_images
from server.generation_recipes.fetch_html_and_screenshot import fetch_html_and_screenshot
from server.generation_recipes.infer_values_and_generate_css import infer_css_vars


class StandardGenerationRecipe(BaseGenerationRecipe):
    def __init__(self, job_id, job_folder, uploaded_files, user_intent, website_url):
        super().__init__(job_id)
        self.job_folder = job_folder
        self.uploaded_files = uploaded_files
        self.user_intent = user_intent
        self.website_url = website_url

    @staticmethod
    def get_id():
        return 'standard_generation_recipe'

    @staticmethod
    def name():
        return 'Standard'

    @staticmethod
    def description():
        return 'A standard generation recipe that generates a webpage based on user intent and uploaded documents.'

    async def run(self):
        try:
            self.set_status(JobStatus.PROCESSING, 'Processing uploaded documents...')
            loop = asyncio.get_running_loop()

            # Group 1: Schedule tasks concurrently and update status
            self.set_status(JobStatus.PROCESSING, 'Scheduling markdown extraction and image loading...')
            markdown_task = loop.run_in_executor(None, extract_markdown_and_images, self.uploaded_files)
            images_task = loop.run_in_executor(None, load_images_from_files, self.uploaded_files)

            self.set_status(JobStatus.PROCESSING, 'Scheduling website screenshot capture...')
            html_screenshot_task = fetch_html_and_screenshot(self.website_url, self.job_folder)

            self.set_status(JobStatus.PROCESSING, 'Scheduling user intent refinement...')
            enhance_user_intent_task = loop.run_in_executor(None, refine_user_intent, self.user_intent)

            # Await results from Group 1
            markdown_content, extracted_images = await markdown_task
            uploaded_images = await images_task
            html, screenshot = await html_screenshot_task
            enhanced_user_intent = await enhance_user_intent_task

            self.set_status(JobStatus.PROCESSING, f'Documents converted: {len(markdown_content)}')
            self.set_status(JobStatus.PROCESSING, f'Images extracted: {len(extracted_images)}')
            self.set_status(JobStatus.PROCESSING, f'Images uploaded: {len(uploaded_images)}')

            all_images = extracted_images | uploaded_images

            # Group 2: Schedule tasks concurrently and update status
            self.set_status(JobStatus.PROCESSING, 'Scheduling image caption generation and page brief creation...')
            caption_task = loop.run_in_executor(None, generate_image_captions, all_images)
            brief_task = loop.run_in_executor(None, create_page_brief, markdown_content, enhanced_user_intent)

            # Await results from Group 2
            image_captions, page_brief = await asyncio.gather(caption_task, brief_task)
            self.set_status(JobStatus.PROCESSING, 'Image captions and page brief generated.')
            print(image_captions)
            print(page_brief)

            # Group 3: Schedule tasks concurrently and update status
            self.set_status(JobStatus.PROCESSING, 'Scheduling page narrative creation and CSS inference...')
            narrative_task = loop.run_in_executor(None, create_page_narrative, markdown_content, page_brief, enhanced_user_intent)
            infer_css_task = loop.run_in_executor(None, infer_css_vars, screenshot)

            # Await results from Group 3
            page_narrative, inferred_css_vars = await asyncio.gather(narrative_task, infer_css_task)
            self.set_status(JobStatus.PROCESSING, 'Page narrative and CSS variables inferred.')
            print(page_narrative)
            print(inferred_css_vars)

            # Group 4: Schedule final tasks and update status
            self.set_status(JobStatus.PROCESSING, 'Scheduling page data model generation...')
            page_data_model = await loop.run_in_executor(
                None, generate_page_data_model, self.job_folder, screenshot, page_brief, page_narrative, enhanced_user_intent, all_images, image_captions
            )
            self.set_status(JobStatus.PROCESSING, 'Page data model generated.')
            print(page_data_model)

            self.set_status(JobStatus.PROCESSING, 'Scheduling page save operation...')
            await loop.run_in_executor(None, create_page_from_data_model, self.job_folder, page_data_model, inferred_css_vars, all_images)
            self.set_status(JobStatus.COMPLETED, 'Page saved.')

        except Exception as e:
            print(e)
            self.set_status(JobStatus.ERROR, f'An error occurred: {e}')
