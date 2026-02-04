"""
AI-Powered Role-Playing Web Application
Runs entirely locally with open-source AI models
"""

from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from app.core.config import settings
from app.api import router

# Initialize FastAPI application
app = FastAPI(title=settings.app_title)

# Include API routes
app.include_router(router)


@app.get("/")
async def root():
    """Serve the main HTML page"""
    return FileResponse("static/index.html")


# Mount static files
app.mount("/static", StaticFiles(directory=settings.static_dir), name="static")
app.mount("/images", StaticFiles(directory=settings.images_dir), name="images")
