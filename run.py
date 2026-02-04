"""Application entry point"""

import uvicorn
from app.core.config import settings


def main():
    """Start the application"""
    print("\nStarting AI-Powered Role-Playing App...")
    print("Make sure Ollama is running: ollama serve")
    print("Download model if needed: ollama pull llama3.2:1b")
    print(f"\nOpen in browser: http://localhost:{settings.app_port}\n")
    
    uvicorn.run(
        "app.main:app",
        host=settings.app_host,
        port=settings.app_port,
        reload=True
    )


if __name__ == "__main__":
    main()
