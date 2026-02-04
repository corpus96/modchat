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
                messages=[{"role": "user", "content": prompt}]
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
        
        response = self.get_response(prompt)
        
        # Extract character ID from response
        for char in state.conversation.characters:
            if char.id in response.lower():
                return char.id
        
        # Default to first non-narrator character
        return next(c.id for c in state.conversation.characters if not c.is_narrator)
    
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
