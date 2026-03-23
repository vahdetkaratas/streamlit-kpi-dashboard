import pytest

from src.upload_limits import UploadTooLargeError, require_upload_under


def test_require_upload_under_accepts_within_limit():
    require_upload_under(size_bytes=100, limit_bytes=200, label="test")


def test_require_upload_under_rejects_over_limit():
    with pytest.raises(UploadTooLargeError):
        require_upload_under(size_bytes=300, limit_bytes=200, label="CSV upload")
