from fastapi import Request
from fastapi.responses import JSONResponse
from fastapi import HTTPException
from ..exceptions import CustomException

async def custom_exception_handler(request: Request, exc: CustomException):
    return JSONResponse(
        status_code=exc.status_code,
        content={
            "error": {
                "detail": exc.detail,
                "title": exc.title,
                "instance": exc.instance,
                "type": exc.type,
                "additional_info": exc.additional_info,
            }
        },
    )

async def http_exception_handler(request: Request, exc: HTTPException):
    return JSONResponse(
        status_code=exc.status_code,
        content={"error": {"detail": exc.detail}},
    )

async def generic_exception_handler(request: Request, exc: Exception):
    return JSONResponse(
        status_code=500,
        content={"error": {"detail": "An unexpected error occurred."}},
    )
