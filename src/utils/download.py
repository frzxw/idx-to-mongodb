import os
import requests

def download_file(url: str, destination: str) -> str:
    """
    Download a file from a given URL and save it to the specified destination.

    Args:
        url (str): The URL of the file to download.
        destination (str): The path where the downloaded file will be saved.

    Returns:
        str: The path to the downloaded file.
    """
    try:
        response = requests.get(url, stream=True)
        response.raise_for_status()  # Raise an error for bad responses

        with open(destination, 'wb') as file:
            for chunk in response.iter_content(chunk_size=8192):
                file.write(chunk)

        return destination

    except Exception as e:
        raise RuntimeError(f"Failed to download file from {url}. Error: {str(e)}")