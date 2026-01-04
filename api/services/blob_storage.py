import vercel_blob
from werkzeug.utils import secure_filename

def upload_to_blob_storage(filename: str, contents: bytes) -> str:
    sanitized_filename = secure_filename(filename)
    blob_result = vercel_blob.put(sanitized_filename, contents)
    return blob_result['url']
