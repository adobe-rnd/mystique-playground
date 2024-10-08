from concurrent.futures import ThreadPoolExecutor, as_completed
from dataclasses import dataclass
from typing import Dict, Any
from PIL import Image
import base64
import io

from server.pipeline_step import StepResultDict, PipelineStep
from server.shared.llm import LlmClient, ModelType


def resize_image(image_data: str, max_size=(128, 128)) -> str:
    try:
        print("Received image data")
        # Check the initial part of the image data string
        print(f"Image data starts with: {image_data[:30]}...")

        # Split the base64 data to isolate the actual image content
        header, encoded = image_data.split(',', 1)
        print(f"Header: {header}")

        # Decode the base64 image data
        image_bytes = base64.b64decode(encoded)
        print("Got image bytes")

        # Load the image using PIL
        image = Image.open(io.BytesIO(image_bytes))
        print("Opened image")

        # Resize the image
        image.thumbnail(max_size, Image.Resampling.BICUBIC)
        print("Resized image")

        # Convert the resized image back to base64
        buffered = io.BytesIO()
        image.save(buffered, format="PNG")
        resized_image_data = base64.b64encode(buffered.getvalue()).decode('utf-8')
        print("Converted image to base64")

        # Return the image data in data URL format
        return f"data:image/png;base64,{resized_image_data}"

    except Exception as e:
        print(f"An error occurred: {e}")
        raise e


def generate_caption_for_image(image_hash: str, data_url: str, llm) -> Dict[str, str]:
    print(f"Generating caption for image {image_hash}...")

    resized_image_url = resize_image(data_url)

    prompt = "Please provide a concise caption for the image below:"
    caption = llm.get_completions(prompt, image_list=[resized_image_url])

    print(f"Generated caption for image {image_hash}: {caption}")

    return {image_hash: caption.strip()}


@dataclass
class ImageCaptions:
    captions: StepResultDict[str]


class GenerateImageCaptionsStep(PipelineStep):
    @staticmethod
    def get_type() -> str:
        return "generate_image_captions"

    @staticmethod
    def get_name() -> str:
        return "Image Captions"

    @staticmethod
    def get_description() -> str:
        return "Generate captions for the provided images."

    def process(self, images: Dict[str, str]) -> ImageCaptions:
        self.push_update("Starting image caption generation...")

        captions = {}
        llm = LlmClient(model=ModelType.GPT_4_OMNI)

        self.push_update("Submitting tasks to generate captions for each image...")

        with ThreadPoolExecutor() as executor:
            future_to_image = {
                executor.submit(generate_caption_for_image, image_hash, data_url, llm): image_hash
                for image_hash, data_url in images.items()
            }

            for future in as_completed(future_to_image):
                try:
                    result = future.result()
                    captions.update(result)
                except Exception as e:
                    print(f"Error generating caption: {e}")
                    self.push_update(f"Error generating caption for an image: {e}")

        self.push_update("Image caption generation completed.")

        return ImageCaptions(captions=captions)
