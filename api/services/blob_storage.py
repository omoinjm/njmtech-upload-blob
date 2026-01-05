import vercel_blob
from werkzeug.utils import secure_filename
from datetime import datetime


def upload_to_blob_storage(filename: str, contents: bytes) -> tuple[str, str]:
    sanitized_filename = secure_filename(filename)
    now = datetime.now().strftime("%Y-%m-%d-%H-%M-%S")
    path = f"njmtech-blob-api/{sanitized_filename}"
    blob_result = vercel_blob.put(path, contents)
    return blob_result["url"], path


def list_blobs():
    result = vercel_blob.list()
    # Filter by prefix manually after getting results
    formatted_blobs = []
    for blob in result.get("blobs", []):
        # Filter by prefix manually after getting results
        pathname = blob.get("pathname", "")
        if pathname.startswith("njmtech-blob-api/"):
            formatted_blobs.append(
                {"url": blob.get("url"), "path": blob.get("pathname")}
            )
    return formatted_blobs
