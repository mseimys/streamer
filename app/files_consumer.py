import shutil
import os
from settings import OUTPUT_DIR, INPUT_DIR, EXTENSIONS_TO_COPY

import glob


def process_file(source_path, destination_dir):
    filename = os.path.basename(source_path)
    destination_path = os.path.join(destination_dir, filename)
    try:
        shutil.move(source_path, destination_path)
        print(f"File moved to: {destination_path}")
    except Exception as e:
        print(f"Error copying file: {e}")


def process_folders(input_dir: str, output_dir: str):
    matching_files = glob.glob(os.path.join(input_dir, EXTENSIONS_TO_COPY))
    for f in matching_files:
        process_file(f, output_dir)


process_folders(INPUT_DIR, OUTPUT_DIR)
