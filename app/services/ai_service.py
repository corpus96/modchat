"""AI service for generating responses"""

import ollama
from typing import Optional
from app.core.config import settings
from app.models import Character, Message
from app.core.state import get_state
from app.utils.prompt_builder import PromptBuilder


class AIService:
    """Service for AI interactions"""
    
    def __init__(self, model: str = None):
        self.model = model or settings.ai_model
        self.prompt_builder = PromptBuilder()
    
    def get_response(self, prompt: str) -> str:
        """Get response from local Ollama AI model"""
        try:
            response = ollama.chat(
                model=self.model,
                messages=[{"role": "user", "content": prompt}],
                options={
                    "temperature": 0.7,
                    "top_p": 0.9,
                }
            )
            return response["message"]["content"]
        except Exception as e:
            return f"[AI Error: {str(e)}. Make sure Ollama is running with: ollama serve]"
    
    async def decide_next_character(self) -> str:
        """Use AI to decide which character should respond next"""
        state = get_state()
        
        if not state.conversation or not state.conversation.messages:
            # First message - narrator starts
            return "narrator"
        
        # Get the last character who spoke
        last_message = state.conversation.messages[-1]
        last_character_id = last_message.character_id
        
        print(f"Last character who spoke: {last_character_id} ({last_message.character_name})")
        
        # Get all non-narrator characters
        non_narrator_chars = [c for c in state.conversation.characters if not c.is_narrator]
        
        # If last speaker was the narrator, pick first non-narrator
        if last_character_id == "narrator":
            next_char = non_narrator_chars[0].id if non_narrator_chars else "narrator"
            print(f"Last was narrator, picking: {next_char}")
            return next_char
        
        # Get characters who haven't spoken yet or spoke least recently
        available_chars = [c for c in non_narrator_chars if c.id != last_character_id]
        
        if not available_chars:
            # Only one character exists, use narrator
            print("Only one character, using narrator")
            return "narrator"
        
        # Simple alternation: pick the first available character that's not the last speaker
        next_char_id = available_chars[0].id
        print(f"Picking next character: {next_char_id} (avoiding {last_character_id})")
        
        return next_char_id
    
    async def generate_character_response(self, character: Character) -> tuple[Optional[str], str]:
        """Generate an AI response for a character"""
        prompt = self.prompt_builder.build_character_prompt(character)
        ai_response = self.get_response(prompt)
        return self._parse_response(ai_response, character.is_narrator)
    
    def _parse_response(self, response: str, is_narrator: bool) -> tuple[Optional[str], str]:
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


# Singleton instance
ai_service = AIService()
