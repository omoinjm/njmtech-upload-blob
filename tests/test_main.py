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
    mock_upload_to_blob_storage.return_value = (f"https://fake-blob-storage.com/{expected_path}", expected_path)
    headers = {"Authorization": f"Bearer {API_TOKEN}"}
    with open(DUMMY_FILE_NAME, "rb") as f:
        response = client.post("/api/v1/upload", files={"file": (DUMMY_FILE_NAME, f, "text/plain")}, headers=headers)
    
    assert response.status_code == 200
    assert response.json() == {"url": f"https://fake-blob-storage.com/{expected_path}", "path": expected_path}
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

@patch("api.routers.upload.list_blobs")
def test_list_files(mock_list_blobs):
    mock_blobs_data = [
        {"url": "https://fake-blob-storage.com/njmtech-blob-api/2023-01-01-12-00-00/file1.txt", "path": "njmtech-blob-api/2023-01-01-12-00-00/file1.txt"},
        {"url": "https://fake-blob-storage.com/njmtech-blob-api/2023-01-01-12-00-00/file2.txt", "path": "njmtech-blob-api/2023-01-01-12-00-00/file2.txt"},
    ]
    mock_list_blobs.return_value = mock_blobs_data
    headers = {"Authorization": f"Bearer {API_TOKEN}"}
    response = client.get("/api/v1/files", headers=headers)
    assert response.status_code == 200
    assert response.json() == mock_blobs_data
    mock_list_blobs.assert_called_once()

@patch("api.services.blob_storage.vercel_blob.list")
def test_list_files_prefix(mock_vercel_blob_list):
    mock_vercel_blob_list.return_value = {"blobs": []}
    headers = {"Authorization": f"Bearer {API_TOKEN}"}
    client.get("/api/v1/files", headers=headers)
    mock_vercel_blob_list.assert_called_once_with(prefix="njmtech-blob-api/")

@patch("api.routers.upload.upload_to_blob_storage")
def test_upload_file_blob_storage_error(mock_upload_to_blob_storage):
    mock_upload_to_blob_storage.side_effect = Exception("Blob storage is down")
    headers = {"Authorization": f"Bearer {API_TOKEN}"}
    with open(DUMMY_FILE_NAME, "rb") as f:
        response = client.post("/api/v1/upload", files={"file": (DUMMY_FILE_NAME, f, "text/plain")}, headers=headers)
    
    assert response.status_code == 500
    assert response.json() == {
        "error": {
            "detail": "Failed to upload file to blob storage.",
            "title": "Blob Storage Error",
            "instance": "/api/v1/upload",
            "type": "https://example.com/errors/blob-storage-error",
            "additional_info": {"original_error": "Blob storage is down"},
        }
    }

@patch("api.routers.upload.list_blobs")
def test_list_files_blob_storage_error(mock_list_blobs):
    mock_list_blobs.side_effect = Exception("Blob storage is down")
    headers = {"Authorization": f"Bearer {API_TOKEN}"}
    response = client.get("/api/v1/files", headers=headers)
    assert response.status_code == 500
    assert response.json() == {
        "error": {
            "detail": "Failed to list files from blob storage.",
            "title": "Blob Storage Error",
            "instance": "/api/v1/files",
            "type": "https://example.com/errors/blob-storage-error",
            "additional_info": {"original_error": "Blob storage is down"},
        }
    }

