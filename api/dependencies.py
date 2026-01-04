from fastapi import HTTPException, Header
from .config import API_TOKEN

async def verify_token(authorization: str = Header(None)):
    if not authorization:
        raise HTTPException(status_code=401, detail="Authorization header is missing")
    token_type, _, token = authorization.partition(' ')
    if token_type.lower() != "bearer" or token != API_TOKEN:
        raise HTTPException(status_code=401, detail="Invalid token")
