import uuid
from pathlib import Path

from fastapi import UploadFile


# Utility function that extracts the file extension from the file name using pathlib
def extract_file_extension(file_name: str) -> str:
    """Extract file extension from the file name.

    Examples:
        >>> extract_file_extension("file.txt")
        ".txt"
        >>> extract_file_extension("file")
        ""
        >>> extract_file_extension("file.")
        "." # This is not a valid file extension

    """
    return Path(file_name).suffix


def generate_random_file_name(file: UploadFile) -> str:
    """Generate a random file name using UUID4.

    Args:
        file: The uploaded file object.

    Returns:
        A random file name with the same extension as the uploaded file.

    Examples:
        >>> file = UploadFile(filename="file.txt")
        >>> generate_random_file_name(file)
        "random-uuid4-value.txt"
        >>> file = UploadFile(filename="file")
        >>> generate_random_file_name(file)
        "random-uuid4-value"
        >>> file = UploadFile(filename="file.")
        >>> generate_random_file_name(file)
        "random-uuid4-value

    """
    file_name_str = file.filename or ""
    ext = extract_file_extension(file_name_str)

    random_name = str(uuid.uuid4())
    return f"{random_name}{ext}" if file_name_str else random_name
