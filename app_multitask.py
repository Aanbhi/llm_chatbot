import streamlit as st
import base64
import io
import json
import os
import re
import math
import random
from datetime import datetime
from typing import Dict, Any, List

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
    page_title="AI Multi-Task Assistant",
    page_icon="🤖",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS for enhanced styling
def load_css():
    st.markdown("""
    <style>
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
    
    .chat-container {
        background: rgba(255,255,255,0.95);
        border-radius: 15px;
        padding: 1rem;
        margin: 1rem 0;
        box-shadow: 0 4px 16px rgba(0,0,0,0.1);
    }
    
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
    
    .capability-card {
        background: linear-gradient(45deg, #f8f9fa, #e9ecef);
        border-radius: 10px;
        padding: 1rem;
        margin: 0.5rem 0;
        border-left: 4px solid var(--accent-color);
    }
    
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
    </style>
    """, unsafe_allow_html=True)

# =============================================================================
# MULTI-TASK AI ASSISTANT CLASS
# =============================================================================

class MultiTaskAI:
    """Advanced multi-tasking AI assistant for conversations and file analysis"""
    
    def __init__(self):
        self.conversation_memory = []
        self.knowledge_base = self._initialize_knowledge_base()
        self.task_categories = {
            'math': ['calculate', 'solve', 'equation', 'math', 'formula', 'number'],
            'programming': ['code', 'python', 'javascript', 'html', 'css', 'programming', 'function'],
            'writing': ['write', 'essay', 'letter', 'email', 'story', 'article', 'content'],
            'analysis': ['analyze', 'examine', 'review', 'compare', 'evaluate', 'assess'],
            'creative': ['design', 'creative', 'idea', 'brainstorm', 'imagine', 'art'],
            'business': ['business', 'market', 'strategy', 'plan', 'proposal', 'report'],
            'education': ['learn', 'teach', 'explain', 'study', 'understand', 'tutorial'],
            'general': ['help', 'question', 'what', 'how', 'why', 'where', 'when']
        }
        
    def _initialize_knowledge_base(self):
        """Initialize knowledge base for various topics"""
        return {
            'greetings': [
                "Hello! I'm your multi-task AI assistant. I can help with conversations, problem-solving, and file analysis.",
                "Hi there! Ready to assist with any task - from answering questions to analyzing files.",
                "Hey! I'm here to help with various tasks including math, writing, coding, analysis, and more.",
                "Welcome! I can handle multiple types of requests - feel free to ask anything or upload files."
            ],
            'capabilities': [
                "I can solve math problems, help with programming, assist with writing, analyze files, and much more!",
                "My abilities include mathematical calculations, code debugging, content creation, file analysis, and general problem-solving.",
                "I handle diverse tasks: computational problems, creative writing, technical analysis, file processing, and educational support.",
                "I'm equipped for multi-tasking: from solving equations to analyzing documents, coding help to creative brainstorming."
            ]
        }
    
    def get_response(self, user_message, file_analysis_results=None, chat_history=None):
        """Generate intelligent response based on task type and context"""
        
        # Store conversation context
        self.conversation_memory.append(user_message.lower())
        if len(self.conversation_memory) > 15:
            self.conversation_memory.pop(0)
        
        user_lower = user_message.lower()
        
        # Handle file analysis
        if file_analysis_results:
            return self._handle_file_analysis_task(user_message, file_analysis_results)
        
        # Determine task category
        task_category = self._identify_task_category(user_lower)
        
        # Route to appropriate handler
        if task_category == 'math':
            return self._handle_math_task(user_message)
        elif task_category == 'programming':
            return self._handle_programming_task(user_message)
        elif task_category == 'writing':
            return self._handle_writing_task(user_message)
        elif task_category == 'analysis':
            return self._handle_analysis_task(user_message)
        elif task_category == 'creative':
            return self._handle_creative_task(user_message)
        elif task_category == 'business':
            return self._handle_business_task(user_message)
        elif task_category == 'education':
            return self._handle_education_task(user_message)
        elif self._is_greeting(user_lower):
            return random.choice(self.knowledge_base['greetings'])
        elif self._is_asking_capabilities(user_lower):
            return random.choice(self.knowledge_base['capabilities'])
        else:
            return self._handle_general_conversation(user_message)
    
    def _identify_task_category(self, text):
        """Identify the type of task based on keywords"""
        for category, keywords in self.task_categories.items():
            if any(keyword in text for keyword in keywords):
                return category
        return 'general'
    
    def _is_greeting(self, text):
        greetings = ['hello', 'hi', 'hey', 'good morning', 'good afternoon', 'good evening']
        return any(greeting in text for greeting in greetings)
    
    def _is_asking_capabilities(self, text):
        capability_phrases = ['what can you do', 'capabilities', 'what are you', 'help me with']
        return any(phrase in text for phrase in capability_phrases)
    
    def _handle_math_task(self, user_message):
        """Handle mathematical problems and calculations"""
        user_lower = user_message.lower()
        
        # Extract numbers from the message
        numbers = re.findall(r'-?\d+\.?\d*', user_message)
        
        if 'calculate' in user_lower or 'solve' in user_lower:
            if '+' in user_message and len(numbers) >= 2:
                result = sum(float(n) for n in numbers)
                return f"Calculating the sum: {' + '.join(numbers)} = {result}"
            
            elif '-' in user_message and len(numbers) >= 2:
                result = float(numbers[0]) - float(numbers[1])
                return f"Calculating the difference: {numbers[0]} - {numbers[1]} = {result}"
            
            elif '*' in user_message or 'multiply' in user_lower:
                if len(numbers) >= 2:
                    result = float(numbers[0]) * float(numbers[1])
                    return f"Calculating the product: {numbers[0]} × {numbers[1]} = {result}"
            
            elif '/' in user_message or 'divide' in user_lower:
                if len(numbers) >= 2 and float(numbers[1]) != 0:
                    result = float(numbers[0]) / float(numbers[1])
                    return f"Calculating the division: {numbers[0]} ÷ {numbers[1]} = {result:.2f}"
        
        elif 'square root' in user_lower or 'sqrt' in user_lower:
            if numbers:
                num = float(numbers[0])
                if num >= 0:
                    result = math.sqrt(num)
                    return f"Square root of {num} = {result:.2f}"
        
        elif 'power' in user_lower or '**' in user_message or '^' in user_message:
            if len(numbers) >= 2:
                base = float(numbers[0])
                exponent = float(numbers[1])
                result = base ** exponent
                return f"{base} to the power of {exponent} = {result}"
        
        elif 'percentage' in user_lower or '%' in user_message:
            if len(numbers) >= 2:
                value = float(numbers[0])
                total = float(numbers[1])
                percentage = (value / total) * 100
                return f"{value} is {percentage:.1f}% of {total}"
        
        return ("I can help with various math operations! Try asking me to:\n"
                "- Calculate additions, subtractions, multiplications, divisions\n"
                "- Find square roots or powers\n"
                "- Calculate percentages\n"
                "- Solve basic equations\n\n"
                f"For your query '{user_message}', please specify the operation more clearly.")
    
    def _handle_programming_task(self, user_message):
        """Handle programming-related questions and tasks"""
        user_lower = user_message.lower()
        
        if 'python' in user_lower:
            if 'function' in user_lower:
                return ("Here's a basic Python function template:\n\n"
                        "```python\n"
                        "def my_function(parameter):\n"
                        "    # Your code here\n"
                        "    result = parameter * 2\n"
                        "    return result\n"
                        "```\n\n"
                        "Functions help organize code into reusable blocks. What specific function do you need help with?")
            
            elif 'loop' in user_lower:
                return ("Python loop examples:\n\n"
                        "**For loop:**\n"
                        "```python\n"
                        "for i in range(5):\n"
                        "    print(i)\n"
                        "```\n\n"
                        "**While loop:**\n"
                        "```python\n"
                        "count = 0\n"
                        "while count < 5:\n"
                        "    print(count)\n"
                        "    count += 1\n"
                        "```")
            
            elif 'list' in user_lower:
                return ("Python list operations:\n\n"
                        "```python\n"
                        "# Create a list\n"
                        "my_list = [1, 2, 3, 4, 5]\n\n"
                        "# Add items\n"
                        "my_list.append(6)\n\n"
                        "# Access items\n"
                        "first_item = my_list[0]\n\n"
                        "# Iterate through list\n"
                        "for item in my_list:\n"
                        "    print(item)\n"
                        "```")
        
        elif 'javascript' in user_lower or 'js' in user_lower:
            return ("JavaScript basics:\n\n"
                    "```javascript\n"
                    "// Variables\n"
                    "let name = 'John';\n"
                    "const age = 25;\n\n"
                    "// Function\n"
                    "function greet(name) {\n"
                    "    return `Hello, ${name}!`;\n"
                    "}\n\n"
                    "// Array\n"
                    "const numbers = [1, 2, 3, 4, 5];\n"
                    "```\n\n"
                    "What specific JavaScript concept do you need help with?")
        
        elif 'html' in user_lower:
            return ("Basic HTML structure:\n\n"
                    "```html\n"
                    "<!DOCTYPE html>\n"
                    "<html>\n"
                    "<head>\n"
                    "    <title>Page Title</title>\n"
                    "</head>\n"
                    "<body>\n"
                    "    <h1>Heading</h1>\n"
                    "    <p>Paragraph text</p>\n"
                    "    <a href='#'>Link</a>\n"
                    "</body>\n"
                    "</html>\n"
                    "```")
        
        elif 'css' in user_lower:
            return ("CSS styling basics:\n\n"
                    "```css\n"
                    "/* Selector and properties */\n"
                    "h1 {\n"
                    "    color: blue;\n"
                    "    font-size: 24px;\n"
                    "    margin: 10px;\n"
                    "}\n\n"
                    ".class-name {\n"
                    "    background-color: #f0f0f0;\n"
                    "    padding: 15px;\n"
                    "}\n\n"
                    "#id-name {\n"
                    "    border: 1px solid black;\n"
                    "}\n"
                    "```")
        
        return ("I can help with programming in various languages:\n"
                "- Python (functions, loops, data structures)\n"
                "- JavaScript (ES6, DOM manipulation, async)\n"
                "- HTML (structure, elements, forms)\n"
                "- CSS (styling, layouts, responsive design)\n"
                "- General programming concepts\n\n"
                f"What specific programming help do you need for: '{user_message}'?")
    
    def _handle_writing_task(self, user_message):
        """Handle writing and content creation tasks"""
        user_lower = user_message.lower()
        
        if 'email' in user_lower:
            return ("Professional email template:\n\n"
                    "**Subject:** [Clear, specific subject line]\n\n"
                    "Dear [Recipient's name],\n\n"
                    "I hope this email finds you well. I am writing to [state purpose].\n\n"
                    "[Main content - be clear and concise]\n\n"
                    "Thank you for your time and consideration. I look forward to hearing from you.\n\n"
                    "Best regards,\n"
                    "[Your name]\n\n"
                    "What type of email are you writing? I can help customize it.")
        
        elif 'essay' in user_lower:
            return ("Essay structure guide:\n\n"
                    "**Introduction (1 paragraph):**\n"
                    "- Hook to grab attention\n"
                    "- Background information\n"
                    "- Clear thesis statement\n\n"
                    "**Body (2-3 paragraphs):**\n"
                    "- Topic sentence for each paragraph\n"
                    "- Supporting evidence and examples\n"
                    "- Analysis and explanation\n\n"
                    "**Conclusion (1 paragraph):**\n"
                    "- Restate thesis\n"
                    "- Summarize main points\n"
                    "- End with impact statement\n\n"
                    "What's your essay topic? I can help you develop it.")
        
        elif 'story' in user_lower:
            return ("Creative story elements:\n\n"
                    "**Plot Structure:**\n"
                    "1. Exposition (introduce characters/setting)\n"
                    "2. Rising action (build conflict)\n"
                    "3. Climax (turning point)\n"
                    "4. Falling action (resolve conflict)\n"
                    "5. Resolution (conclusion)\n\n"
                    "**Key Elements:**\n"
                    "- Compelling characters with clear motivations\n"
                    "- Vivid setting descriptions\n"
                    "- Engaging dialogue\n"
                    "- Show, don't tell\n\n"
                    "What genre or theme are you exploring?")
        
        elif 'letter' in user_lower:
            return ("Formal letter format:\n\n"
                    "[Your address]\n"
                    "[Date]\n\n"
                    "[Recipient's address]\n\n"
                    "Dear [Title] [Last name],\n\n"
                    "[Opening paragraph - state purpose]\n\n"
                    "[Body paragraphs - provide details]\n\n"
                    "[Closing paragraph - summarize and next steps]\n\n"
                    "Sincerely,\n"
                    "[Your signature]\n"
                    "[Your printed name]\n\n"
                    "What type of formal letter are you writing?")
        
        return ("I can assist with various writing tasks:\n"
                "- Professional emails and letters\n"
                "- Academic essays and papers\n"
                "- Creative stories and content\n"
                "- Business proposals and reports\n"
                "- Social media content\n\n"
                f"What specific writing help do you need for: '{user_message}'?")
    
    def _handle_creative_task(self, user_message):
        """Handle creative and brainstorming tasks"""
        user_lower = user_message.lower()
        
        if 'brainstorm' in user_lower or 'idea' in user_lower:
            return ("Creative brainstorming techniques:\n\n"
                    "**Mind Mapping:**\n"
                    "- Start with central concept\n"
                    "- Branch out with related ideas\n"
                    "- Connect different branches\n\n"
                    "**SCAMPER Method:**\n"
                    "- Substitute: What can be substituted?\n"
                    "- Combine: What can be combined?\n"
                    "- Adapt: What can be adapted?\n"
                    "- Modify: What can be modified?\n"
                    "- Put to other uses\n"
                    "- Eliminate: What can be removed?\n"
                    "- Reverse: What can be rearranged?\n\n"
                    "What topic are you brainstorming about?")
        
        elif 'design' in user_lower:
            return ("Design principles:\n\n"
                    "**Visual Design:**\n"
                    "- Balance: Distribute elements evenly\n"
                    "- Contrast: Create visual interest\n"
                    "- Emphasis: Highlight important elements\n"
                    "- Unity: Create cohesive appearance\n\n"
                    "**Color Theory:**\n"
                    "- Primary colors: Red, Blue, Yellow\n"
                    "- Complementary: Opposite colors\n"
                    "- Analogous: Adjacent colors\n"
                    "- Monochromatic: Shades of one color\n\n"
                    "What type of design project are you working on?")
        
        return ("Creative assistance available:\n"
                "- Brainstorming and idea generation\n"
                "- Design concepts and principles\n"
                "- Creative writing prompts\n"
                "- Problem-solving approaches\n"
                "- Innovation techniques\n\n"
                f"What creative challenge can I help you with: '{user_message}'?")
    
    def _handle_business_task(self, user_message):
        """Handle business-related queries"""
        user_lower = user_message.lower()
        
        if 'plan' in user_lower:
            return ("Business plan structure:\n\n"
                    "1. **Executive Summary**\n"
                    "2. **Company Description**\n"
                    "3. **Market Analysis**\n"
                    "4. **Organization & Management**\n"
                    "5. **Products/Services**\n"
                    "6. **Marketing & Sales Strategy**\n"
                    "7. **Financial Projections**\n"
                    "8. **Funding Requirements**\n\n"
                    "What type of business are you planning?")
        
        elif 'strategy' in user_lower:
            return ("Strategic planning framework:\n\n"
                    "**SWOT Analysis:**\n"
                    "- Strengths: Internal positive factors\n"
                    "- Weaknesses: Internal negative factors\n"
                    "- Opportunities: External positive factors\n"
                    "- Threats: External negative factors\n\n"
                    "**Strategic Goals:**\n"
                    "- Specific and measurable\n"
                    "- Achievable and realistic\n"
                    "- Time-bound\n\n"
                    "What strategic challenge are you addressing?")
        
        return ("Business assistance available:\n"
                "- Business planning and strategy\n"
                "- Market analysis techniques\n"
                "- Financial planning basics\n"
                "- Marketing strategies\n"
                "- Project management\n\n"
                f"What business topic can I help with: '{user_message}'?")
    
    def _handle_education_task(self, user_message):
        """Handle educational and learning requests"""
        return ("Learning assistance:\n"
                "- Concept explanations\n"
                "- Study techniques\n"
                "- Research methods\n"
                "- Academic writing\n"
                "- Problem-solving strategies\n\n"
                f"What educational topic would you like help with: '{user_message}'?")
    
    def _handle_analysis_task(self, user_message):
        """Handle analytical requests"""
        return ("I can help analyze:\n"
                "- Data patterns and trends\n"
                "- Text content and structure\n"
                "- Problem decomposition\n"
                "- Comparative analysis\n"
                "- Decision-making frameworks\n\n"
                f"What would you like me to analyze: '{user_message}'?")
    
    def _handle_file_analysis_task(self, user_message, file_analysis_results):
        """Handle file analysis with contextual conversation"""
        response = f"I've analyzed {len(file_analysis_results)} file(s) for you:\n\n"
        
        for i, result in enumerate(file_analysis_results, 1):
            response += f"**File {i}: {result['filename']}**\n"
            response += f"- Type: {result['file_type']}\n"
            response += f"- Size: {result['size'] / 1024:.1f} KB\n\n"
            
            if result['analysis']:
                response += f"**Analysis:**\n{result['analysis']}\n\n"
        
        # Add contextual response based on user's question
        user_lower = user_message.lower()
        if 'summarize' in user_lower:
            response += "**Summary:** The files have been processed and key information extracted."
        elif 'explain' in user_lower:
            response += "**Explanation:** Each file was analyzed for structure, content, and technical specifications."
        elif any(word in user_lower for word in ['problem', 'issue', 'error']):
            response += "**Analysis:** I've examined the files for potential issues and structural problems."
        
        return response
    
    def _handle_general_conversation(self, user_message):
        """Handle general conversational queries"""
        responses = [
            f"That's an interesting question about '{user_message[:50]}...'. I can help with math, programming, writing, analysis, and file processing. What specific task can I assist you with?",
            f"I understand you're asking about '{user_message[:40]}...'. I'm equipped to handle various tasks including calculations, coding help, content creation, and file analysis.",
            f"Regarding '{user_message[:45]}...', I can provide assistance with multiple types of tasks. Would you like help with problem-solving, creative work, or technical analysis?",
            "I'm a multi-task assistant ready to help with diverse challenges. Whether it's math problems, writing tasks, code debugging, or file analysis - I'm here to assist!"
        ]
        return random.choice(responses)

# =============================================================================
# FILE PROCESSOR CLASS
# =============================================================================

class FileProcessor:
    """Enhanced file processor for comprehensive analysis"""
    
    def __init__(self):
        self.supported_types = {
            'image': ['image/jpeg', 'image/png', 'image/gif', 'image/bmp', 'image/webp'],
            'text': ['text/plain', 'text/csv', 'text/markdown'],
            'pdf': ['application/pdf'],
            'code': ['text/python', 'text/javascript', 'text/html', 'text/css']
        }
    
    def detect_file_type(self, file_bytes):
        """Enhanced file type detection"""
        try:
            mime_type = magic.from_buffer(file_bytes, mime=True)
            return mime_type
        except:
            # Enhanced fallback detection
            if file_bytes.startswith(b'%PDF'):
                return 'application/pdf'
            elif file_bytes.startswith(b'\xff\xd8\xff'):
                return 'image/jpeg'
            elif file_bytes.startswith(b'\x89PNG'):
                return 'image/png'
            elif file_bytes.startswith(b'GIF8'):
                return 'image/gif'
            else:
                return 'text/plain'
    
    def process_file(self, uploaded_file):
        """Enhanced file processing with multiple analysis types"""
        file_bytes = uploaded_file.read()
        uploaded_file.seek(0)
        
        mime_type = self.detect_file_type(file_bytes)
        
        analysis_result = {
            'filename': uploaded_file.name,
            'file_type': mime_type,
            'size': len(file_bytes),
            'analysis': '',
            'base64_data': None,
            'metadata': {}
        }
        
        try:
            if any(mime_type in types for types in self.supported_types['image']):
                analysis_result['analysis'] = self._analyze_image(file_bytes)
                analysis_result['base64_data'] = base64.b64encode(file_bytes).decode('utf-8')
                
            elif any(mime_type in types for types in self.supported_types['pdf']):
                analysis_result['analysis'] = self._analyze_pdf(file_bytes)
                
            elif any(mime_type in types for types in self.supported_types['text']):
                analysis_result['analysis'] = self._analyze_text(file_bytes)
                
            else:
                analysis_result['analysis'] = self._analyze_unknown(file_bytes, mime_type)
                
        except Exception as e:
            analysis_result['analysis'] = f"Error during analysis: {str(e)}"
        
        return analysis_result
    
    def _analyze_image(self, file_bytes):
        """Comprehensive image analysis"""
        try:
            image = Image.open(io.BytesIO(file_bytes))
            
            analysis = "**Comprehensive Image Analysis**\n\n"
            analysis += f"**Technical Specifications:**\n"
            analysis += f"• Dimensions: {image.width} × {image.height} pixels\n"
            analysis += f"• Format: {image.format}\n"
            analysis += f"• Color Mode: {image.mode}\n"
            analysis += f"• File Size: {len(file_bytes) / 1024:.1f} KB\n"
            analysis += f"• Aspect Ratio: {image.width/image.height:.2f}:1\n\n"
            
            # Advanced analysis
            total_pixels = image.width * image.height
            analysis += f"**Image Metrics:**\n"
            analysis += f"• Total Pixels: {total_pixels:,}\n"
            analysis += f"• Pixel Density: {total_pixels / (len(file_bytes) / 1024):.0f} pixels/KB\n"
            
            if image.mode in ['RGB', 'RGBA']:
                analysis += f"• Color Channels: {len(image.mode)}\n"
                if hasattr(image, 'getcolors'):
                    colors = image.getcolors(maxcolors=256*256*256)
                    if colors:
                        analysis += f"• Unique Colors: {len(colors)}\n"
            
            # Quality assessment
            if total_pixels > 4000000:
                quality = "Ultra High Resolution (4K+)"
            elif total_pixels > 2000000:
                quality = "High Resolution (2K+)"
            elif total_pixels > 500000:
                quality = "Standard Resolution"
            else:
                quality = "Low Resolution"
            
            analysis += f"• Quality Category: {quality}\n"
            
            return analysis
            
        except Exception as e:
            return f"Image analysis error: {str(e)}"
    
    def _analyze_pdf(self, file_bytes):
        """Comprehensive PDF analysis"""
        try:
            pdf_reader = PyPDF2.PdfReader(io.BytesIO(file_bytes))
            
            num_pages = len(pdf_reader.pages)
            analysis = "**Comprehensive PDF Analysis**\n\n"
            analysis += f"**Document Structure:**\n"
            analysis += f"• Total Pages: {num_pages}\n"
            analysis += f"• File Size: {len(file_bytes) / 1024:.1f} KB\n"
            analysis += f"• Average Page Size: {(len(file_bytes) / 1024) / num_pages:.1f} KB\n\n"
            
            # Text extraction and analysis
            total_text = ""
            readable_pages = 0
            
            for page_num in range(min(10, num_pages)):
                try:
                    page = pdf_reader.pages[page_num]
                    page_text = page.extract_text()
                    if page_text.strip():
                        total_text += page_text + "\n"
                        readable_pages += 1
                except:
                    continue
            
            if total_text.strip():
                words = total_text.split()
                word_count = len(words)
                char_count = len(total_text)
                
                analysis += f"**Content Analysis:**\n"
                analysis += f"• Readable Pages: {readable_pages}/{num_pages}\n"
                analysis += f"• Total Words: {word_count:,}\n"
                analysis += f"• Total Characters: {char_count:,}\n"
                analysis += f"• Average Words per Page: {word_count//readable_pages if readable_pages > 0 else 0}\n"
                analysis += f"• Reading Time: ~{word_count//200} minutes\n\n"
                
                # Content preview
                preview = total_text[:400] + "..." if len(total_text) > 400 else total_text
                analysis += f"**Content Preview:**\n```\n{preview}\n```\n"
            else:
                analysis += "**Content Status:** No extractable text found (may be image-based)\n"
            
            return analysis
            
        except Exception as e:
            return f"PDF analysis error: {str(e)}"
    
    def _analyze_text(self, file_bytes):
        """Comprehensive text analysis"""
        try:
            # Encoding detection
            encoding_info = chardet.detect(file_bytes)
            encoding = encoding_info.get('encoding', 'utf-8')
            confidence = encoding_info.get('confidence', 0)
            
            text_content = file_bytes.decode(encoding, errors='ignore')
            
            # Comprehensive statistics
            words = text_content.split()
            lines = text_content.splitlines()
            paragraphs = [p for p in text_content.split('\n\n') if p.strip()]
            
            analysis = "**Comprehensive Text Analysis**\n\n"
            analysis += f"**File Properties:**\n"
            analysis += f"• Encoding: {encoding} (confidence: {confidence:.1%})\n"
            analysis += f"• File Size: {len(file_bytes) / 1024:.1f} KB\n\n"
            
            analysis += f"**Content Structure:**\n"
            analysis += f"• Total Characters: {len(text_content):,}\n"
            analysis += f"• Total Words: {len(words):,}\n"
            analysis += f"• Total Lines: {len(lines):,}\n"
            analysis += f"• Paragraphs: {len(paragraphs):,}\n"
            analysis += f"• Average Words per Line: {len(words)/len(lines):.1f}\n"
            analysis += f"• Average Words per Paragraph: {len(words)/len(paragraphs):.1f}\n\n"
            
            # Reading metrics
            reading_time = len(words) / 200  # Average reading speed
            analysis += f"**Reading Metrics:**\n"
            analysis += f"• Estimated Reading Time: {reading_time:.1f} minutes\n"
            analysis += f"• Character Density: {len(text_content.replace(' ', '')) / len(words):.1f} chars/word\n\n"
            
            # Content preview
            preview = text_content[:300] + "..." if len(text_content) > 300 else text_content
            analysis += f"**Content Preview:**\n```\n{preview}\n```"
            
            return analysis
            
        except Exception as e:
            return f"Text analysis error: {str(e)}"
    
    def _analyze_unknown(self, file_bytes, mime_type):
        """Analysis for unknown file types"""
        return (f"**File Type Analysis**\n\n"
                f"• Detected Type: {mime_type}\n"
                f"• File Size: {len(file_bytes) / 1024:.1f} KB\n"
                f"• Binary Data: {len(file_bytes)} bytes\n\n"
                f"This file type is not fully supported for content analysis, "
                f"but basic properties have been extracted.")

# =============================================================================
# UI FUNCTIONS
# =============================================================================

def render_header():
    """Render the main header"""
    st.markdown("""
    <div class="main-header">
        <h1>AI Multi-Task Assistant</h1>
        <p>Conversations, Problem Solving & File Analysis</p>
    </div>
    """, unsafe_allow_html=True)

def render_sidebar_features():
    """Render sidebar with capabilities"""
    st.sidebar.markdown("### Capabilities")
    
    capabilities = [
        ("Mathematics", "Solve equations, calculations, formulas"),
        ("Programming", "Code help, debugging, examples"),
        ("Writing", "Essays, emails, creative content"),
        ("Analysis", "Data analysis, problem-solving"),
        ("Creative", "Brainstorming, design concepts"),
        ("Business", "Plans, strategies, reports"),
        ("Education", "Learning, explanations, tutorials"),
        ("Files", "Image, PDF, text analysis")
    ]
    
    for title, desc in capabilities:
        st.sidebar.markdown(f"""
        <div class="capability-card">
            <strong>{title}</strong><br>
            <small>{desc}</small>
        </div>
        """, unsafe_allow_html=True)

def render_sidebar_stats():
    """Render session statistics"""
    st.sidebar.markdown("### Session Stats")
    
    total_messages = len(st.session_state.messages)
    user_messages = sum(1 for msg in st.session_state.messages if msg["role"] == "user")
    files_processed = len(st.session_state.get('uploaded_files', []))
    
    col1, col2 = st.sidebar.columns(2)
    with col1:
        st.metric("Messages", total_messages)
        st.metric("Files", files_processed)
    with col2:
        st.metric("Questions", user_messages)
        st.metric("Responses", total_messages - user_messages)

def render_file_upload():
    """Render file upload section"""
    st.sidebar.markdown("### File Upload")
    
    uploaded_files = st.sidebar.file_uploader(
        "Upload files for analysis",
        type=['txt', 'pdf', 'png', 'jpg', 'jpeg', 'gif', 'bmp', 'csv', 'md', 'py', 'js', 'html', 'css'],
        accept_multiple_files=True,
        help="Support for images, documents, code files"
    )
    
    return uploaded_files

def render_quick_actions():
    """Render quick action buttons"""
    st.sidebar.markdown("### Quick Actions")
    
    col1, col2 = st.sidebar.columns(2)
    with col1:
        if st.button("Math Help", use_container_width=True):
            st.session_state.quick_prompt = "help me solve a math problem"
        if st.button("Code Help", use_container_width=True):
            st.session_state.quick_prompt = "help me with programming"
    
    with col2:
        if st.button("Writing", use_container_width=True):
            st.session_state.quick_prompt = "help me write something"
        if st.button("Creative", use_container_width=True):
            st.session_state.quick_prompt = "help me brainstorm ideas"

def render_chat_controls():
    """Render chat control buttons"""
    st.sidebar.markdown("### Controls")
    
    col1, col2 = st.sidebar.columns(2)
    with col1:
        if st.button("Clear Chat", use_container_width=True):
            st.session_state.messages = []
            st.session_state.uploaded_files = []
            st.rerun()
    
    with col2:
        if st.button("Export", use_container_width=True):
            if st.session_state.messages:
                chat_data = {
                    "timestamp": datetime.now().isoformat(),
                    "messages": st.session_state.messages
                }
                json_data = json.dumps(chat_data, indent=2)
                st.sidebar.download_button(
                    "Download Chat",
                    json_data,
                    f"chat_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json",
                    "application/json"
                )

# =============================================================================
# MAIN APPLICATION
# =============================================================================

@st.cache_resource
def init_assistants():
    """Initialize AI assistant and file processor"""
    ai_assistant = MultiTaskAI()
    file_processor = FileProcessor()
    return ai_assistant, file_processor

def main():
    """Main application function"""
    load_css()
    
    # Initialize assistants
    ai_assistant, file_processor = init_assistants()
    
    # Initialize session state
    if 'messages' not in st.session_state:
        st.session_state.messages = []
    if 'uploaded_files' not in st.session_state:
        st.session_state.uploaded_files = []
    
    # Render header
    render_header()
    
    # Sidebar
    with st.sidebar:
        render_sidebar_features()
        uploaded_files = render_file_upload()
        render_quick_actions()
        render_chat_controls()
        render_sidebar_stats()
    
    # Main chat interface
    st.markdown('<div class="chat-container">', unsafe_allow_html=True)
    
    # Welcome message
    if not st.session_state.messages:
        st.markdown("""
        <div class="ai-message">
            <h3>Welcome to your AI Multi-Task Assistant!</h3>
            <p>I can help you with:</p>
            <ul>
                <li>Mathematical calculations and problem-solving</li>
                <li>Programming assistance and code examples</li>
                <li>Writing support and content creation</li>
                <li>Creative brainstorming and design concepts</li>
                <li>Business planning and analysis</li>
                <li>File analysis and document processing</li>
            </ul>
            <p>Ask me anything or upload files for analysis!</p>
        </div>
        """, unsafe_allow_html=True)
    
    # Display chat history
    for message in st.session_state.messages:
        with st.chat_message(message["role"]):
            st.write(message["content"])
            if "files" in message and message["files"]:
                st.caption("Files: " + ", ".join([f['name'] for f in message["files"]]))
    
    st.markdown('</div>', unsafe_allow_html=True)
    
    # Handle quick prompts
    if hasattr(st.session_state, 'quick_prompt'):
        prompt = st.session_state.quick_prompt
        del st.session_state.quick_prompt
        st.rerun()
    
    # Chat input
    if prompt := st.chat_input("Ask me anything or upload files for analysis..."):
        # Process uploaded files
        file_analysis_results = []
        current_files = []
        
        if uploaded_files:
            with st.spinner("Analyzing uploaded files..."):
                progress_bar = st.progress(0)
                for i, uploaded_file in enumerate(uploaded_files):
                    try:
                        progress_bar.progress((i + 1) / len(uploaded_files))
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
        
        # Add user message
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
            if current_files:
                st.caption("Files: " + ", ".join([f['name'] for f in current_files]))
        
        # Generate AI response
        with st.chat_message("assistant"):
            with st.spinner("Processing your request..."):
                try:
                    response = ai_assistant.get_response(
                        prompt,
                        file_analysis_results,
                        st.session_state.messages[:-1]
                    )
                    
                    st.write(response)
                    
                    # Add assistant response
                    assistant_message = {
                        "role": "assistant",
                        "content": response,
                        "timestamp": datetime.now().strftime("%H:%M:%S")
                    }
                    st.session_state.messages.append(assistant_message)
                    
                except Exception as e:
                    error_msg = f"I encountered an error: {str(e)}"
                    st.error(error_msg)
                    
                    error_message = {
                        "role": "assistant",
                        "content": error_msg,
                        "timestamp": datetime.now().strftime("%H:%M:%S")
                    }
                    st.session_state.messages.append(error_message)
        
        # Update session state
        st.session_state.uploaded_files = current_files
        st.rerun()

if __name__ == "__main__":
    main()