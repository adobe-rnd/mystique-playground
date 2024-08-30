import asyncio
from dataclasses import dataclass
from typing import List, Any

from server.generation_pipelines.legacy_pipelines.create_page_brief import create_page_brief
from server.generation_pipelines.legacy_pipelines.create_page_from_data_model import create_page_from_data_model
from server.generation_pipelines.legacy_pipelines.create_page_narrative import create_page_narrative
from server.generation_pipelines.legacy_pipelines.extract_markdown_and_images import extract_markdown_and_images
from server.generation_pipelines.legacy_pipelines.fetch_html_and_screenshot import fetch_html_and_screenshot
from server.generation_pipelines.legacy_pipelines.generate_image_captions import generate_image_captions
from server.generation_pipelines.legacy_pipelines.generate_page_data_model import generate_page_data_model
from server.generation_pipelines.legacy_pipelines.infer_values_and_generate_css import infer_css_vars
from server.generation_pipelines.legacy_pipelines.load_images_from_files import load_images_from_files
from server.generation_pipelines.legacy_pipelines.refine_user_intent import refine_user_intent
from server.pipeline_step import PipelineStep, StepResultDict

PREVIEW_URL_TEMPLATE = "http://localhost:4003/preview/{jobId}"

@dataclass
class CreatedPage:
    urls: StepResultDict[str]


class StandardGenerationStep(PipelineStep):
    def __init__(self, job_id: str, job_folder: str, **kwargs):
        super().__init__(**kwargs)
        self.job_id = job_id
        self.job_folder = job_folder

    @staticmethod
    def get_unique_id():
        return 'standard_generation_step'

    @staticmethod
    def get_name():
        return 'Standard Generation Step'

    @staticmethod
    def get_description():
        return 'A standard generation recipe that generates a webpage based using a data model.'

    async def process(self, uploaded_files: List[str],  user_intent: str, website_url: str, **kwargs: Any) -> CreatedPage:
        self.push_update('Processing uploaded documents...')
        loop = asyncio.get_running_loop()

        # Group 1: Schedule tasks concurrently and update status
        self.push_update('Scheduling markdown extraction and image loading...')
        markdown_task = loop.run_in_executor(None, extract_markdown_and_images, uploaded_files)
        images_task = loop.run_in_executor(None, load_images_from_files, uploaded_files)

        self.push_update('Scheduling website screenshot capture...')
        html_screenshot_task = fetch_html_and_screenshot(website_url, self.job_folder)

        self.push_update('Scheduling user intent refinement...')
        enhance_user_intent_task = loop.run_in_executor(None, refine_user_intent, user_intent)

        # Await results from Group 1
        markdown_content, extracted_images = await markdown_task
        uploaded_images = await images_task
        html, screenshot = await html_screenshot_task
        enhanced_user_intent = await enhance_user_intent_task

        self.push_update(f'Documents converted: {len(markdown_content)}')
        self.push_update(f'Images extracted: {len(extracted_images)}')
        self.push_update(f'Images uploaded: {len(uploaded_images)}')

        all_images = extracted_images | uploaded_images

        # Group 2: Schedule tasks concurrently and update status
        self.push_update('Scheduling image caption generation and page brief creation...')
        caption_task = loop.run_in_executor(None, generate_image_captions, all_images)
        brief_task = loop.run_in_executor(None, create_page_brief, markdown_content, enhanced_user_intent)

        # Await results from Group 2
        image_captions, page_brief = await asyncio.gather(caption_task, brief_task)
        self.push_update('Image captions and page brief generated.')
        print(image_captions)
        print(page_brief)

        # Group 3: Schedule tasks concurrently and update status
        self.push_update('Scheduling page narrative creation and CSS inference...')
        narrative_task = loop.run_in_executor(None, create_page_narrative, markdown_content, page_brief, enhanced_user_intent)
        infer_css_task = loop.run_in_executor(None, infer_css_vars, screenshot)

        # Await results from Group 3
        page_narrative, inferred_css_vars = await asyncio.gather(narrative_task, infer_css_task)
        self.push_update('Page narrative and CSS variables inferred.')
        print(page_narrative)
        print(inferred_css_vars)

        # Group 4: Schedule final tasks and update status
        self.push_update('Scheduling page data model generation...')
        page_data_model = await loop.run_in_executor(
            None, generate_page_data_model, self.job_folder, screenshot, page_brief, page_narrative, enhanced_user_intent, all_images, image_captions
        )
        self.push_update('Page data model generated.')
        print(page_data_model)

        self.push_update('Scheduling page save operation...')
        await loop.run_in_executor(None, create_page_from_data_model, self.job_folder, page_data_model, inferred_css_vars, all_images)
        self.push_update('Page saved.')

        url = PREVIEW_URL_TEMPLATE.format(jobId=self.job_id)

        return CreatedPage(urls={'url0': url})
