from fastapi import APIRouter, HTTPException, Header
import os
from ..services.blob_storage import list_blobs, invalidate_cache

router = APIRouter(prefix="/api/cron", tags=["Cron"])

CRON_SECRET = os.environ.get("CRON_SECRET")

@router.get("/refresh-cache")
async def refresh_cache(authorization: str = Header(None)):
    """
    Cron job to refresh the blob list cache.
    Hobby plan allows 1 cron job per day.
    """
    if CRON_SECRET and authorization != f"Bearer {CRON_SECRET}":
        raise HTTPException(status_code=401, detail="Unauthorized")
    
    # Invalidate existing cache
    invalidate_cache()
    
    # Trigger a new list() call to re-populate cache
    # This uses 1 Advanced Operation once a day
    data = list_blobs()
    
    return {"status": "success", "message": "Cache refreshed", "items": len(data)}
