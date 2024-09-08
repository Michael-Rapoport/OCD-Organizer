# error_handling.py
import os

class FileOrganizerError(Exception):
    """Base exception class for File Organizer"""
    pass

class DirectoryNotFoundError(FileOrganizerError):
    """Raised when the specified directory is not found"""
    pass

class InvalidFileTypeError(FileOrganizerError):
    """Raised when an invalid file type is encountered"""
    pass

def validate_directory(directory):
    if not os.path.isdir(directory):
        raise DirectoryNotFoundError(f"The directory '{directory}' does not exist.")

def validate_file_type(file_path, allowed_extensions):
    _, extension = os.path.splitext(file_path)
    if extension.lower() not in allowed_extensions:
        raise InvalidFileTypeError(f"The file '{file_path}' has an invalid extension.")

def handle_error(error, logger):
    if isinstance(error, FileOrganizerError):
        logger.error(str(error))
    else:
        logger.error(f"An unexpected error occurred: {str(error)}")