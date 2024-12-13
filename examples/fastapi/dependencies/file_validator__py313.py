from typing import Annotated

from fastapi import Depends, FastAPI, UploadFile

from fastapi_batteries.fastapi.deps import FileValidator
from fastapi_batteries.utils.size import mb_to_bytes

app = FastAPI()


img_validator_upto_1mb = FileValidator(
    max_size_bytes=mb_to_bytes(1),
    allowed_mime_types=["image/jpeg", "image/png", "image/svg+xml", "image/webp"],
)

pdf_validator_upto_5mb = FileValidator(max_size_bytes=mb_to_bytes(5), allowed_mime_types=["application/pdf"])


@app.post("/upload/")
async def upload_file(file: Annotated[UploadFile, Depends(img_validator_upto_1mb)]): ...
