# core/file_ops.py
"""
File operations — create, read, delete files and folders.
"""

import logging
import os

logger = logging.getLogger("VoiceAssist.FileOps")

DEFAULT_DIR = os.path.expanduser("~")


def create_file(filename: str, content: str = "", directory: str = DEFAULT_DIR) -> str:
    """Create a file with optional content."""
    try:
        # Add .txt extension if no extension provided
        if "." not in filename:
            filename = filename + ".txt"

        path = os.path.join(directory, filename)
        with open(path, "w", encoding="utf-8") as f:
            f.write(content)

        return f"Done. File {filename} has been created successfully."

    except PermissionError:
        logger.warning(f"Permission denied creating {filename}")
        return f"Permission denied. Could not create {filename}"
    except Exception as e:
        logger.error(f"Unexpected error in create_file: {e}", exc_info=True)
        return f"Sorry, could not create {filename}"


def read_file(filename: str, directory: str = DEFAULT_DIR) -> str:
    """Read and return the contents of a file."""
    try:
        # Add .txt extension if no extension provided
        if "." not in filename:
            filename = filename + ".txt"

        path = os.path.join(directory, filename)

        # Search in directory
        if not os.path.isfile(path):
            # Try one level deep in subdirectories
            found = False
            for subdir in os.listdir(directory):
                subdir_path = os.path.join(directory, subdir)
                if os.path.isdir(subdir_path):
                    candidate = os.path.join(subdir_path, filename)
                    if os.path.isfile(candidate):
                        path = candidate
                        found = True
                        break
            if not found:
                return f"File {filename} not found"

        with open(path, "r", encoding="utf-8", errors="replace") as f:
            content = f.read()

        # Truncate for TTS
        if len(content) > 500:
            content = content[:500] + "..."

        return f"The file contains: {content}"

    except FileNotFoundError:
        return f"File {filename} not found"
    except Exception as e:
        logger.error(f"Unexpected error in read_file: {e}", exc_info=True)
        return f"Sorry, could not read {filename}"


def delete_file(filename: str, directory: str = DEFAULT_DIR) -> str:
    """Delete a file."""
    try:
        if "." not in filename:
            filename = filename + ".txt"

        path = os.path.join(directory, filename)

        if not os.path.isfile(path):
            return f"File {filename} not found"

        os.remove(path)
        return f"Done. File {filename} has been deleted successfully."

    except PermissionError:
        logger.warning(f"Permission denied deleting {filename}")
        return f"Permission denied. Could not delete {filename}"
    except Exception as e:
        logger.error(f"Unexpected error in delete_file: {e}", exc_info=True)
        return f"Could not delete {filename}: {e}"


def list_files(directory: str = DEFAULT_DIR) -> str:
    """List files in a directory."""
    try:
        items = os.listdir(directory)
        files = [f for f in items if os.path.isfile(os.path.join(directory, f))]

        if not files:
            return "No files found in the directory"

        # Limit spoken list to 10 items
        count = len(files)
        display_files = files[:10]
        file_list = ", ".join(display_files)

        if count > 10:
            return f"Found {count} files. The first 10 are: {file_list}"
        else:
            return f"Found {count} files: {file_list}"

    except PermissionError:
        logger.warning(f"Permission denied listing {directory}")
        return "Permission denied. Could not list files"
    except Exception as e:
        logger.error(f"Unexpected error in list_files: {e}", exc_info=True)
        return "Sorry, could not list files"


def create_folder(folder_name: str, parent: str = DEFAULT_DIR) -> str:
    """Create a folder."""
    try:
        path = os.path.join(parent, folder_name)
        os.makedirs(path, exist_ok=True)
        return f"Done. Folder {folder_name} has been created successfully."
    except PermissionError:
        logger.warning(f"Permission denied creating folder {folder_name}")
        return f"Permission denied. Could not create folder {folder_name}"
    except Exception as e:
        logger.error(f"Unexpected error in create_folder: {e}", exc_info=True)
        return f"Sorry, could not create folder {folder_name}"
