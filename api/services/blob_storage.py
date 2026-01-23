import vercel_blob
from werkzeug.utils import secure_filename
# from datetime import datetime


def upload_to_blob_storage(
    filename: str, contents: bytes, blob_path: str
) -> tuple[str, str]:
    sanitized_filename = secure_filename(filename)

    # now = datetime.now().strftime("%Y-%m-%d_%H:%M:%S")

    path = f"njmtech-blob-api/{blob_path}/{sanitized_filename}.txt"
    blob_result = vercel_blob.put(path, contents)
    return blob_result["url"], path


def list_blobs():
    # Wrap the prefix in an options dictionary
    options = {"prefix": "njmtech-blob-api/"}
    result = vercel_blob.list(options)

    formatted_blobs = []

    # Access the list of blobs from the result
    blobs_list = result.get("blobs", [])

    for blob in blobs_list:
        formatted_blobs.append({"url": blob.get("url"), "path": blob.get("pathname")})

    return formatted_blobs
