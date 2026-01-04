import os
from fastapi import FastAPI, UploadFile, File, HTTPException
from fastapi.responses import JSONResponse
import vercel_blob
from dotenv import load_dotenv

load_dotenv()

app = FastAPI()

@app.post("/api/upload")
async def upload(file: UploadFile = File(...)):
    try:
        if not file:
            raise HTTPException(status_code=400, detail="No file sent.")

        # Read the file content
        contents = await file.read()
        
        # Upload the file to Vercel Blob
        blob_result = vercel_blob.put(file.filename, contents)
        
        return JSONResponse(status_code=200, content={"url": blob_result['url']})

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
