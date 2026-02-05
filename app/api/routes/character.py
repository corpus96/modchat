"""Character management routes"""

from fastapi import APIRouter, HTTPException, UploadFile, File, Form
from datetime import datetime
import os

from app.models import Character
from app.core.config import settings
from app.core.state import get_state

router = APIRouter()


@router.post("/character/add")
async def add_character(name: str = Form(...), description: str = Form("")):
    """Add a new character to the current conversation"""
    from app.services.ai_service import ai_service
    state = get_state()
    
    if not state.conversation:
        raise HTTPException(status_code=400, detail="No active conversation")
    
    # Generate description if empty
    if not description or description.strip() == "":
        prompt = f"""Create a character description for someone named {name}.

Setting: {state.conversation.scenario.description}

Write 1-2 sentences describing their personality, background, and speaking style. Make them fit the story and be interesting.

Character description:"""
        description = ai_service.get_response(prompt).strip()
    
    char_id = f"char{len(state.conversation.characters)}"
    new_char = Character(
        id=char_id,
        name=name,
        description=description
    )
    
    state.conversation.characters.append(new_char)
    return {"status": "success", "character": new_char}


@router.post("/character/{character_id}/image")
async def upload_character_image(character_id: str, file: UploadFile = File(...)):
    """Upload an image for a character"""
    state = get_state()
    
    if not state.conversation:
        raise HTTPException(status_code=400, detail="No active conversation")
    
    # Find character
    character = next((c for c in state.conversation.characters if c.id == character_id), None)
    if not character:
        raise HTTPException(status_code=404, detail="Character not found")
    
    # Save image
    file_extension = os.path.splitext(file.filename)[1]
    image_filename = f"{character_id}_{datetime.now().strftime('%Y%m%d_%H%M%S')}{file_extension}"
    image_path = os.path.join(settings.images_dir, image_filename)
    
    with open(image_path, "wb") as f:
        content = await file.read()
        f.write(content)
    
    character.image_path = image_path
    return {"status": "success", "image_path": image_path}
