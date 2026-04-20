from fastapi import APIRouter, UploadFile, File, Depends, Query
from fastapi.responses import JSONResponse
from ..dependencies import verify_token
from ..services.blob_storage import (
    upload_to_blob_storage,
    list_blobs,
    delete_from_blob_storage,
)
from ..helpers.blob import get_filename

router = APIRouter(tags=["Vercel Blob"])


@router.get("/", summary="Root endpoint")
def read_root():
    """Returns a simple welcome message."""
    return JSONResponse(
        status_code=200, content={"message": "Welcome to the Vercel Blob API"}
    )


@router.get("/files", dependencies=[Depends(verify_token)], summary="List all files")
async def list_files():
    """
    Returns a list of all files in Vercel Blob storage, grouped by their parent directory.
    Each record includes the timestamp, .txt URL, and .md.txt URL where applicable.
    """
    return JSONResponse(status_code=200, content={"data": list_blobs()})


@router.delete("/delete", dependencies=[Depends(verify_token)], summary="Delete a blob")
async def delete_blob(
    path: str = Query(..., description="The absolute pathname of the blob to delete")
):
    """
    Deletes a single blob from storage using its absolute pathname.
    Returns 404 if the path is not found.
    """
    success = delete_from_blob_storage(path)
    if success:
        return JSONResponse(
            status_code=200, content={"message": "Blob deleted successfully"}
        )
    else:
        return JSONResponse(status_code=404, content={"message": "Blob not found"})


@router.post("/upload", dependencies=[Depends(verify_token)], summary="Upload a file")
async def upload(
    blob_path: str = Query(..., description="The directory path in blob storage"),
    allow_overwrite: bool = Query(
        False, description="Whether to allow overwriting existing files"
    ),
    file: UploadFile = File(..., description="The file to upload"),
):
    """
    Uploads a file to the specified directory in Vercel Blob storage.
    Automatically appends .txt extension for consistency.
    """
    contents = await file.read()

    file_size = len(contents)
    content_type = file.content_type
    pathname = file.filename

    url, stored_pathname = upload_to_blob_storage(
        get_filename(file),
        contents,
        blob_path,
        allow_overwrite=allow_overwrite,
    )

    return JSONResponse(
        status_code=200,
        content={
            "url": url,
            "pathname": stored_pathname or pathname,
            "content_type": content_type,
            "size": file_size,
        },
    )
