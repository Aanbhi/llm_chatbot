
#!/usr/bin/env python3
"""
Create a downloadable package of the AI ChatBot Pro project with all essential files
"""

import os
import zipfile
import json
from datetime import datetime

def create_download_package():
    """Create a ZIP file with all 9 essential project files plus Docker configuration"""
    
    # Package information
    package_info = {
        "name": "AI ChatBot Pro - Complete Package",
        "version": "2.0.0",
        "description": "Advanced AI Chatbot with File Analysis and Docker Support",
        "created": datetime.now().isoformat(),
        "author": "AI ChatBot Pro Team",
        "license": "MIT",
        "python_version": "3.11+",
        "dependencies": [
            "streamlit>=1.46.0",
            "openai>=1.90.0", 
            "pillow>=11.2.1",
            "pypdf2>=3.0.1",
            "python-magic>=0.4.27",
            "chardet>=5.2.0",
            "requests>=2.31.0"
        ],
        "features": [
            "GPT-4o Integration",
            "Multi-format File Analysis", 
            "Modern Colorful UI",
            "Real-time Chat",
            "Export Capabilities",
            "Progress Tracking",
            "Docker Support",
            "Production Ready"
        ],
        "included_files": [
            "app.py - Main Streamlit application",
            "requirements.txt - Python dependencies",
            "Dockerfile - Docker configuration",
            "docker-compose.yml - Docker Compose setup",
            "README.md - Comprehensive documentation",
            ".streamlit/config.toml - Streamlit configuration",
            "run.py - Smart launcher script",
            "install.sh - Installation script",
            "demo_files/sample_text.txt - Sample file for testing"
        ]
    }
    
    # Essential files to include (9 core files + Docker)
    files_to_include = [
        'app.py',                    # 1. Main application
        'requirements.txt',          # 2. Dependencies  
        'Dockerfile',               # 3. Docker configuration
        'docker-compose.yml',       # 4. Docker Compose
        'README.md',                # 5. Documentation
        '.streamlit/config.toml',   # 6. Streamlit config
        'run.py',                   # 7. Launcher script
        'install.sh',               # 8. Installation script
        'demo_files/sample_text.txt' # 9. Sample file
    ]
    
    # Create package info file
    with open('package_info.json', 'w') as f:
        json.dump(package_info, f, indent=2)
    
    # Create setup instructions
    setup_instructions = """# 🚀 AI ChatBot Pro - Complete Setup Guide

## 📦 Package Contents
This package contains all 9 essential files plus Docker configuration:

1. **app.py** - Main Streamlit application with colorful UI
2. **requirements.txt** - Python dependencies
3. **Dockerfile** - Docker container configuration  
4. **docker-compose.yml** - Docker Compose setup
5. **README.md** - Comprehensive documentation
6. **.streamlit/config.toml** - Streamlit server configuration
7. **run.py** - Smart launcher with dependency checks
8. **install.sh** - Automated installation script
9. **demo_files/sample_text.txt** - Sample file for testing

## 🐳 Quick Start with Docker (Recommended)

### Prerequisites
- Docker and Docker Compose installed
- OpenAI API key

### Setup Steps
```bash
# 1. Extract the package
unzip ai_chatbot_pro_complete_v*.zip
cd ai_chatbot_pro_complete

# 2. Set your API key
export OPENAI_API_KEY='your_api_key_here'

# 3. Build and run with Docker
docker-compose up --build

# 4. Access the app
# Open http://localhost:5000 in your browser
```

## 🐍 Manual Python Setup

### Prerequisites
- Python 3.11 or higher
- OpenAI API key

### Setup Steps
```bash
# 1. Extract and navigate
unzip ai_chatbot_pro_complete_v*.zip
cd ai_chatbot_pro_complete

# 2. Install dependencies
pip install -r requirements.txt

# 3. Set API key
export OPENAI_API_KEY='your_api_key_here'

# 4. Run the application
python run.py
# OR
streamlit run app.py --server.port 5000
```

## ⚡ Features Ready to Use

### 🤖 AI Capabilities
- GPT-4o powered conversations
- Intelligent file analysis
- Multi-modal understanding (text + images)
- Context-aware responses

### 📁 File Support
- Images: JPEG, PNG, GIF, BMP, WebP
- Documents: PDF, TXT, DOC, DOCX  
- Data: CSV, JSON
- Code files and more

### 🎨 Modern Interface
- Colorful gradient design
- Real-time progress indicators
- Interactive sidebar controls
- Export functionality
- Quick action buttons

## 🔧 Configuration Options

### Environment Variables
```bash
OPENAI_API_KEY=your_api_key_here
STREAMLIT_SERVER_PORT=5000
STREAMLIT_SERVER_ADDRESS=0.0.0.0
```

### Docker Environment
- Automatic health checks
- Volume mounting for uploads
- Restart policies configured
- Production-ready settings

## 🛠️ Development

### Local Development
```bash
# Install in development mode
pip install -e .

# Run with hot reload
streamlit run app.py --logger.level debug
```

### Docker Development
```bash
# Build development image
docker build -t ai-chatbot-pro:dev .

# Run with volume mounting
docker run -p 5000:5000 -v $(pwd):/app ai-chatbot-pro:dev
```

## 📊 Usage Examples

### Basic Chat
1. Open the application
2. Type your message in the chat input
3. Get intelligent AI responses

### File Analysis
1. Upload files using the sidebar
2. Ask questions about your files
3. Get comprehensive analysis results

### Export Chat
1. Click "Export" in the sidebar
2. Download your conversation history
3. Save for future reference

## 🚨 Troubleshooting

### Common Issues
- **Port 5000 in use**: Change port in docker-compose.yml or config.toml
- **API key errors**: Verify your OpenAI API key is valid
- **File processing errors**: Check file formats and sizes
- **Docker issues**: Ensure Docker is running and has sufficient resources

### Getting Help
- Check the README.md for detailed documentation
- Review container logs: `docker-compose logs`
- Verify API key at: https://platform.openai.com

## 🎉 You're All Set!

Your AI ChatBot Pro is ready to use with:
- ✅ Modern, responsive interface
- ✅ Advanced AI capabilities  
- ✅ File analysis features
- ✅ Docker deployment ready
- ✅ Production configuration

Enjoy your intelligent AI assistant! 🤖✨
"""
    
    # Create ZIP file
    zip_filename = f"ai_chatbot_pro_complete_v{package_info['version']}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.zip"
    
    with zipfile.ZipFile(zip_filename, 'w', zipfile.ZIP_DEFLATED) as zipf:
        # Add package info and setup guide
        zipf.writestr('ai_chatbot_pro_complete/package_info.json', json.dumps(package_info, indent=2))
        zipf.writestr('ai_chatbot_pro_complete/SETUP_GUIDE.md', setup_instructions)
        
        # Add all essential files
        for file_path in files_to_include:
            if os.path.exists(file_path):
                zipf.write(file_path, f'ai_chatbot_pro_complete/{file_path}')
                print(f"✅ Added: {file_path}")
            else:
                print(f"⚠️ Missing: {file_path}")
        
        # Create .env template
        env_template = """# AI ChatBot Pro Environment Configuration
# Copy this file to .env and fill in your values

# OpenAI API Key (Required)
OPENAI_API_KEY=your_openai_api_key_here

# Server Configuration
STREAMLIT_SERVER_PORT=5000
STREAMLIT_SERVER_ADDRESS=0.0.0.0

# Optional: Enable debug mode
# STREAMLIT_LOGGER_LEVEL=debug
"""
        zipf.writestr('ai_chatbot_pro_complete/.env.template', env_template)
    
    # Cleanup temporary file
    if os.path.exists('package_info.json'):
        os.remove('package_info.json')
    
    print(f"\n🎉 Complete package created: {zip_filename}")
    print(f"📦 Package size: {os.path.getsize(zip_filename) / 1024:.1f} KB")
    print(f"📁 Contains {len(files_to_include)} essential files + Docker configuration")
    
    return zip_filename

if __name__ == '__main__':
    create_download_package()
