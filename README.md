# 🎭 AI-Powered Role-Playing Web Application

A fully local, AI-powered role-playing chat application that runs entirely on your machine. Create immersive stories with multiple characters, each powered by open-source AI models.

## ✨ Features

### 🎬 Story Creation
- Define detailed scenarios with rich descriptions
- Create unlimited characters with unique personalities
- Built-in Narrator to guide the story
- Upload character images (for main characters)

### 💬 Dynamic Conversations
- **Automatic Mode**: AI decides which character responds next
- **Manual Mode**: You control who speaks
- Natural dialogue with emotional reactions and gestures
- Toggle to show/hide reaction descriptions
- Edit any message to change the story direction

### 🧠 AI-Powered
- Uses **Ollama** with local LLM models (completely free!)
- No external APIs or cloud services required
- Characters maintain personality and context throughout
- Intelligent response generation based on character traits

### 💾 Save & Load
- Save conversations as JSON files
- Load and continue previous stories
- Automatic summarization for long conversations
- Navigate backward/forward through message history

### 🎮 Advanced Controls
- **What Happens Next**: Guide the story direction
- **Never Forget**: Important facts that persist in memory
- **Regenerate**: Reroll the last AI response
- **Message Navigation**: Browse conversation history

## 📋 Requirements

- **Python 3.8+** (tested with Python 3.13.9)
- **Ollama** (for local AI models)
- Modern web browser

## 🚀 Installation

### Step 1: Install Ollama

**Windows:**
1. Download from: https://ollama.com/download/windows
2. Run the installer
3. Ollama will start automatically

**macOS:**
```bash
brew install ollama
```

**Linux:**
```bash
curl -fsSL https://ollama.com/install.sh | sh
```

### Step 2: Download AI Model

Open a terminal and run:
```bash
ollama pull llama3.2:1b
```

This downloads a 1.3GB model. For better quality (but slower), you can use:
```bash
ollama pull llama3.2:3b
```

### Step 3: Install Python Dependencies

Navigate to the project directory and run:
```bash
pip install -r requirements.txt
```

## 🎮 Usage

### 1. Start Ollama (if not running)

**Windows/macOS:**
Ollama should start automatically. If not:
```bash
ollama serve
```

**Linux:**
```bash
ollama serve
```

### 2. Start the Application

```bash
python main.py
```

You should see:
```
🎭 Starting AI-Powered Role-Playing App...
📝 Make sure Ollama is running: ollama serve
📚 Download model if needed: ollama pull llama3.2:1b

🌐 Open in browser: http://localhost:8000
```

### 3. Open Your Browser

Navigate to: **http://localhost:8000**

## 📖 How to Use

### Creating Your First Story

1. Click **"New Story"** in the header
2. Fill in:
   - **Scenario Description**: The world, setting, and initial situation
   - **Character 1**: Name and detailed description (personality, background, motivations)
   - **Character 2**: Name and detailed description
3. Click **"Create"**

### Starting the Conversation

**Automatic Mode (Default):**
- Click **"Generate AI Response"**
- The AI will choose which character speaks and generate their response

**Manual Mode:**
1. Toggle off **"Auto Response"**
2. Select a character from the dropdown
3. Either:
   - Click **"Generate AI Response"** to let AI write as that character
   - Type your own message and click **"Send"**

### Guiding the Story

**Right Panel - Scenario Section:**
- **What Happens Next**: Tell the AI what should happen in the story
- **Never Forget**: Add important facts that should always be remembered
- Click **"Update"** after making changes

### Character Management

- Click **"Add Character"** to add more characters anytime
- Upload images for main characters using the file input in their card
- Click on character cards to quickly select them

### Message Controls

- **Edit**: Click "Edit" on any message to change it
- **Regenerate**: Reroll the last AI response
- **⬅️ Back**: Go to previous message state
- **➡️ Forward**: Return to newer message state

### Saving & Loading

- **Save**: Click "Save" to store your conversation as JSON
- **Load**: Click "Load" to browse and restore saved conversations
- Conversations are saved in the `saved_conversations/` folder

## 🎨 Character Creation Tips

### Good Character Descriptions

Include:
- **Personality traits**: Brave, cautious, witty, serious
- **Background**: Noble knight, street urchin, wise scholar
- **Motivations**: Seeking revenge, protecting family, finding truth
- **Speech patterns**: Formal, slang, poetic, technical
- **Quirks**: Nervous habits, catchphrases, mannerisms

### Example:
```
Name: Captain Elena Voss

Description: A battle-hardened starship captain in her 40s. 
Personality: Cynical but fair, trusts her gut, protects her crew fiercely.
Speech: Direct and military-precise, uses naval terminology.
Motivations: Redemption for a past mission failure, ensuring crew safety.
Quirks: Drums fingers when thinking, quotes old Earth literature.
```

## 🛠️ Advanced Configuration

### Changing the AI Model

In `main.py`, locate the `get_ai_response()` function:
```python
def get_ai_response(prompt: str, model: str = "llama3.2:1b") -> str:
```

Change `"llama3.2:1b"` to any model you've downloaded with Ollama:
- `llama3.2:3b` - Better quality, slower
- `mistral:7b` - High quality, needs more RAM
- `phi3:mini` - Faster, less accurate

### Adjusting Summary Frequency

In `main.py`, change:
```python
MAX_MESSAGES_BEFORE_SUMMARY = 20
```

Higher values = less frequent summaries but longer context.

### Custom Port

```bash
python main.py
```

Or edit the last line in `main.py`:
```python
uvicorn.run(app, host="0.0.0.0", port=8000)  # Change 8000 to your port
```

## 📁 Project Structure

```
modchat/
├── main.py                    # FastAPI backend
├── requirements.txt           # Python dependencies
├── README.md                  # This file
├── static/                    # Frontend files
│   ├── index.html            # Main UI
│   └── app.js                # Frontend logic
├── saved_conversations/       # Saved JSON files
└── character_images/          # Uploaded character images
```

## 🐛 Troubleshooting

### "AI Error: Connection refused"
- Make sure Ollama is running: `ollama serve`
- Check if Ollama is on port 11434 (default)

### "AI Error: Model not found"
- Download the model: `ollama pull llama3.2:1b`
- Verify: `ollama list`

### Slow AI Responses
- Use a smaller model: `llama3.2:1b` instead of `3b`
- Close other applications to free up RAM
- Check CPU usage - AI inference is CPU-intensive

### Port Already in Use
- Change the port in `main.py` (last line)
- Or kill the process using port 8000:
  - Windows: `netstat -ano | findstr :8000` then `taskkill /PID <PID> /F`
  - Linux/Mac: `lsof -ti:8000 | xargs kill`

### Can't Upload Images
- Make sure `character_images/` directory exists
- Check file permissions
- Try smaller image files (< 5MB)

## 🎯 Tips for Great Stories

1. **Start Small**: Begin with 2-3 characters before adding more
2. **Be Specific**: Detailed character descriptions = better AI responses
3. **Guide the AI**: Use "What Happens Next" to steer the story
4. **Edit Freely**: Don't hesitate to edit AI responses to fit your vision
5. **Save Often**: Save your conversations regularly
6. **Experiment**: Try regenerating responses for different outcomes

## 🔒 Privacy & Security

- **100% Local**: No data leaves your machine
- **No Tracking**: No analytics or external connections
- **Your Stories**: All saved conversations are yours
- **Open Source**: Review the code anytime

## 🤝 Contributing

This is a learning project, but feel free to:
- Report bugs
- Suggest features
- Share your story ideas
- Improve the prompts

## 📜 License

This project uses:
- **FastAPI** (MIT License)
- **Ollama** (MIT License)
- **Pydantic** (MIT License)

The application itself is provided as-is for educational and personal use.

## 🎉 Credits

Built with:
- **FastAPI** - Modern Python web framework
- **Ollama** - Local LLM runtime
- **llama3.2** - Meta's open-source language model

## 🚀 What's Next?

Potential future features:
- Character portraits generation
- Voice synthesis for dialogue
- Branching storylines
- Collaborative multiplayer mode
- Export to different formats (PDF, ePub)
- Custom AI model fine-tuning

---

**Enjoy creating your stories! 🎭📖✨**

For questions or issues, check the Troubleshooting section or review the code in `main.py` and `static/app.js`.
