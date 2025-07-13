
import streamlit as st
import base64
import io
import json
import os
from datetime import datetime
from typing import Dict, Any, List
import re

# External imports
try:
    import magic
    import chardet
    from PIL import Image
    import PyPDF2
    from openai import OpenAI
except ImportError as e:
    st.error(f"Missing required library: {e}")
    st.stop()

# Page configuration
st.set_page_config(
    page_title="AI ChatBot Pro",
    page_icon="🔸",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Enhanced colorful CSS
def load_css():
    st.markdown("""
    <style>
    /* Vibrant theme colors */
    :root {
        --primary-gradient: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        --secondary-gradient: linear-gradient(135deg, #f093fb 0%, #f5576c 100%);
        --success-gradient: linear-gradient(135deg, #4facfe 0%, #00f2fe 100%);
        --warning-gradient: linear-gradient(135deg, #43e97b 0%, #38f9d7 100%);
        --chat-user-bg: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        --chat-ai-bg: linear-gradient(135deg, #f093fb 0%, #f5576c 100%);
        --sidebar-bg: linear-gradient(180deg, #667eea 0%, #764ba2 100%);
    }
    
    /* Main container */
    .main .block-container {
        padding-top: 1rem;
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        border-radius: 20px;
        margin: 10px;
    }
    
    /* Header styling */
    .main-header {
        background: var(--secondary-gradient);
        padding: 2rem;
        border-radius: 20px;
        margin-bottom: 2rem;
        text-align: center;
        color: white;
        box-shadow: 0 15px 35px rgba(0,0,0,0.3);
        border: 3px solid rgba(255,255,255,0.2);
    }
    
    .main-header h1 {
        font-size: 3.5rem;
        margin: 0;
        text-shadow: 3px 3px 6px rgba(0,0,0,0.4);
        background: linear-gradient(45deg, #fff, #ffd700);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        background-clip: text;
    }
    
    .main-header p {
        font-size: 1.3rem;
        margin: 1rem 0 0 0;
        opacity: 0.95;
        text-shadow: 1px 1px 2px rgba(0,0,0,0.3);
    }
    
    /* Sidebar styling */
    .css-1d391kg {
        background: var(--sidebar-bg);
    }
    
    .css-1lcbmhc {
        background: var(--sidebar-bg);
    }
    
    /* Chat messages */
    .stChatMessage {
        border-radius: 15px;
        margin: 1rem 0;
        box-shadow: 0 8px 25px rgba(0,0,0,0.15);
        border: 2px solid rgba(255,255,255,0.1);
    }
    
    .stChatMessage[data-testid="user-message"] {
        background: var(--chat-user-bg);
        color: white;
    }
    
    .stChatMessage[data-testid="assistant-message"] {
        background: var(--chat-ai-bg);
        color: white;
    }
    
    /* Buttons */
    .stButton > button {
        background: var(--success-gradient);
        color: white;
        border: none;
        border-radius: 25px;
        padding: 0.75rem 2rem;
        font-weight: bold;
        font-size: 1rem;
        transition: all 0.3s ease;
        box-shadow: 0 8px 20px rgba(0,0,0,0.2);
        border: 2px solid rgba(255,255,255,0.2);
    }
    
    .stButton > button:hover {
        transform: translateY(-3px);
        box-shadow: 0 12px 30px rgba(0,0,0,0.3);
        background: var(--warning-gradient);
    }
    
    /* Metrics */
    .metric-container {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        padding: 1rem;
        border-radius: 15px;
        color: white;
        text-align: center;
        box-shadow: 0 8px 20px rgba(0,0,0,0.2);
        border: 2px solid rgba(255,255,255,0.2);
        margin: 0.5rem;
    }
    
    /* File uploader */
    .stFileUploader {
        background: linear-gradient(135deg, #43e97b 0%, #38f9d7 100%);
        padding: 1rem;
        border-radius: 15px;
        border: 3px dashed rgba(255,255,255,0.4);
    }
    
    .uploadedFile {
        background: rgba(255,255,255,0.95);
        border-radius: 10px;
        padding: 0.8rem;
        margin: 0.5rem 0;
        border-left: 5px solid #667eea;
        box-shadow: 0 4px 15px rgba(0,0,0,0.1);
    }
    
    /* Chat input */
    .stChatInput > div {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        border-radius: 25px;
        border: 3px solid rgba(255,255,255,0.3);
    }
    
    .stChatInput input {
        background: transparent;
        color: white;
        border: none;
        font-size: 1.1rem;
    }
    
    .stChatInput input::placeholder {
        color: rgba(255,255,255,0.7);
    }
    
    /* Sidebar elements */
    .css-1lcbmhc .stMarkdown {
        color: white;
    }
    
    .css-1lcbmhc h3 {
        color: #ffd700;
        text-shadow: 1px 1px 2px rgba(0,0,0,0.3);
    }
    
    /* Alerts */
    .stAlert {
        border-radius: 15px;
        border: 2px solid rgba(255,255,255,0.2);
        box-shadow: 0 8px 20px rgba(0,0,0,0.15);
    }
    
    /* Progress bars */
    .stProgress .st-bo {
        background: var(--success-gradient);
        border-radius: 10px;
    }
    
    /* Selectbox and other inputs */
    .stSelectbox > div {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        border-radius: 10px;
        border: 2px solid rgba(255,255,255,0.2);
    }
    
    /* Welcome card */
    .welcome-card {
        background: linear-gradient(135deg, #f093fb 0%, #f5576c 100%);
        padding: 2rem;
        border-radius: 20px;
        color: white;
        text-align: center;
        box-shadow: 0 15px 35px rgba(0,0,0,0.3);
        border: 3px solid rgba(255,255,255,0.2);
        margin: 2rem 0;
    }
    
    .welcome-card h2 {
        color: #ffd700;
        text-shadow: 2px 2px 4px rgba(0,0,0,0.3);
        margin-bottom: 1rem;
    }
    
    .feature-list {
        text-align: left;
        margin: 1rem 0;
        font-size: 1.1rem;
    }
    
    .feature-list li {
        margin: 0.5rem 0;
        text-shadow: 1px 1px 2px rgba(0,0,0,0.2);
    }
    
    /* Animations */
    @keyframes pulse {
        0% { transform: scale(1); }
        50% { transform: scale(1.05); }
        100% { transform: scale(1); }
    }
    
    .pulse {
        animation: pulse 2s infinite;
    }
    
    @keyframes fadeIn {
        from { opacity: 0; transform: translateY(20px); }
        to { opacity: 1; transform: translateY(0); }
    }
    
    .fade-in {
        animation: fadeIn 0.8s ease-out;
    }
    
    </style>
    """, unsafe_allow_html=True)

# =============================================================================
# OPENAI CLIENT CLASS
# =============================================================================

class AIClient:
    """Client for interacting with OpenAI API"""
    
    def __init__(self):
        # Get API key from environment variable
        api_key = os.getenv("OPENAI_API_KEY")
        if not api_key:
            raise ValueError("OPENAI_API_KEY environment variable is not set")
        
        self.client = OpenAI(api_key=api_key)
        self.text_model = "gpt-4o"
        self.vision_model = "gpt-4o"
    
    def get_response(self, user_message, file_analysis_results=None, chat_history=None):
        """Get response from OpenAI API with optional file context"""
        try:
            # Determine if we need vision model
            has_images = False
            if file_analysis_results:
                has_images = any(
                    result.get('file_type', '').startswith('image/') and result.get('base64_data')
                    for result in file_analysis_results
                )
            
            # Prepare messages
            messages = []
            
            # Add system context
            system_message = {
                "role": "system",
                "content": (
                    "You are a helpful AI assistant. You can analyze files and have "
                    "conversations with users. When files are provided, incorporate their "
                    "analysis into your responses. Be helpful, accurate, and engaging."
                )
            }
            messages.append(system_message)
            
            # Add chat history (last 5 messages to manage context)
            if chat_history:
                recent_history = chat_history[-5:] if len(chat_history) > 5 else chat_history
                for msg in recent_history:
                    if msg['role'] in ['user', 'assistant']:
                        messages.append({
                            "role": msg['role'],
                            "content": msg['content']
                        })
            
            # Prepare current user message
            if has_images:
                # Use vision model with images
                content_parts = [{"type": "text", "text": user_message}]
                
                # Add images to the message
                if file_analysis_results:
                    for result in file_analysis_results:
                        if (result.get('file_type', '').startswith('image/') and 
                            result.get('base64_data')):
                            
                            image_url = f"data:{result['file_type']};base64,{result['base64_data']}"
                            content_parts.append({
                                "type": "image_url",
                                "image_url": {"url": image_url}
                            })
                
                messages.append({
                    "role": "user",
                    "content": content_parts
                })
                
                # Generate response with vision model
                response = self.client.chat.completions.create(
                    model=self.vision_model,
                    messages=messages,
                    max_tokens=1000,
                    temperature=0.7
                )
                
            else:
                # Use text model
                user_content = user_message
                
                # Add file analysis context if available
                if file_analysis_results:
                    user_content += "\n\nFile Analysis Context:\n"
                    for result in file_analysis_results:
                        user_content += f"\nFile: {result['filename']}\n"
                        user_content += f"Type: {result['file_type']}\n"
                        user_content += f"Analysis: {result['analysis']}\n"
                
                messages.append({
                    "role": "user",
                    "content": user_content
                })
                
                # Generate response with text model
                response = self.client.chat.completions.create(
                    model=self.text_model,
                    messages=messages,
                    max_tokens=1000,
                    temperature=0.7
                )
            
            return response.choices[0].message.content
            
        except Exception as e:
            error_str = str(e).lower()
            
            if "quota" in error_str or "insufficient_quota" in error_str:
                return self._handle_quota_exceeded(user_message, file_analysis_results)
            elif "api_key" in error_str:
                return "**API Key Error**: Please verify your OpenAI API key is correct and active."
            elif "rate limit" in error_str:
                return "**Rate Limit**: Too many requests. Please wait a moment before trying again."
            elif "connection" in error_str:
                return "**Connection Error**: Please check your internet connection and try again."
            else:
                return f"**API Error**: {str(e)}\n\nPlease check your OpenAI account status and try again."
    
    def _handle_quota_exceeded(self, user_message, file_analysis_results=None):
        """Handle quota exceeded scenario with helpful response"""
        response = "**OpenAI API Quota Exceeded**\n\n"
        response += "Your OpenAI API usage limit has been reached. Here's what you can do:\n\n"
        response += "**Immediate Solutions:**\n"
        response += "• Check your OpenAI billing dashboard at https://platform.openai.com/account/billing\n"
        response += "• Add payment method or increase usage limits\n"
        response += "• Wait for your monthly quota to reset\n\n"
        
        response += "**Your Question Analysis:**\n"
        response += f"You asked: *{user_message[:200]}{'...' if len(user_message) > 200 else ''}*\n\n"
        
        if file_analysis_results:
            response += "**File Analysis Completed:**\n"
            for i, result in enumerate(file_analysis_results, 1):
                response += f"{i}. **{result['filename']}** ({result['file_type']})\n"
                response += f"   {result['analysis'][:150]}{'...' if len(result['analysis']) > 150 else ''}\n\n"
        
        response += "**Alternative Options:**\n"
        response += "• Use a different OpenAI account with available quota\n"
        response += "• Try other AI services like Anthropic Claude or Google Gemini\n"
        response += "• Wait for quota reset and return later\n\n"
        
        response += "**Tip**: Monitor your usage at https://platform.openai.com/account/usage to avoid quota issues."
        
        return response

# =============================================================================
# FILE PROCESSOR CLASS
# =============================================================================

class FileProcessor:
    """Handles processing of different file types for analysis"""
    
    def __init__(self):
        self.supported_image_types = ['image/jpeg', 'image/png', 'image/gif', 'image/bmp']
        self.supported_text_types = ['text/plain']
        self.supported_pdf_types = ['application/pdf']
    
    def detect_file_type(self, file_bytes):
        """Detect file type using python-magic"""
        try:
            mime_type = magic.from_buffer(file_bytes, mime=True)
            return mime_type
        except:
            # Fallback to basic detection
            if file_bytes.startswith(b'%PDF'):
                return 'application/pdf'
            elif file_bytes.startswith(b'\xff\xd8\xff'):
                return 'image/jpeg'
            elif file_bytes.startswith(b'\x89PNG'):
                return 'image/png'
            else:
                return 'text/plain'
    
    def process_file(self, uploaded_file):
        """Process uploaded file and return analysis results"""
        # Read file bytes
        file_bytes = uploaded_file.read()
        uploaded_file.seek(0)  # Reset file pointer
        
        # Detect file type
        mime_type = self.detect_file_type(file_bytes)
        
        analysis_result = {
            'filename': uploaded_file.name,
            'file_type': mime_type,
            'size': len(file_bytes),
            'analysis': '',
            'base64_data': None
        }
        
        try:
            if mime_type in self.supported_image_types:
                analysis_result['analysis'] = self._process_image(file_bytes)
                analysis_result['base64_data'] = base64.b64encode(file_bytes).decode('utf-8')
                
            elif mime_type in self.supported_pdf_types:
                analysis_result['analysis'] = self._process_pdf(file_bytes)
                
            elif mime_type in self.supported_text_types or 'text' in mime_type:
                analysis_result['analysis'] = self._process_text(file_bytes)
                
            else:
                analysis_result['analysis'] = f"Unsupported file type: {mime_type}"
                
        except Exception as e:
            analysis_result['analysis'] = f"Error processing file: {str(e)}"
        
        return analysis_result
    
    def _process_image(self, file_bytes):
        """Process image files and extract basic information"""
        try:
            image = Image.open(io.BytesIO(file_bytes))
            
            # Basic image analysis
            analysis = f"🖼️ **Image Analysis Report**\n\n"
            analysis += f"**Technical Specifications:**\n"
            analysis += f"• Dimensions: {image.width} × {image.height} pixels\n"
            analysis += f"• Format: {image.format}\n"
            analysis += f"• Color Mode: {image.mode}\n"
            analysis += f"• File Size: {len(file_bytes) / 1024:.1f} KB\n\n"
            
            # Color analysis
            if image.mode in ['RGB', 'RGBA']:
                colors = image.getcolors(maxcolors=256*256*256)
                if colors:
                    analysis += f"• Color Information: Rich color palette detected\n"
            
            # Size categories
            total_pixels = image.width * image.height
            if total_pixels < 100000:
                size_cat = "Small (Thumbnail/Icon)"
            elif total_pixels < 1000000:
                size_cat = "Medium (Web/Screen)"
            else:
                size_cat = "Large (High-resolution)"
            
            analysis += f"• Size Category: {size_cat}\n"
            analysis += f"• Total Pixels: {total_pixels:,}\n\n"
            analysis += "**AI Vision Analysis Ready** ✅\n"
            analysis += "This image is prepared for detailed AI visual analysis."
            
            return analysis
            
        except Exception as e:
            return f"Error analyzing image: {str(e)}"
    
    def _process_pdf(self, file_bytes):
        """Process PDF files and extract text content"""
        try:
            pdf_reader = PyPDF2.PdfReader(io.BytesIO(file_bytes))
            
            # Basic PDF info
            num_pages = len(pdf_reader.pages)
            analysis = f"📄 **PDF Document Analysis**\n\n"
            analysis += f"**Document Structure:**\n"
            analysis += f"• Total Pages: {num_pages}\n"
            analysis += f"• File Size: {len(file_bytes) / 1024:.1f} KB\n\n"
            
            # Extract text from first few pages
            extracted_text = ""
            pages_to_process = min(5, num_pages)
            
            for page_num in range(pages_to_process):
                try:
                    page = pdf_reader.pages[page_num]
                    page_text = page.extract_text()
                    extracted_text += page_text + "\n"
                except:
                    continue
            
            if extracted_text.strip():
                word_count = len(extracted_text.split())
                char_count = len(extracted_text)
                
                analysis += f"**Content Analysis:**\n"
                analysis += f"• Characters: {char_count:,}\n"
                analysis += f"• Words: {word_count:,}\n"
                analysis += f"• Pages Processed: {pages_to_process}\n\n"
                
                # Content preview
                preview = extracted_text[:600] + "..." if len(extracted_text) > 600 else extracted_text
                analysis += f"**Content Preview:**\n```\n{preview}\n```\n\n"
                analysis += "**Text Extraction: Successful** ✅"
            else:
                analysis += "**Content Status:** No readable text found (may contain images or scanned content)"
            
            return analysis
            
        except Exception as e:
            return f"Error analyzing PDF: {str(e)}"
    
    def _process_text(self, file_bytes):
        """Process text files and analyze content"""
        try:
            # Detect encoding
            encoding_info = chardet.detect(file_bytes)
            encoding = encoding_info.get('encoding', 'utf-8')
            
            # Decode text
            text_content = file_bytes.decode(encoding, errors='ignore')
            
            # Comprehensive text analysis
            word_count = len(text_content.split())
            line_count = len(text_content.splitlines())
            char_count = len(text_content)
            
            analysis = f"📝 **Text Document Analysis**\n\n"
            analysis += f"**File Properties:**\n"
            analysis += f"• Encoding: {encoding}\n"
            analysis += f"• File Size: {len(file_bytes) / 1024:.1f} KB\n"
            analysis += f"• Text Length: {char_count:,} characters\n\n"
            
            analysis += f"**Content Statistics:**\n"
            analysis += f"• Words: {word_count:,}\n"
            analysis += f"• Lines: {line_count:,}\n"
            analysis += f"• Average words per line: {word_count/line_count:.1f}\n\n"
            
            # Content preview
            preview = text_content[:500] + "..." if len(text_content) > 500 else text_content
            analysis += f"**Content Preview:**\n```\n{preview}\n```\n\n"
            analysis += "**Text Processing: Complete** ✅"
            
            return analysis
            
        except Exception as e:
            return f"Error analyzing text file: {str(e)}"

# Initialize clients
@st.cache_resource
def init_clients():
    """Initialize file processor and AI client"""
    file_processor = FileProcessor()
    ai_client = AIClient()
    return file_processor, ai_client

def render_header():
    """Render the vibrant header"""
    st.markdown("""
    <div class="main-header fade-in">
        <h1 class="pulse">AI ChatBot Pro</h1>
        <p>Your Intelligent Assistant for Everything</p>
    </div>
    """, unsafe_allow_html=True)

def render_sidebar_stats():
    """Render colorful sidebar statistics"""
    st.sidebar.markdown("### Session Statistics")
    
    total_messages = len(st.session_state.messages)
    user_messages = sum(1 for msg in st.session_state.messages if msg["role"] == "user")
    ai_messages = sum(1 for msg in st.session_state.messages if msg["role"] == "assistant")
    files_processed = len(st.session_state.get('uploaded_files', []))
    
    col1, col2 = st.sidebar.columns(2)
    with col1:
        st.markdown(f"""
        <div class="metric-container">
            <h3>{total_messages}</h3>
            <p>Total Messages</p>
        </div>
        """, unsafe_allow_html=True)
        
        st.markdown(f"""
        <div class="metric-container">
            <h3>{files_processed}</h3>
            <p>Files Processed</p>
        </div>
        """, unsafe_allow_html=True)
    
    with col2:
        st.markdown(f"""
        <div class="metric-container">
            <h3>{user_messages}</h3>
            <p>Your Messages</p>
        </div>
        """, unsafe_allow_html=True)
        
        st.markdown(f"""
        <div class="metric-container">
            <h3>{ai_messages}</h3>
            <p>AI Responses</p>
        </div>
        """, unsafe_allow_html=True)

def render_file_upload_section():
    """Render enhanced file upload section"""
    st.sidebar.markdown("### Upload Your Files")
    
    # File uploader
    uploaded_files = st.sidebar.file_uploader(
        "Drag and drop or browse files",
        type=['txt', 'pdf', 'png', 'jpg', 'jpeg', 'gif', 'bmp', 'doc', 'docx', 'csv', 'json'],
        accept_multiple_files=True,
        help="AI can analyze images, documents, and text files!"
    )
    
    if uploaded_files:
        st.sidebar.markdown("#### Ready to Analyze:")
        for i, file in enumerate(uploaded_files, 1):
            file_size = f"{file.size / 1024:.1f} KB" if file.size < 1024*1024 else f"{file.size / (1024*1024):.1f} MB"
            st.sidebar.markdown(f"""
            <div class="uploadedFile">
                <strong>{file.name}</strong><br>
                <small>{file_size} • {file.type or 'Unknown'}</small>
            </div>
            """, unsafe_allow_html=True)
    
    return uploaded_files

def render_chat_controls():
    """Render colorful chat control buttons"""
    st.sidebar.markdown("### Chat Controls")
    
    col1, col2 = st.sidebar.columns(2)
    with col1:
        if st.button("Clear Chat", use_container_width=True):
            st.session_state.messages = []
            st.session_state.uploaded_files = []
            st.rerun()
    
    with col2:
        if st.button("Export", use_container_width=True):
            export_chat_history()

def export_chat_history():
    """Export chat history as JSON"""
    if st.session_state.messages:
        chat_data = {
            "export_date": datetime.now().isoformat(),
            "total_messages": len(st.session_state.messages),
            "messages": st.session_state.messages
        }
        
        json_data = json.dumps(chat_data, indent=2, ensure_ascii=False)
        st.sidebar.download_button(
            label="Download Chat",
            data=json_data,
            file_name=f"chat_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json",
            mime="application/json",
            use_container_width=True
        )
        st.sidebar.success("Ready to download!")

def main():
    # Load custom CSS
    load_css()
    
    # Initialize clients
    file_processor, ai_client = init_clients()
    
    # Initialize session state
    if 'messages' not in st.session_state:
        st.session_state.messages = []
    if 'uploaded_files' not in st.session_state:
        st.session_state.uploaded_files = []
    
    # Render header
    render_header()
    
    # Sidebar content
    with st.sidebar:
        render_sidebar_stats()
        uploaded_files = render_file_upload_section()
        render_chat_controls()
        
        
    
    # Welcome message for new users
    if not st.session_state.messages:
        st.markdown("""
        <div class="welcome-card fade-in">
            <h2>Welcome to Your AI Assistant!</h2>
            <div class="feature-list">
                <p><strong>Ready to help you with:</strong></p>
                <ul>
                    <li>Writing and content creation</li>
                    <li>Image and document analysis</li>
                    <li>Data insights and calculations</li>
                    <li>Programming and coding help</li>
                    <li>Creative problem solving</li>
                </ul>
            </div>
            <p><strong>Upload a file or start chatting to begin!</strong></p>
        </div>
        """, unsafe_allow_html=True)
    
    # Display chat history
    for message in st.session_state.messages:
        with st.chat_message(message["role"]):
            st.write(message["content"])
    
    # Handle quick prompts
    if hasattr(st.session_state, 'quick_prompt'):
        prompt = st.session_state.quick_prompt
        del st.session_state.quick_prompt
        st.rerun()
    
    # Chat input
    if prompt := st.chat_input("Ask me anything or upload files for analysis..."):
        # Process uploaded files if any
        file_analysis_results = []
        current_files = []
        
        if uploaded_files:
            with st.spinner("Processing your files..."):
                progress_bar = st.progress(0)
                for i, uploaded_file in enumerate(uploaded_files):
                    try:
                        # Update progress
                        progress_bar.progress((i + 1) / len(uploaded_files))
                        
                        # Process the file
                        analysis_result = file_processor.process_file(uploaded_file)
                        file_analysis_results.append(analysis_result)
                        
                        current_files.append({
                            'name': uploaded_file.name,
                            'type': analysis_result['file_type'],
                            'size': uploaded_file.size
                        })
                        
                    except Exception as e:
                        st.error(f"Error processing {uploaded_file.name}: {str(e)}")
                
                progress_bar.empty()
                if file_analysis_results:
                    st.success(f"Successfully processed {len(file_analysis_results)} files!")
        
        # Add user message to chat history
        user_message = {
            "role": "user",
            "content": prompt,
            "files": current_files,
            "timestamp": datetime.now().strftime("%H:%M:%S")
        }
        st.session_state.messages.append(user_message)
        
        # Display user message
        with st.chat_message("user"):
            st.write(prompt)
        
        # Generate AI response
        with st.chat_message("assistant"):
            with st.spinner("AI is thinking..."):
                try:
                    # Prepare context with file analysis
                    context = prompt
                    if file_analysis_results:
                        context += "\n\nFile Analysis Results:\n"
                        for i, result in enumerate(file_analysis_results, 1):
                            context += f"\n{i}. **File**: {result['filename']}\n"
                            context += f"   **Type**: {result['file_type']}\n"
                            context += f"   **Analysis**: {result['analysis']}\n"
                    
                    # Get response from AI
                    response = ai_client.get_response(
                        context, 
                        file_analysis_results,
                        st.session_state.messages[:-1]  # Previous messages for context
                    )
                    
                    st.write(response)
                    
                    # Add assistant response to chat history
                    assistant_message = {
                        "role": "assistant",
                        "content": response,
                        "timestamp": datetime.now().strftime("%H:%M:%S")
                    }
                    st.session_state.messages.append(assistant_message)
                    
                except Exception as e:
                    error_msg = f"Sorry, I encountered an error: {str(e)}"
                    st.error(error_msg)
                    
                    # Add error message to chat history
                    error_message = {
                        "role": "assistant",
                        "content": error_msg,
                        "timestamp": datetime.now().strftime("%H:%M:%S")
                    }
                    st.session_state.messages.append(error_message)
        
        # Update uploaded files in session state
        st.session_state.uploaded_files = current_files
        
        # Rerun to update the chat display
        st.rerun()

if __name__ == "__main__":
    main()
