"""Prompt building utilities for AI interactions"""

from app.models import Character
from app.core.state import get_state


class PromptBuilder:
    """Builder for AI prompts"""
    
    def build_character_prompt(self, character: Character) -> str:
        """Build a prompt for generating character response"""
        state = get_state()
        
        if not state.conversation:
            return ""
        
        # Get more context - last 10 messages or all if fewer
        message_count = min(10, len(state.conversation.messages))
        recent_messages = state.conversation.messages[-message_count:] if message_count > 0 else []
        
        # Build context with clear speaker labels
        context = "\n".join([
            f"{m.character_name}: {m.content}"
            for m in recent_messages
        ])
        
        if character.is_narrator:
            return self._build_narrator_prompt(context, recent_messages)
        else:
            return self._build_character_prompt(character, context, recent_messages)
    
    def _build_narrator_prompt(self, context: str, recent_messages: list) -> str:
        """Build prompt for narrator"""
        state = get_state()
        scenario = state.conversation.scenario
        
        prompt = f"""You are the Narrator describing this scene.

Setting: {scenario.description}

Recent events:
{context if context else '(Story beginning)'}

Describe what happens next. Write 2-3 sentences about the scene, atmosphere, or events. Do NOT write character dialogue.

Your narration:"""
        
        return prompt
    
    def _build_character_prompt(self, character: Character, context: str, recent_messages: list) -> str:
        """Build prompt for regular character"""
        state = get_state()
        scenario = state.conversation.scenario
        
        # Get the last message to respond to
        last_msg = recent_messages[-1] if recent_messages else None
        last_speaker = last_msg.character_name if last_msg else "unknown"
        last_content = last_msg.content if last_msg else "nothing yet"
        
        prompt = f"""You are {character.name}.

Character: {character.description}
Setting: {scenario.description}

Conversation:
{context if context else '(Just starting)'}

{last_speaker} just said: "{last_content}"

Respond as {character.name}. Write your response in this format:
[physical action or emotion] "what you say"

Example: [smiles warmly] "That's exactly what I was thinking!"

Your response:"""
        
        return prompt
