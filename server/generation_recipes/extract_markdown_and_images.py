import os
import base64
import hashlib
from typing import List, Tuple, Dict

import mammoth
from docx import Document


def extract_images_from_docx(docx_file_path: str) -> Dict[str, str]:
    image_hash_map = {}
    document = Document(docx_file_path)

    for rel in document.part.rels.values():
        if "image" in rel.target_ref:
            image_data = rel.target_part.blob
            # Convert the image to a base64-encoded string
            encoded_image = base64.b64encode(image_data).decode('utf-8')
            # Determine the image type (e.g., png, jpeg)
            content_type = rel.target_part.content_type
            # Create a proper data URL
            data_url = f"data:{content_type};base64,{encoded_image}"
            # Generate a hash for the image and store it
            url_hash = hashlib.md5(data_url.encode()).hexdigest()
            image_hash_map[url_hash] = data_url

    return image_hash_map


def skip_images(image):
    # This function explicitly skips images
    return {}


def extract_markdown_and_images(file_paths: List[str]) -> Tuple[List[str], Dict[str, str]]:
    markdown_content = []
    image_hash_map = {}

    docx_files = [file_path for file_path in file_paths if file_path.endswith('.docx')]

    for file_path in docx_files:
        # Here you can use Mammoth for text extraction
        with open(file_path, "rb") as docx_file:
            # Extract text content using Mammoth
            result = mammoth.convert_to_markdown(docx_file, convert_image=skip_images)
            markdown_content.append(result.value)

        # Extract images using python-docx
        extracted_images = extract_images_from_docx(file_path)
        image_hash_map.update(extracted_images)

        # Optionally, remove the docx file if needed
        os.remove(file_path)

    return markdown_content, image_hash_map
