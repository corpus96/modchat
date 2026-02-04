# Project Structure Overview

## 📁 Complete File Tree

```
modchat/
│
├── 📂 app/                           # Main application package
│   ├── 📄 __init__.py               # Package initialization
│   ├── 📄 main.py                   # FastAPI app setup & route mounting
│   │
│   ├── 📂 models/                   # 📦 Data Models Layer
│   │   ├── 📄 __init__.py          # Export all models
│   │   ├── 📄 character.py         # Character data model
│   │   ├── 📄 message.py           # Message data model
│   │   ├── 📄 scenario.py          # Scenario data model
│   │   └── 📄 conversation.py      # Conversation & ConversationState models
│   │
│   ├── 📂 api/                      # 🌐 API Layer
│   │   ├── 📄 __init__.py          # Export main router
│   │   └── 📂 routes/               # API endpoint handlers
│   │       ├── 📄 __init__.py      # Aggregate all route routers
│   │       ├── 📄 conversation.py  # /conversation/* endpoints
│   │       ├── 📄 character.py     # /character/* endpoints
│   │       ├── 📄 message.py       # /message/* endpoints
│   │       └── 📄 settings.py      # /settings/* endpoints
│   │
│   ├── 📂 services/                 # ⚙️ Business Logic Layer
│   │   ├── 📄 __init__.py          # Export services
│   │   ├── 📄 ai_service.py        # Ollama integration, AI response generation
│   │   └── 📄 summary_service.py   # Conversation summarization logic
│   │
│   ├── 📂 core/                     # 🔧 Core Configuration
│   │   ├── 📄 __init__.py          # Export settings & state
│   │   ├── 📄 config.py            # Application settings (env vars)
│   │   └── 📄 state.py             # Global application state
│   │
│   └── 📂 utils/                    # 🛠️ Utilities
│       ├── 📄 __init__.py          # Export utilities
│       └── 📄 prompt_builder.py    # AI prompt construction helpers
│
├── 📂 static/                       # 🎨 Frontend Assets
│   ├── 📄 index.html               # Main HTML page
│   └── 📄 app.js                   # Frontend JavaScript (UI logic)
│
├── 📂 saved_conversations/          # 💾 Saved Data
│   └── 📄 .gitkeep                 # Keep directory in git
│
├── 📂 character_images/             # 🖼️ Uploaded Images
│   └── 📄 .gitkeep                 # Keep directory in git
│
├── 📄 run.py                        # 🚀 Application Entry Point
├── 📄 requirements.txt              # 📦 Python Dependencies
├── 📄 .env.example                  # 🔐 Environment Variables Template
├── 📄 .gitignore                    # 🚫 Git Ignore Rules
│
├── 📄 README.md                     # 📖 Main Documentation
├── 📄 ARCHITECTURE.md               # 🏗️ Architecture Guide
├── 📄 MIGRATION_GUIDE.md            # 🔄 Migration Instructions
├── 📄 PROJECT_STRUCTURE.md          # 📁 This File
├── 📄 FEATURES.md                   # ✨ Feature Documentation
├── 📄 PROJECT_SUMMARY.md            # 📊 Project Summary
├── 📄 QUICKSTART.md                 # ⚡ Quick Start Guide
│
├── 📄 start.bat                     # 🪟 Windows Start Script
├── 📄 start.sh                      # 🐧 Linux/Mac Start Script
│
└── 📄 main.py.backup                # 💾 Original Monolithic File (backup)
```

## 📊 Module Breakdown

### 📦 Models (app/models/) - 4 files
**Purpose:** Define data structures

| File | Lines | Purpose |
|------|-------|---------|
| `character.py` | ~15 | Character entity definition |
| `message.py` | ~15 | Message entity with timestamp |
| `scenario.py` | ~10 | Story scenario/context |
| `conversation.py` | ~25 | Conversation & state models |

**Dependencies:** `pydantic` only

---

### 🌐 API Routes (app/api/routes/) - 5 files
**Purpose:** HTTP endpoint handlers

| File | Lines | Endpoints | Purpose |
|------|-------|-----------|---------|
| `conversation.py` | ~150 | 6 endpoints | Conversation CRUD, scenario updates |
| `character.py` | ~50 | 2 endpoints | Character management, image uploads |
| `message.py` | ~130 | 5 endpoints | Message generation, editing, navigation |
| `settings.py` | ~20 | 1 endpoint | Toggle application settings |

**Total Endpoints:** 14 REST API endpoints

---

### ⚙️ Services (app/services/) - 2 files
**Purpose:** Business logic and external integrations

| File | Lines | Purpose |
|------|-------|---------|
| `ai_service.py` | ~90 | Ollama integration, character decision logic |
| `summary_service.py` | ~50 | Conversation summarization |

**Dependencies:** `ollama`, models, core, utils

---

### 🔧 Core (app/core/) - 2 files
**Purpose:** Configuration and state management

| File | Lines | Purpose |
|------|-------|---------|
| `config.py` | ~30 | Settings from environment variables |
| `state.py` | ~20 | Global application state singleton |

**Dependencies:** `pydantic-settings`, models

---

### 🛠️ Utils (app/utils/) - 1 file
**Purpose:** Helper functions

| File | Lines | Purpose |
|------|-------|---------|
| `prompt_builder.py` | ~80 | AI prompt construction |

**Dependencies:** models, core

---

## 🔄 Data Flow Diagram

```
┌─────────────────────────────────────────────────────────────┐
│                         User Browser                         │
│                      (static/index.html)                     │
└──────────────────────────┬──────────────────────────────────┘
                           │
                           │ HTTP Request
                           ↓
┌─────────────────────────────────────────────────────────────┐
│                      FastAPI Application                     │
│                        (app/main.py)                         │
└──────────────────────────┬──────────────────────────────────┘
                           │
                           │ Route to endpoint
                           ↓
┌─────────────────────────────────────────────────────────────┐
│                       API Router Layer                       │
│                    (app/api/routes/*.py)                     │
│  ┌─────────────┬─────────────┬─────────────┬─────────────┐  │
│  │conversation │  character  │   message   │  settings   │  │
│  └─────────────┴─────────────┴─────────────┴─────────────┘  │
└──────────────────────────┬──────────────────────────────────┘
                           │
                           │ Call business logic
                           ↓
┌─────────────────────────────────────────────────────────────┐
│                      Services Layer                          │
│                   (app/services/*.py)                        │
│  ┌──────────────────────────────┬──────────────────────────┐│
│  │      AIService               │   SummaryService         ││
│  │  - decide_next_character     │  - generate_summary      ││
│  │  - generate_response         │  - should_generate       ││
│  └──────────────┬───────────────┴──────────────────────────┘│
└─────────────────┼──────────────────────────────────────────┘
                  │
                  │ Build prompts
                  ↓
┌─────────────────────────────────────────────────────────────┐
│                    Utilities Layer                           │
│                  (app/utils/*.py)                            │
│  ┌──────────────────────────────────────────────────────┐   │
│  │           PromptBuilder                              │   │
│  │  - build_character_prompt                            │   │
│  │  - build_narrator_prompt                             │   │
│  └──────────────────────────────────────────────────────┘   │
└──────────────────────────┬──────────────────────────────────┘
                           │
                           │ Call AI API
                           ↓
┌─────────────────────────────────────────────────────────────┐
│                      Ollama AI Server                        │
│                   (External Dependency)                      │
└──────────────────────────┬──────────────────────────────────┘
                           │
                           │ AI Response
                           ↓
┌─────────────────────────────────────────────────────────────┐
│                    State Management                          │
│                   (app/core/state.py)                        │
│  - Update conversation state                                 │
│  - Store messages                                            │
└──────────────────────────┬──────────────────────────────────┘
                           │
                           │ Return response
                           ↓
┌─────────────────────────────────────────────────────────────┐
│                       User Browser                           │
│                    (Display Response)                        │
└─────────────────────────────────────────────────────────────┘
```

## 🎯 Layer Responsibilities

### Layer 1: Models
- Define data structures
- Validation rules
- Serialization/deserialization
- **No business logic**

### Layer 2: API Routes
- HTTP request handling
- Input validation
- Response formatting
- **Delegates to services**

### Layer 3: Services
- Business logic execution
- External API integration (Ollama)
- Complex workflows
- **Uses models and utils**

### Layer 4: Utils
- Helper functions
- Prompt templates
- Formatting utilities
- **Stateless operations**

### Layer 5: Core
- Application configuration
- Global state management
- Initialization logic
- **Singleton patterns**

## 📝 Import Pattern

### ✅ Correct Import Flow
```
Models ← Services ← API Routes
  ↑         ↑          ↑
  └─────────┴──────────┴─── Core (Config & State)
  
Utilities ← Services ← API Routes
```

### ❌ Avoid Circular Imports
- Models should NOT import from services or routes
- Core should NOT import from services or routes
- Utils should NOT import from services or routes

## 🚀 Starting the Application

### Option 1: Using run.py (Recommended)
```bash
python run.py
```

This will:
1. Import `app.main:app`
2. Start uvicorn with hot reload
3. Serve on http://localhost:8000

### Option 2: Using uvicorn directly
```bash
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

### Option 3: Using start scripts
```bash
# Windows
start.bat

# Linux/Mac
./start.sh
```

## 📏 Code Statistics

| Component | Files | Lines of Code | Purpose |
|-----------|-------|---------------|---------|
| Models | 4 | ~65 | Data structures |
| API Routes | 4 | ~350 | HTTP endpoints |
| Services | 2 | ~140 | Business logic |
| Core | 2 | ~50 | Configuration |
| Utils | 1 | ~80 | Helpers |
| Main App | 1 | ~25 | FastAPI setup |
| Entry Point | 1 | ~20 | Run script |
| **Total** | **15** | **~730** | Application code |

**Original main.py:** 536 lines
**New structure:** ~730 lines (more modular, better organized)

The increase in line count comes from:
- Proper imports/exports in `__init__.py` files
- Documentation and docstrings
- Better code organization and spacing
- Separation of concerns

## 🔍 Finding Features

| Want to modify... | Go to... |
|-------------------|----------|
| Character attributes | `app/models/character.py` |
| Message format | `app/models/message.py` |
| API endpoints | `app/api/routes/*.py` |
| AI prompts | `app/utils/prompt_builder.py` |
| AI integration | `app/services/ai_service.py` |
| Settings | `app/core/config.py` or `.env` |
| Global state | `app/core/state.py` |
| Summarization | `app/services/summary_service.py` |

## 🎓 Learning Path

For new contributors:

1. **Start:** Read `README.md` and `QUICKSTART.md`
2. **Understand:** Review `ARCHITECTURE.md`
3. **Explore:** Look at `app/models/` to understand data
4. **Learn:** Study `app/api/routes/` to see endpoints
5. **Deep dive:** Examine `app/services/` for business logic
6. **Customize:** Modify `app/core/config.py` and `.env`

## 📚 Documentation Files

| File | Purpose | When to Read |
|------|---------|--------------|
| `README.md` | Main documentation | First time setup |
| `QUICKSTART.md` | Quick start guide | Getting started |
| `ARCHITECTURE.md` | Detailed architecture | Understanding design |
| `MIGRATION_GUIDE.md` | Migration from old structure | Updating from v1.0 |
| `PROJECT_STRUCTURE.md` | This file | Understanding layout |
| `FEATURES.md` | Feature documentation | Learning capabilities |
| `PROJECT_SUMMARY.md` | Project overview | High-level understanding |

---

**Last Updated:** 2024
**Structure Version:** 2.0 (Modular)
