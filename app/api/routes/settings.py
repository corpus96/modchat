"""Application settings routes"""

from fastapi import APIRouter, HTTPException
from app.core.state import get_state

router = APIRouter()


@router.post("/settings/toggle")
async def toggle_setting(setting: str, value: bool):
    """Toggle application settings"""
    state = get_state()
    
    if setting == "auto_response":
        state.auto_response_enabled = value
    elif setting == "show_reactions":
        state.show_reactions = value
    else:
        raise HTTPException(status_code=400, detail="Unknown setting")
    
    return {"status": "success", "setting": setting, "value": value}
