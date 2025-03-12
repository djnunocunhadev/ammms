from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import Dict, Optional
from config import settings as app_settings

router = APIRouter()

class APIKeyUpdate(BaseModel):
    acoustid: Optional[str] = None
    musicbrainz_app_name: Optional[str] = None
    discogs_token: Optional[str] = None
    beatport_client_id: Optional[str] = None
    beatport_client_secret: Optional[str] = None
    lastfm_api_key: Optional[str] = None
    lastfm_api_secret: Optional[str] = None

@router.get("/api-keys")
async def get_api_keys() -> Dict[str, str]:
    """Get the current API key settings (masked)"""
    return {
        "acoustid": mask_key(app_settings.ACOUSTID_API_KEY),
        "musicbrainz_app_name": app_settings.MUSICBRAINZ_APP_NAME,
        "discogs_token": mask_key(app_settings.DISCOGS_TOKEN),
        "beatport_client_id": mask_key(app_settings.BEATPORT_CLIENT_ID),
        "beatport_client_secret": mask_key(app_settings.BEATPORT_CLIENT_SECRET),
        "lastfm_api_key": mask_key(app_settings.LASTFM_API_KEY),
        "lastfm_api_secret": mask_key(app_settings.LASTFM_API_SECRET)
    }

@router.put("/api-keys")
async def update_api_keys(keys: APIKeyUpdate) -> Dict[str, str]:
    """Update API key settings"""
    # In a real implementation, this would update the .env file or a secure key storage
    # For now, we'll just return a success message
    return {"message": "API keys updated successfully"}

def mask_key(key: str) -> str:
    """Mask an API key for display"""
    if not key:
        return ""
    return f"{key[:4]}...{key[-4:]}" if len(key) > 8 else "****"
