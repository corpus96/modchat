"""
AI-Powered Role-Playing Web Application
Runs entirely locally with open-source AI models
"""

from fastapi import FastAPI, HTTPException, UploadFile, File
from fastapi.staticfiles import StaticFiles
from fastapi.responses import HTMLResponse, FileResponse
from pydantic import BaseModel, Field
from typing import List, Optional, Dict, Any
import json
import os
from datetime import datetime
import base64
import ollama

app = FastAPI(title="Local AI RPG Chat")

# Data Models
class Character(BaseModel):
    id: str
    name: str
    description: str
    personality: str = ""
    speech_patterns: str = ""
    motivations: str = ""
    image_path: Optional[str] = None
    is_narrator: bool = False

class Message(BaseModel):
    id: str
    character_id: str
    character_name: str
    content: str
    reaction: Optional[str] = None
    timestamp: str = Field(default_factory=lambda: datetime.now().isoformat())

class Scenario(BaseModel):
    description: str
    current_state: str = ""
    what_happens_next: str = ""
    never_forget: str = ""

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

# Global state
state = ConversationState()
SAVE_DIR = "saved_conversations"
IMAGES_DIR = "character_images"
MAX_MESSAGES_BEFORE_SUMMARY = 20

# Ensure directories exist
os.makedirs(SAVE_DIR, exist_ok=True)
os.makedirs(IMAGES_DIR, exist_ok=True)

# Initialize Ollama client
def get_ai_response(prompt: str, model: str = "llama3.2:1b") -> str:
    """Get response from local Ollama AI model"""
    try:
        response = ollama.chat(
            model=model,
            messages=[{"role": "user", "content": prompt}]
        )
        return response["message"]["content"]
    except Exception as e:
        return f"[AI Error: {str(e)}. Make sure Ollama is running with: ollama serve]"

# API Endpoints
@app.get("/", response_class=HTMLResponse)
async def root():
    """Serve the main HTML page"""
    return FileResponse("static/index.html")

@app.post("/api/conversation/new")
async def create_conversation(
    scenario_description: str,
    character1_name: str,
    character1_description: str,
    character2_name: str,
    character2_description: str
):
    """Create a new conversation with initial setup"""
    global state
    
    conv_id = f"conv_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
    
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

@app.post("/api/character/add")
async def add_character(name: str, description: str):
    """Add a new character to the current conversation"""
    if not state.conversation:
        raise HTTPException(status_code=400, detail="No active conversation")
    
    char_id = f"char{len(state.conversation.characters)}"
    new_char = Character(
        id=char_id,
        name=name,
        description=description
    )
    
    state.conversation.characters.append(new_char)
    return {"status": "success", "character": new_char}

@app.post("/api/character/{character_id}/image")
async def upload_character_image(character_id: str, file: UploadFile = File(...)):
    """Upload an image for a character"""
    if not state.conversation:
        raise HTTPException(status_code=400, detail="No active conversation")
    
    # Find character
    character = next((c for c in state.conversation.characters if c.id == character_id), None)
    if not character:
        raise HTTPException(status_code=404, detail="Character not found")
    
    # Save image
    file_extension = os.path.splitext(file.filename)[1]
    image_filename = f"{character_id}_{datetime.now().strftime('%Y%m%d_%H%M%S')}{file_extension}"
    image_path = os.path.join(IMAGES_DIR, image_filename)
    
    with open(image_path, "wb") as f:
        content = await file.read()
        f.write(content)
    
    character.image_path = image_path
    return {"status": "success", "image_path": image_path}

@app.post("/api/message/generate")
async def generate_message(character_id: Optional[str] = None):
    """Generate an AI response for a character"""
    if not state.conversation:
        raise HTTPException(status_code=400, detail="No active conversation")
    
    # Decide which character should respond
    if state.auto_response_enabled and not character_id:
        # AI decides who responds
        character_id = await decide_next_character()
    elif not character_id:
        raise HTTPException(status_code=400, detail="Character ID required when auto-response is disabled")
    
    # Get character
    character = next((c for c in state.conversation.characters if c.id == character_id), None)
    if not character:
        raise HTTPException(status_code=404, detail="Character not found")
    
    # Build prompt
    prompt = build_character_prompt(character)
    
    # Get AI response
    ai_response = get_ai_response(prompt)
    
    # Parse response into reaction and dialogue
    reaction, dialogue = parse_ai_response(ai_response, character.is_narrator)
    
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
    if len(state.conversation.messages) >= MAX_MESSAGES_BEFORE_SUMMARY:
        if len(state.conversation.messages) % MAX_MESSAGES_BEFORE_SUMMARY == 0:
            await generate_summary()
    
    return {"status": "success", "message": message}

@app.post("/api/message/manual")
async def add_manual_message(character_id: str, content: str, reaction: Optional[str] = None):
    """Add a manually written message"""
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

@app.put("/api/message/{message_index}/edit")
async def edit_message(message_index: int, content: str, reaction: Optional[str] = None):
    """Edit an existing message"""
    if not state.conversation:
        raise HTTPException(status_code=400, detail="No active conversation")
    
    if message_index < 0 or message_index >= len(state.conversation.messages):
        raise HTTPException(status_code=404, detail="Message not found")
    
    message = state.conversation.messages[message_index]
    message.content = content
    if reaction is not None:
        message.reaction = reaction
    
    return {"status": "success", "message": message}

@app.post("/api/message/regenerate")
async def regenerate_last_message():
    """Regenerate the last message"""
    if not state.conversation or not state.conversation.messages:
        raise HTTPException(status_code=400, detail="No messages to regenerate")
    
    # Remove last message
    last_message = state.conversation.messages.pop()
    
    # Generate new response for the same character
    return await generate_message(character_id=last_message.character_id)

@app.post("/api/message/navigate")
async def navigate_messages(direction: str):
    """Navigate forward or backward in message history"""
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

@app.post("/api/settings/toggle")
async def toggle_setting(setting: str, value: bool):
    """Toggle application settings"""
    if setting == "auto_response":
        state.auto_response_enabled = value
    elif setting == "show_reactions":
        state.show_reactions = value
    else:
        raise HTTPException(status_code=400, detail="Unknown setting")
    
    return {"status": "success", "setting": setting, "value": value}

@app.post("/api/scenario/update")
async def update_scenario(
    what_happens_next: Optional[str] = None,
    never_forget: Optional[str] = None
):
    """Update scenario fields"""
    if not state.conversation:
        raise HTTPException(status_code=400, detail="No active conversation")
    
    if what_happens_next is not None:
        state.conversation.scenario.what_happens_next = what_happens_next
    if never_forget is not None:
        state.conversation.scenario.never_forget = never_forget
    
    return {"status": "success", "scenario": state.conversation.scenario}

@app.post("/api/conversation/save")
async def save_conversation():
    """Save the current conversation to a JSON file"""
    if not state.conversation:
        raise HTTPException(status_code=400, detail="No active conversation")
    
    filename = f"{state.conversation.id}.json"
    filepath = os.path.join(SAVE_DIR, filename)
    
    with open(filepath, "w", encoding="utf-8") as f:
        json.dump(state.conversation.model_dump(), f, indent=2, ensure_ascii=False)
    
    return {"status": "success", "filename": filename, "path": filepath}

@app.post("/api/conversation/load")
async def load_conversation(filename: str):
    """Load a conversation from a JSON file"""
    global state
    
    filepath = os.path.join(SAVE_DIR, filename)
    if not os.path.exists(filepath):
        raise HTTPException(status_code=404, detail="Conversation file not found")
    
    with open(filepath, "r", encoding="utf-8") as f:
        data = json.load(f)
    
    state.conversation = Conversation(**data)
    state.current_message_index = len(state.conversation.messages) - 1
    
    return {"status": "success", "conversation": state.conversation}

@app.get("/api/conversation/list")
async def list_conversations():
    """List all saved conversations"""
    files = [f for f in os.listdir(SAVE_DIR) if f.endswith(".json")]
    conversations = []
    
    for filename in files:
        filepath = os.path.join(SAVE_DIR, filename)
        with open(filepath, "r", encoding="utf-8") as f:
            data = json.load(f)
            conversations.append({
                "filename": filename,
                "name": data.get("name", "Unnamed"),
                "created_at": data.get("created_at", ""),
                "message_count": len(data.get("messages", []))
            })
    
    return {"conversations": conversations}

@app.get("/api/state")
async def get_state():
    """Get current application state"""
    return {
        "conversation": state.conversation,
        "auto_response_enabled": state.auto_response_enabled,
        "show_reactions": state.show_reactions,
        "current_message_index": state.current_message_index
    }

# Helper Functions
async def decide_next_character() -> str:
    """Use AI to decide which character should respond next"""
    if not state.conversation or not state.conversation.messages:
        # First message - narrator starts
        return "narrator"
    
    # Build prompt for AI to decide
    recent_messages = state.conversation.messages[-3:]
    context = "\n".join([f"{m.character_name}: {m.content}" for m in recent_messages])
    
    characters_list = "\n".join([
        f"- {c.id}: {c.name} ({c.description[:50]}...)"
        for c in state.conversation.characters
        if not c.is_narrator
    ])
    
    prompt = f"""Given this conversation context:
{context}

Available characters:
{characters_list}

Scenario: {state.conversation.scenario.description}

Who should respond next? Reply with ONLY the character ID (e.g., char1, char2, narrator).
Consider the flow of conversation and who would naturally speak next."""
    
    response = get_ai_response(prompt)
    
    # Extract character ID from response
    for char in state.conversation.characters:
        if char.id in response.lower():
            return char.id
    
    # Default to first non-narrator character
    return next(c.id for c in state.conversation.characters if not c.is_narrator)

def build_character_prompt(character: Character) -> str:
    """Build a prompt for generating character response"""
    if not state.conversation:
        return ""
    
    # Get recent context
    recent_messages = state.conversation.messages[-5:]
    context = "\n".join([
        f"{m.character_name}: {m.reaction or ''} \"{m.content}\""
        for m in recent_messages
    ])
    
    if character.is_narrator:
        prompt = f"""You are the Narrator of this story.

Scenario: {state.conversation.scenario.description}
Current State: {state.conversation.scenario.current_state}
What Happens Next: {state.conversation.scenario.what_happens_next}
Never Forget: {state.conversation.scenario.never_forget}

Recent conversation:
{context}

Describe what happens next in the story. Write a vivid, engaging narrative description.
Format: [Narrative description]

Keep it concise (2-3 sentences)."""
    else:
        prompt = f"""You are {character.name}.

Description: {character.description}
Personality: {character.personality}
Speech Patterns: {character.speech_patterns}
Motivations: {character.motivations}

Scenario: {state.conversation.scenario.description}
Never Forget: {state.conversation.scenario.never_forget}

Recent conversation:
{context}

Respond as {character.name}. Show your character's personality and emotions.
Format:
[Physical/emotional reaction] "Your spoken dialogue"

Example:
[She crosses her arms, eyes narrowing with suspicion] "I don't believe you for a second."

Keep it natural and in-character."""
    
    return prompt

def parse_ai_response(response: str, is_narrator: bool) -> tuple[Optional[str], str]:
    """Parse AI response into reaction and dialogue"""
    if is_narrator:
        # Narrator doesn't have reactions, just narrative
        return None, response.strip()
    
    # Try to extract [reaction] "dialogue" format
    if "[" in response and "]" in response and '"' in response:
        try:
            reaction_end = response.index("]")
            reaction = response[response.index("[") + 1:reaction_end].strip()
            
            dialogue_start = response.index('"', reaction_end)
            dialogue_end = response.rindex('"')
            dialogue = response[dialogue_start + 1:dialogue_end].strip()
            
            return reaction, dialogue
        except (ValueError, IndexError):
            pass
    
    # Fallback: treat entire response as dialogue
    return None, response.strip()

async def generate_summary():
    """Generate a summary of recent messages"""
    if not state.conversation or len(state.conversation.messages) < MAX_MESSAGES_BEFORE_SUMMARY:
        return
    
    # Get messages since last summary
    start_idx = len(state.conversation.summaries) * MAX_MESSAGES_BEFORE_SUMMARY
    messages_to_summarize = state.conversation.messages[start_idx:]
    
    context = "\n".join([
        f"{m.character_name}: {m.content}"
        for m in messages_to_summarize
    ])
    
    prompt = f"""Summarize this section of the story, preserving:
1. Key events and developments
2. Character emotions and relationships
3. Important dialogue and decisions
4. Current scenario state

Conversation:
{context}

Write a concise summary (3-4 sentences)."""
    
    summary = get_ai_response(prompt)
    state.conversation.summaries.append(summary)

# Mount static files
app.mount("/static", StaticFiles(directory="static"), name="static")
app.mount("/images", StaticFiles(directory=IMAGES_DIR), name="images")

if __name__ == "__main__":
    import uvicorn
    print("\n🎭 Starting AI-Powered Role-Playing App...")
    print("📝 Make sure Ollama is running: ollama serve")
    print("📚 Download model if needed: ollama pull llama3.2:1b")
    print("\n🌐 Open in browser: http://localhost:8000\n")
    uvicorn.run(app, host="0.0.0.0", port=8000)
