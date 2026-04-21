import vercel_blob
from werkzeug.utils import secure_filename
from pathlib import Path
import os
import redis
import json

# Initialize Redis client
REDIS_URL = os.environ.get("REDIS_URL")
r = redis.Redis.from_url(REDIS_URL) if REDIS_URL else None
CACHE_KEY = "blob_files_cache"
CACHE_TTL = 86400  # 24 hours


def get_cached_blobs():
    if not r:
        return None
    cached_data = r.get(CACHE_KEY)
    if cached_data:
        return json.loads(cached_data)
    return None


def set_cached_blobs(data):
    if r:
        r.set(CACHE_KEY, json.dumps(data), ex=CACHE_TTL)


def invalidate_cache():
    if r:
        r.delete(CACHE_KEY)


def upload_to_blob_storage(
    filename: str, contents: bytes, blob_path: str, allow_overwrite: bool = False
) -> tuple[str, str]:
    sanitized_filename = secure_filename(filename)

    # Check if the filename already has a markdown extension
    if sanitized_filename.lower().endswith((".md", ".markdown")):
        # Save without appending .txt
        path = f"njmtech-blob-api/{blob_path}/{sanitized_filename}"
    else:
        # Maintain existing logic for all other files
        path = f"njmtech-blob-api/{blob_path}/{sanitized_filename}.txt"

    blob_result = vercel_blob.put(path, contents, {"allowOverwrite": allow_overwrite})

    # Invalidate cache on new upload
    invalidate_cache()

    return blob_result["url"], path


def list_blobs():
    # Try to get from cache first
    cached_data = get_cached_blobs()
    if cached_data is not None:
        return cached_data

    # Wrap the prefix in an options dictionary
    options = {"prefix": "njmtech-blob-api/"}
    result = vercel_blob.list(options)

    # Access the list of blobs from the result
    blobs_list = result.get("blobs", [])

    groups = {}

    for blob in blobs_list:
        pathname = blob.get("pathname", "")
        url = blob.get("url")
        uploaded_at = blob.get("uploadedAt")

        # Group by the parent directory
        p = Path(pathname)
        parent_dir = str(p.parent)
        filename = p.name

        if parent_dir not in groups:
            groups[parent_dir] = {
                "path": parent_dir,
                "timestamp": uploaded_at,
                "txt_url": None,
                "md_url": None,
            }

        # Update timestamp to the latest file in that directory
        if uploaded_at and (
            not groups[parent_dir]["timestamp"]
            or uploaded_at > groups[parent_dir]["timestamp"]
        ):
            groups[parent_dir]["timestamp"] = uploaded_at

        # Map files based on suffix
        if filename.endswith(".md"):
            groups[parent_dir]["md_url"] = url
        elif filename.endswith(".txt"):
            groups[parent_dir]["txt_url"] = url

    # Sort by path for consistent output
    sorted_groups = [groups[k] for k in sorted(groups.keys())]

    # Save to cache
    set_cached_blobs(sorted_groups)

    return sorted_groups


def delete_from_blob_storage(url: str):
    """
    Deletes a blob directly using its URL.
    This saves one Advanced Operation by avoiding the list() call.
    """
    try:
        vercel_blob.delete(url)
        invalidate_cache()
        return True
    except Exception:
        return False
