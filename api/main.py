from fastapi import FastAPI, Request
from fastapi.encoders import jsonable_encoder
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
from .routers import vercel_blob, home, data
from .middleware.error_handling_middleware import ErrorHandlingMiddleware

app = FastAPI()


app.add_middleware(ErrorHandlingMiddleware)


@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request: Request, exc: RequestValidationError):
    return JSONResponse(
        status_code=422,
        content=jsonable_encoder({"detail": exc.errors(), "body": exc.body}),
    )


app.include_router(home.router)
app.include_router(data.router, prefix="/api/v1/demo")
app.include_router(vercel_blob.router, prefix="/api/v1/blob")
