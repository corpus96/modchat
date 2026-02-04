"""Character model"""

from pydantic import BaseModel
from typing import Optional


class Character(BaseModel):
    id: str
    name: str
    description: str
    personality: str = ""
    speech_patterns: str = ""
    motivations: str = ""
    image_path: Optional[str] = None
    is_narrator: bool = False
