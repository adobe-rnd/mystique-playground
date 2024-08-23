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


def generate_dalle_image(dalle, prompt, url_mapping, job_id):
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
    image_url = f"/generated/{job_id}/{url_hash}.png"
    url_mapping.update({image_url: data_url})

    return url_hash


def background_image_generator(dalle, url_mapping, job_id):
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
        return generate_dalle_image(dalle, prompt, url_mapping, job_id)

    return generate_image


def generate_page_html(job_folder: str, markdown_content: List[str], uploaded_images: Dict[str, str], image_captions: Dict[str, str], screenshot: bytes) -> str:
    try:
        # Prepare image captions and hashes for the prompt
        image_info_list = []
        for url_hash, image_url in uploaded_images.items():
            caption = image_captions.get(url_hash, "No caption provided")
            image_url = f"/{job_folder}/{url_hash}.png"
            image_info_list.append(f"Image URL: {image_url}, Caption: {caption}")

        prompt = f'''
        Generate new HTML code that precisely replicates the design and layout shown in the screenshot.
        
        Important details:
        
        1. Use the provided page brief, narrative, and image content for the page. The content must come exclusively from the provided data, not the screenshot.
        2. The screenshot should be used solely as a reference for the layout, structure, and styling.
        3. Ensure that the placement and sizing of elements match the screenshot’s design, using only the provided image URLs and captions.
        4. Include image size styles (width, height) directly in the HTML code to match the proportions and layout in the screenshot. Ensure images maintain their aspect ratios while fitting into the layout.
        5. Maintain the visual hierarchy, alignment, and overall layout identical to the screenshot, but with the content provided below.
        
        ### Provided Data ###
        
        **Page Content:**
        {'\n\n'.join(markdown_content)}
        
        **Image Information (including URLs):**
        {'\n'.join(image_info_list)}
        
        Your task is to create HTML code that exactly mirrors the design in the screenshot using the provided content.
        '''

        client = LlmClient(model=ModelType.GPT_4_OMNI)
        llm_response = client.get_completions(prompt, temperature=1.0, image_list=[screenshot])
        return parse_markdown_output(llm_response, lang='html')

    except Exception as e:
        print(f"An error occurred: {e}")
        raise e
