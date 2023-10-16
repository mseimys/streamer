import os
import shutil
import glob

from settings import ORIGINAL_DIR, INPUT_DIR, EXTENSIONS_TO_COPY


def safe_copy_file(source_path, destination_dir):
    # Get the filename from the source path
    filename = os.path.basename(source_path)

    # Generate a temporary filename in the destination directory
    temp_filename = os.path.join(destination_dir, f"{filename}.tmp")

    try:
        # Copy the file to the temporary filename
        shutil.copy2(source_path, temp_filename)

        # Rename the temporary file to the original filename
        final_destination = os.path.join(destination_dir, filename)
        os.rename(temp_filename, final_destination)

        print(f"File copied to: {final_destination}")
    except Exception as e:
        print(f"Error copying file: {e}")


def scan_directory_and_safe_copy_files(input_dir: str, output_dir: str):
    matching_files = glob.glob(os.path.join(input_dir, EXTENSIONS_TO_COPY))
    for f in matching_files:
        safe_copy_file(f, output_dir)


scan_directory_and_safe_copy_files(ORIGINAL_DIR, INPUT_DIR)
