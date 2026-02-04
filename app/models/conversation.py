"""Conversation and state models"""

from pydantic import BaseModel, Field
from typing import List, Optional
from datetime import datetime
from .character import Character
from .message import Message
from .scenario import Scenario


class Conversation(BaseModel):
    id: str
    name: str
    scenario: Scenario
    characters: List[Character]
    messages: List[Message]
    summaries: List[str] = []
    created_at: str = Field(default_factory=lambda: datetime.now().isoformat())
    updated_at: str = Field(default_factory=lambda: datetime.now().isoformat())


class ConversationState(BaseModel):
    conversation: Optional[Conversation] = None
    auto_response_enabled: bool = True
    show_reactions: bool = True
    current_message_index: int = -1
