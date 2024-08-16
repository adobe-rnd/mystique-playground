import os
import hashlib
from typing import List, Dict
from PIL import Image
import base64
import io


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

                url_hash = f"hash://{hashlib.md5(encoded_image.encode()).hexdigest()}"

                hash_map[url_hash] = data_url

        except Exception as e:
            print(f"Error processing file {file_path}: {e}")

    return hash_map
