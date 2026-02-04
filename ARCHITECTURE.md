# Project Architecture

This document describes the modular architecture of the AI RPG Chat application.

## Directory Structure

```
modchat/
├── app/                          # Main application package
│   ├── __init__.py              # Package initialization
│   ├── main.py                  # FastAPI application setup
│   │
│   ├── models/                  # Data models (Pydantic)
│   │   ├── __init__.py
│   │   ├── character.py         # Character model
│   │   ├── message.py           # Message model
│   │   ├── scenario.py          # Scenario model
│   │   └── conversation.py      # Conversation & state models
│   │
│   ├── api/                     # API layer
│   │   ├── __init__.py
│   │   └── routes/              # API route handlers
│   │       ├── __init__.py      # Router aggregation
│   │       ├── conversation.py  # Conversation management
│   │       ├── character.py     # Character management
│   │       ├── message.py       # Message management
│   │       └── settings.py      # Application settings
│   │
│   ├── services/                # Business logic layer
│   │   ├── __init__.py
│   │   ├── ai_service.py        # AI/Ollama integration
│   │   └── summary_service.py   # Summary generation
│   │
│   ├── core/                    # Core configuration
│   │   ├── __init__.py
│   │   ├── config.py            # Application settings
│   │   └── state.py             # Global state management
│   │
│   └── utils/                   # Utility functions
│       ├── __init__.py
│       └── prompt_builder.py    # AI prompt construction
│
├── static/                      # Frontend assets
│   ├── index.html              # Main HTML page
│   └── app.js                  # Frontend JavaScript
│
├── saved_conversations/         # Saved conversation JSON files
├── character_images/            # Character image uploads
│
├── run.py                       # Application entry point
├── requirements.txt             # Python dependencies
├── .env                         # Environment configuration (optional)
└── README.md                    # Project documentation
```

## Architecture Layers

### 1. Models Layer (`app/models/`)
**Purpose:** Define data structures using Pydantic models

- `character.py` - Character entity model
- `message.py` - Message entity model
- `scenario.py` - Scenario/story context model
- `conversation.py` - Conversation and application state models

**Key Features:**
- Type validation via Pydantic
- Automatic JSON serialization
- Clear separation of concerns

### 2. Core Layer (`app/core/`)
**Purpose:** Application configuration and global state

- `config.py` - Application settings (directories, AI model, etc.)
- `state.py` - Global conversation state management

**Key Features:**
- Environment variable support via `.env`
- Centralized configuration
- Singleton state pattern

### 3. Services Layer (`app/services/`)
**Purpose:** Business logic and external service integration

- `ai_service.py` - Ollama AI integration, response generation, character decision logic
- `summary_service.py` - Conversation summarization logic

**Key Features:**
- Encapsulated AI interactions
- Reusable business logic
- Testable service components

### 4. Utils Layer (`app/utils/`)
**Purpose:** Helper functions and utilities

- `prompt_builder.py` - AI prompt construction and formatting

**Key Features:**
- Reusable utility functions
- Prompt templating
- Clean separation from business logic

### 5. API Layer (`app/api/`)
**Purpose:** HTTP endpoint definitions

- `routes/conversation.py` - CRUD operations for conversations
- `routes/character.py` - Character management endpoints
- `routes/message.py` - Message generation and editing
- `routes/settings.py` - Application settings toggles

**Key Features:**
- RESTful API design
- Clear route organization by domain
- Request/response validation

### 6. Main Application (`app/main.py`)
**Purpose:** FastAPI application initialization

**Responsibilities:**
- Create FastAPI app instance
- Mount static file directories
- Include API routers
- Serve main HTML page

## Design Principles

### 1. **Separation of Concerns**
Each module has a single, well-defined responsibility:
- Models: Data structure
- Services: Business logic
- API: HTTP interface
- Core: Configuration
- Utils: Helpers

### 2. **Dependency Injection**
Services and state are imported where needed, making components:
- Testable
- Reusable
- Loosely coupled

### 3. **Single Source of Truth**
- Configuration: `app/core/config.py`
- State: `app/core/state.py`
- Models: `app/models/`

### 4. **Scalability**
The modular structure allows for:
- Easy addition of new routes
- New service integrations
- Additional models
- Feature extensions

## Data Flow

```
User Request
    ↓
FastAPI Route (app/api/routes/)
    ↓
Service Layer (app/services/)
    ↓
AI/Ollama (via ai_service)
    ↓
State Update (app/core/state.py)
    ↓
Response to User
```

## Configuration

### Environment Variables
Create a `.env` file to customize settings:

```env
APP_TITLE="Local AI RPG Chat"
APP_HOST="0.0.0.0"
APP_PORT=8000
AI_MODEL="llama3.2:1b"
MAX_MESSAGES_BEFORE_SUMMARY=20
```

### Settings Access
```python
from app.core.config import settings

print(settings.ai_model)  # Access configuration
```

## Running the Application

### Using the entry point:
```bash
python run.py
```

### Or directly with uvicorn:
```bash
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

## Testing Strategy

### Unit Tests
Test individual components:
- Models: Validation logic
- Services: Business logic
- Utils: Helper functions

### Integration Tests
Test API endpoints:
- Route handlers
- Request/response validation
- State management

### Example Test Structure
```python
tests/
├── test_models.py
├── test_services.py
├── test_api/
│   ├── test_conversation.py
│   ├── test_character.py
│   └── test_message.py
└── test_utils.py
```

## Migration from Old Structure

The original `main.py` (536 lines) has been split into:

| Original Section | New Location |
|-----------------|--------------|
| Data Models | `app/models/` |
| API Endpoints | `app/api/routes/` |
| AI Integration | `app/services/ai_service.py` |
| Prompt Building | `app/utils/prompt_builder.py` |
| Configuration | `app/core/config.py` |
| State Management | `app/core/state.py` |
| App Initialization | `app/main.py` |

## Benefits of New Structure

1. **Maintainability** - Easy to locate and modify specific features
2. **Testability** - Each component can be tested independently
3. **Scalability** - Simple to add new features without affecting existing code
4. **Readability** - Clear organization makes code easier to understand
5. **Reusability** - Services and utils can be reused across different parts
6. **Collaboration** - Multiple developers can work on different modules

## Future Enhancements

Potential additions to the architecture:

1. **Database Layer** - Replace JSON file storage with database
2. **Middleware** - Add authentication, logging, rate limiting
3. **Background Tasks** - Async summary generation
4. **Caching** - Redis integration for conversation state
5. **WebSocket** - Real-time message streaming
6. **Testing** - Comprehensive test suite
7. **Docker** - Containerization for easy deployment

## Contributing

When adding new features:

1. **Models** - Add new Pydantic models in `app/models/`
2. **Services** - Add business logic in `app/services/`
3. **Routes** - Add endpoints in `app/api/routes/`
4. **Utils** - Add helpers in `app/utils/`
5. **Config** - Add settings in `app/core/config.py`

Always maintain separation of concerns and follow existing patterns.
