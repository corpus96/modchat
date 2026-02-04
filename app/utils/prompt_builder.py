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
        
        # Get recent context
        recent_messages = state.conversation.messages[-5:]
        context = "\n".join([
            f"{m.character_name}: {m.reaction or ''} \"{m.content}\""
            for m in recent_messages
        ])
        
        if character.is_narrator:
            return self._build_narrator_prompt(context)
        else:
            return self._build_character_prompt(character, context)
    
    def _build_narrator_prompt(self, context: str) -> str:
        """Build prompt for narrator"""
        state = get_state()
        scenario = state.conversation.scenario
        
        prompt = f"""You are the Narrator of this story.

Scenario: {scenario.description}
Current State: {scenario.current_state}
What Happens Next: {scenario.what_happens_next}
Never Forget: {scenario.never_forget}

Recent conversation:
{context}

Describe what happens next in the story. Write a vivid, engaging narrative description.
Format: [Narrative description]

Keep it concise (2-3 sentences)."""
        
        return prompt
    
    def _build_character_prompt(self, character: Character, context: str) -> str:
        """Build prompt for regular character"""
        state = get_state()
        scenario = state.conversation.scenario
        
        prompt = f"""You are {character.name}.

Description: {character.description}
Personality: {character.personality}
Speech Patterns: {character.speech_patterns}
Motivations: {character.motivations}

Scenario: {scenario.description}
Never Forget: {scenario.never_forget}

Recent conversation:
{context}

Respond as {character.name}. Show your character's personality and emotions.
Format:
[Physical/emotional reaction] "Your spoken dialogue"

Example:
[She crosses her arms, eyes narrowing with suspicion] "I don't believe you for a second."

Keep it natural and in-character."""
        
        return prompt
