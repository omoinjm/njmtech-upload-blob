from fastapi import FastAPI, Request
from fastapi.encoders import jsonable_encoder
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
from .routers import upload
from .middleware.error_handling_middleware import ErrorHandlingMiddleware

app = FastAPI()

app.add_middleware(ErrorHandlingMiddleware)

@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request: Request, exc: RequestValidationError):
    return JSONResponse(
        status_code=422,
        content=jsonable_encoder({"detail": exc.errors(), "body": exc.body}),
    )

@app.get("/health")
async def health_check():
    return JSONResponse(status_code=200, content={"status": "ok"})

app.include_router(upload.router, prefix="/api/v1")