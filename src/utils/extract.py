# filepath: idx-to-mongodb/idx-to-mongodb/src/utils/extract.py

def extract_zip(zip_path: str, extract_dir: str) -> List[str]:
    """
    Extracts the contents of a ZIP file to a specified directory.

    Args:
        zip_path: Path to the ZIP file.
        extract_dir: Directory where the contents will be extracted.

    Returns:
        List of paths to the extracted files.
    """
    extracted_files = []
    try:
        with zipfile.ZipFile(zip_path, 'r') as zip_ref:
            zip_ref.extractall(extract_dir)
            extracted_files = [os.path.join(extract_dir, file) for file in zip_ref.namelist()]
    except Exception as e:
        logger.error(f"Error extracting {zip_path}: {str(e)}")
    
    return extracted_files