import hashlib
from dataclasses import dataclass

from server.generation_pipelines.pipeline_steps.read_schemas import bundle_schemas
from server.pipeline_step import PipelineStep
import json
from typing import Dict
from jsonschema.validators import validate
from server.shared.dalle import DalleClient
from server.shared.llm import LlmClient, ModelType, parse_markdown_output

def generate_dalle_image(dalle, prompt, url_mapping, job_folder):
    data_url = dalle.generate_image(prompt)
    url_hash = hashlib.md5(data_url.encode()).hexdigest()
    url_mapping.update({url_hash: data_url})
    return f"/{job_folder}/{url_hash}.png"

def background_image_generator(dalle, url_mapping, job_folder):
    def generate_image(prompt):
        """
        description: Generate a background image based on the provided prompt.
        parameters:
          prompt:
            type: string
            description: The prompt for generating the image.
        returns:
          type: string
          description: The image URL generated based on the prompt.
        """
        return generate_dalle_image(dalle, prompt, url_mapping, job_folder)

    return generate_image

@dataclass
class StepResult:
    data_model: str

class GeneratePageDataModelStep(PipelineStep):
    def __init__(self, job_folder: str, **kwargs):
        super().__init__(**kwargs)
        self.job_folder = job_folder

    @staticmethod
    def get_unique_id() -> str:
        return "generate_page_data_model"

    @staticmethod
    def get_name() -> str:
        return "Data Model"

    @staticmethod
    def get_description() -> str:
        return "Generates a JSON data model for a web page based on provided inputs."

    async def process(self, page_content: str, screenshot: bytes, images: Dict[str, str], captions: Dict[str, str], **kwargs) -> StepResult:
        self.push_update("Generating page data model...")

        try:
            root_schema_file = "server/generation_pipelines/component_schemas/page.json"
            bundled_schema = bundle_schemas(root_schema_file)

            url_mapping = {}
            generate_background_image = background_image_generator(DalleClient(), url_mapping, self.job_folder)

            # Prepare image captions and hashes for the prompt
            image_info_list = []
            for url_hash, image_url in images.items():
                caption = captions.get(url_hash, "No caption provided")
                image_url = f"/{self.job_folder}/{url_hash}.png"
                image_info_list.append(f"Image URL: {image_url}, Caption: {caption}")

            image_info_text = "\n".join(image_info_list)

            full_prompt = f'''
                You are a professional web developer tasked with creating a data model for a new web page.
                The client has provided the following information:
                
                ### Page Content ###
                {page_content}
                
                ### Uploaded Images and Captions ###
                {image_info_text}
                
                Your task is to transform the provided page brief, 
                and page narrative into a well-structured JSON data model that adheres to the page schema.
                
                You generate background images based on the provided prompts to enhance the page data model.
                
                You MUST use provided image URLs literally without any modifications.
                            
                ### Page Data Schema ###
                {json.dumps(bundled_schema, indent=2)}

                The output should be a JSON object that conforms to the provided schema.
                The JSON object MUST not contain the parts of the schema.

                Output the generated data model only in JSON format.
            '''

            client = LlmClient(model=ModelType.GPT_4_OMNI)
            llm_response = client.get_completions(full_prompt, temperature=0.2, json_output=True, json_schema=bundled_schema, image_list=[screenshot], tools=[generate_background_image])
            data_model = parse_markdown_output(llm_response, lang='json')

            validate(instance=json.loads(data_model), schema=bundled_schema)

            # Update the URL mapping with the generated image URLs
            images.update(url_mapping)

            return StepResult(data_model=data_model)

        except Exception as e:
            self.push_update(f"An error occurred: {e}")
            raise e
