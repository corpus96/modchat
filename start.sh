#!/bin/bash

echo ""
echo "========================================"
echo "  AI Role-Playing App - Quick Start"
echo "========================================"
echo ""

echo "Checking Python..."
python3 --version
echo ""

echo "Checking if Ollama is running..."
if ! curl -s http://localhost:11434/api/tags > /dev/null 2>&1; then
    echo "WARNING: Ollama is not running!"
    echo "Please start Ollama first:"
    echo "   ollama serve"
    echo ""
    echo "Or install from: https://ollama.com"
    exit 1
fi

echo "Ollama is running!"
echo ""

echo "Starting application..."
echo ""
python3 run.py
