
import zipfile
import os
from datetime import datetime

def create_chatbot_download_package():
    """Create a comprehensive ZIP package of all chatbot Python code"""
    
    # Get current timestamp for unique filename
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    zip_filename = f"ai_chatbot_pro_complete_v2.1.0_{timestamp}.zip"
    
    # Files to include in the package
    files_to_include = [
        # Main application files
        ("app.py", "Main application with colorful UI and complete features"),
        ("app_complete.py", "Alternative complete version"),
        ("app_smart.py", "Smart assistant version"),
        ("app_functional.py", "Functional version"),
        
        # Utility modules
        ("utils/ai_client.py", "OpenAI API client with error handling"),
        ("utils/file_processor.py", "File processing utilities"),
        
        # Configuration files
        ("requirements.txt", "Python dependencies"),
        ("pyproject.toml", "Project configuration"),
        (".streamlit/config.toml", "Streamlit configuration"),
        
        # Documentation
        ("README.md", "Complete project documentation"),
        ("usage_guide.md", "Usage instructions and troubleshooting"),
        ("quota_solution.md", "OpenAI quota management guide"),
        ("DOWNLOAD_PACKAGE.md", "Package information"),
        ("project_structure.md", "Project structure documentation"),
        
        # Docker support
        ("Dockerfile", "Docker containerization"),
        ("docker-compose.yml", "Docker Compose configuration"),
        ("install.sh", "Installation script"),
        
        # Demo files
        ("demo_files/sample_text.txt", "Sample file for testing"),
        
        # Utility scripts
        ("run.py", "Alternative run script"),
        ("create_download_package.py", "Package creation script")
    ]
    
    # Create the ZIP file
    with zipfile.ZipFile(zip_filename, 'w', zipfile.ZIP_DEFLATED) as zipf:
        # Add main files
        for file_path, description in files_to_include:
            if os.path.exists(file_path):
                zipf.write(file_path, file_path)
                print(f"✅ Added: {file_path}")
            else:
                print(f"⚠️  Missing: {file_path}")
        
        # Create a comprehensive README for the package
        readme_content = f"""# AI ChatBot Pro - Complete Package v2.1.0
Generated: {datetime.now().strftime("%Y-%m-%d %H:%M:%S")}

## 🎯 What's Included

### Core Application Files:
- `app.py` - Main colorful chatbot application (RECOMMENDED)
- `app_complete.py` - Alternative complete version
- `app_smart.py` - Smart assistant variant
- `app_functional.py` - Functional minimal version

### Utility Modules:
- `utils/ai_client.py` - OpenAI API client with quota handling
- `utils/file_processor.py` - File analysis capabilities

### Configuration:
- `requirements.txt` - Python dependencies
- `pyproject.toml` - Project metadata
- `.streamlit/config.toml` - Streamlit settings

### Documentation:
- `README.md` - Complete project documentation
- `usage_guide.md` - Usage instructions
- `quota_solution.md` - OpenAI quota troubleshooting
- `project_structure.md` - Code organization

### Deployment:
- `Dockerfile` - Container configuration
- `docker-compose.yml` - Multi-container setup
- `install.sh` - Quick installation script

### Demo Content:
- `demo_files/` - Sample files for testing

## 🚀 Quick Start

### Option 1: Local Installation
```bash
# Install dependencies
pip install -r requirements.txt

# Set your OpenAI API key
export OPENAI_API_KEY="your_api_key_here"

# Run the application
streamlit run app.py --server.port 5000
```

### Option 2: Docker
```bash
# Build and run with Docker
docker-compose up --build
```

### Option 3: Replit (Recommended)
1. Upload this package to a new Repl
2. Set OPENAI_API_KEY in Secrets
3. Run the application

## 💡 Key Features

### ✨ Advanced AI Chatbot
- **GPT-4o Integration**: Latest OpenAI model
- **Multi-modal Support**: Text + Image analysis
- **Smart Context**: Maintains conversation history
- **Quota Management**: Intelligent error handling

### 📁 File Analysis
- **Images**: Format, dimensions, color analysis
- **PDFs**: Text extraction, page counting
- **Text Files**: Encoding detection, statistics
- **Progress Tracking**: Real-time processing

### 🎨 Modern Interface
- **Colorful Design**: Gradient backgrounds
- **Responsive Layout**: Works on all devices
- **Interactive Controls**: Sidebar management
- **Export Features**: Download chat history

### 🛡️ Error Handling
- **Quota Exceeded**: Helpful solutions and links
- **API Key Issues**: Clear troubleshooting steps
- **Connection Errors**: User-friendly messages
- **File Processing**: Graceful error recovery

## 🔧 Configuration

### Environment Variables:
```bash
OPENAI_API_KEY=your_openai_api_key
STREAMLIT_SERVER_PORT=5000
STREAMLIT_SERVER_ADDRESS=0.0.0.0
```

### OpenAI Quota Management:
If you see quota exceeded errors:
1. Visit https://platform.openai.com/account/billing
2. Add payment method or increase limits
3. Monitor usage at https://platform.openai.com/account/usage

## 📊 Project Structure
```
ai_chatbot_pro/
├── app.py                    # Main application (USE THIS)
├── utils/
│   ├── ai_client.py         # OpenAI integration
│   └── file_processor.py    # File handling
├── requirements.txt         # Dependencies
├── README.md               # Documentation
└── demo_files/             # Test files
```

## 🎯 Recommended Usage

1. **Start with `app.py`** - It has the best UI and features
2. **Set up OpenAI API key** in environment variables
3. **Test with demo files** before using your own
4. **Monitor API usage** to avoid quota issues

## 🆘 Support

### Common Issues:
- **Quota Exceeded**: Check OpenAI billing dashboard
- **API Key Error**: Verify key is correct and active
- **File Processing**: Ensure files are under 10MB
- **Connection Issues**: Check internet and firewall

### Resources:
- OpenAI Platform: https://platform.openai.com
- Streamlit Docs: https://docs.streamlit.io
- Project Issues: Check error messages for guidance

## 📝 License & Credits

This project demonstrates advanced AI chatbot capabilities with:
- OpenAI GPT-4o integration
- Streamlit web framework
- Modern Python best practices
- Comprehensive error handling

Perfect for learning, development, or production use!

---
**Package Version**: 2.1.0
**Generated**: {datetime.now().strftime("%Y-%m-%d %H:%M:%S")}
**Python Version**: 3.11+
**Framework**: Streamlit + OpenAI
"""
        
        # Add the package README
        zipf.writestr("PACKAGE_README.md", readme_content)
        
        # Add a setup script
        setup_script = """#!/bin/bash
# AI ChatBot Pro - Quick Setup Script

echo "🤖 AI ChatBot Pro Setup"
echo "======================="

# Install Python dependencies
echo "📦 Installing dependencies..."
pip install -r requirements.txt

# Check for OpenAI API key
if [ -z "$OPENAI_API_KEY" ]; then
    echo "⚠️  OpenAI API key not found!"
    echo "Please set your API key:"
    echo "export OPENAI_API_KEY='your_api_key_here'"
    echo ""
    echo "Get your API key from: https://platform.openai.com/account/api-keys"
else
    echo "✅ OpenAI API key found"
fi

echo ""
echo "🚀 Ready to run!"
echo "Start the application with:"
echo "streamlit run app.py --server.port 5000"
echo ""
echo "Or use Docker:"
echo "docker-compose up --build"
"""
        zipf.writestr("setup.sh", setup_script)
        
        # Add version info
        version_info = {
            "version": "2.1.0",
            "generated": datetime.now().isoformat(),
            "description": "AI ChatBot Pro - Complete Package",
            "main_file": "app.py",
            "python_version": "3.11+",
            "framework": "Streamlit + OpenAI GPT-4o",
            "features": [
                "Advanced AI chat with GPT-4o",
                "Multi-modal file analysis",
                "Colorful modern UI with gradients",
                "Intelligent quota management",
                "Export chat history",
                "Docker support",
                "Comprehensive documentation"
            ]
        }
        
        import json
        zipf.writestr("version.json", json.dumps(version_info, indent=2))
    
    print(f"\n🎉 Package created successfully!")
    print(f"📦 File: {zip_filename}")
    print(f"📁 Size: {os.path.getsize(zip_filename) / 1024 / 1024:.1f} MB")
    print(f"\n📋 Package Contents:")
    print(f"   • Complete AI chatbot application")
    print(f"   • All Python source code")
    print(f"   • Documentation and guides")
    print(f"   • Docker configuration")
    print(f"   • Demo files and examples")
    print(f"   • Setup scripts")
    
    return zip_filename

if __name__ == "__main__":
    create_chatbot_download_package()
