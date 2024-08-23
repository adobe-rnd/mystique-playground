import base64
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

    return Image.open(image)


def crop_and_downscale_image(image_data, max_width=1024, max_height=1024, crop=False):
    # Convert the bytes input to a PIL Image object
    image = Image.open(BytesIO(image_data))

    if crop:
        # If the image is wider than it is tall, crop using the full height
        if image.width > image.height:
            cropped_image = image.crop((0, 0, image.height, image.height))
        else:
            # Crop a square from the top using the image's width
            square_size = image.width
            cropped_image = image.crop((0, 0, square_size, square_size))

        # Calculate the new dimensions to fit the cropped image within the bounding box
        aspect_ratio = cropped_image.width / cropped_image.height
        if aspect_ratio > 1:  # Wide image, fit to width
            new_width = min(max_width, cropped_image.width)
            new_height = round(new_width / aspect_ratio)
        else:  # Tall or square image, fit to height
            new_height = min(max_height, cropped_image.height)
            new_width = round(new_height * aspect_ratio)

        # Resize the cropped image to fit within the bounding box
        image = cropped_image.resize((new_width, new_height))
    else:
        # Downscaling logic
        img_ratio = image.width / image.height
        target_ratio = max_width / max_height

        if img_ratio > target_ratio:
            new_width = max_width
            new_height = round(max_width / img_ratio)
        else:
            new_height = max_height
            new_width = round(max_height * img_ratio)

        image = image.resize((new_width, new_height))

    # Convert the image back to bytes
    output_buffer = BytesIO()
    image.save(output_buffer, format='PNG')  # You can change format if needed
    return output_buffer.getvalue()


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


def image_to_data_url(image: Image.Image, format: str = 'PNG') -> str:
    image_bytes = image_to_bytes(image, format)
    image_encoded_data = base64.b64encode(image_bytes).decode('utf-8')
    return f"data:image/{format.lower()};base64,{image_encoded_data}"
