# 🚀 Quick Start Guide

Get your AI Role-Playing app running in 3 simple steps!

## Step 1: Install Ollama (One-Time Setup)

### Windows:
1. Download from: **https://ollama.com/download/windows**
2. Run the installer
3. Ollama starts automatically!

### macOS:
```bash
brew install ollama
```

### Linux:
```bash
curl -fsSL https://ollama.com/install.sh | sh
```

## Step 2: Download AI Model

Open a terminal/command prompt and run:

```bash
ollama pull llama3.2:1b
```

**This downloads a 1.3GB model** - it's small, fast, and works great for dialogue!

### Want Better Quality?
For more detailed responses (but slower):
```bash
ollama pull llama3.2:3b
```

## Step 3: Start the App

### Windows:
Double-click `start.bat`

**OR** open Command Prompt and run:
```cmd
python main.py
```

### macOS/Linux:
```bash
chmod +x start.sh
./start.sh
```

**OR**:
```bash
python3 main.py
```

## You're Ready! 🎉

Open your browser and go to: **http://localhost:8000**

---

## Creating Your First Story

1. Click **"New Story"** in the top right
2. Fill in the form:
   - **Scenario**: "A medieval tavern at midnight. A mysterious stranger just walked in."
   - **Character 1 Name**: "Elena"
   - **Character 1 Description**: "A seasoned warrior with a haunted past. Speaks gruffly but has a kind heart. Distrusts strangers."
   - **Character 2 Name**: "Marcus"
   - **Character 2 Description**: "A charming rogue and smooth talker. Always has a plan. Quick with jokes but hides his true feelings."
3. Click **"Create"**
4. Click **"Generate AI Response"** to start!

---

## Troubleshooting

### "AI Error: Connection refused"
**Fix:** Start Ollama:
```bash
ollama serve
```

### "AI Error: Model not found"
**Fix:** Download the model:
```bash
ollama pull llama3.2:1b
```

### Port 8000 Already in Use
**Fix:** Edit `main.py`, find the last line and change `port=8000` to `port=8001`

### Slow AI Responses
- Use a smaller model: `llama3.2:1b`
- Close other programs to free up RAM
- Your CPU generates the AI - faster CPU = faster responses

---

## Tips for Great Stories 💡

1. **Be Specific**: Detailed character descriptions = better AI responses
2. **Use "What Happens Next"**: Guide the story in the right panel
3. **Edit Freely**: Don't like a response? Click "Edit" or "Regenerate"
4. **Save Often**: Click "Save" regularly
5. **Experiment**: Try different scenarios and character combinations!

---

## Need Help?

- Check the full **README.md** for detailed documentation
- Review `main.py` to see how it works
- Visit **https://ollama.com** for Ollama documentation

---

**Enjoy your storytelling adventure! 🎭✨**
