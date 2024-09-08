# file_organizer.py
import os
import shutil
from error_handling import validate_directory, validate_file_type
from config import config
from logger import logger

class FileOrganizer:
    def __init__(self):
        self.last_reorganization = []

    def get_directory_structure(self, directory):
        structure = {}
        for root, dirs, files in os.walk(directory):
            current = structure
            path = os.path.relpath(root, directory).split(os.sep)
            for folder in path:
                if folder not in current:
                    current[folder] = {}
                current = current[folder]
            current['files'] = files
        return structure

    def get_proposed_structure(self, current_structure, suggestions):
        # This is a simplified implementation. In a real-world scenario,
        # you would need to parse the AI suggestions and apply them to the current structure.
        proposed_structure = current_structure.copy()
        
        # Example: Add a new folder for each file type
        file_types = set()
        for folder in proposed_structure.values():
            for file in folder.get('files', []):
                _, ext = os.path.splitext(file)
                if ext:
                    file_types.add(ext[1:])  # Remove the leading dot
        
        for file_type in file_types:
            proposed_structure[f"{file_type.upper()} Files"] = {}
        
        return proposed_structure

    def analyze_directory(self, directory):
        validate_directory(directory)
        file_list = []
        for root, _, files in os.walk(directory):
            for file in files:
                file_path = os.path.join(root, file)
                file_list.append(file_path)
        return file_list

    def preview_reorganization(self, file_list, proposed_structure):
        preview = []
        for file_path in file_list:
            try:
                validate_file_type(file_path, config.get("allowed_extensions"))
                new_location = self.get_new_location(file_path, proposed_structure)
                preview.append((file_path, new_location))
            except Exception as e:
                logger.error(f"Error processing file {file_path}: {str(e)}")
        return preview

    def reorganize_files(self, file_list, proposed_structure):
        self.last_reorganization = []
        for file_path in file_list:
            try:
                validate_file_type(file_path, config.get("allowed_extensions"))
                new_location = self.get_new_location(file_path, proposed_structure)
                self.last_reorganization.append((file_path, new_location))
                self.move_file(file_path, new_location)
            except Exception as e:
                logger.error(f"Error processing file {file_path}: {str(e)}")

    def get_new_location(self, file_path, proposed_structure):
        # This is a simplified implementation. In a real-world scenario,
        # you would need to determine the new location based on the proposed structure.
        file_name = os.path.basename(file_path)
        _, ext = os.path.splitext(file_name)
        if ext:
            new_folder = f"{ext[1:].upper()} Files"
            return os.path.join(os.path.dirname(file_path), new_folder, file_name)
        return file_path

    def move_file(self, source, destination):
        os.makedirs(os.path.dirname(destination), exist_ok=True)
        shutil.move(source, destination)

    def undo_last_reorganization(self):
        for old_path, new_path in reversed(self.last_reorganization):
            try:
                self.move_file(new_path, old_path)
                logger.info(f"Moved {new_path} back to {old_path}")
            except Exception as e:
                logger.error(f"Error undoing move for {new_path}: {str(e)}")
        self.last_reorganization = []

file_organizer = FileOrganizer()