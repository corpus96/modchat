"""API routes"""

from fastapi import APIRouter
from .conversation import router as conversation_router
from .character import router as character_router
from .message import router as message_router
from .settings import router as settings_router

# Main API router
router = APIRouter(prefix="/api")

# Include sub-routers
router.include_router(conversation_router, tags=["conversation"])
router.include_router(character_router, tags=["character"])
router.include_router(message_router, tags=["message"])
router.include_router(settings_router, tags=["settings"])

__all__ = ["router"]
