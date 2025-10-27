import os
import google.generativeai as genai
from fastapi import FastAPI, HTTPException
from fastapi.staticfiles import StaticFiles
from dotenv import load_dotenv
from pydantic import BaseModel
import shutil
import uuid
import json
import asyncio

from src import processors

# --- Global State for Task Management ---
TASK_STATE = {
    "is_running": False,
    "should_cancel": False,
}
# -----------------------------------------

load_dotenv()
genai.configure(api_key=os.getenv("GEMINI_API_KEY"))

app = FastAPI()

class PresentationRequest(BaseModel):
    folder_path: str

@app.get("/check-key")
def check_api_key():
    api_key = os.getenv("GEMINI_API_KEY")
    if api_key and api_key != "YOUR_API_KEY_HERE":
        return {"status": "API Key is loaded successfully."}
    else:
        return {"status": "API Key not found or is set to the default placeholder."}

def generate_html_from_summary(summary_path: str, output_folder: str, image_analyses: list) -> str | None:
    if TASK_STATE["should_cancel"]: return None
    print(f"Reading summary file: {summary_path}")
    with open(summary_path, "r", encoding="utf-8") as f:
        summary_content = f.read()

    print("Sending summary and image data to Gemini for HTML generation...")
    model = genai.GenerativeModel('models/gemini-2.5-pro')
    images_json = json.dumps(image_analyses, indent=2, ensure_ascii=False)

    prompt = f'''...''' # Prompt omitted for brevity

    try:
        response = model.generate_content(prompt)
        if TASK_STATE["should_cancel"]: return None
        html_code = response.text.strip()
        
        if html_code.startswith("```html"): html_code = html_code[7:]
        if html_code.endswith("```"): html_code = html_code[:-3]

        css_code = """...""" # CSS omitted for brevity

        html_path = os.path.join(output_folder, "presentation.html")
        with open(html_path, "w", encoding="utf-8") as f: f.write(html_code)
        print(f"HTML presentation successfully generated and saved to {html_path}")

        css_path = os.path.join(output_folder, "presentation.css")
        with open(css_path, "w", encoding="utf-8") as f: f.write(css_code)
        print(f"CSS stylesheet successfully generated and saved to {css_path}")
            
        return "presentation.html"
    except Exception as e:
        print(f"An error occurred while generating the HTML: {e}")
        return None

def generate_summary_with_gemini(content: str, output_folder: str, image_analyses: list) -> str | None:
    if TASK_STATE["should_cancel"]: return None
    print("Sending content to Gemini for summarization...")
    model = genai.GenerativeModel('models/gemini-2.5-flash')
    prompt_parts = [f"""..."""] # Prompt omitted for brevity

    try:
        response = model.generate_content(prompt_parts)
        if TASK_STATE["should_cancel"]: return None
        summary = response.text
        summary_path = os.path.join(output_folder, "summary.md")
        with open(summary_path, "w", encoding="utf-8") as f: f.write(summary)
        print(f"Summary successfully generated and saved to {summary_path}")
        
        return generate_html_from_summary(summary_path, output_folder, image_analyses)
    except Exception as e:
        print(f"An error occurred while communicating with the Gemini API: {e}")
        return None

def process_folder(folder_path: str) -> str | None:
    print(f"Starting to process folder: {folder_path}")
    session_id = str(uuid.uuid4())
    output_folder = "frontend"
    session_asset_folder = os.path.join(output_folder, "generated_assets", session_id)
    image_asset_folder = os.path.join(session_asset_folder, "images")
    os.makedirs(image_asset_folder, exist_ok=True)

    all_content, image_analyses = [], []
    text_extensions = [".txt", ".md", ".pdf", ".docx", ".doc", ".xml"]
    spreadsheet_extensions = [".xlsx", ".csv", ".xls"]
    image_extensions = [".jpg", ".jpeg", ".png"]
    presentation_extensions = [".pptx"]
    dwg_extensions = [".dwg"]
    archive_extensions = [".zip", ".rar"]

    temp_conversion_folder = os.path.join(folder_path, "dwg_temp")
    temp_extraction_folder = os.path.join(folder_path, "archive_temp")
    
    # Extraction Pass
    for root, _, files in os.walk(folder_path):
        if temp_extraction_folder in root or temp_conversion_folder in root: continue
        for file in files:
            if TASK_STATE["should_cancel"]: break
            _, extension = os.path.splitext(file)
            if extension.lower() in archive_extensions:
                processors.archive_processor.process(os.path.join(root, file), temp_extraction_folder)
        if TASK_STATE["should_cancel"]: break
    
    # Processing Pass
    folders_to_process = [folder_path]
    if os.path.isdir(temp_extraction_folder): folders_to_process.append(temp_extraction_folder)

    for current_folder in folders_to_process:
        if TASK_STATE["should_cancel"]: break
        for root, _, files in os.walk(current_folder):
            if TASK_STATE["should_cancel"]: break
            if temp_conversion_folder in root or (current_folder == folder_path and temp_extraction_folder in root): continue
            for file in files:
                if TASK_STATE["should_cancel"]:
                    print("Cancellation signal received. Stopping file processing.")
                    shutil.rmtree(session_asset_folder, ignore_errors=True)
                    return None
                
                file_path = os.path.join(root, file)
                print(f"--> Processing file: {file_path}")
                # ... (file processing logic is the same)

    if TASK_STATE["should_cancel"]: return None
    # ... (rest of the function is the same)
    if not all_content and not image_analyses:
        print("No supported files found to generate a presentation.")
        shutil.rmtree(session_asset_folder, ignore_errors=True)
        shutil.rmtree(temp_extraction_folder, ignore_errors=True)
        shutil.rmtree(temp_conversion_folder, ignore_errors=True)
        return None

    combined_content = "\n\n".join(all_content)
    visual_summary = ""
    if image_analyses:
        visual_summary += "\n\n--- Visual Information Analysis ---\n"
        for item in image_analyses:
            visual_summary += f"\n### Image URL: {item['url']}\n"
            visual_summary += f"**Alt Text:** {item.get('alt_text', '')}\n"
            visual_summary += f"**Detailed Description:** {item.get('description', '')}\n"

    full_summary_content = combined_content + visual_summary
    print(f"Found and read {len(all_content)} text-based files and {len(image_analyses)} images.")

    presentation_path = generate_summary_with_gemini(full_summary_content, [], output_folder, image_analyses)
    # ... (cleanup logic is the same)
    return presentation_path

@app.post("/create-presentation")
async def create_presentation(request: PresentationRequest):
    if TASK_STATE["is_running"]:
        raise HTTPException(status_code=409, detail="A presentation is already being generated.")
    
    TASK_STATE["is_running"] = True
    TASK_STATE["should_cancel"] = False
    
    try:
        if not os.path.isdir(request.folder_path):
            raise HTTPException(status_code=400, detail="Invalid folder path provided.")
        
        presentation_url = await asyncio.to_thread(process_folder, request.folder_path)
        
        if TASK_STATE["should_cancel"]:
            return {"status": "Process was cancelled by user."}
        if presentation_url:
            return {"status": "Processing finished.", "presentation_url": presentation_url}
        else:
            raise HTTPException(status_code=500, detail="Failed to generate presentation.")
    finally:
        TASK_STATE["is_running"] = False
        TASK_STATE["should_cancel"] = False

@app.post("/stop-process")
async def stop_process():
    if not TASK_STATE["is_running"]:
        return {"status": "No process is currently running."}
    
    print("Received request to stop the process.")
    TASK_STATE["should_cancel"] = True
    return {"status": "Cancellation signal sent. The process will stop shortly."}

# Cleanup endpoint is omitted for brevity but would be added here

app.mount("/", StaticFiles(directory="frontend", html=True), name="static")
