import pytest
from fastapi.testclient import TestClient
from api.main import app
import os

from unittest.mock import patch

client = TestClient(app)

# Create a dummy file for testing
DUMMY_FILE_CONTENT = b"Hello, this is a test file."
DUMMY_FILE_NAME = "test_file.txt"

@pytest.fixture(scope="module", autouse=True)
def create_dummy_file():
    with open(DUMMY_FILE_NAME, "wb") as f:
        f.write(DUMMY_FILE_CONTENT)
    yield
    os.remove(DUMMY_FILE_NAME)

@patch("api.main.vercel_blob.put")
def test_upload_file(mock_put):
    mock_put.return_value = {"url": "https://fake-blob-storage.com/test_file.txt"}
    with open(DUMMY_FILE_NAME, "rb") as f:
        response = client.post("/api/upload", files={"file": (DUMMY_FILE_NAME, f, "text/plain")})
    
    assert response.status_code == 200
    assert response.json() == {"url": "https://fake-blob-storage.com/test_file.txt"}

def test_upload_no_file():
    response = client.post("/api/upload")
    assert response.status_code == 422
