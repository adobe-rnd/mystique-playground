import base64
import io
import os
from dataclasses import dataclass

from PIL import Image
from server.pipeline_step import PipelineStep, StepResultDict

PREVIEW_URL_TEMPLATE = "http://localhost:4003/preview/{jobId}"


@dataclass
class StepResult:
    url: str


class CreatePageFromDataModelStep(PipelineStep):
    def __init__(self, job_id: str, job_folder: str, **kwargs):
        super().__init__(**kwargs)
        self.job_id = job_id
        self.job_folder = job_folder

    @staticmethod
    def get_type() -> str:
        return "create_page_from_data_model"

    @staticmethod
    def get_name() -> str:
        return "Page from Data Model"

    @staticmethod
    def get_description() -> str:
        return "Creates an HTML page, saves images, and writes CSS and JS files from the provided data model."

    async def process(self, data_model: str, css_vars: str, images: dict, **kwargs) -> StepResult:
        self.push_update("Creating page from data model...")

        try:
            # Save CSS variables
            with open(os.path.join(self.job_folder, 'tokens.css'), 'w') as f:
                f.write(css_vars)

            # Save JavaScript data model
            with open(os.path.join(self.job_folder, 'data.js'), 'w') as f:
                f.write(f"export const data = {data_model};")

            # Process and save images
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

                # Save the image file
                filename = f'{image_hash}.png'
                with open(os.path.join(self.job_folder, filename), 'wb') as f:
                    f.write(data)

            # Create and save the HTML page
            with open(os.path.join(self.job_folder, 'index.html'), 'w') as f:
                f.write(f"""
                    <!DOCTYPE html>
                    <html lang="en">
                    <head>
                      <meta charset="UTF-8">
                      <meta name="viewport" content="width=device-width, initial-scale=1.0">
                      <title>Mystique Reference Page</title>
                      <link rel="stylesheet" href="/static/styles.css">
                      <link rel="stylesheet" href="/{self.job_folder}/tokens.css">   
                      <script type="module">
                        import {{ render }} from '/static/scripts.js';
                        import {{ data }} from '/{self.job_folder}/data.js';
                        render(data);
                      </script>
                    </head>
                    <body>
                    </body>
                    </html>
                """)

            self.push_update("Page creation from data model completed successfully.")

            # Return the URLs of the saved images
            page_url = PREVIEW_URL_TEMPLATE.format(jobId=self.job_id)

            return StepResult(url=page_url)

        except Exception as e:
            self.push_update(f"An error occurred: {e}")
            raise e
