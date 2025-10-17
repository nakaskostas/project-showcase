import os
import fitz  # PyMuPDF
import docx

def _read_txt_or_md(file_path: str) -> str:
    """Reads a .txt or .md file."""
    with open(file_path, "r", encoding="utf-8") as f:
        return f.read()

def _read_pdf(file_path: str) -> str:
    """Reads a .pdf file."""
    try:
        doc = fitz.open(file_path)
        text = ""
        for page in doc:
            text += page.get_text()
        return text
    except Exception as e:
        print(f"Error reading PDF {file_path}: {e}")
        return ""

def _read_docx(file_path: str) -> str:
    """Reads a .docx file."""
    try:
        doc = docx.Document(file_path)
        text = ""
        for para in doc.paragraphs:
            text += para.text + "\n"
        return text
    except Exception as e:
        print(f"Error reading DOCX {file_path}: {e}")
        return ""

def process(file_path: str) -> str:
    """
    Processes a text-based file based on its extension.
    """
    _, extension = os.path.splitext(file_path)
    extension = extension.lower()

    if extension in [".txt", ".md"]:
        return _read_txt_or_md(file_path)
    elif extension == ".pdf":
        return _read_pdf(file_path)
    elif extension == ".docx":
        return _read_docx(file_path)
    
    return ""
