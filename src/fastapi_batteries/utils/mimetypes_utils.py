# TODO: Move generic utils that are not related to fastapi batteries to a separate package "pytils-jd"
# Common MIME types: https://developer.mozilla.org/en-US/docs/Web/HTTP/MIME_types/Common_types
from mimetypes import types_map
from typing import Literal
from typing import get_args as typing_get_args

# TODO: Can we get this type from mimetypes module?
type MimeType = Literal[
    "application/atom+xml",
    "application/ecmascript",
    "application/json",
    "application/javascript",
    "application/octet-stream",
    "application/ogg",
    "application/pdf",
    "application/postscript",
    "application/rdf+xml",
    "application/rss+xml",
    "application/soap+xml",
    "application/font-woff",
    "application/xhtml+xml",
    "application/xml",
    "application/zip",
    "application/gzip",
    "application/x-www-form-urlencoded",
    "application/x-dvi",
    "application/x-latex",
    "application/x-font-ttf",
    "application/x-shockwave-flash",
    "application/x-stuffit",
    "application/x-tar",
    "application/x-x509-ca-cert",
    "audio/midi",
    "audio/mpeg",
    "audio/webm",
    "audio/ogg",
    "audio/wav",
    "image/bmp",
    "image/gif",
    "image/jpeg",
    "image/png",
    "image/svg+xml",
    "image/tiff",
    "image/webp",
    "multipart/form-data",
    "text/css",
    "text/csv",
    "text/html",
    "text/javascript",
    "text/plain",
    "text/xml",
    "video/mpeg",
    "video/mp4",
    "video/ogg",
    "video/quicktime",
    "video/webm",
    "video/x-ms-wmv",
    "video/x-flv",
]

MIME_TYPES: tuple[MimeType, ...] = typing_get_args(MimeType)


def get_file_labels_from_mime_types(mime_types: list[str] | list[MimeType]):
    file_labels: set[str] = set()
    for ext, mime_type in types_map.items():
        if mime_type in mime_types:
            file_labels.add(ext.lstrip(".").upper())

    return file_labels


def get_file_label_from_mime_type(mime_type: str | MimeType):
    result = get_file_labels_from_mime_types([mime_type])
    return result.pop() if result else None
