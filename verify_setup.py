"""
Setup Verification Script
Run this to verify your installation is correct
"""

import sys
import os
from pathlib import Path


def check_python_version():
    """Check if Python version is compatible"""
    version = sys.version_info
    if version.major < 3 or (version.major == 3 and version.minor < 8):
        print("[FAIL] Python 3.8+ required. Current:", f"{version.major}.{version.minor}")
        return False
    print(f"[OK] Python version: {version.major}.{version.minor}.{version.micro}")
    return True


def check_directories():
    """Check if required directories exist"""
    required_dirs = [
        "app",
        "app/models",
        "app/api",
        "app/api/routes",
        "app/services",
        "app/core",
        "app/utils",
        "static",
        "saved_conversations",
        "character_images",
    ]
    
    all_exist = True
    for dir_path in required_dirs:
        if os.path.isdir(dir_path):
            print(f"[OK] Directory exists: {dir_path}")
        else:
            print(f"[FAIL] Directory missing: {dir_path}")
            all_exist = False
    
    return all_exist


def check_files():
    """Check if required files exist"""
    required_files = [
        "app/__init__.py",
        "app/main.py",
        "app/models/__init__.py",
        "app/models/character.py",
        "app/models/message.py",
        "app/models/scenario.py",
        "app/models/conversation.py",
        "app/api/__init__.py",
        "app/api/routes/__init__.py",
        "app/api/routes/conversation.py",
        "app/api/routes/character.py",
        "app/api/routes/message.py",
        "app/api/routes/settings.py",
        "app/services/__init__.py",
        "app/services/ai_service.py",
        "app/services/summary_service.py",
        "app/core/__init__.py",
        "app/core/config.py",
        "app/core/state.py",
        "app/utils/__init__.py",
        "app/utils/prompt_builder.py",
        "run.py",
        "requirements.txt",
        "static/index.html",
        "static/app.js",
    ]
    
    all_exist = True
    for file_path in required_files:
        if os.path.isfile(file_path):
            print(f"[OK] File exists: {file_path}")
        else:
            print(f"[FAIL] File missing: {file_path}")
            all_exist = False
    
    return all_exist


def check_imports():
    """Check if all modules can be imported"""
    imports = [
        ("app.models", "Character, Message, Scenario, Conversation"),
        ("app.services", "AIService, SummaryService"),
        ("app.core", "settings, app_state"),
        ("app.utils", "PromptBuilder"),
    ]
    
    all_imports_ok = True
    for module, items in imports:
        try:
            exec(f"from {module} import {items}")
            print(f"[OK] Import successful: from {module} import {items}")
        except ImportError as e:
            print(f"[FAIL] Import failed: from {module} import {items}")
            print(f"   Error: {e}")
            all_imports_ok = False
    
    return all_imports_ok


def check_dependencies():
    """Check if required packages are installed"""
    required_packages = [
        "fastapi",
        "uvicorn",
        "pydantic",
        "pydantic_settings",
        "ollama",
    ]
    
    all_installed = True
    for package in required_packages:
        try:
            __import__(package)
            print(f"[OK] Package installed: {package}")
        except ImportError:
            print(f"[FAIL] Package missing: {package}")
            print(f"   Install with: pip install {package}")
            all_installed = False
    
    return all_installed


def check_ollama():
    """Check if Ollama is accessible"""
    try:
        import requests
        response = requests.get("http://localhost:11434/api/tags", timeout=2)
        if response.status_code == 200:
            print("[OK] Ollama is running and accessible")
            return True
        else:
            print("[WARNING] Ollama responded but with unexpected status code")
            return False
    except Exception as e:
        print("[WARNING] Ollama is not running or not accessible")
        print("   Start Ollama with: ollama serve")
        print("   Or install from: https://ollama.com/download")
        return False


def main():
    """Run all verification checks"""
    print("\n" + "="*60)
    print(" AI RPG Chat - Setup Verification")
    print("="*60 + "\n")
    
    checks = []
    
    print("\n[*] Checking Python version...")
    checks.append(("Python Version", check_python_version()))
    
    print("\n[*] Checking directories...")
    checks.append(("Directories", check_directories()))
    
    print("\n[*] Checking files...")
    checks.append(("Files", check_files()))
    
    print("\n[*] Checking dependencies...")
    checks.append(("Dependencies", check_dependencies()))
    
    print("\n[*] Checking imports...")
    checks.append(("Imports", check_imports()))
    
    print("\n[*] Checking Ollama...")
    checks.append(("Ollama", check_ollama()))
    
    # Summary
    print("\n" + "="*60)
    print(" Verification Summary")
    print("="*60 + "\n")
    
    all_passed = True
    for check_name, result in checks:
        status = "[OK] PASS" if result else "[FAIL] FAIL"
        print(f"{status} - {check_name}")
        if not result:
            all_passed = False
    
    print("\n" + "="*60)
    
    if all_passed:
        print("\n[SUCCESS] All checks passed! Your setup is ready.")
        print("\nNext steps:")
        print("1. Start the application: python run.py")
        print("2. Open browser: http://localhost:8000")
        print("3. Start creating conversations!")
    else:
        print("\n[WARNING] Some checks failed. Please fix the issues above.")
        print("\nCommon fixes:")
        print("1. Install dependencies: pip install -r requirements.txt")
        print("2. Make sure you're in the project root directory")
        print("3. Start Ollama: ollama serve")
    
    print("\n" + "="*60 + "\n")
    
    return 0 if all_passed else 1


if __name__ == "__main__":
    sys.exit(main())
