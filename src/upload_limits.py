from __future__ import annotations

# Defensive defaults for untrusted uploads (Streamlit file_uploader).
MAX_CSV_UPLOAD_BYTES = 25 * 1024 * 1024  # 25 MiB
MAX_PRESET_JSON_BYTES = 512 * 1024  # 512 KiB


class UploadTooLargeError(ValueError):
    """Raised when an uploaded file exceeds the configured limit."""


def require_upload_under(*, size_bytes: int, limit_bytes: int, label: str) -> None:
    if size_bytes > limit_bytes:
        mb = limit_bytes / (1024 * 1024)
        if mb >= 1:
            cap = f"{mb:.0f} MB"
        else:
            cap = f"{limit_bytes // 1024} KB"
        raise UploadTooLargeError(f"{label} is too large (max {cap}).")
