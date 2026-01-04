from fastapi import FastAPI, HTTPException
from fastapi.responses import JSONResponse
from .routers import upload
from .middleware.error_handling import http_exception_handler, generic_exception_handler, custom_exception_handler
from .exceptions import CustomException

app = FastAPI()

app.add_exception_handler(HTTPException, http_exception_handler)
app.add_exception_handler(Exception, generic_exception_handler)
app.add_exception_handler(CustomException, custom_exception_handler)

@app.get("/health")
async def health_check():
    return JSONResponse(status_code=200, content={"status": "ok"})

app.include_router(upload.router, prefix="/api/v1")