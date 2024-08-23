import json
from typing import Dict, List

from jsonschema.validators import validate

from server.generation_recipes.read_schemas import bundle_schemas
from server.shared.dalle import DalleClient
from server.shared.llm import LlmClient, ModelType, parse_markdown_output

import os
import base64
import datetime
import hashlib
import random

GENERATED_IMAGES_DIR = 'pictures'


def generate_dalle_image(dalle, prompt, url_mapping, job_folder):
    data_url = dalle.generate_image(prompt)

    # Save the image to a file
    os.makedirs('pictures', exist_ok=True)
    header, encoded = data_url.split(",", 1)
    file_extension = header.split("/")[-1].split(";")[0]
    data = base64.b64decode(encoded)
    filename = 'screenshot_{}.{}'.format(datetime.datetime.now().strftime("%Y%m%d_%H%M%S"), file_extension)
    with open(os.path.join(GENERATED_IMAGES_DIR, filename), 'wb') as f:
        f.write(data)

    url_hash = hashlib.md5(data_url.encode()).hexdigest()
    image_url = f"/{job_folder}/{url_hash}.png"
    url_mapping.update({image_url: data_url})

    return url_hash


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


def generate_page_data_model(job_folder: str, markdown_content: List[str], screenshot: bytes, page_brief: str, page_narrative: str, user_intent: str, uploaded_images: Dict[str, str], image_captions: Dict[str, str]) -> str:
    try:
        root_schema_file = "server/generation_recipes/component_schemas/page.json"
        bundled_schema = bundle_schemas(root_schema_file)

        url_mapping = {}
        generate_background_image = background_image_generator(DalleClient(), url_mapping, job_folder)

        # Prepare image captions and hashes for the prompt
        image_info_list = []
        for url_hash, image_url in uploaded_images.items():
            caption = image_captions.get(url_hash, "No caption provided")
            image_url = f"/{job_folder}/{url_hash}.png"
            image_info_list.append(f"Image URL: {image_url}, Caption: {caption}")

        image_info_text = "\n".join(image_info_list)

        full_prompt = f'''
            You are a professional web developer tasked with creating a data model for a new web page.
            The client has provided the following information:
            
            ### Page Brief ###
            {page_brief}
            
            ### Page Narrative ###
            {page_narrative}
            
            ### User Intent ###
            {user_intent}

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
        generated_data = parse_markdown_output(llm_response, lang='json')

        print("Generated data:")
        print(generated_data)

        validate(instance=json.loads(generated_data), schema=bundled_schema)

        return generated_data

    except Exception as e:
        print(f"An error occurred: {e}")
        raise e
