"""Application configuration"""

import os
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    """Application settings"""
    
    # Application
    app_title: str = "Local AI RPG Chat"
    app_host: str = "0.0.0.0"
    app_port: int = 8000
    
    # Directories
    save_dir: str = "saved_conversations"
    images_dir: str = "character_images"
    static_dir: str = "static"
    
    # AI Model
    ai_model: str = "llama3.2:1b"
    
    # Conversation
    max_messages_before_summary: int = 20
    
    class Config:
        env_file = ".env"
        case_sensitive = False


settings = Settings()

# Ensure directories exist
os.makedirs(settings.save_dir, exist_ok=True)
os.makedirs(settings.images_dir, exist_ok=True)
