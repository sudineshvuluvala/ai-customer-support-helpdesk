import io
import os
import uuid
import zipfile

from werkzeug.utils import secure_filename

from .error_handlers import ApiError

MIME_BY_EXT = {
    "pdf": "application/pdf",
    "png": "image/png",
    "jpg": "image/jpeg",
    "jpeg": "image/jpeg",
    "txt": "text/plain",
    "docx": "application/vnd.openxmlformats-officedocument.wordprocessingml.document",
}


def _content_matches(ext, data):
    """Validate the real file content (magic bytes), not just the extension."""
    if ext == "pdf":
        return data[:5] == b"%PDF-"
    if ext == "png":
        return data[:8] == b"\x89PNG\r\n\x1a\n"
    if ext in ("jpg", "jpeg"):
        return data[:3] == b"\xff\xd8\xff"
    if ext == "txt":
        if b"\x00" in data:
            return False
        try:
            data.decode("utf-8")
            return True
        except UnicodeDecodeError:
            return False
    if ext == "docx":
        try:
            with zipfile.ZipFile(io.BytesIO(data)) as z:
                names = z.namelist()
                return "[Content_Types].xml" in names and any(n.startswith("word/") for n in names)
        except zipfile.BadZipFile:
            return False
    return False


def validate_upload(file_storage, allowed, max_bytes):
    """Returns (data, ext, mime, safe_original_name) or raises ApiError."""
    original = secure_filename(file_storage.filename or "")
    if not original or "." not in original:
        raise ApiError("Invalid file name.", 422, "invalid_file")
    ext = original.rsplit(".", 1)[1].lower()
    if ext not in allowed:
        raise ApiError(f"File type .{ext} is not allowed. Allowed: {', '.join(sorted(allowed))}.", 422, "invalid_file_type")
    data = file_storage.read(max_bytes + 1)
    if not data:
        raise ApiError("File is empty.", 422, "invalid_file")
    if len(data) > max_bytes:
        raise ApiError(f"File exceeds the {max_bytes // (1024 * 1024)} MB limit.", 413, "file_too_large")
    if not _content_matches(ext, data):
        raise ApiError("File content does not match its extension.", 422, "invalid_file_content")
    return data, ext, MIME_BY_EXT[ext], original


def store_file(root, ticket_id, data, ext):
    """Saves with a random name outside any public web root. Returns (stored_filename, relative_path)."""
    stored = f"{uuid.uuid4().hex}.{ext}"
    rel = os.path.join(str(ticket_id), stored)
    full = os.path.join(root, rel)
    os.makedirs(os.path.dirname(full), exist_ok=True)
    with open(full, "wb") as f:
        f.write(data)
    return stored, rel.replace("\\", "/")


def resolve_path(root, rel):
    full = os.path.abspath(os.path.join(root, rel))
    if not full.startswith(os.path.abspath(root) + os.sep):
        raise ApiError("Invalid file path.", 400, "invalid_path")
    return full
