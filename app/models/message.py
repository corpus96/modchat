"""Message model"""

from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime


class Message(BaseModel):
    id: str
    character_id: str
    character_name: str
    content: str
    reaction: Optional[str] = None
    timestamp: str = Field(default_factory=lambda: datetime.now().isoformat())
