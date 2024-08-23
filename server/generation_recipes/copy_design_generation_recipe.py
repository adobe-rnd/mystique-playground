import os
import asyncio
from concurrent.futures import ThreadPoolExecutor

from server.generation_recipes.create_page_from_html import create_page_from_html
from server.generation_recipes.enhance_user_intent import enhance_user_intent
from server.generation_recipes.generate_image_captions import generate_image_captions
from server.generation_recipes.generate_page_html import generate_page_html
from server.generation_recipes.load_images_from_files import load_images_from_files
from server.job_manager import JobStatus, Job
from server.generation_recipes.extract_markdown_and_images import extract_markdown_and_images
from server.generation_recipes.fetch_html_and_screenshot import fetch_html_and_screenshot


class CopyDesignGenerationRecipe(Job):
    def __init__(self, job_id, job_folder, uploaded_files, user_intent, website_url):
        super().__init__(job_id)
        self.job_folder = job_folder
        self.uploaded_files = uploaded_files
        self.user_intent = user_intent
        self.website_url = website_url

    async def run(self):
        try:
            self.set_status(JobStatus.PROCESSING, 'Processing uploaded documents...')
            loop = asyncio.get_running_loop()

            # Group 1: Schedule tasks concurrently and update status
            self.set_status(JobStatus.PROCESSING, 'Scheduling markdown extraction, image loading, and screenshot capture...')
            markdown_task = loop.run_in_executor(None, extract_markdown_and_images, self.uploaded_files)
            images_task = loop.run_in_executor(None, load_images_from_files, self.uploaded_files)
            html_screenshot_task = fetch_html_and_screenshot(self.website_url, self.job_folder)
            enhance_user_intent_task = loop.run_in_executor(None, enhance_user_intent, self.user_intent)

            # Await results from Group 1 concurrently
            (markdown_content, extracted_images), uploaded_images, (html, screenshot), enhanced_user_intent = await asyncio.gather(
                markdown_task,
                images_task,
                html_screenshot_task,
                enhance_user_intent_task
            )

            self.set_status(JobStatus.PROCESSING, f'Documents converted: {len(markdown_content)}')
            self.set_status(JobStatus.PROCESSING, f'Images extracted: {len(extracted_images)}')
            self.set_status(JobStatus.PROCESSING, f'Images uploaded: {len(uploaded_images)}')

            all_images = {**extracted_images, **uploaded_images}  # Merging the dictionaries

            # Group 2: Schedule image caption generation
            self.set_status(JobStatus.PROCESSING, 'Scheduling image caption generation...')
            caption_task = loop.run_in_executor(None, generate_image_captions, all_images)

            # Await results from Group 2 concurrently
            image_captions = await caption_task
            self.set_status(JobStatus.PROCESSING, 'Image captions generated.')
            print(image_captions)

            # Group 3: Schedule final tasks and update status
            self.set_status(JobStatus.PROCESSING, 'Scheduling HTML generation...')
            page_html_task = loop.run_in_executor(
                None, generate_page_html, self.job_folder, markdown_content, all_images, image_captions, screenshot
            )
            page_html = await page_html_task
            self.set_status(JobStatus.PROCESSING, 'HTML generated.')
            print(page_html)

            self.set_status(JobStatus.PROCESSING, 'Scheduling page save operation...')
            await loop.run_in_executor(None, create_page_from_html, self.job_folder, page_html, all_images)
            self.set_status(JobStatus.COMPLETED, 'Page saved.')

        except Exception as e:
            print(e)
            self.set_status(JobStatus.ERROR, error=str(e))
