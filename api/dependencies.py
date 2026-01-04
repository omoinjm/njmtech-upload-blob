from fastapi import Header
from .config import API_TOKEN
from .exceptions import CustomException

async def verify_token(authorization: str = Header(None)):
    if not authorization:
        raise CustomException(
            status_code=401,
            detail="Authorization header is missing",
            title="Unauthorized",
            type="https://example.com/errors/unauthorized",
        )
    token_type, _, token = authorization.partition(' ')
    if token_type.lower() != "bearer" or token != API_TOKEN:
        raise CustomException(
            status_code=401,
            detail="Invalid token",
            title="Unauthorized",
            type="https://example.com/errors/unauthorized",
        )
