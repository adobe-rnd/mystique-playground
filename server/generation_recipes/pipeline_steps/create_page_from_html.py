import base64
import io
import os
from typing import Dict, Any
from PIL import Image
from server.generation_recipes.base_pipeline_step import BasePipelineStep


class CreatePageFromHtmlStep(BasePipelineStep):
    def __init__(self, job_folder: str, **kwargs: Any):
        super().__init__(**kwargs)
        self.job_folder = job_folder

    @staticmethod
    def get_unique_id() -> str:
        return "create_page_from_html"

    @staticmethod
    def get_name() -> str:
        return "Create Page from HTML"

    @staticmethod
    def get_description() -> str:
        return "Create a web page from the provided HTML content and save images."

    def process(self, html: str, images: Dict[str, str], **kwargs: Any):
        try:
            # Update status
            self.update_status("Starting to create the page from HTML and saving images...")

            # Ensure the job folder exists
            os.makedirs(self.job_folder, exist_ok=True)

            for image_hash, image_data in images.items():
                header, encoded = image_data.split(",", 1)
                file_extension = header.split("/")[-1].split(";")[0]
                data = base64.b64decode(encoded)

                # Convert non-PNG images to PNG format
                if file_extension != 'png':
                    img = Image.open(io.BytesIO(data))
                    buffered = io.BytesIO()
                    img.save(buffered, format='PNG')
                    data = buffered.getvalue()

                filename = f'{image_hash}.png'
                with open(os.path.join(self.job_folder, filename), 'wb') as f:
                    f.write(data)

            # Save the HTML page
            with open(os.path.join(self.job_folder, 'index.html'), 'w') as f:
                f.write(html)

            self.update_status("Page creation and image saving completed successfully.")

        except Exception as e:
            self.update_status(f"An error occurred: {e}")
            raise e
