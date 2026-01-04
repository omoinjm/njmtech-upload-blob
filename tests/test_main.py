import pytest
from fastapi.testclient import TestClient
from api.main import app
import os
from werkzeug.utils import secure_filename

from unittest.mock import patch

client = TestClient(app)

# Create a dummy file for testing
DUMMY_FILE_CONTENT = b"Hello, this is a test file."
DUMMY_FILE_NAME = "test file with spaces & special chars.txt"
API_TOKEN = "test-token"

@pytest.fixture(scope="module", autouse=True)
def create_dummy_file():
    with open(DUMMY_FILE_NAME, "wb") as f:
        f.write(DUMMY_FILE_CONTENT)
    yield
    os.remove(DUMMY_FILE_NAME)

import pytest
from fastapi.testclient import TestClient
from api.main import app
import os
from werkzeug.utils import secure_filename
from unittest.mock import patch
from datetime import datetime

client = TestClient(app)

# Create a dummy file for testing
DUMMY_FILE_CONTENT = b"Hello, this is a test file."
DUMMY_FILE_NAME = "test file with spaces & special chars.txt"
API_TOKEN = "test-token"
FIXED_DATETIME = datetime(2023, 1, 1, 12, 0, 0)
FIXED_DATETIME_STR = FIXED_DATETIME.strftime("%Y-%m-%d-%H-%M-%S")

@pytest.fixture(scope="module", autouse=True)
def create_dummy_file():
    with open(DUMMY_FILE_NAME, "wb") as f:
        f.write(DUMMY_FILE_CONTENT)
    yield
    os.remove(DUMMY_FILE_NAME)

@patch("api.services.blob_storage.datetime", wraps=datetime)
@patch("api.routers.upload.upload_to_blob_storage")
def test_upload_file(mock_upload_to_blob_storage, mock_datetime):
    mock_datetime.now.return_value = FIXED_DATETIME
    sanitized_filename = secure_filename(DUMMY_FILE_NAME)
    expected_path = f"njmtech-blob-api/{FIXED_DATETIME_STR}/{sanitized_filename}"
    mock_upload_to_blob_storage.return_value = f"https://fake-blob-storage.com/{expected_path}"
    headers = {"Authorization": f"Bearer {API_TOKEN}"}
    with open(DUMMY_FILE_NAME, "rb") as f:
        response = client.post("/api/v1/upload", files={"file": (DUMMY_FILE_NAME, f, "text/plain")}, headers=headers)
    
    assert response.status_code == 200
    assert response.json() == {"url": f"https://fake-blob-storage.com/{expected_path}"}
    mock_upload_to_blob_storage.assert_called_once_with(DUMMY_FILE_NAME, DUMMY_FILE_CONTENT)

def test_upload_file_no_token():
    with open(DUMMY_FILE_NAME, "rb") as f:
        response = client.post("/api/v1/upload", files={"file": (DUMMY_FILE_NAME, f, "text/plain")})
    assert response.status_code == 401
    assert response.json() == {"error": {"detail": "Authorization header is missing"}}

def test_upload_file_invalid_token():
    headers = {"Authorization": "Bearer invalid-token"}
    with open(DUMMY_FILE_NAME, "rb") as f:
        response = client.post("/api/v1/upload", files={"file": (DUMMY_FILE_NAME, f, "text/plain")}, headers=headers)
    assert response.status_code == 401
    assert response.json() == {"error": {"detail": "Invalid token"}}

def test_upload_no_file():
    headers = {"Authorization": f"Bearer {API_TOKEN}"}
    response = client.post("/api/v1/upload", headers=headers)
    assert response.status_code == 422

def test_health_check():
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json() == {"status": "ok"}