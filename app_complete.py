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
    page_icon="🤖",
    layout="wide",
    initial_sidebar_state="expanded"
)

# =============================================================================
# OPENAI CLIENT CLASS
# =============================================================================

class AIClient:
    """Client for interacting with OpenAI API"""
    
    def __init__(self):
        # Set your API key directly
        api_key = "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"
        
        self.client = OpenAI(api_key=api_key)
        # the newest OpenAI model is "gpt-4o" which was released May 13, 2024.
        # do not change this unless explicitly requested by the user
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
            error_msg = f"Failed to get response from OpenAI API: {str(e)}"
            if "api_key" in str(e).lower():
                error_msg += "\n\nPlease check that your OpenAI API key is valid."
            elif "rate limit" in str(e).lower():
                error_msg += "\n\nRate limit exceeded. Please wait a moment before trying again."
            elif "quota" in str(e).lower():
                error_msg += "\n\nAPI quota exceeded. Please check your OpenAI billing and usage."
            elif "connection" in str(e).lower():
                error_msg += "\n\nConnection error. Please check your internet connection."
            
            return error_msg

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

# =============================================================================
# STYLING AND UI FUNCTIONS
# =============================================================================

def load_css():
    """Load custom CSS for enhanced styling"""
    st.markdown("""
    <style>
    /* Main theme colors */
    :root {
        --primary-color: #FF6B6B;
        --secondary-color: #4ECDC4;
        --accent-color: #45B7D1;
        --background-gradient: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        --chat-user-bg: #e3f2fd;
        --chat-ai-bg: #f3e5f5;
    }
    
    /* Header styling */
    .main-header {
        background: var(--background-gradient);
        padding: 2rem;
        border-radius: 15px;
        margin-bottom: 2rem;
        text-align: center;
        color: white;
        box-shadow: 0 8px 32px rgba(0,0,0,0.1);
    }
    
    .main-header h1 {
        font-size: 3rem;
        margin: 0;
        text-shadow: 2px 2px 4px rgba(0,0,0,0.3);
    }
    
    .main-header p {
        font-size: 1.2rem;
        margin: 0.5rem 0 0 0;
        opacity: 0.9;
    }
    
    /* Chat container styling */
    .chat-container {
        background: rgba(255,255,255,0.95);
        border-radius: 15px;
        padding: 1rem;
        margin: 1rem 0;
        box-shadow: 0 4px 16px rgba(0,0,0,0.1);
    }
    
    /* Message styling */
    .user-message {
        background: var(--chat-user-bg);
        padding: 1rem;
        border-radius: 15px 15px 5px 15px;
        margin: 0.5rem 0;
        border-left: 4px solid var(--accent-color);
    }
    
    .ai-message {
        background: var(--chat-ai-bg);
        padding: 1rem;
        border-radius: 15px 15px 15px 5px;
        margin: 0.5rem 0;
        border-left: 4px solid var(--secondary-color);
    }
    
    /* File uploader */
    .uploadedFile {
        background: rgba(255,255,255,0.9);
        border-radius: 10px;
        padding: 0.5rem;
        margin: 0.25rem 0;
        border-left: 4px solid var(--accent-color);
    }
    
    /* Buttons */
    .stButton > button {
        background: linear-gradient(45deg, var(--primary-color), var(--secondary-color));
        color: white;
        border: none;
        border-radius: 25px;
        padding: 0.5rem 2rem;
        font-weight: bold;
        transition: all 0.3s ease;
    }
    
    .stButton > button:hover {
        transform: translateY(-2px);
        box-shadow: 0 4px 12px rgba(0,0,0,0.2);
    }
    
    /* Success/Error messages */
    .element-container .stAlert {
        border-radius: 10px;
    }
    
    /* Progress bars */
    .stProgress .st-bo {
        background: var(--background-gradient);
    }
    
    </style>
    """, unsafe_allow_html=True)

def render_header():
    """Render the main header"""
    st.markdown("""
    <div class="main-header">
        <h1>🤖 AI ChatBot Pro</h1>
        <p>Advanced AI Assistant with File Analysis & Multi-Modal Capabilities</p>
    </div>
    """, unsafe_allow_html=True)

def render_sidebar_stats():
    """Render sidebar statistics"""
    st.sidebar.markdown("### 📊 Session Stats")
    
    total_messages = len(st.session_state.messages)
    user_messages = sum(1 for msg in st.session_state.messages if msg["role"] == "user")
    ai_messages = sum(1 for msg in st.session_state.messages if msg["role"] == "assistant")
    files_processed = len(st.session_state.get('uploaded_files', []))
    
    col1, col2 = st.sidebar.columns(2)
    with col1:
        st.metric("Total Messages", total_messages)
        st.metric("Files Processed", files_processed)
    with col2:
        st.metric("User Messages", user_messages)
        st.metric("AI Responses", ai_messages)

def render_file_upload_section():
    """Render enhanced file upload section"""
    st.sidebar.markdown("### 📁 File Upload Center")
    
    # File uploader with enhanced styling
    uploaded_files = st.sidebar.file_uploader(
        "Upload your files for AI analysis",
        type=['txt', 'pdf', 'png', 'jpg', 'jpeg', 'gif', 'bmp', 'doc', 'docx', 'csv', 'json'],
        accept_multiple_files=True,
        help="Supported: Text, PDF, Images, Documents, Data files"
    )
    
    if uploaded_files:
        st.sidebar.markdown("#### 📋 Uploaded Files:")
        for i, file in enumerate(uploaded_files, 1):
            file_size = f"{file.size / 1024:.1f} KB" if file.size < 1024*1024 else f"{file.size / (1024*1024):.1f} MB"
            st.sidebar.markdown(f"""
            <div class="uploadedFile">
                <b>{i}.</b> {file.name}<br>
                <small>Size: {file_size} | Type: {file.type or 'Unknown'}</small>
            </div>
            """, unsafe_allow_html=True)
    
    return uploaded_files

def render_chat_controls():
    """Render chat control buttons"""
    st.sidebar.markdown("### 🎛️ Chat Controls")
    
    col1, col2 = st.sidebar.columns(2)
    with col1:
        if st.button("🗑️ Clear Chat", use_container_width=True):
            st.session_state.messages = []
            st.session_state.uploaded_files = []
            st.rerun()
    
    with col2:
        if st.button("💾 Export Chat", use_container_width=True):
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
            label="📥 Download Chat History",
            data=json_data,
            file_name=f"chat_history_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json",
            mime="application/json",
            use_container_width=True
        )
        st.sidebar.success("Chat history ready for download!")

def render_chat_message(message, is_user=True):
    """Render a chat message with enhanced styling"""
    timestamp = message.get("timestamp", "")
    role_icon = "👤" if is_user else "🤖"
    role_name = "You" if is_user else "AI Assistant"
    
    with st.chat_message(message["role"]):
        # Message header
        st.markdown(f"**{role_icon} {role_name}** *{timestamp}*")
        
        # Message content
        st.write(message["content"])
        
        # File attachments
        if "files" in message and message["files"]:
            st.markdown("📎 **Attached files:**")
            for file_info in message["files"]:
                st.markdown(f"• `{file_info['name']}` ({file_info['type']})")

# =============================================================================
# MAIN APPLICATION
# =============================================================================

@st.cache_resource
def init_clients():
    """Initialize file processor and AI client"""
    file_processor = FileProcessor()
    ai_client = AIClient()
    return file_processor, ai_client

def main():
    """Main application function"""
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
        
        # AI Model Info
        st.markdown("### 🧠 AI Model Info")
        st.info("**Model**: GPT-4o (OpenAI)\n**Capabilities**: Text, Image, Code, Analysis")
        
        # Quick Actions
        st.markdown("### ⚡ Quick Actions")
        if st.button("💡 Get Writing Help", use_container_width=True):
            st.session_state.quick_prompt = "Help me write a professional email"
        if st.button("🔍 Analyze Data", use_container_width=True):
            st.session_state.quick_prompt = "Analyze the data I've uploaded and provide insights"
        if st.button("💭 Brainstorm Ideas", use_container_width=True):
            st.session_state.quick_prompt = "Help me brainstorm creative ideas for my project"
    
    # Main chat interface
    st.markdown('<div class="chat-container">', unsafe_allow_html=True)
    
    # Welcome message for new users
    if not st.session_state.messages:
        st.markdown("""
        <div class="ai-message">
            <h3>👋 Welcome to AI ChatBot Pro!</h3>
            <p>I'm your advanced AI assistant powered by GPT-4o. I can help you with:</p>
            <ul>
                <li>📝 Writing and editing content</li>
                <li>🖼️ Analyzing images and documents</li>
                <li>📊 Data analysis and insights</li>
                <li>💻 Coding and technical questions</li>
                <li>🎯 Creative problem solving</li>
            </ul>
            <p><strong>Try uploading a file or ask me anything to get started!</strong></p>
        </div>
        """, unsafe_allow_html=True)
    
    # Display chat history
    for message in st.session_state.messages:
        render_chat_message(message, message["role"] == "user")
    
    st.markdown('</div>', unsafe_allow_html=True)
    
    # Handle quick prompts
    if hasattr(st.session_state, 'quick_prompt'):
        prompt = st.session_state.quick_prompt
        del st.session_state.quick_prompt
        st.rerun()
    
    # Chat input
    if prompt := st.chat_input("💬 Type your message here... (Supports text, questions, file analysis requests)"):
        # Process uploaded files if any
        file_analysis_results = []
        current_files = []
        
        if uploaded_files:
            with st.spinner("🔄 Processing uploaded files..."):
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
                        st.error(f"❌ Error processing {uploaded_file.name}: {str(e)}")
                
                progress_bar.empty()
                if file_analysis_results:
                    st.success(f"✅ Successfully processed {len(file_analysis_results)} files!")
        
        # Add user message to chat history
        user_message = {
            "role": "user",
            "content": prompt,
            "files": current_files,
            "timestamp": datetime.now().strftime("%H:%M:%S")
        }
        st.session_state.messages.append(user_message)
        
        # Display user message
        render_chat_message(user_message, True)
        
        # Generate AI response
        with st.chat_message("assistant"):
            with st.spinner("🤔 AI is thinking..."):
                try:
                    # Prepare context with file analysis
                    context = prompt
                    if file_analysis_results:
                        context += "\n\n📋 File Analysis Results:\n"
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
                    
                    # Display response with typing effect simulation
                    message_placeholder = st.empty()
                    full_response = ""
                    
                    # Simulate typing effect (optional)
                    words = response.split()
                    for i, word in enumerate(words):
                        full_response += word + " "
                        if i % 10 == 0:  # Update every 10 words
                            message_placeholder.write(full_response)
                    
                    message_placeholder.write(response)
                    
                    # Add assistant response to chat history
                    assistant_message = {
                        "role": "assistant",
                        "content": response,
                        "timestamp": datetime.now().strftime("%H:%M:%S")
                    }
                    st.session_state.messages.append(assistant_message)
                    
                except Exception as e:
                    error_msg = f"❌ Sorry, I encountered an error: {str(e)}"
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
    
    # Footer
    st.markdown("---")
    st.markdown("""
    <div style="text-align: center; color: #666; padding: 1rem;">
        <p>🚀 AI ChatBot Pro - Powered by GPT-4o | Built with Streamlit</p>
        <p>💡 <em>Upload files, ask questions, get intelligent responses!</em></p>
    </div>
    """, unsafe_allow_html=True)

if __name__ == "__main__":
    main()