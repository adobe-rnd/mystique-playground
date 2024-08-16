from typing import Dict

from server.generation_recipes.css_styles import css_styles
from server.generation_recipes.html_fragments import html_fragments_concatenated
from server.shared.dalle import DalleClient
from server.shared.html_utils import insert_css_into_html, convert_hashes_to_urls
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

    url_hash = f"hash://{hashlib.md5(data_url.encode()).hexdigest()}"
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
        if uploaded_images and len(uploaded_images) > 0:
            # Choose a random image from the uploaded images
            selected_hash = random.choice(list(uploaded_images.keys()))
            print(f"Selected image hash: {selected_hash}")
            return selected_hash
        else:
            # Fall back to using DALL-E
            return generate_dalle_image(dalle, prompt, url_mapping)

    return generate_image


def generate_html_layout(page_structure: str, markdown_content: str, uploaded_images: Dict[str, str], inferred_css_vars: str, user_intent: str) -> str:
    client = LlmClient(model=ModelType.GPT_4_OMNI)

    url_mapping = {}
    generate_image = make_image_generator(DalleClient(), url_mapping, uploaded_images)

    full_prompt = f'''
        You are a professional web developer tasked with transforming markdown content into a well-structured HTML page layout.
        
        INSTRUCTIONS:        
        - The page must be composed only of the components defined in the given HTML structure.
        - Do not generate CSS classes or IDs.
        - Do not generate inline styles.
        - You MUST replace or create image src attributes with generated image URLs formatted as 'hash://<hash_value>'.
        
        Ensure the layout aligns with the user's intent: {user_intent}.
            
        Page structure in JSON format:
        
        {page_structure} 
    
        HTML Fragments to Use:
        
        {html_fragments_concatenated}
    
        {markdown_content}

        INSTRUCTIONS:        
        - The page must be composed only of the components defined in the given HTML structure.
        - Do not generate CSS classes or IDs.
        - Do not generate inline styles.
        - You MUST replace or create image src attributes with generated image URLs formatted as 'hash://<hash_value>'.
        
        GOAL: Create a well-structured HTML page layout based on the provided markdown content, components templates and user intent.
    '''

    llm_response = client.get_completions(full_prompt, temperature=0.0, tools=[generate_image])

    generated_page = parse_markdown_output(llm_response, lang='html')
    generated_page_with_images = convert_hashes_to_urls(generated_page, url_mapping | uploaded_images)
    final_page = insert_css_into_html(generated_page_with_images, [inferred_css_vars, css_styles])

    return final_page
