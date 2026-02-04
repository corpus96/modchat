# Migration Guide: From Monolithic to Modular Structure

This guide helps you transition from the old single-file structure to the new modular architecture.

## What Changed?

### Before (Old Structure)
```
modchat/
├── main.py (536 lines - everything in one file)
├── static/
├── requirements.txt
└── README.md
```

### After (New Structure)
```
modchat/
├── app/                    # NEW: Application package
│   ├── models/            # Data models
│   ├── api/routes/        # API endpoints
│   ├── services/          # Business logic
│   ├── core/              # Configuration & state
│   ├── utils/             # Helpers
│   └── main.py            # FastAPI app
├── run.py                 # NEW: Entry point
├── static/                # Unchanged
├── requirements.txt       # Updated (added pydantic-settings)
└── main.py.backup         # Your original file (backup)
```

## Step-by-Step Migration

### 1. Install New Dependencies
```bash
pip install -r requirements.txt
```

**New dependency:** `pydantic-settings==2.5.2` (for configuration management)

### 2. Update Start Command

**Old way:**
```bash
python main.py
```

**New way:**
```bash
python run.py
```

Or use the provided scripts:
- Windows: `start.bat`
- Linux/Mac: `./start.sh`

### 3. Environment Configuration (Optional)

Create a `.env` file for custom settings:

```bash
cp .env.example .env
```

Edit `.env` to customize:
```env
APP_PORT=8000
AI_MODEL="llama3.2:1b"
MAX_MESSAGES_BEFORE_SUMMARY=20
```

## What Stays the Same?

✅ **API Endpoints** - All endpoints work exactly as before:
- `/api/conversation/new`
- `/api/message/generate`
- `/api/character/add`
- etc.

✅ **Frontend** - `static/index.html` and `static/app.js` unchanged

✅ **Data Files** - Saved conversations and images in same locations

✅ **Functionality** - All features work identically

## Code Changes Mapping

If you have custom modifications in the old `main.py`, here's where to move them:

### Data Models
**Old location:** Lines 20-58 in `main.py`

**New location:**
- `app/models/character.py`
- `app/models/message.py`
- `app/models/scenario.py`
- `app/models/conversation.py`

**Example:**
```python
# Old: In main.py
class Character(BaseModel):
    id: str
    name: str
    # ...

# New: In app/models/character.py
class Character(BaseModel):
    id: str
    name: str
    # ...
```

### API Routes
**Old location:** Lines 83-382 in `main.py`

**New location:** Split across:
- `app/api/routes/conversation.py` - Conversation CRUD
- `app/api/routes/character.py` - Character management
- `app/api/routes/message.py` - Message operations
- `app/api/routes/settings.py` - Settings toggles

**Example:**
```python
# Old: In main.py
@app.post("/api/conversation/new")
async def create_conversation(...):
    # ...

# New: In app/api/routes/conversation.py
@router.post("/conversation/new")
async def create_conversation(...):
    # ...
```

### AI Integration
**Old location:** Lines 71-80, 385-420 in `main.py`

**New location:** `app/services/ai_service.py`

**Example:**
```python
# Old: In main.py
def get_ai_response(prompt: str, model: str = "llama3.2:1b") -> str:
    # ...

# New: In app/services/ai_service.py
class AIService:
    def get_response(self, prompt: str) -> str:
        # ...
```

### Prompt Building
**Old location:** Lines 422-471 in `main.py`

**New location:** `app/utils/prompt_builder.py`

### Configuration
**Old location:** Lines 62-68 in `main.py`

**New location:** `app/core/config.py`

**Example:**
```python
# Old: In main.py
SAVE_DIR = "saved_conversations"
MAX_MESSAGES_BEFORE_SUMMARY = 20

# New: In app/core/config.py
class Settings(BaseSettings):
    save_dir: str = "saved_conversations"
    max_messages_before_summary: int = 20
```

### Global State
**Old location:** Lines 61, throughout `main.py`

**New location:** `app/core/state.py`

**Example:**
```python
# Old: In main.py
state = ConversationState()

# New: In app/core/state.py
app_state = ConversationState()

def get_state() -> ConversationState:
    return app_state
```

## Custom Modifications

### If you modified the AI model:

**Old:**
```python
# main.py
def get_ai_response(prompt: str, model: str = "your-custom-model") -> str:
```

**New:**
Either update `.env`:
```env
AI_MODEL="your-custom-model"
```

Or modify `app/services/ai_service.py`:
```python
def __init__(self, model: str = None):
    self.model = model or "your-custom-model"
```

### If you added custom routes:

**Old:**
```python
# main.py
@app.post("/api/my-custom-route")
async def my_route():
    # ...
```

**New:**
Create `app/api/routes/custom.py`:
```python
from fastapi import APIRouter

router = APIRouter()

@router.post("/my-custom-route")
async def my_route():
    # ...
```

Then include in `app/api/routes/__init__.py`:
```python
from .custom import router as custom_router

router.include_router(custom_router, tags=["custom"])
```

### If you modified character prompt logic:

**Old:**
```python
# main.py
def build_character_prompt(character: Character) -> str:
    # your custom logic
```

**New:**
Modify `app/utils/prompt_builder.py`:
```python
class PromptBuilder:
    def build_character_prompt(self, character: Character) -> str:
        # your custom logic
```

## Testing the Migration

### 1. Check Installation
```bash
python -c "import app; print('✓ Import successful')"
```

### 2. Verify Routes
```bash
python run.py
# Should start without errors
```

### 3. Test API
Visit: `http://localhost:8000/docs`

You should see the FastAPI automatic documentation with all endpoints.

### 4. Test Frontend
Visit: `http://localhost:8000`

The application should work exactly as before.

## Rollback (If Needed)

If you need to revert to the old structure:

### Option 1: Use the Backup
```bash
# Stop the new application
# Restore the original
mv main.py.backup main.py

# Revert requirements.txt
pip install fastapi==0.115.0 uvicorn[standard]==0.32.0 pydantic==2.9.0 ollama==0.4.0 python-multipart==0.0.12

# Start the old way
python main.py
```

### Option 2: Keep Both
You can keep both structures and switch between them:
- New structure: `python run.py`
- Old structure: `python main.py.backup`

## Benefits of the New Structure

1. **Easier to Find Code** - Need to modify AI prompts? Check `app/utils/prompt_builder.py`
2. **Easier to Test** - Test individual services without running the whole app
3. **Easier to Extend** - Add new features in separate files
4. **Better Performance** - Only import what you need
5. **Team Collaboration** - Multiple people can work on different modules
6. **Industry Standard** - Follows FastAPI best practices

## Common Issues & Solutions

### Issue: Import Error
```
ModuleNotFoundError: No module named 'app'
```

**Solution:**
```bash
# Make sure you're in the project root directory
cd c:\Cursor_Repos\modchat

# Install dependencies
pip install -r requirements.txt
```

### Issue: "pydantic_settings" not found
```
ImportError: cannot import name 'BaseSettings' from 'pydantic'
```

**Solution:**
```bash
pip install pydantic-settings==2.5.2
```

### Issue: Config Error
```
ValidationError: settings
```

**Solution:**
The app expects certain directories. They're created automatically, but if you get this error:
```bash
mkdir saved_conversations character_images
```

### Issue: Routes Not Found (404)
```
404 Not Found: /api/conversation/new
```

**Solution:**
Make sure you're using `python run.py`, not `python main.py` (unless you restored the backup).

## Getting Help

If you encounter issues:

1. Check the `ARCHITECTURE.md` for detailed structure information
2. Review your custom modifications against the mapping above
3. Check the backup file: `main.py.backup`
4. Compare your changes with the new modular files

## Next Steps

After successful migration:

1. ✅ Delete `main.py.backup` (once you're confident)
2. ✅ Review `ARCHITECTURE.md` to understand the new structure
3. ✅ Create a `.env` file for your custom settings
4. ✅ Consider adding tests for your custom features
5. ✅ Explore the modular structure and plan future enhancements

---

**Questions or Issues?** Open an issue or check the documentation!
