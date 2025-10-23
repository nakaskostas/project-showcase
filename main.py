import os
import google.generativeai as genai
from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from dotenv import load_dotenv
from pydantic import BaseModel

from src import processors

# Load environment variables from .env file
load_dotenv()

# Configure the Gemini API key
genai.configure(api_key=os.getenv("GEMINI_API_KEY"))

app = FastAPI()


class PresentationRequest(BaseModel):
    folder_path: str

# An endpoint to demonstrate that the API key is loaded (for testing purposes)
# In a real app, you would NOT expose the key like this.
@app.get("/check-key")
def check_api_key():
    api_key = os.getenv("GEMINI_API_KEY")
    if api_key and api_key != "YOUR_API_KEY_HERE":
        return {"status": "API Key is loaded successfully."}
    else:
        return {"status": "API Key not found or is set to the default placeholder."}


def generate_html_from_summary(summary_path: str, output_folder: str) -> str | None:
    """
    Uses the Gemini API to generate an HTML presentation from a Markdown summary.
    Returns the path to the generated HTML file.
    """
    print(f"Reading summary file: {summary_path}")
    with open(summary_path, "r", encoding="utf-8") as f:
        summary_content = f.read()

    print("Sending summary to Gemini for HTML generation...")
    model = genai.GenerativeModel('models/gemini-2.5-pro')

    prompt = '''You are a code generator. Based on the following Markdown summary, generate a complete, single-page, responsive HTML presentation **in the Greek language**.
Your response MUST consist of two parts:
1. The HTML code, enclosed in a ```html ... ``` block.
2. The CSS code, enclosed in a ```css ... ``` block.

Do NOT include any other text, explanations, or conversational filler.

The HTML must be in Greek and include:
- A <head> section with a title and a link to a `presentation.css` file.
- A <body> containing:
  - A <header> with the main project title and a "Back to Home" button styled as a modern button that links to `/`. The button text should be "Επιστροφή στην Αρχική".
  - A <nav> bar with anchor links to the different sections of the page. All navigation links must be in Greek.
  - A <main> section with the content from the Markdown, divided into logical <section> tags, each with a unique ID for the nav links. All content in this section must be translated to Greek.
  - A <footer> with the text 'Δημιουργήθηκε από τον Epirus Showcase Agent'.

The CSS should be modern and ensure the page is responsive.

Here is the Markdown content:
---
''' + summary_content

    try:
        response = model.generate_content(prompt)
        full_response_text = response.text

        # Robustly find HTML and CSS code blocks
        html_code = ""
        css_code = ""

        # Find HTML block
        html_start = full_response_text.find("```html")
        if html_start != -1:
            html_end = full_response_text.find("```", html_start + 7)
            if html_end != -1:
                html_code = full_response_text[html_start + 7 : html_end].strip()

        # Find CSS block
        css_start = full_response_text.find("```css")
        if css_start != -1:
            css_end = full_response_text.find("```", css_start + 6)
            if css_end != -1:
                css_code = full_response_text[css_start + 6 : css_end].strip()

        # Fallback for cases where the model might not generate the ```html part
        if not html_code and (css_start != -1):
            # Assume HTML is everything before the CSS block
            potential_html = full_response_text[:css_start].strip()
            # Clean up potential markdown/code fences
            if potential_html.startswith("```"):
                potential_html = potential_html[3:]
            if potential_html.endswith("```"):
                potential_html = potential_html[:-3]
            html_code = potential_html.strip()


        if not html_code and not css_code:
            # If we can't find any blocks, assume the whole response is HTML
            # and remove potential conversational parts
            lines = full_response_text.split('\n')
            # A simple heuristic: find the first line that looks like HTML
            first_html_line = -1
            for i, line in enumerate(lines):
                if line.strip().startswith('<!DOCTYPE html>') or line.strip().startswith('<html'):
                    first_html_line = i
                    break
            if first_html_line != -1:
                html_code = '\n'.join(lines[first_html_line:])
            else:
                # As a last resort, just use the whole text, it might be just the code
                html_code = full_response_text


        html_path = os.path.join(output_folder, "presentation.html")
        with open(html_path, "w", encoding="utf-8") as f:
            f.write(html_code)
        print(f"HTML presentation successfully generated and saved to {html_path}")

        if css_code:
            css_path = os.path.join(output_folder, "presentation.css")
            with open(css_path, "w", encoding="utf-8") as f:
                f.write(css_code)
            print(f"CSS stylesheet successfully generated and saved to {css_path}")
            
        return "presentation.html"

    except Exception as e:
        print(f"An error occurred while generating the HTML: {e}")
        return None


def generate_summary_with_gemini(content: str, image_parts: list, output_folder: str) -> str | None:
    """
    Uses the Gemini API to generate a summary from text and images, then triggers HTML generation.
    Returns the path to the generated HTML file.
    """
    print("Sending content and images to Gemini for summarization...")
    model = genai.GenerativeModel('models/gemini-2.5-flash-image')

    # Combine text and image parts for the prompt
    prompt_parts = [f"""Based on the following text and images extracted from various project documents, 
create a comprehensive and well-structured summary in Markdown format. 
The summary should identify and highlight key information such as: Project Title, Budget, Timeline, Key Stakeholders, Objectives, and a general Technical Description. 
Analyze the images to extract visual information like construction status, architectural plans, or location context.
Structure the output with clear headings and bullet points. The file should be named 'summary.md'.

---

{content}
"""]
    prompt_parts.extend(image_parts)

    try:
        response = model.generate_content(prompt_parts)
        summary = response.text
        
        summary_path = os.path.join(output_folder, "summary.md")
        with open(summary_path, "w", encoding="utf-8") as f:
            f.write(summary)
        print(f"Summary successfully generated and saved to {summary_path}")
        
        return generate_html_from_summary(summary_path, output_folder)

    except Exception as e:
        print(f"An error occurred while communicating with the Gemini API: {e}")
        return None


def cleanup_old_files(output_folder: str):
    """Deletes old generated files to ensure a clean slate."""
    files_to_delete = ["summary.md", "presentation.html", "presentation.css"]
    for filename in files_to_delete:
        file_path = os.path.join(output_folder, filename)
        if os.path.exists(file_path):
            os.remove(file_path)
            print(f"Deleted old file: {file_path}")


def process_folder(folder_path: str) -> str | None:
    """
    Recursively walks through a folder, reads supported files,
    and triggers the summary and presentation generation.
    Returns the path to the generated presentation.
    """
    print(f"Starting to process folder: {folder_path}")
    all_content = []
    image_parts = []
    video_frames_count = 0

    # Define supported extensions for each processor
    text_extensions = [".txt", ".md", ".pdf", ".docx"]
    spreadsheet_extensions = [".xlsx"]
    image_extensions = [".jpg", ".jpeg", ".png"]
    video_extensions = [".mp4", ".mov", ".avi"]
    presentation_extensions = [".pptx"]

    for root, _, files in os.walk(folder_path):
        for file in files:
            file_path = os.path.join(root, file)
            _, extension = os.path.splitext(file_path)
            extension = extension.lower()

            if extension in text_extensions:
                content = processors.text_processor.process(file_path)
                if content:
                    all_content.append(f"--- Content from {file} ---\n{content}")
            elif extension in spreadsheet_extensions:
                content = processors.spreadsheet_processor.process(file_path)
                if content:
                    all_content.append(f"--- Content from {file} ---\n{content}")
            elif extension in presentation_extensions:
                content = processors.presentation_processor.process(file_path)
                if content:
                    all_content.append(f"--- Content from {file} ---\n{content}")
            elif extension in image_extensions:
                image_data = processors.image_processor.process(file_path)
                if image_data:
                    image_parts.append(f"--- Image from {file} ---")
                    image_parts.extend(image_data)
            elif extension in video_extensions:
                video_frames = processors.video_processor.process(file_path)
                if video_frames:
                    image_parts.append(f"--- Video frames from {file} ---")
                    image_parts.extend(video_frames)
                    video_frames_count += len(video_frames)
            else:
                print(f"Skipping unsupported file type: {file_path}")

    if not all_content and not image_parts:
        print("No supported files found in the provided folder.")
        return None

    # Each image adds a text part and a data dict. Each video frame is just a data dict.
    # The logic for counting images needs to be adjusted.
    # Let's count the number of "---" separators to get the number of files.
    file_marker_count = sum(1 for item in image_parts if isinstance(item, str))
    image_count = file_marker_count - (1 if video_frames_count > 0 else 0)

    print(f"Found and read {len(all_content)} text-based files, {image_count} images, and processed {video_frames_count} frames from videos.")
    combined_content = "\n\n".join(all_content)

    output_folder = "frontend"
    return generate_summary_with_gemini(combined_content, image_parts, output_folder)


@app.post("/create-presentation")
async def create_presentation(request: PresentationRequest):
    """
    This endpoint receives a folder path, processes all the files within it,
    and will eventually generate a presentation.
    """
    if not os.path.isdir(request.folder_path):
        return {"error": "Invalid folder path provided."}, 400

    presentation_url = process_folder(request.folder_path)
    
    if presentation_url:
        return {"status": "Processing finished.", "presentation_url": presentation_url}
    else:
        return {"error": "Failed to generate presentation."},


# According to tech_stack.txt, we will use uvicorn to run this.
# To run the server, you would use the command in your terminal:
# .\.venv\Scripts\activate
# uvicorn main:app --reload

# Mount the 'frontend' directory to serve static files like CSS and JS
# This should be after all API routes are defined
app.mount("/", StaticFiles(directory="frontend", html=True), name="static")
