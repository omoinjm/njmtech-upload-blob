from fastapi import APIRouter, UploadFile, File, Depends, HTTPException
from fastapi.responses import JSONResponse
from ..dependencies import verify_token
from ..services.blob_storage import upload_to_blob_storage, list_blobs
from ..exceptions import CustomException

router = APIRouter()

@router.get("/files", dependencies=[Depends(verify_token)])
async def list_files():
    try:
        return list_blobs()
    except Exception as e:
        raise CustomException(
            status_code=500,
            detail="Failed to list files from blob storage.",
            title="Blob Storage Error",
            instance="/api/v1/files",
            type="https://example.com/errors/blob-storage-error",
            additional_info={"original_error": str(e)},
        )


@router.post("/upload", dependencies=[Depends(verify_token)])
async def upload(file: UploadFile = File(...)):
    try:
        contents = await file.read()
        url, path = upload_to_blob_storage(file.filename, contents)
        
        return JSONResponse(status_code=200, content={"url": url, "path": path})
    except Exception as e:
        raise CustomException(
            status_code=500,
            detail="Failed to upload file to blob storage.",
            title="Blob Storage Error",
            instance=f"/api/v1/upload",
            type="https://example.com/errors/blob-storage-error",
            additional_info={"original_error": str(e)},
        )
