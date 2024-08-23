import base64
import io
import os

from PIL import Image

def create_page_from_html(job_folder, page_html, all_images):
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
        f.write(page_html)
