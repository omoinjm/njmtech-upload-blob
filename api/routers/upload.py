from fastapi import APIRouter, UploadFile, File, Depends, HTTPException
from fastapi.responses import JSONResponse
from ..dependencies import verify_token
from ..services.blob_storage import upload_to_blob_storage

router = APIRouter()

@router.post("/upload", dependencies=[Depends(verify_token)])
async def upload(file: UploadFile = File(...)):
    contents = await file.read()
    url = upload_to_blob_storage(file.filename, contents)
    
    return JSONResponse(status_code=200, content={"url": url})
