"""Scenario model"""

from pydantic import BaseModel


class Scenario(BaseModel):
    description: str
    current_state: str = ""
    what_happens_next: str = ""
    never_forget: str = ""
