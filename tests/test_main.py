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

@patch("api.routers.upload.upload_to_blob_storage")
def test_upload_file(mock_upload_to_blob_storage):
    sanitized_filename = secure_filename(DUMMY_FILE_NAME)
    mock_upload_to_blob_storage.return_value = f"https://fake-blob-storage.com/{sanitized_filename}"
    headers = {"Authorization": f"Bearer {API_TOKEN}"}
    with open(DUMMY_FILE_NAME, "rb") as f:
        response = client.post("/api/v1/upload", files={"file": (DUMMY_FILE_NAME, f, "text/plain")}, headers=headers)
    
    assert response.status_code == 200
    assert response.json() == {"url": f"https://fake-blob-storage.com/{sanitized_filename}"}
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