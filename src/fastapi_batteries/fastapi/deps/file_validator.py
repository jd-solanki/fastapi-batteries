import magic
from fastapi import UploadFile, status

from fastapi_batteries.exceptions.api_exception import APIException
from fastapi_batteries.utils import mimetypes_utils
from fastapi_batteries.utils import size as size_utils


class FileValidator:
    def __init__(self, max_size_bytes: int, allowed_mime_types: list[mimetypes_utils.MimeType]) -> None:
        """Validate file size and extension.

        max_size_kb: Maximum file size allowed (in kilobytes).
        allowed_mime_types: List of valid MIME types (e.g. ['image/jpeg', 'image/png']).
        """
        self.max_size_bytes = max_size_bytes  # Convert KB to bytes using provided utility function
        self.allowed_mime_types = allowed_mime_types

        self.allowed_files_labels = mimetypes_utils.get_file_labels_from_mime_types(allowed_mime_types)

    async def __call__(self, file: UploadFile) -> UploadFile:
        # Validate file size and content type
        await self._validate_file_size(file)
        await self._validate_file_type(file)
        return file

    async def _validate_file_size(self, file: UploadFile) -> None:
        # Read the entire file to calculate its size in bytes
        file_content = await file.read()
        file_size_bytes = len(file_content)

        if file_size_bytes > self.max_size_bytes:
            max_size_mb = size_utils.bytes_to_mb(self.max_size_bytes)  # Convert bytes to MB for the error message
            raise APIException(
                status=status.HTTP_400_BAD_REQUEST,
                title=f"File size exceeds the maximum limit of {max_size_mb:.2f} MB.",
            )
        # Reset the file cursor to the beginning after reading
        await file.seek(0)

    async def _validate_file_type(self, file: UploadFile) -> None:
        # Read the first 2048 bytes of the file for magic number detection
        file_content = await file.read(2048)
        file_type = magic.from_buffer(file_content, mime=True)  # Detect MIME type from the first 2048 bytes

        if file_type not in self.allowed_mime_types:
            file_type_label = mimetypes_utils.get_file_label_from_mime_type(file_type)

            raise APIException(
                status=status.HTTP_400_BAD_REQUEST,
                title=f"Invalid file type '{file_type_label or file_type}'. Allowed types: {", ".join(self.allowed_files_labels)}.",
            )
        # Reset the file cursor to the beginning after reading
        await file.seek(0)


img_validator_upto_1mb = FileValidator(
    max_size_bytes=size_utils.mb_to_bytes(1),
    allowed_mime_types=["image/jpeg", "image/png", "image/svg+xml", "image/webp"],
)
pdf_validator_upto_5mb = FileValidator(max_size_bytes=size_utils.mb_to_bytes(5), allowed_mime_types=["application/pdf"])
