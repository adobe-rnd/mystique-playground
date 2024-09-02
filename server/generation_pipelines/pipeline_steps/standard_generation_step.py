import asyncio
from dataclasses import dataclass
from typing import List, Any, Dict

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

    def process(
            self,
            user_intent: str,
            text_content: str,
            images: Dict[str, str],
            captions: Dict[str, str],
            screenshot: bytes,
            **kwargs: Any
    ) -> CreatedPage:

        self.push_update('Processing uploaded documents...')

        self.push_update('Refining user intent...')
        refined_user_intent = refine_user_intent(user_intent)

        self.push_update('Creating page brief...')
        page_brief = create_page_brief([text_content], refined_user_intent)

        self.push_update('Creating page narrative...')
        page_narrative = create_page_narrative([text_content], page_brief, refined_user_intent)

        self.push_update('Inferring CSS variables...')
        inferred_css_vars = infer_css_vars(screenshot)

        self.push_update('Generating page data model...')
        page_data_model = generate_page_data_model(self.job_folder, screenshot, page_brief, page_narrative, refined_user_intent, images, captions)

        self.push_update('Creating page from data model...')
        create_page_from_data_model(self.job_folder, page_data_model, inferred_css_vars, images)

        self.push_update('Page saved.')

        url = PREVIEW_URL_TEMPLATE.format(jobId=self.job_id)

        return CreatedPage(urls={'url0': url})
