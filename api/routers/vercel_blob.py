from fastapi import APIRouter, UploadFile, File, Depends, Query
from fastapi.responses import JSONResponse
from ..dependencies import verify_token
from ..services.blob_storage import (
    upload_to_blob_storage,
    list_blobs,
    delete_from_blob_storage,
)
from ..helpers.blob import get_filename

router = APIRouter()


@router.get("/")
def read_root():
    return JSONResponse(
        status_code=200, content={"message": "Welcome to the Vercel Blob API"}
    )


@router.get("/files", dependencies=[Depends(verify_token)])
async def list_files():
    return JSONResponse(status_code=200, content={"data": list_blobs()})


@router.delete("/delete", dependencies=[Depends(verify_token)])
async def delete_blob(path: str = Query(...)):
    success = delete_from_blob_storage(path)
    if success:
        return JSONResponse(
            status_code=200, content={"message": "Blob deleted successfully"}
        )
    else:
        return JSONResponse(status_code=404, content={"message": "Blob not found"})


@router.post("/upload", dependencies=[Depends(verify_token)])
async def upload(
    blob_path: str = Query(...),
    allow_overwrite: bool = Query(False),
    file: UploadFile = File(...),
):
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
