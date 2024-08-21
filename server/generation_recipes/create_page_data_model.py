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


def generate_dalle_image(dalle, prompt, url_mapping):
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
    url_mapping.update({url_hash: data_url})

    return url_hash


def make_image_generator(dalle, url_mapping, uploaded_images):
    def generate_image(prompt):
        """
        description: Generate an image URL based on the provided prompt.
        parameters:
          prompt:
            type: string
            description: The prompt for generating the image.
        returns:
          type: string
          description: The image URL generated based on the prompt.
        """
        print(f"Randomly selecting image from uploaded images: {len(uploaded_images)}")
        if uploaded_images and len(uploaded_images) > 0:
            # Choose a random image from the uploaded images
            selected_hash = random.choice(list(uploaded_images.keys()))
            print(f"Selected image hash: {selected_hash}")
            return selected_hash
        else:
            # Fall back to using DALL-E
            return generate_dalle_image(dalle, prompt, url_mapping)

    return generate_image


def create_page_data_model(job_id: str, markdown_content: List[str], screenshot: bytes, page_brief: str, page_narrative: str, user_intent: str, uploaded_images: Dict[str, str]) -> str:
    try:
        root_schema_file = "server/generation_recipes/component_schemas/page.json"
        bundled_schema = bundle_schemas(root_schema_file)

        url_mapping = {}
        generate_image = make_image_generator(DalleClient(), url_mapping, uploaded_images)

        full_prompt = f'''
            You are a professional web developer tasked with creating a data model for a new web page.
            The client has provided the following information:
            
            ### Markdown Content ###
            {'\n'.join(markdown_content)}
            
            ### Page Brief ###
            {page_brief}
            
            ### Page Narrative ###
            {page_narrative}
            
            ### User Intent ###
            {user_intent}
            
            Your task is to transform the provided markdown content, page brief, 
            and page narrative into a well-structured JSON data model that adheres to the page schema.
                        
            ### Page Data Schema ###
            {json.dumps(bundled_schema, indent=2)}

            You MUST generate images URLs for the images and include them in the JSON structure.
            Insert the image URLs like this: /generated/{job_id}/<image_url_hash_string>.png

            The output should be a JSON object that conforms to the provided schema.
            The JSON object MUST not contain the parts of the schema.

            Output the generated data model only in JSON format.
        '''

        client = LlmClient(model=ModelType.GPT_4_OMNI)
        llm_response = client.get_completions(full_prompt, temperature=1.0, json_output=True, json_schema=bundled_schema, tools=[generate_image], image_list=[screenshot])
        generated_data = parse_markdown_output(llm_response, lang='json')

        print("Generated data:")
        print(generated_data)

        validate(instance=json.loads(generated_data), schema=bundled_schema)

        return generated_data

    except Exception as e:
        print(f"An error occurred: {e}")
        raise e
