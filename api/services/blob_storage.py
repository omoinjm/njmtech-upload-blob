import vercel_blob
from werkzeug.utils import secure_filename
from pathlib import Path


def upload_to_blob_storage(
    filename: str, contents: bytes, blob_path: str, allow_overwrite: bool = False
) -> tuple[str, str]:
    sanitized_filename = secure_filename(filename)

    path = f"njmtech-blob-api/{blob_path}/{sanitized_filename}.txt"
    blob_result = vercel_blob.put(path, contents, {"allowOverwrite": allow_overwrite})
    return blob_result["url"], path


def list_blobs():
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
        if filename.endswith(".md.txt"):
            groups[parent_dir]["md_url"] = url
        elif filename.endswith(".txt"):
            groups[parent_dir]["txt_url"] = url

    # Sort by path for consistent output
    sorted_groups = [groups[k] for k in sorted(groups.keys())]
    return sorted_groups
