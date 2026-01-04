from fastapi import APIRouter, UploadFile, File, Depends
from fastapi.responses import JSONResponse
from ..dependencies import verify_token
from ..services.blob_storage import upload_to_blob_storage, list_blobs

router = APIRouter()

@router.get("/files", dependencies=[Depends(verify_token)])
async def list_files():
    return list_blobs()


@router.post("/upload", dependencies=[Depends(verify_token)])
async def upload(file: UploadFile = File(...)):
    contents = await file.read()
    url, path = upload_to_blob_storage(file.filename, contents)
    
    return JSONResponse(status_code=200, content={"url": url, "path": path})
