import google.generativeai as genai
import PIL.Image
from typing import Dict

def process(file_path: str) -> Dict[str, str]:
    """
    Processes an image file using a multimodal LLM to generate a detailed
    description and a concise alt text.

    Args:
        file_path: The absolute path to the image file.

    Returns:
        A dictionary containing the 'description' and 'alt_text'.
    """
    img = PIL.Image.open(file_path)
    model = genai.GenerativeModel('models/gemini-2.5-flash-image')

    # Generate the detailed description
    response_description = model.generate_content(
        ["Δώσε μια λεπτομερή περιγραφή αυτής της εικόνας, κατάλληλη για την παρουσίαση ενός έργου.", img],
        stream=True
    )
    response_description.resolve()

    # Generate the concise alt text
    response_alt = model.generate_content(
        ["Δώσε ένα σύντομο, περιγραφικό alt text για αυτή την εικόνα, μέχρι 125 χαρακτήρες.", img],
        stream=True
    )
    response_alt.resolve()

    return {
        "description": response_description.text,
        "alt_text": response_alt.text
    }
