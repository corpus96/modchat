"""Conversation management routes"""

from fastapi import APIRouter, HTTPException, Form
from datetime import datetime
from typing import Optional
import json
import os

from app.models import Character, Scenario, Conversation
from app.core.config import settings
from app.core.state import get_state

router = APIRouter()


@router.post("/conversation/new")
async def create_conversation(
    scenario_description: str = Form(""),
    character1_name: str = Form(...),
    character1_description: str = Form(""),
    character2_name: str = Form(...),
    character2_description: str = Form("")
):
    """Create a new conversation with initial setup"""
    from app.services.ai_service import ai_service
    state = get_state()
    
    conv_id = f"conv_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
    
    # Generate scenario if empty
    if not scenario_description or scenario_description.strip() == "":
        scenario_description = _generate_scenario(character1_name, character2_name)
    
    # Generate character descriptions if empty
    if not character1_description or character1_description.strip() == "":
        character1_description = _generate_character_description(character1_name, scenario_description)
    
    if not character2_description or character2_description.strip() == "":
        character2_description = _generate_character_description(character2_name, scenario_description)
    
    # Create narrator (fixed character)
    narrator = Character(
        id="narrator",
        name="Narrator",
        description="The omniscient narrator who describes the world and guides the story",
        personality="Objective, descriptive, engaging storyteller",
        is_narrator=True
    )
    
    # Create main characters
    char1 = Character(
        id="char1",
        name=character1_name,
        description=character1_description
    )
    
    char2 = Character(
        id="char2",
        name=character2_name,
        description=character2_description
    )
    
    # Create scenario
    scenario = Scenario(description=scenario_description)
    
    # Create conversation
    conversation = Conversation(
        id=conv_id,
        name=f"Story: {scenario_description[:50]}",
        scenario=scenario,
        characters=[narrator, char1, char2],
        messages=[]
    )
    
    state.conversation = conversation
    state.current_message_index = -1
    
    return {"status": "success", "conversation_id": conv_id}


def _generate_scenario(char1_name: str, char2_name: str) -> str:
    """Generate a scenario based on character names"""
    from app.services.ai_service import ai_service
    
    prompt = f"""Create a brief scenario for a story featuring two characters named {char1_name} and {char2_name}.

Write 1-2 sentences describing the setting and situation. Be creative and interesting.

Scenario:"""
    
    response = ai_service.get_response(prompt)
    return response.strip()


def _generate_character_description(name: str, scenario: str) -> str:
    """Generate a character description based on name and scenario"""
    from app.services.ai_service import ai_service
    
    prompt = f"""Create a character description for someone named {name}.

Setting: {scenario}

Write 1-2 sentences describing their personality, background, and speaking style. Make them interesting and unique.

Character description:"""
    
    response = ai_service.get_response(prompt)
    return response.strip()


@router.post("/conversation/save")
async def save_conversation():
    """Save the current conversation to a JSON file"""
    state = get_state()
    
    if not state.conversation:
        raise HTTPException(status_code=400, detail="No active conversation")
    
    filename = f"{state.conversation.id}.json"
    filepath = os.path.join(settings.save_dir, filename)
    
    with open(filepath, "w", encoding="utf-8") as f:
        json.dump(state.conversation.model_dump(), f, indent=2, ensure_ascii=False)
    
    return {"status": "success", "filename": filename, "path": filepath}


@router.post("/conversation/load")
async def load_conversation(filename: str = Form(...)):
    """Load a conversation from a JSON file"""
    state = get_state()
    
    filepath = os.path.join(settings.save_dir, filename)
    if not os.path.exists(filepath):
        raise HTTPException(status_code=404, detail="Conversation file not found")
    
    with open(filepath, "r", encoding="utf-8") as f:
        data = json.load(f)
    
    state.conversation = Conversation(**data)
    state.current_message_index = len(state.conversation.messages) - 1
    
    return {"status": "success", "conversation": state.conversation}


@router.get("/conversation/list")
async def list_conversations():
    """List all saved conversations"""
    files = [f for f in os.listdir(settings.save_dir) if f.endswith(".json")]
    conversations = []
    
    for filename in files:
        filepath = os.path.join(settings.save_dir, filename)
        with open(filepath, "r", encoding="utf-8") as f:
            data = json.load(f)
            conversations.append({
                "filename": filename,
                "name": data.get("name", "Unnamed"),
                "created_at": data.get("created_at", ""),
                "message_count": len(data.get("messages", []))
            })
    
    return {"conversations": conversations}


@router.post("/scenario/update")
async def update_scenario(
    what_happens_next: Optional[str] = Form(None),
    never_forget: Optional[str] = Form(None)
):
    """Update scenario fields"""
    state = get_state()
    
    if not state.conversation:
        raise HTTPException(status_code=400, detail="No active conversation")
    
    if what_happens_next is not None:
        state.conversation.scenario.what_happens_next = what_happens_next
    if never_forget is not None:
        state.conversation.scenario.never_forget = never_forget
    
    return {"status": "success", "scenario": state.conversation.scenario}


@router.get("/state")
async def get_application_state():
    """Get current application state"""
    state = get_state()
    
    return {
        "conversation": state.conversation,
        "auto_response_enabled": state.auto_response_enabled,
        "show_reactions": state.show_reactions,
        "current_message_index": state.current_message_index
    }
