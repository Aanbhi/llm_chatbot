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

# Custom CSS for enhanced styling (no emojis)
def load_css():
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
        --success-color: #28a745;
        --warning-color: #ffc107;
        --error-color: #dc3545;
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
    
    /* Status indicators */
    .status-success {
        color: var(--success-color);
        font-weight: bold;
    }
    
    .status-warning {
        color: var(--warning-color);
        font-weight: bold;
    }
    
    .status-error {
        color: var(--error-color);
        font-weight: bold;
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
    
    /* Progress bars */
    .stProgress .st-bo {
        background: var(--background-gradient);
    }
    
    </style>
    """, unsafe_allow_html=True)

# =============================================================================
# LOCAL AI CHATBOT CLASS
# =============================================================================

class LocalChatBot:
    """Advanced local chatbot with natural conversation capabilities"""
    
    def __init__(self):
        self.conversation_context = []
        self.response_templates = {
            'greetings': [
                "Hello! How can I assist you today?",
                "Hi there! What would you like to work on?",
                "Hey! I'm here to help with your files and questions.",
                "Good to see you! What can I help you with?",
                "Welcome back! How can I assist you today?"
            ],
            'capabilities': [
                "I specialize in analyzing files and providing detailed insights about their content and structure.",
                "I can process images, PDFs, and text files to extract technical specifications and content analysis.",
                "My expertise includes file format detection, content extraction, and providing technical documentation.",
                "I analyze uploaded files and provide comprehensive reports on their properties and content."
            ],
            'file_questions': [
                "Please upload the file you'd like me to analyze, and I'll provide detailed insights.",
                "I can examine any file you upload and give you comprehensive analysis results.",
                "Upload your file and I'll break down its technical specifications and content for you.",
                "Share your file with me and I'll provide a thorough analysis of its structure and content."
            ],
            'general_knowledge': [
                "I focus on file analysis and technical documentation. Could you upload a file for me to examine?",
                "My expertise is in processing and analyzing files. What file would you like me to review?",
                "I'm designed for file analysis tasks. Feel free to upload any document, image, or text file.",
                "I excel at examining files and extracting insights. What would you like me to analyze?"
            ]
        }
        
        self.conversation_memory = []
        self.context_keywords = {
            'technical': ['code', 'programming', 'algorithm', 'data', 'structure', 'format'],
            'creative': ['design', 'art', 'creative', 'visual', 'aesthetic', 'style'],
            'business': ['report', 'document', 'presentation', 'analysis', 'business'],
            'academic': ['research', 'study', 'paper', 'thesis', 'academic', 'scholarly']
        }
        
    def get_response(self, user_message, file_analysis_results=None, chat_history=None):
        """Generate contextual response based on user input and conversation history"""
        import random
        
        # Store conversation context
        self.conversation_memory.append(user_message.lower())
        if len(self.conversation_memory) > 10:
            self.conversation_memory.pop(0)
        
        user_lower = user_message.lower()
        
        # File analysis response
        if file_analysis_results:
            return self._generate_file_analysis_response(user_message, file_analysis_results)
        
        # Contextual conversation responses
        if self._is_greeting(user_lower):
            return random.choice(self.response_templates['greetings'])
        
        elif self._is_question_about_capabilities(user_lower):
            return random.choice(self.response_templates['capabilities'])
        
        elif self._is_asking_for_help(user_lower):
            return self._contextual_help_response(user_message)
        
        elif self._is_thanking(user_lower):
            return self._gratitude_response()
        
        elif self._is_asking_about_files(user_lower):
            return random.choice(self.response_templates['file_questions'])
        
        elif self._is_general_question(user_lower):
            return self._intelligent_general_response(user_message)
        
        else:
            return self._contextual_fallback_response(user_message)
    
    def _generate_file_analysis_response(self, user_message, file_analysis_results):
        """Generate response based on file analysis results"""
        response = "**File Analysis Complete**\n\n"
        response += f"I've analyzed {len(file_analysis_results)} file(s) for you:\n\n"
        
        for i, result in enumerate(file_analysis_results, 1):
            response += f"**File {i}: {result['filename']}**\n"
            response += f"- Type: {result['file_type']}\n"
            response += f"- Size: {result['size'] / 1024:.1f} KB\n\n"
            
            # Add detailed analysis
            if result['analysis']:
                response += f"**Analysis Results:**\n{result['analysis']}\n\n"
        
        # Provide contextual advice based on user message
        user_lower = user_message.lower()
        if 'summarize' in user_lower or 'summary' in user_lower:
            response += "**Summary Insights:**\n"
            response += "Based on the file analysis, I've extracted key information including file properties, content statistics, and technical details. "
            response += "The files have been processed and analyzed for their structure and content.\n\n"
        
        elif 'explain' in user_lower or 'tell me about' in user_lower:
            response += "**Detailed Explanation:**\n"
            response += "The uploaded files contain various types of content. Each file has been processed using specialized algorithms "
            response += "to extract relevant information, detect file types, and analyze content structure.\n\n"
        
        response += "**What I can help you with:**\n"
        response += "- Content analysis and insights\n"
        response += "- File format and technical details\n"
        response += "- Data extraction and processing\n"
        response += "- Recommendations for file optimization\n"
        
        return response
    

    
    def _is_greeting(self, text):
        greetings = ['hello', 'hi', 'hey', 'good morning', 'good afternoon', 'good evening', 'greetings']
        return any(greeting in text for greeting in greetings)
    
    def _is_question_about_capabilities(self, text):
        capability_words = ['what can you do', 'capabilities', 'what are you', 'who are you', 'what is this']
        return any(phrase in text for phrase in capability_words)
    
    def _is_asking_for_help(self, text):
        help_words = ['help', 'assist', 'support', 'guide', 'how to', 'explain']
        return any(word in text for word in help_words)
    
    def _is_thanking(self, text):
        thanks = ['thank', 'thanks', 'appreciate', 'grateful']
        return any(thank in text for thank in thanks)
    
    def _is_asking_about_files(self, text):
        file_words = ['file', 'document', 'upload', 'analyze', 'examine', 'process']
        return any(word in text for word in file_words)
    
    def _is_general_question(self, text):
        question_words = ['what', 'how', 'why', 'when', 'where', 'who', 'which', 'can you']
        return any(word in text for word in question_words)
    
    def _contextual_help_response(self, user_message):
        """Provide contextual help based on user's specific question"""
        user_lower = user_message.lower()
        
        if 'upload' in user_lower or 'file' in user_lower:
            return "To upload files, use the file uploader in the sidebar. I can analyze images, PDFs, and text documents to provide detailed insights about their content and technical specifications."
        
        elif 'analyze' in user_lower:
            return "I can analyze various file types including images (technical specs, dimensions), PDFs (text extraction, structure), and text files (content statistics, encoding). Just upload a file and I'll provide comprehensive analysis."
        
        elif 'feature' in user_lower or 'function' in user_lower:
            return "My main features include file analysis, content extraction, technical specification reporting, and conversational assistance. I process files locally and provide detailed insights."
        
        else:
            return "I'm here to help with file analysis and technical documentation. Upload any file you'd like me to examine, or ask me specific questions about my capabilities."
    
    def _gratitude_response(self):
        """Respond to thank you messages"""
        import random
        responses = [
            "You're welcome! Happy to help with your file analysis needs.",
            "Glad I could assist! Feel free to upload more files or ask any questions.",
            "My pleasure! I'm here whenever you need file analysis or technical insights.",
            "You're very welcome! Let me know if you need anything else analyzed."
        ]
        return random.choice(responses)
    
    def _intelligent_general_response(self, user_message):
        """Generate intelligent responses for general questions"""
        user_lower = user_message.lower()
        
        # Detect context from keywords
        context = self._detect_context(user_lower)
        
        if 'name' in user_lower:
            return "I'm an AI assistant specialized in file analysis and technical documentation. You can call me your File Analysis Assistant."
        
        elif 'how are you' in user_lower or 'how do you do' in user_lower:
            return "I'm functioning well and ready to help you analyze files and extract insights from your documents!"
        
        elif context == 'technical':
            return "I excel at technical analysis of files including code structure, data formats, and technical specifications. What technical file would you like me to examine?"
        
        elif context == 'creative':
            return "I can analyze creative files like images and documents, providing technical details about formats, dimensions, and content structure."
        
        elif context == 'business':
            return "I'm great at analyzing business documents, extracting content, and providing structural insights about reports and presentations."
        
        else:
            return f"That's an interesting question about '{user_message[:50]}...'. While I specialize in file analysis, I'd be happy to examine any documents or files you'd like to share."
    
    def _detect_context(self, text):
        """Detect conversation context from keywords"""
        for context, keywords in self.context_keywords.items():
            if any(keyword in text for keyword in keywords):
                return context
        return 'general'
    
    def _contextual_fallback_response(self, user_message):
        """Intelligent fallback response that acknowledges the user's input"""
        import random
        
        responses = [
            f"I understand you're interested in '{user_message[:40]}...'. I'm specialized in file analysis - would you like to upload a file for me to examine?",
            f"That's an interesting point about '{user_message[:40]}...'. My expertise is in analyzing files and documents. What would you like me to review?",
            f"I see you're asking about '{user_message[:40]}...'. I focus on file analysis and technical documentation. Feel free to share any files you'd like analyzed.",
            "I'd love to help with that! My strength is in analyzing files and extracting insights. Do you have any documents or files you'd like me to examine?"
        ]
        
        return random.choice(responses)

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
            analysis = f"**Image Analysis Report**\n\n"
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
                    analysis += f"• Unique Colors: {len(colors)} different colors\n"
            
            # Size categories
            total_pixels = image.width * image.height
            if total_pixels < 100000:
                size_cat = "Small (Thumbnail/Icon)"
            elif total_pixels < 1000000:
                size_cat = "Medium (Web/Screen)"
            else:
                size_cat = "Large (High-resolution)"
            
            analysis += f"• Size Category: {size_cat}\n"
            analysis += f"• Total Pixels: {total_pixels:,}\n"
            analysis += f"• Aspect Ratio: {image.width/image.height:.2f}:1\n\n"
            
            # Quality assessment
            if total_pixels > 2000000:
                analysis += "**Quality Assessment:** High-resolution image suitable for print\n"
            elif total_pixels > 500000:
                analysis += "**Quality Assessment:** Good quality for web and digital use\n"
            else:
                analysis += "**Quality Assessment:** Standard resolution for basic use\n"
            
            analysis += "**Image Processing Complete**\n"
            analysis += "Local analysis completed successfully with technical specifications extracted."
            
            return analysis
            
        except Exception as e:
            return f"Error analyzing image: {str(e)}"
    
    def _process_pdf(self, file_bytes):
        """Process PDF files and extract text content"""
        try:
            pdf_reader = PyPDF2.PdfReader(io.BytesIO(file_bytes))
            
            # Basic PDF info
            num_pages = len(pdf_reader.pages)
            analysis = f"**PDF Document Analysis**\n\n"
            analysis += f"**Document Structure:**\n"
            analysis += f"• Total Pages: {num_pages}\n"
            analysis += f"• File Size: {len(file_bytes) / 1024:.1f} KB\n"
            analysis += f"• Average Page Size: {(len(file_bytes) / 1024) / num_pages:.1f} KB per page\n\n"
            
            # Extract text from first few pages
            extracted_text = ""
            pages_to_process = min(5, num_pages)
            successful_pages = 0
            
            for page_num in range(pages_to_process):
                try:
                    page = pdf_reader.pages[page_num]
                    page_text = page.extract_text()
                    if page_text.strip():
                        extracted_text += page_text + "\n"
                        successful_pages += 1
                except:
                    continue
            
            if extracted_text.strip():
                word_count = len(extracted_text.split())
                char_count = len(extracted_text)
                
                analysis += f"**Content Analysis:**\n"
                analysis += f"• Characters Extracted: {char_count:,}\n"
                analysis += f"• Words Extracted: {word_count:,}\n"
                analysis += f"• Pages Successfully Processed: {successful_pages}\n"
                analysis += f"• Average Words per Page: {word_count//successful_pages if successful_pages > 0 else 0}\n\n"
                
                # Content preview
                preview = extracted_text[:600] + "..." if len(extracted_text) > 600 else extracted_text
                analysis += f"**Content Preview:**\n```\n{preview}\n```\n\n"
                
                # Language detection (basic)
                if any(char.isalpha() for char in extracted_text):
                    analysis += "**Content Type:** Text-based document with readable content\n"
                else:
                    analysis += "**Content Type:** Document may contain non-text elements\n"
                
                analysis += "**Text Extraction: Successful**"
            else:
                analysis += "**Content Status:** No readable text found\n"
                analysis += "This may be a scan-based PDF or contain primarily images"
            
            return analysis
            
        except Exception as e:
            return f"Error analyzing PDF: {str(e)}"
    
    def _process_text(self, file_bytes):
        """Process text files and analyze content"""
        try:
            # Detect encoding
            encoding_info = chardet.detect(file_bytes)
            encoding = encoding_info.get('encoding', 'utf-8')
            confidence = encoding_info.get('confidence', 0)
            
            # Decode text
            text_content = file_bytes.decode(encoding, errors='ignore')
            
            # Comprehensive text analysis
            word_count = len(text_content.split())
            line_count = len(text_content.splitlines())
            char_count = len(text_content)
            char_count_no_spaces = len(text_content.replace(' ', '').replace('\n', '').replace('\t', ''))
            
            analysis = f"**Text Document Analysis**\n\n"
            analysis += f"**File Properties:**\n"
            analysis += f"• Encoding: {encoding} (confidence: {confidence:.1%})\n"
            analysis += f"• File Size: {len(file_bytes) / 1024:.1f} KB\n"
            analysis += f"• Text Length: {char_count:,} characters\n"
            analysis += f"• Text Length (no spaces): {char_count_no_spaces:,} characters\n\n"
            
            analysis += f"**Content Statistics:**\n"
            analysis += f"• Total Words: {word_count:,}\n"
            analysis += f"• Total Lines: {line_count:,}\n"
            analysis += f"• Average Words per Line: {word_count/line_count:.1f}\n"
            analysis += f"• Average Characters per Word: {char_count_no_spaces/word_count:.1f}\n\n"
            
            # Content structure analysis
            empty_lines = text_content.count('\n\n')
            paragraphs = len([p for p in text_content.split('\n\n') if p.strip()])
            
            analysis += f"**Document Structure:**\n"
            analysis += f"• Estimated Paragraphs: {paragraphs}\n"
            analysis += f"• Empty Lines: {empty_lines}\n"
            analysis += f"• Average Words per Paragraph: {word_count//paragraphs if paragraphs > 0 else 0}\n\n"
            
            # Content preview
            preview = text_content[:500] + "..." if len(text_content) > 500 else text_content
            analysis += f"**Content Preview:**\n```\n{preview}\n```\n\n"
            analysis += "**Text Processing: Complete**"
            
            return analysis
            
        except Exception as e:
            return f"Error analyzing text file: {str(e)}"

# =============================================================================
# UI FUNCTIONS
# =============================================================================

def render_header():
    """Render the main header"""
    st.markdown("""
    <div class="main-header">
        <h1>AI Chatbot</h1>
        <p>File Analysis Assistant</p>
    </div>
    """, unsafe_allow_html=True)

def render_sidebar_stats():
    """Render sidebar statistics"""
    st.sidebar.markdown("### Session Statistics")
    
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
    st.sidebar.markdown("### File Upload Center")
    
    # File uploader
    uploaded_files = st.sidebar.file_uploader(
        "Upload your files for analysis",
        type=['txt', 'pdf', 'png', 'jpg', 'jpeg', 'gif', 'bmp', 'doc', 'docx', 'csv', 'json'],
        accept_multiple_files=True,
        help="Supported: Text, PDF, Images, Documents, Data files"
    )
    
    if uploaded_files:
        st.sidebar.markdown("#### Uploaded Files:")
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
    st.sidebar.markdown("### Chat Controls")
    
    col1, col2 = st.sidebar.columns(2)
    with col1:
        if st.button("Clear Chat", use_container_width=True):
            st.session_state.messages = []
            st.session_state.uploaded_files = []
            st.rerun()
    
    with col2:
        if st.button("Export Chat", use_container_width=True):
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
            label="Download Chat History",
            data=json_data,
            file_name=f"chat_history_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json",
            mime="application/json",
            use_container_width=True
        )
        st.sidebar.success("Chat history ready for download!")

def render_chat_message(message, is_user=True):
    """Render a chat message with enhanced styling"""
    timestamp = message.get("timestamp", "")
    role_icon = "User" if is_user else "Assistant"
    
    with st.chat_message(message["role"]):
        # Message header
        st.markdown(f"**{role_icon}** *{timestamp}*")
        
        # Message content
        st.write(message["content"])
        
        # File attachments
        if "files" in message and message["files"]:
            st.markdown("**Attached files:**")
            for file_info in message["files"]:
                st.markdown(f"• `{file_info['name']}` ({file_info['type']})")

# =============================================================================
# MAIN APPLICATION
# =============================================================================

@st.cache_resource
def init_clients():
    """Initialize file processor and AI client"""
    file_processor = FileProcessor()
    chatbot = LocalChatBot()
    return file_processor, chatbot

def main():
    """Main application function"""
    # Load custom CSS
    load_css()
    
    # Initialize clients
    file_processor, chatbot = init_clients()
    
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
        

        
        # Quick Actions
        st.markdown("### Quick Actions")
        if st.button("Get Help", use_container_width=True):
            st.session_state.quick_prompt = "help"
        if st.button("Show Capabilities", use_container_width=True):
            st.session_state.quick_prompt = "what can you do"
        if st.button("Analysis Guide", use_container_width=True):
            st.session_state.quick_prompt = "how to analyze files"
    
    # Main chat interface
    st.markdown('<div class="chat-container">', unsafe_allow_html=True)
    
    # Welcome message for new users
    if not st.session_state.messages:
        st.markdown("""
        <div class="ai-message">
            <h3>Welcome!</h3>
            <p>Upload files for analysis or ask questions.</p>
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
    if prompt := st.chat_input("Type your message here..."):
        # Process uploaded files if any
        file_analysis_results = []
        current_files = []
        
        if uploaded_files:
            with st.spinner("Processing uploaded files..."):
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
        render_chat_message(user_message, True)
        
        # Generate AI response
        with st.chat_message("assistant"):
            with st.spinner("Processing your request..."):
                try:
                    # Get response from local chatbot
                    response = chatbot.get_response(
                        prompt, 
                        file_analysis_results,
                        st.session_state.messages[:-1]  # Previous messages for context
                    )
                    
                    # Display response
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