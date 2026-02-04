"""Global application state"""

from app.models import ConversationState


# Global state instance
app_state = ConversationState()


def get_state() -> ConversationState:
    """Get the current application state"""
    return app_state


def reset_state():
    """Reset the application state"""
    global app_state
    app_state = ConversationState()
