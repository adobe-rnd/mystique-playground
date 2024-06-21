import io

from PIL import Image
from io import BytesIO
import requests


def load_image(image_source):
    if image_source.startswith('http://') or image_source.startswith('https://'):
        response = requests.get(image_source)
        image = BytesIO(response.content)
    else:
        with open(image_source, "rb") as image_file:
            image = BytesIO(image_file.read())

    return image.read()


def downscale_image(image, max_width, max_height):
    img_ratio = image.width / image.height
    target_ratio = max_width / max_height

    if img_ratio > target_ratio:
        new_width = max_width
        new_height = round(max_width / img_ratio)
    else:
        new_height = max_height
        new_width = round(max_height * img_ratio)

    downscaled_image = image.resize((new_width, new_height))

    return downscaled_image


def image_to_bytes(image: Image.Image, format: str = 'PNG') -> bytes:
    # Create a BytesIO buffer
    buffer = io.BytesIO()
    # Save the image to the buffer in the specified format
    image.save(buffer, format=format)
    # Retrieve the bytes from the buffer
    image_bytes = buffer.getvalue()
    # Close the buffer
    buffer.close()
    return image_bytes
