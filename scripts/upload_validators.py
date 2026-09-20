import json

from django.core.exceptions import ValidationError

from scripts import constants

PDF_SIGNATURE = b"%PDF-"
PDF_SIGNATURE_WINDOW = 1024


def _format_size(size_in_bytes: int) -> str:
    if size_in_bytes >= 1024 * 1024:
        return f"{size_in_bytes / (1024 * 1024):g} MB"
    return f"{size_in_bytes // 1024} KB"


def _size_of(value) -> int | None:
    """
    Best effort size, in bytes, of an uploaded file, a raw string/bytes payload or already parsed JSON.
    """
    if hasattr(value, "size"):
        return value.size
    if isinstance(value, (bytes, bytearray)):
        return len(value)
    if isinstance(value, str):
        return len(value.encode("utf-8"))
    try:
        return len(json.dumps(value).encode("utf-8"))
    except (TypeError, ValueError):
        return None


def validate_max_size(value, max_bytes: int) -> None:
    size = _size_of(value)
    if size is not None and size > max_bytes:
        raise ValidationError(
            f"This upload is too large. The maximum allowed size is {_format_size(max_bytes)}.",
            code="upload_too_large",
        )


def validate_json_upload_size(value) -> None:
    validate_max_size(value, constants.MAX_JSON_UPLOAD_BYTES)


def validate_pdf_upload_size(value) -> None:
    validate_max_size(value, constants.MAX_PDF_UPLOAD_BYTES)


def validate_pdf_signature(value) -> None:
    """
    Sanity check that an upload named .pdf really starts like a PDF. This is not full validation,
    it only stops arbitrary files (HTML, executables...) being hosted under a .pdf name.
    """
    header = value.read(PDF_SIGNATURE_WINDOW)
    value.seek(0)
    if PDF_SIGNATURE not in header:
        raise ValidationError("This file is not a valid PDF.", code="invalid_pdf")
