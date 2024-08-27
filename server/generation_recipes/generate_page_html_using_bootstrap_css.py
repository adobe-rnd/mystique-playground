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

def generate_page_html_using_bootstrap_css(job_folder: str, page_brief: str, uploaded_images: Dict[str, str], image_captions: Dict[str, str], screenshot: bytes) -> str:
    try:
        # Prepare image captions and hashes for the prompt
        image_info_list = []
        for url_hash, image_url in uploaded_images.items():
            caption = image_captions.get(url_hash, "No caption provided")
            image_url = f"/{job_folder}/{url_hash}.png"
            image_info_list.append(f"Image URL: {image_url}, Caption: {caption}")

        prompt = f'''
        Design a responsive web page using the content provided below. The page should be visually appealing, easy to navigate, and styled consistently with the provided design references.
        
        Requirements:
        
        - The output should be in a single HTML file with all styles embedded within <style> tags.
        - Use Bootstrap’s grid system for the layout structure, and include appropriate Bootstrap components such as buttons, cards, alerts, and navigation bars.
        - The design should match the visual style seen in the provided screenshot, including color schemes, fonts, padding, and margins.
        - Ensure the page includes essential web elements (headers, paragraphs, lists, images, buttons, links, etc.).
        - Organize the content into a clean hierarchy with clear section divisions.
        - The page should either be 70% or 100% width, centered on the screen based on best design practices.
        
        CDN Links for Bootstrap:
        
        <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.2/dist/css/bootstrap.min.css" rel="stylesheet">
        <script src="https://cdn.jsdelivr.net/npm/bootstrap@5.3.2/dist/js/bootstrap.bundle.min.js"></script>
        
        Provided Data:
        
        Page Content:
        {page_brief}
        
        Image Information (including URLs):
        {'\n'.join(image_info_list)}
        
        Important Notes:
        
        - The layout should be clean, well-organized, and visually balanced.
        - Pay attention to typography (font styles, sizes, and weights) and spacing (padding, margins) to align with the provided design reference.
        - Ensure all links and buttons are styled consistently and are easy to interact with.
        - Follow accessibility best practices, including using proper alt text for images and ARIA attributes where relevant.
        '''

        client = LlmClient(model=ModelType.GPT_4_OMNI)
        llm_response = client.get_completions(prompt, temperature=1.0, image_list=[screenshot])
        return parse_markdown_output(llm_response, lang='html')

    except Exception as e:
        print(f"An error occurred: {e}")
        raise e
