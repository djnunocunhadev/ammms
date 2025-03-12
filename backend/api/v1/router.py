from fastapi import APIRouter
from .endpoints import audio, metadata, settings

api_router = APIRouter()

api_router.include_router(audio.router, prefix="/audio", tags=["audio"])
api_router.include_router(metadata.router, prefix="/metadata", tags=["metadata"])
api_router.include_router(settings.router, prefix="/settings", tags=["settings"])
