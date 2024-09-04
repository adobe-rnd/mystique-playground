import os
import base64
import hashlib
from dataclasses import dataclass
from typing import List, Tuple, Dict, Any
import mammoth
from docx import Document
from PIL import Image
import io

from server.pipeline_step import StepResultDict, PipelineStep


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

    return markdown_content, image_hash_map


def load_images_from_files(file_paths: List[str]) -> Dict[str, str]:
    allowed_extensions = {'.png', '.jpg', '.jpeg', '.gif', '.bmp', '.tiff', '.webp'}

    hash_map = {}

    image_files = [file_path for file_path in file_paths if os.path.splitext(file_path)[1].lower() in allowed_extensions]

    for file_path in image_files:
        try:
            with Image.open(file_path) as img:
                buffered = io.BytesIO()
                img_format = img.format.lower()  # Convert format to lowercase for consistency
                img.save(buffered, format=img.format)
                encoded_image = base64.b64encode(buffered.getvalue()).decode()

                data_url = f"data:image/{img_format};base64,{encoded_image}"

                url_hash = hashlib.md5(data_url.encode()).hexdigest()

                hash_map[url_hash] = data_url

        except Exception as e:
            print(f"Error processing file {file_path}: {e}")

    return hash_map


@dataclass
class TextContentAndImages:
    text_content: str
    images: StepResultDict[str]


class ProcessUploadedFilesStep(PipelineStep):
    @staticmethod
    def get_type() -> str:
        return "process_files"

    @staticmethod
    def get_name() -> str:
        return "Process Files"

    @staticmethod
    def get_description() -> str:
        return "This step extracts markdown content and images from uploaded DOCX files."

    def process(self, uploaded_files: List[str], **kwargs: Any) -> TextContentAndImages:
        # Update the job status at the start of processing
        self.push_update("Starting extraction of markdown content and images...")

        # Extract markdown and images from DOCX files
        text_content, images = extract_markdown_and_images(uploaded_files)

        # Update status after DOCX processing
        self.push_update(f"Processed {len(uploaded_files)} uploaded DOCX files.")

        # Load additional images from uploaded files
        uploaded_images = load_images_from_files(uploaded_files)

        # Merge both image hash maps
        images.update(uploaded_images)

        # Update status after processing
        self.push_update(f"Processed {len(uploaded_files)} uploaded files.")
        self.push_update(f"Extracted {len(images)} images.")
        self.push_update(f"Extracted {len(text_content)} markdown content blocks.")

        return TextContentAndImages(text_content="\n".join(text_content), images=images)
