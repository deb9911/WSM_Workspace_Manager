import os
import pickle
from pathlib import Path

INDEX_FILE = "files_index.pkl"


def index_files(root_directories=None):
    """Index files in specified directories and save to a pickle file."""
    if root_directories is None:
        root_directories = [Path.home()]  # Default to user home directory

    file_index = {}
    for root_dir in root_directories:
        for dirpath, _, filenames in os.walk(root_dir):
            for filename in filenames:
                file_path = os.path.join(dirpath, filename)
                file_index[filename] = file_index.get(filename, []) + [file_path]

    # Save the file index
    with open(INDEX_FILE, 'wb') as index_file:
        pickle.dump(file_index, index_file)


def load_file_index():
    """Load the file index from the pickle file."""
    if not os.path.exists(INDEX_FILE):
        index_files()
    with open(INDEX_FILE, 'rb') as index_file:
        return pickle.load(index_file)
