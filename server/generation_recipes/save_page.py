import base64
import io
import os

from PIL import Image

OUTPUT_DIR = 'generated'


def save_page(job_id, page_data_model, inferred_css_vars, all_images):

    folder_path = os.path.join(OUTPUT_DIR, job_id)
    os.makedirs(folder_path)

    with open(os.path.join(folder_path, 'tokens.css'), 'w') as f:
        f.write(inferred_css_vars)

    with open(os.path.join(folder_path, 'data.js'), 'w') as f:
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
        with open(os.path.join(folder_path, filename), 'wb') as f:
            f.write(data)

    with open(os.path.join(folder_path, 'index.html'), 'w') as f:
        f.write(f"""
            <!DOCTYPE html>
            <html lang="en">
            <head>
              <meta charset="UTF-8">
              <meta name="viewport" content="width=device-width, initial-scale=1.0">
              <title>Mystique Reference Page</title>
              <link rel="stylesheet" href="/static/styles.css">
              <link rel="stylesheet" href="/generated/{job_id}/tokens.css">   
              <script type="module">
                import {{ render }} from '/static/scripts.js';
                import {{ data }} from '/generated/{job_id}/data.js';
                render(data);
              </script>
            </head>
            <body>
            </body>
            </html>
        """)
