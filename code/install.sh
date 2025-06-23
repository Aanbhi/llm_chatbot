#!/bin/bash

# AI ChatBot Pro Installation Script
echo "🤖 AI ChatBot Pro - Installation Script"
echo "======================================="

# Check Python version
python_version=$(python3 --version 2>&1 | grep -Po '(?<=Python )\d+\.\d+')
required_version="3.11"

if [ "$(printf '%s\n' "$required_version" "$python_version" | sort -V | head -n1)" = "$required_version" ]; then
    echo "✅ Python $python_version detected (requirement: $required_version+)"
else
    echo "❌ Python $required_version or higher is required. Found: $python_version"
    echo "Please install Python $required_version+ and try again."
    exit 1
fi

# Create virtual environment
echo "📦 Creating virtual environment..."
python3 -m venv venv

# Activate virtual environment
echo "🔧 Activating virtual environment..."
source venv/bin/activate

# Upgrade pip
echo "⬆️ Upgrading pip..."
pip install --upgrade pip

# Install requirements
echo "📥 Installing dependencies..."
pip install -r requirements.txt

echo ""
echo "🎉 Installation completed successfully!"
echo ""
echo "🚀 To run the application:"
echo "1. Activate the virtual environment: source venv/bin/activate"
echo "2. Set your OpenAI API key: export OPENAI_API_KEY='your_api_key_here'"
echo "3. Run the app: streamlit run app.py --server.port 5000"
echo "4. Open http://localhost:5000 in your browser"
echo ""
echo "📚 Check README.md for detailed instructions and troubleshooting."