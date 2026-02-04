"""Message management routes"""

from fastapi import APIRouter, HTTPException
from typing import Optional

from app.models import Message
from app.core.state import get_state
from app.services.ai_service import ai_service
from app.services.summary_service import summary_service

router = APIRouter()


@router.post("/message/generate")
async def generate_message(character_id: Optional[str] = None):
    """Generate an AI response for a character"""
    state = get_state()
    
    if not state.conversation:
        raise HTTPException(status_code=400, detail="No active conversation")
    
    # Decide which character should respond
    if state.auto_response_enabled and not character_id:
        # AI decides who responds
        character_id = await ai_service.decide_next_character()
    elif not character_id:
        raise HTTPException(status_code=400, detail="Character ID required when auto-response is disabled")
    
    # Get character
    character = next((c for c in state.conversation.characters if c.id == character_id), None)
    if not character:
        raise HTTPException(status_code=404, detail="Character not found")
    
    # Generate AI response
    reaction, dialogue = await ai_service.generate_character_response(character)
    
    # Create message
    message = Message(
        id=f"msg_{len(state.conversation.messages)}",
        character_id=character.id,
        character_name=character.name,
        content=dialogue,
        reaction=reaction if state.show_reactions else None
    )
    
    # Add to conversation
    state.conversation.messages.append(message)
    state.current_message_index = len(state.conversation.messages) - 1
    
    # Check if summary is needed
    if summary_service.should_generate_summary():
        await summary_service.generate_summary()
    
    return {"status": "success", "message": message}


@router.post("/message/manual")
async def add_manual_message(character_id: str, content: str, reaction: Optional[str] = None):
    """Add a manually written message"""
    state = get_state()
    
    if not state.conversation:
        raise HTTPException(status_code=400, detail="No active conversation")
    
    character = next((c for c in state.conversation.characters if c.id == character_id), None)
    if not character:
        raise HTTPException(status_code=404, detail="Character not found")
    
    message = Message(
        id=f"msg_{len(state.conversation.messages)}",
        character_id=character.id,
        character_name=character.name,
        content=content,
        reaction=reaction if state.show_reactions else None
    )
    
    state.conversation.messages.append(message)
    state.current_message_index = len(state.conversation.messages) - 1
    
    return {"status": "success", "message": message}


@router.put("/message/{message_index}/edit")
async def edit_message(message_index: int, content: str, reaction: Optional[str] = None):
    """Edit an existing message"""
    state = get_state()
    
    if not state.conversation:
        raise HTTPException(status_code=400, detail="No active conversation")
    
    if message_index < 0 or message_index >= len(state.conversation.messages):
        raise HTTPException(status_code=404, detail="Message not found")
    
    message = state.conversation.messages[message_index]
    message.content = content
    if reaction is not None:
        message.reaction = reaction
    
    return {"status": "success", "message": message}


@router.post("/message/regenerate")
async def regenerate_last_message():
    """Regenerate the last message"""
    state = get_state()
    
    if not state.conversation or not state.conversation.messages:
        raise HTTPException(status_code=400, detail="No messages to regenerate")
    
    # Remove last message
    last_message = state.conversation.messages.pop()
    
    # Generate new response for the same character
    return await generate_message(character_id=last_message.character_id)


@router.post("/message/navigate")
async def navigate_messages(direction: str):
    """Navigate forward or backward in message history"""
    state = get_state()
    
    if not state.conversation:
        raise HTTPException(status_code=400, detail="No active conversation")
    
    if direction == "back":
        if state.current_message_index > 0:
            state.current_message_index -= 1
    elif direction == "forward":
        if state.current_message_index < len(state.conversation.messages) - 1:
            state.current_message_index += 1
    
    return {
        "status": "success",
        "current_index": state.current_message_index,
        "total_messages": len(state.conversation.messages)
    }
