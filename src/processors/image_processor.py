
import base64
from typing import List, Dict, Union

def process(file_path: str) -> List[Dict[str, Union[str, Dict]]]:
    """
    Processes an image file by reading it and encoding it in base64.
    This prepares the image to be sent to a multimodal LLM like Gemini.

    Args:
        file_path: The absolute path to the image file.

    Returns:
        A list containing a dictionary that represents the image data
        in the format expected by the Gemini API.
    """
    # Get the image format (e.g., 'png', 'jpeg') from the file extension
    image_format = file_path.split('.')[-1]
    if image_format == 'jpg':
        image_format = 'jpeg'

    # Read the image file in binary mode
    with open(file_path, "rb") as image_file:
        # Encode the binary data into base64
        encoded_string = base64.b64encode(image_file.read()).decode('utf-8')

    # Structure the data for the Gemini API
    image_data = [
        {
            "inline_data": {
                "mime_type": f"image/{image_format}",
                "data": encoded_string
            }
        }
    ]

    return image_data
