import vercel_blob
from werkzeug.utils import secure_filename
from datetime import datetime

def upload_to_blob_storage(filename: str, contents: bytes) -> str:
    sanitized_filename = secure_filename(filename)
    now = datetime.now().strftime("%Y-%m-%d-%H-%M-%S")
    path = f"njmtech-blob-api/{now}/{sanitized_filename}"
    blob_result = vercel_blob.put(path, contents)
    return blob_result['url']
