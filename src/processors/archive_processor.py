import os
import zipfile
import rarfile
import shutil

def _ensure_dir(directory: str):
    """Ensures that a directory exists."""
    if not os.path.isdir(directory):
        os.makedirs(directory)

def _extract_zip(file_path: str, output_folder: str):
    """Extracts a .zip file."""
    try:
        with zipfile.ZipFile(file_path, 'r') as zip_ref:
            zip_ref.extractall(output_folder)
        print(f"Successfully extracted {os.path.basename(file_path)} to {output_folder}")
    except Exception as e:
        print(f"Failed to extract ZIP file {file_path}: {e}")

def _extract_rar(file_path: str, output_folder: str):
    """Extracts a .rar file."""
    try:
        with rarfile.RarFile(file_path, 'r') as rar_ref:
            rar_ref.extractall(output_folder)
        print(f"Successfully extracted {os.path.basename(file_path)} to {output_folder}")
    except rarfile.NeedFirstVolume:
        print(f"Skipping multi-volume RAR archive: {file_path}")
    except Exception as e:
        print(f"Failed to extract RAR file {file_path}: {e}")

def process(file_path: str, output_folder: str):
    """
    Processes an archive file (.zip or .rar) by extracting its contents.
    """
    _ensure_dir(output_folder)
    _, extension = os.path.splitext(file_path)
    extension = extension.lower()

    if extension == '.zip':
        _extract_zip(file_path, output_folder)
    elif extension == '.rar':
        _extract_rar(file_path, output_folder)
    else:
        print(f"Unsupported archive format: {extension}")

def cleanup(folder_path: str):
    """Deletes the temporary extraction folder."""
    if os.path.isdir(folder_path):
        try:
            shutil.rmtree(folder_path)
            print(f"Successfully cleaned up temporary archive folder: {folder_path}")
        except Exception as e:
            print(f"Error cleaning up temporary archive folder {folder_path}: {e}")
