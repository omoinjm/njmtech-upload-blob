from fastapi import Depends
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from .config import API_TOKEN
from .exceptions import CustomException

security = HTTPBearer()

async def verify_token(credentials: HTTPAuthorizationCredentials = Depends(security)):
    token = credentials.credentials
    if token != API_TOKEN:
        raise CustomException(
            status_code=401,
            detail="Invalid token",
            title="Unauthorized",
            type="https://example.com/errors/unauthorized",
        )
