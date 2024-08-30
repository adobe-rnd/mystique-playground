import base64
import io
import os

from PIL import Image

OUTPUT_DIR = 'generated'


def create_page_from_data_model(job_folder, page_data_model, inferred_css_vars, all_images):

    with open(os.path.join(job_folder, 'tokens.css'), 'w') as f:
        f.write(inferred_css_vars)

    with open(os.path.join(job_folder, 'data.js'), 'w') as f:
        f.write(f"export const data = {page_data_model}")

    for image_hash, image_data in all_images.items():
        header, encoded = image_data.split(",", 1)
        file_extension = header.split("/")[-1].split(";")[0]
        data = base64.b64decode(encoded)
        if file_extension != 'png':
            img = Image.open(io.BytesIO(data))
            buffered = io.BytesIO()
            img.save(buffered, format='PNG')
            data = buffered.getvalue()
        filename = f'{image_hash}.png'
        with open(os.path.join(job_folder, filename), 'wb') as f:
            f.write(data)

    with open(os.path.join(job_folder, 'index.html'), 'w') as f:
        f.write(f"""
            <!DOCTYPE html>
            <html lang="en">
            <head>
              <meta charset="UTF-8">
              <meta name="viewport" content="width=device-width, initial-scale=1.0">
              <title>Mystique Reference Page</title>
              <link rel="stylesheet" href="/static/styles.css">
              <link rel="stylesheet" href="/{job_folder}/tokens.css">   
              <script type="module">
                import {{ render }} from '/static/scripts.js';
                import {{ data }} from '/{job_folder}/data.js';
                render(data);
              </script>
            </head>
            <body>
            </body>
            </html>
        """)
