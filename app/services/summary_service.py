"""Service for generating conversation summaries"""

from app.core.config import settings
from app.core.state import get_state
from app.services.ai_service import ai_service


class SummaryService:
    """Service for generating summaries of conversations"""
    
    async def generate_summary(self) -> str:
        """Generate a summary of recent messages"""
        state = get_state()
        
        if not state.conversation or len(state.conversation.messages) < settings.max_messages_before_summary:
            return ""
        
        # Get messages since last summary
        start_idx = len(state.conversation.summaries) * settings.max_messages_before_summary
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
        
        summary = ai_service.get_response(prompt)
        state.conversation.summaries.append(summary)
        
        return summary
    
    def should_generate_summary(self) -> bool:
        """Check if a summary should be generated"""
        state = get_state()
        
        if not state.conversation:
            return False
        
        message_count = len(state.conversation.messages)
        
        if message_count < settings.max_messages_before_summary:
            return False
        
        return message_count % settings.max_messages_before_summary == 0


# Singleton instance
summary_service = SummaryService()
