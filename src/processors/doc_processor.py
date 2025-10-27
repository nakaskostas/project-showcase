import os
import win32com.client
import pythoncom

def process_doc(file_path):
    """
    Processes a .doc file using the Word COM object to extract text.
    
    Args:
        file_path (str): The absolute path to the .doc file.
        
    Returns:
        str: The extracted text content of the file, or an error message.
    """
    # CoInitialize is necessary for COM objects in a multithreaded environment
    pythoncom.CoInitialize()
    word = None
    doc = None
    try:
        # Create a new Word Application instance
        word = win32com.client.Dispatch("Word.Application")
        word.Visible = False  # Run in the background

        # Open the document
        doc = word.Documents.Open(file_path, ReadOnly=True)
        
        # Extract the full text content
        content = doc.Content.Text
        
        return content

    except pythoncom.com_error as e:
        # This error often means Word is not installed or there's a permission issue
        return f"Error processing {os.path.basename(file_path)}: Could not access the Word application. Please ensure Microsoft Word is installed. Details: {e}"
    except Exception as e:
        return f"An unexpected error occurred while processing {os.path.basename(file_path)}: {e}"
    finally:
        # Ensure everything is closed and released properly
        if doc:
            doc.Close(False) # False means don't save changes
        if word:
            word.Quit()
        # Uninitialize the COM library
        pythoncom.CoUninitialize()
