import requests
from pathlib import Path


def upload_images(folder: Path, endpoint_url: str):
    """
    Scan a folder for images and upload them to the specified endpoint

    """
    # Supported image extensions
    image_extensions = (".jpg", ".jpeg", ".png", ".gif", ".bmp")

    # Check if folder exists
    if not folder.exists() or not folder.is_dir():
        print(f"Error: '{folder}' is not a valid directory")
        return

    # Counter for uploaded files
    uploaded_count = 0
    error_count = 0

    print(f"Scanning folder: {folder}")

    # Iterate through all files in the folder
    for file_path in folder.iterdir():
        # Check if it's a file and has an image extension
        if file_path.is_file() and file_path.suffix.lower() in image_extensions:
            try:
                # Open file in binary mode
                with open(file_path, "rb") as image_file:
                    # Prepare the file for upload
                    files = {"file": (file_path.name, image_file, "image/" + file_path.suffix[1:])}

                    # Send POST request to endpoint
                    response = requests.post(endpoint_url, files=files)

                    # Check if upload was successful
                    if response.status_code == 200:
                        print(f"Successfully uploaded: {file_path.name}", response.json())
                        uploaded_count += 1
                    else:
                        print(f"Failed to upload {file_path.name}: Status code {response.status_code}")
                        error_count += 1

            except requests.exceptions.RequestException as e:
                print(f"Error uploading {file_path.name}: {str(e)}")
                error_count += 1
            except Exception as e:
                print(f"Unexpected error with {file_path.name}: {str(e)}")
                error_count += 1

    # Print summary
    print("\nUpload Summary:")
    print(f"Successfully uploaded: {uploaded_count} images")
    print(f"Failed uploads: {error_count}")


if __name__ == "__main__":
    folder = Path(__file__).parent.parent / "TEMP"
    endpoint_url = "http://localhost:5000/images/"
    upload_images(folder, endpoint_url=endpoint_url)
