 AI ChatBot Pro - Advanced Conversational AI with File Analysis

A powerful, feature-rich chatbot application built with Streamlit and OpenAI's GPT-4o, offering advanced file analysis capabilities and an intuitive user interface.

##  Features

###  Core Capabilities
- **Advanced AI Conversations**: Powered by OpenAI's GPT-4o model
- **Multi-Modal File Analysis**: Support for images, PDFs, text files, and more
- **Real-time Chat Interface**: Modern, responsive chat experience
- **Session Management**: Chat history with export capabilities
- **Progress Tracking**: Real-time file processing with progress indicators

### Supported File Types
- **Images**: JPEG, PNG, GIF, BMP, WebP
- **Documents**: PDF, TXT, DOC, DOCX
- **Data Files**: CSV, JSON
- **Code Files**: Various text-based formats

### User Interface
- **Colorful Modern Design**: Gradient backgrounds and smooth animations
- **Responsive Layout**: Works on desktop and mobile devices
- **Interactive Sidebar**: File uploads, statistics, and quick actions
- **Chat Export**: Download conversation history as JSON
- **Real-time Statistics**: Message counts and file processing stats

##  Quick Start

### Prerequisites
- Python 3.11 or higher
- OpenAI API key (get from [OpenAI Platform](https://platform.openai.com))

### Installation

1. **Clone or download this project**
2. **Install dependencies**:
   
   pip install streamlit openai pillow pypdf2 python-magic chardet
   

3. **Set up your OpenAI API key**:
   - Create a `.env` file in the project root
   - Add your API key: `OPENAI_API_KEY=your_api_key_here`
   - Or set it as an environment variable

4. **Run the application**:
  
   streamlit run app.py --server.port 5000

5. **Open your browser** and navigate to `http://localhost:5000`

## Project Structure

ai-chatbot-pro/

├── app.py                 # Main Streamlit application

├── utils/

│   ├── ai_client.py       # OpenAI API client

│   └── file_processor.py  # File analysis engine

├── .streamlit/

│   └── config.toml        # Streamlit configuration

├── pyproject.toml         # Project dependencies

├── README.md              # This file

└── requirements.txt       # Python dependencies

##  Configuration

### Streamlit Configuration (`.streamlit/config.toml`)

[server]
headless = true
address = "0.0.0.0"
port = 5000


### Environment Variables

- `OPENAI_API_KEY`: Your OpenAI API key (required)

##  Usage Examples

###  Basic Conversation

Simply type your message in the chat input and get intelligent responses from GPT-4o.

###  File Analysis

1. Upload files using the sidebar file uploader
2. Ask questions about your files: "Analyze this data" or "What's in this image?"
3. Get comprehensive analysis results with insights

###  Quick Actions

Use the sidebar quick action buttons for common tasks:
- **Writing Help**: Get assistance with writing tasks
- **Data Analysis**: Analyze uploaded data files
- **Brainstorming**: Generate creative ideas

###  Export Chat History

Click the "Export Chat" button to download your conversation history as a JSON file.

##  Technical Details

### AI Models Used

- **Primary Model**: GPT-4o (OpenAI)
- **Capabilities**: Text understanding, image analysis, code assistance, data insights

### File Processing Engine
- **Image Analysis**: Dimensions, format, color analysis, complexity assessment
- **PDF Processing**: Text extraction, page analysis, content statistics
- **Text Analysis**: Encoding detection, content statistics, language analysis
- **Data Files**: Structure analysis for CSV/JSON files

### Performance Features
- **Caching**: Streamlit resource caching for optimal performance
- **Progress Indicators**: Real-time feedback during file processing
- **Error Handling**: Comprehensive error management with user-friendly messages

##  Customization

### Color Scheme
The application uses a modern gradient color scheme defined in CSS variables:
- Primary: #FF6B6B (Coral)
- Secondary: #4ECDC4 (Turquoise)
- Accent: #45B7D1 (Blue)

### Styling
All styling is contained in the `load_css()` function in `app.py`. You can modify colors, fonts, and layouts by editing the CSS.

##  Security

- API keys are handled securely through environment variables
- File processing is done locally without external uploads
- Chat history remains on your local session

##  Troubleshooting

### Common Issues

1. **"Invalid API key" error**
   - Verify your OpenAI API key is correct
   - Check that the environment variable is set properly

2. **File processing errors**
   - Ensure files are not corrupted
   - Check file size limits (recommended < 10MB)

3. **Slow performance**
   - Large files may take time to process
   - Consider reducing file sizes for faster analysis

##  Dependencies

### Core Dependencies
- `streamlit>=1.46.0` - Web application framework
- `openai>=1.90.0` - OpenAI API client
- `pillow>=11.2.1` - Image processing
- `pypdf2>=3.0.1` - PDF text extraction
- `python-magic>=0.4.27` - File type detection
- `chardet>=5.2.0` - Character encoding detection

## Contributing

Feel free to enhance this project by:
1. Adding support for more file types
2. Improving the UI/UX design
3. Adding new AI capabilities
4. Optimizing performance

## Support

For questions or issues:
1. Check the troubleshooting section above
2. Review the code comments for implementation details
3. Refer to the OpenAI API documentation for API-related questions
