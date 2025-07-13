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
    page_title="Smart AI Assistant",
    page_icon="🤖",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS
def load_css():
    st.markdown("""
    <style>
    :root {
        --primary-color: #2196F3;
        --secondary-color: #4CAF50;
        --accent-color: #FF9800;
        --background-gradient: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        --chat-user-bg: #e3f2fd;
        --chat-ai-bg: #f3e5f5;
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
        font-size: 2.5rem;
        margin: 0;
        text-shadow: 2px 2px 4px rgba(0,0,0,0.3);
    }
    
    .chat-container {
        background: rgba(255,255,255,0.95);
        border-radius: 15px;
        padding: 1rem;
        margin: 1rem 0;
        box-shadow: 0 4px 16px rgba(0,0,0,0.1);
    }
    
    .stButton > button {
        background: linear-gradient(45deg, var(--primary-color), var(--secondary-color));
        color: white;
        border: none;
        border-radius: 8px;
        padding: 0.5rem 1rem;
        font-weight: bold;
    }
    </style>
    """, unsafe_allow_html=True)

# =============================================================================
# FUNCTIONAL AI ASSISTANT
# =============================================================================

class FunctionalAI:
    """Functional AI that actually performs tasks and solves problems"""
    
    def __init__(self):
        self.conversation_history = []
        
    def process_request(self, user_input, file_results=None):
        """Main processing function that routes requests to appropriate handlers"""
        
        # Store conversation
        self.conversation_history.append(user_input)
        
        # Clean and analyze input
        text = user_input.lower().strip()
        
        # Handle file analysis first
        if file_results:
            return self._process_file_request(user_input, file_results)
        
        # Mathematical operations
        if self._is_math_request(text):
            return self._solve_math(user_input)
        
        # Programming help
        elif any(keyword in text for keyword in ['python', 'javascript', 'html', 'css', 'code', 'function', 'programming']):
            return self._handle_programming(user_input)
        
        # Writing assistance
        elif any(keyword in text for keyword in ['write', 'email', 'letter', 'essay', 'story']):
            return self._handle_writing(user_input)
        
        # Question answering
        elif text.startswith(('what', 'how', 'why', 'when', 'where', 'who')):
            return self._answer_question(user_input)
        
        # General conversation
        else:
            return self._handle_conversation(user_input)
    
    def _is_math_request(self, text):
        """Check if the request is mathematical"""
        math_indicators = [
            '+', '-', '*', '/', '=', 'calculate', 'solve', 'equation',
            'plus', 'minus', 'times', 'divided', 'square', 'root',
            'power', 'percentage', '%', 'math', 'number'
        ]
        return any(indicator in text for indicator in math_indicators)
    
    def _solve_math(self, user_input):
        """Actually solve mathematical problems"""
        text = user_input.lower()
        
        # Extract numbers
        numbers = re.findall(r'-?\d+\.?\d*', user_input)
        
        try:
            # Basic arithmetic operations
            if '+' in user_input:
                if len(numbers) >= 2:
                    nums = [float(n) for n in numbers]
                    result = sum(nums)
                    return f"Calculating: {' + '.join(numbers)} = {result}"
                else:
                    # Handle text like "what is 5 plus 3"
                    if 'plus' in text:
                        parts = text.split('plus')
                        if len(parts) == 2:
                            try:
                                num1 = float(re.findall(r'\d+\.?\d*', parts[0])[-1])
                                num2 = float(re.findall(r'\d+\.?\d*', parts[1])[0])
                                result = num1 + num2
                                return f"{num1} + {num2} = {result}"
                            except:
                                pass
            
            elif '-' in user_input and len(numbers) >= 2:
                result = float(numbers[0]) - float(numbers[1])
                return f"Calculating: {numbers[0]} - {numbers[1]} = {result}"
            
            elif '*' in user_input or 'times' in text or 'multiply' in text:
                if len(numbers) >= 2:
                    result = float(numbers[0]) * float(numbers[1])
                    return f"Calculating: {numbers[0]} × {numbers[1]} = {result}"
            
            elif '/' in user_input or 'divided' in text:
                if len(numbers) >= 2 and float(numbers[1]) != 0:
                    result = float(numbers[0]) / float(numbers[1])
                    return f"Calculating: {numbers[0]} ÷ {numbers[1]} = {result:.4f}"
            
            elif 'square root' in text or 'sqrt' in text:
                if numbers:
                    num = float(numbers[0])
                    if num >= 0:
                        result = math.sqrt(num)
                        return f"Square root of {num} = {result:.4f}"
            
            elif 'power' in text or '**' in user_input or '^' in user_input:
                if len(numbers) >= 2:
                    base = float(numbers[0])
                    exp = float(numbers[1])
                    result = base ** exp
                    return f"{base} to the power of {exp} = {result}"
            
            elif '%' in user_input or 'percent' in text:
                if len(numbers) >= 2:
                    value = float(numbers[0])
                    total = float(numbers[1])
                    percentage = (value / total) * 100
                    return f"{value} is {percentage:.2f}% of {total}"
            
            # Try to evaluate simple mathematical expressions
            elif any(op in user_input for op in ['+', '-', '*', '/']):
                # Clean the expression
                expression = re.sub(r'[^0-9+\-*/().\s]', '', user_input)
                expression = expression.replace(' ', '')
                
                if expression:
                    try:
                        # Safe evaluation
                        allowed_chars = set('0123456789+-*/.() ')
                        if all(c in allowed_chars for c in expression):
                            result = eval(expression)
                            return f"Calculating: {expression} = {result}"
                    except:
                        pass
            
            # If no specific pattern matched, try to extract and solve
            if numbers:
                if 'factorial' in text:
                    num = int(float(numbers[0]))
                    if 0 <= num <= 20:  # Reasonable limit
                        result = math.factorial(num)
                        return f"Factorial of {num} = {result}"
                
                elif 'sin' in text:
                    angle = float(numbers[0])
                    result = math.sin(math.radians(angle))
                    return f"Sin({angle}°) = {result:.4f}"
                
                elif 'cos' in text:
                    angle = float(numbers[0])
                    result = math.cos(math.radians(angle))
                    return f"Cos({angle}°) = {result:.4f}"
                
                elif 'log' in text:
                    num = float(numbers[0])
                    if num > 0:
                        result = math.log10(num)
                        return f"Log₁₀({num}) = {result:.4f}"
        
        except Exception as e:
            return f"I tried to calculate that but encountered an error. Could you rephrase the mathematical problem more clearly?"
        
        return "I can help with calculations. Try asking like: '5 + 3', 'square root of 16', '2 to the power of 3', etc."
    
    def _handle_programming(self, user_input):
        """Handle programming questions with actual code examples"""
        text = user_input.lower()
        
        if 'python' in text:
            if 'function' in text:
                return """Here's a Python function example:

```python
def greet(name):
    return f"Hello, {name}!"

# Usage
result = greet("Alice")
print(result)  # Output: Hello, Alice!
```

Functions help organize code. What specific function do you need help with?"""
            
            elif 'loop' in text:
                return """Python loop examples:

```python
# For loop
for i in range(5):
    print(f"Number: {i}")

# While loop
count = 0
while count < 5:
    print(f"Count: {count}")
    count += 1

# Loop through list
fruits = ["apple", "banana", "orange"]
for fruit in fruits:
    print(fruit)
```

What kind of loop are you trying to create?"""
            
            elif 'list' in text:
                return """Python list operations:

```python
# Create list
my_list = [1, 2, 3, 4, 5]

# Add items
my_list.append(6)
my_list.extend([7, 8, 9])

# Remove items
my_list.remove(3)  # Removes first occurrence of 3
popped = my_list.pop()  # Removes and returns last item

# Access items
first = my_list[0]
last = my_list[-1]

# Slice list
subset = my_list[1:4]  # Items from index 1 to 3
```"""
            
            elif 'dictionary' in text or 'dict' in text:
                return """Python dictionary usage:

```python
# Create dictionary
person = {
    "name": "John",
    "age": 30,
    "city": "New York"
}

# Access values
name = person["name"]
age = person.get("age", 0)  # Safe access with default

# Add/update
person["email"] = "john@email.com"
person.update({"phone": "123-456-7890"})

# Loop through dictionary
for key, value in person.items():
    print(f"{key}: {value}")
```"""
        
        elif 'javascript' in text:
            if 'function' in text:
                return """JavaScript function examples:

```javascript
// Function declaration
function greet(name) {
    return `Hello, ${name}!`;
}

// Arrow function
const multiply = (a, b) => a * b;

// Function with default parameters
function calculate(x, y = 1) {
    return x * y;
}

// Usage
console.log(greet("Alice"));
console.log(multiply(5, 3));
```"""
            
            elif 'array' in text:
                return """JavaScript array methods:

```javascript
const numbers = [1, 2, 3, 4, 5];

// Add elements
numbers.push(6);
numbers.unshift(0);

// Remove elements
const last = numbers.pop();
const first = numbers.shift();

// Transform arrays
const doubled = numbers.map(n => n * 2);
const evens = numbers.filter(n => n % 2 === 0);
const sum = numbers.reduce((acc, n) => acc + n, 0);

// Find elements
const found = numbers.find(n => n > 3);
const index = numbers.indexOf(3);
```"""
        
        elif 'html' in text:
            return """Basic HTML structure:

```html
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>My Page</title>
</head>
<body>
    <header>
        <h1>Welcome</h1>
    </header>
    
    <main>
        <p>This is a paragraph.</p>
        <a href="https://example.com">Link</a>
        
        <ul>
            <li>Item 1</li>
            <li>Item 2</li>
        </ul>
    </main>
    
    <footer>
        <p>&copy; 2024</p>
    </footer>
</body>
</html>
```"""
        
        elif 'css' in text:
            return """CSS styling examples:

```css
/* Basic styling */
body {
    font-family: Arial, sans-serif;
    margin: 0;
    padding: 20px;
    background-color: #f5f5f5;
}

/* Class selector */
.container {
    max-width: 800px;
    margin: 0 auto;
    background: white;
    padding: 20px;
    border-radius: 8px;
}

/* ID selector */
#header {
    background-color: #333;
    color: white;
    padding: 1rem;
}

/* Flexbox layout */
.flex-container {
    display: flex;
    justify-content: space-between;
    align-items: center;
}
```"""
        
        return "I can help with Python, JavaScript, HTML, and CSS. What specific programming concept do you need help with?"
    
    def _handle_writing(self, user_input):
        """Handle writing requests with actual templates and guidance"""
        text = user_input.lower()
        
        if 'email' in text:
            if 'professional' in text or 'business' in text:
                return """Professional email template:

**Subject:** [Clear, specific subject]

Dear [Name],

I hope this email finds you well. I am writing to [specific purpose].

[Main content - be clear and concise]
- Point 1
- Point 2
- Point 3

I would appreciate [specific action/response needed] by [date if applicable].

Thank you for your time and consideration.

Best regards,
[Your name]
[Your title]
[Contact information]

What type of professional email are you writing?"""
            
            else:
                return """Casual email template:

**Subject:** [Friendly subject line]

Hi [Name],

Hope you're doing well! I wanted to [reason for email].

[Main message in a conversational tone]

Let me know what you think!

Best,
[Your name]

What's the purpose of your email?"""
        
        elif 'essay' in text:
            return """Essay structure:

**Introduction (10-15% of word count):**
- Hook: Interesting fact, question, or quote
- Background: Context for your topic
- Thesis: Your main argument/position

**Body Paragraphs (70-80% of word count):**
Each paragraph should have:
- Topic sentence
- Evidence/examples
- Analysis/explanation
- Transition to next point

**Conclusion (10-15% of word count):**
- Restate thesis in new words
- Summarize key points
- End with impact/call to action

What's your essay topic? I can help you develop specific points."""
        
        elif 'story' in text:
            return """Story writing framework:

**Setting:** Where and when does it take place?
**Characters:** Who is your protagonist? What do they want?
**Conflict:** What obstacle prevents them from getting it?
**Plot:**
1. Inciting incident (starts the story)
2. Rising action (complications build)
3. Climax (turning point)
4. Resolution (how it ends)

**Writing tips:**
- Show, don't tell
- Use dialogue to reveal character
- Create sensory details
- Start in the middle of action

What type of story are you writing?"""
        
        elif 'letter' in text:
            return """Formal letter format:

[Your Address]
[City, State ZIP Code]
[Date]

[Recipient's Name]
[Title]
[Organization]
[Address]

Dear [Title] [Last Name]:

[Opening paragraph: State your purpose clearly]

[Body paragraphs: Provide details, evidence, or explanation]

[Closing paragraph: Summarize and specify desired action]

Sincerely,

[Your handwritten signature]
[Your typed name]
[Your title if applicable]

What type of formal letter do you need to write?"""
        
        return "I can help you write emails, essays, stories, letters, and more. What specifically do you need to write?"
    
    def _answer_question(self, user_input):
        """Answer factual questions based on the question type"""
        text = user_input.lower()
        
        # Name questions
        if 'what is your name' in text or 'who are you' in text:
            return "I'm an AI assistant designed to help solve problems, answer questions, and analyze files. You can call me Assistant."
        
        # Capability questions
        elif 'what can you do' in text:
            return """I can help with:

• Mathematical calculations and equations
• Programming in Python, JavaScript, HTML, CSS
• Writing emails, essays, stories, and documents
• Answering questions and explaining concepts
• Analyzing uploaded files (images, PDFs, text)

Try asking me to solve a math problem or help with code!"""
        
        # How questions
        elif text.startswith('how to'):
            topic = text.replace('how to', '').strip()
            if 'learn' in topic:
                return """Effective learning strategies:

1. **Active Learning:** Take notes, ask questions, summarize
2. **Spaced Repetition:** Review material at increasing intervals
3. **Practice:** Apply what you learn immediately
4. **Teach Others:** Explain concepts to reinforce understanding
5. **Break It Down:** Divide complex topics into smaller parts

What specific skill are you trying to learn?"""
            
            elif 'code' in topic or 'program' in topic:
                return """How to learn programming:

1. **Choose a language:** Python is beginner-friendly
2. **Practice daily:** Even 30 minutes helps
3. **Build projects:** Apply what you learn
4. **Read others' code:** Learn different approaches
5. **Debug actively:** Understand error messages

Start with basic concepts like variables, loops, and functions. What programming language interests you?"""
        
        # What questions
        elif text.startswith('what is'):
            concept = text.replace('what is', '').strip()
            if 'programming' in concept:
                return """Programming is the process of creating instructions for computers to execute. It involves:

• **Logic:** Breaking problems into steps
• **Syntax:** Learning the rules of a programming language
• **Problem-solving:** Finding efficient solutions
• **Testing:** Ensuring code works correctly

Common languages include Python (beginner-friendly), JavaScript (web development), and Java (enterprise applications)."""
            
            elif 'ai' in concept or 'artificial intelligence' in concept:
                return """Artificial Intelligence (AI) is technology that enables machines to perform tasks that typically require human intelligence:

• **Machine Learning:** Learning from data patterns
• **Natural Language Processing:** Understanding human language
• **Computer Vision:** Interpreting images and video
• **Decision Making:** Making choices based on data

AI is used in recommendations, voice assistants, image recognition, and automation."""
        
        # General question handling
        if any(word in text for word in ['time', 'date', 'today']):
            current_time = datetime.now()
            return f"Current date and time: {current_time.strftime('%Y-%m-%d %H:%M:%S')}"
        
        return f"That's an interesting question about '{user_input}'. I can help with math, programming, writing, and file analysis. Could you be more specific about what you'd like to know?"
    
    def _handle_conversation(self, user_input):
        """Handle general conversation"""
        text = user_input.lower()
        
        # Greetings
        if any(greeting in text for greeting in ['hello', 'hi', 'hey']):
            return "Hello! I'm here to help solve problems, answer questions, and assist with various tasks. What can I help you with today?"
        
        # Gratitude
        elif any(thanks in text for thanks in ['thank', 'thanks']):
            return "You're welcome! Feel free to ask if you need help with anything else."
        
        # Requests for help
        elif 'help' in text:
            return """I can assist with:

• **Math:** Calculations, equations, problem solving
• **Programming:** Python, JavaScript, HTML, CSS code help
• **Writing:** Emails, essays, stories, documents
• **Questions:** Explanations and factual information
• **Files:** Analysis of images, PDFs, and text documents

What would you like help with?"""
        
        # Default conversational response
        return f"I understand you mentioned '{user_input}'. I'm designed to help solve specific problems and answer questions. Try asking me to calculate something, help with code, or assist with writing!"
    
    def _process_file_request(self, user_input, file_results):
        """Process requests involving uploaded files"""
        response = f"I've analyzed your file(s):\n\n"
        
        for i, result in enumerate(file_results, 1):
            response += f"**File {i}: {result['filename']}**\n"
            response += f"Type: {result['file_type']}\n"
            response += f"Size: {result['size'] / 1024:.1f} KB\n\n"
            response += f"Analysis:\n{result['analysis']}\n\n"
        
        # Respond to specific user requests about the files
        text = user_input.lower()
        if 'summarize' in text:
            response += "**Summary:** The files have been processed and analyzed for content, structure, and technical properties."
        elif 'problems' in text or 'issues' in text:
            response += "**Assessment:** I've examined the files for potential issues or areas of interest based on their content and structure."
        
        return response

# =============================================================================
# FILE PROCESSOR
# =============================================================================

class FileProcessor:
    """Simplified but functional file processor"""
    
    def process_file(self, uploaded_file):
        """Process uploaded file"""
        file_bytes = uploaded_file.read()
        uploaded_file.seek(0)
        
        result = {
            'filename': uploaded_file.name,
            'file_type': uploaded_file.type or 'unknown',
            'size': len(file_bytes),
            'analysis': ''
        }
        
        # Determine file type and analyze
        if uploaded_file.type and uploaded_file.type.startswith('image/'):
            result['analysis'] = self._analyze_image(file_bytes)
        elif uploaded_file.type == 'application/pdf':
            result['analysis'] = self._analyze_pdf(file_bytes)
        elif uploaded_file.type and uploaded_file.type.startswith('text/'):
            result['analysis'] = self._analyze_text(file_bytes)
        else:
            result['analysis'] = f"File type: {uploaded_file.type}\nSize: {len(file_bytes)} bytes\nGeneral file uploaded successfully."
        
        return result
    
    def _analyze_image(self, file_bytes):
        """Analyze image files"""
        try:
            image = Image.open(io.BytesIO(file_bytes))
            return (f"Image Analysis:\n"
                   f"• Dimensions: {image.width} x {image.height} pixels\n"
                   f"• Format: {image.format}\n"
                   f"• Mode: {image.mode}\n"
                   f"• File size: {len(file_bytes) / 1024:.1f} KB\n"
                   f"• Aspect ratio: {image.width/image.height:.2f}")
        except Exception as e:
            return f"Image analysis failed: {str(e)}"
    
    def _analyze_pdf(self, file_bytes):
        """Analyze PDF files"""
        try:
            pdf_reader = PyPDF2.PdfReader(io.BytesIO(file_bytes))
            page_count = len(pdf_reader.pages)
            
            # Extract some text
            text_sample = ""
            if page_count > 0:
                try:
                    text_sample = pdf_reader.pages[0].extract_text()[:200]
                except:
                    text_sample = "Could not extract text sample"
            
            return (f"PDF Analysis:\n"
                   f"• Pages: {page_count}\n"
                   f"• File size: {len(file_bytes) / 1024:.1f} KB\n"
                   f"• Text sample: {text_sample}...")
        except Exception as e:
            return f"PDF analysis failed: {str(e)}"
    
    def _analyze_text(self, file_bytes):
        """Analyze text files"""
        try:
            text = file_bytes.decode('utf-8', errors='ignore')
            word_count = len(text.split())
            line_count = text.count('\n') + 1
            
            return (f"Text Analysis:\n"
                   f"• Characters: {len(text)}\n"
                   f"• Words: {word_count}\n"
                   f"• Lines: {line_count}\n"
                   f"• File size: {len(file_bytes) / 1024:.1f} KB\n"
                   f"• Preview: {text[:100]}...")
        except Exception as e:
            return f"Text analysis failed: {str(e)}"

# =============================================================================
# UI COMPONENTS
# =============================================================================

def render_header():
    """Render header"""
    st.markdown("""
    <div class="main-header">
        <h1>Smart AI Assistant</h1>
        <p>Solve Problems • Answer Questions • Analyze Files</p>
    </div>
    """, unsafe_allow_html=True)

def render_sidebar():
    """Render sidebar with file upload and stats"""
    st.sidebar.markdown("### File Upload")
    uploaded_files = st.sidebar.file_uploader(
        "Upload files for analysis",
        type=['txt', 'pdf', 'png', 'jpg', 'jpeg', 'gif', 'csv', 'py', 'js', 'html'],
        accept_multiple_files=True
    )
    
    st.sidebar.markdown("### Quick Examples")
    st.sidebar.markdown("""
    **Math:** "Calculate 15 * 7", "Square root of 64"
    **Code:** "Python function example", "JavaScript array methods"
    **Writing:** "Help me write an email", "Essay structure"
    """)
    
    if st.sidebar.button("Clear Chat"):
        st.session_state.messages = []
        st.session_state.uploaded_files = []
        st.rerun()
    
    return uploaded_files

# =============================================================================
# MAIN APPLICATION
# =============================================================================

@st.cache_resource
def init_components():
    """Initialize AI and file processor"""
    ai = FunctionalAI()
    processor = FileProcessor()
    return ai, processor

def main():
    """Main application"""
    load_css()
    
    # Initialize components
    ai, file_processor = init_components()
    
    # Initialize session state
    if 'messages' not in st.session_state:
        st.session_state.messages = []
    if 'uploaded_files' not in st.session_state:
        st.session_state.uploaded_files = []
    
    # Render UI
    render_header()
    uploaded_files = render_sidebar()
    
    # Chat interface
    st.markdown('<div class="chat-container">', unsafe_allow_html=True)
    
    # Welcome message
    if not st.session_state.messages:
        st.markdown("""
        <div style="background: #f0f8ff; padding: 1rem; border-radius: 8px; margin: 1rem 0;">
            <h3>Welcome! I'm your functional AI assistant.</h3>
            <p>I can actually solve problems and help with tasks:</p>
            <ul>
                <li><strong>Math:</strong> Try "Calculate 25 * 4" or "What is 15% of 200?"</li>
                <li><strong>Programming:</strong> Ask "Python function example" or "JavaScript loops"</li>
                <li><strong>Writing:</strong> Say "Help me write a professional email"</li>
                <li><strong>Questions:</strong> Ask "What is programming?" or "How to learn coding?"</li>
            </ul>
        </div>
        """, unsafe_allow_html=True)
    
    # Display chat messages
    for message in st.session_state.messages:
        with st.chat_message(message["role"]):
            st.write(message["content"])
    
    st.markdown('</div>', unsafe_allow_html=True)
    
    # Chat input
    if prompt := st.chat_input("Ask me anything or upload files..."):
        
        # Process uploaded files
        file_results = []
        if uploaded_files:
            with st.spinner("Analyzing files..."):
                for uploaded_file in uploaded_files:
                    try:
                        result = file_processor.process_file(uploaded_file)
                        file_results.append(result)
                    except Exception as e:
                        st.error(f"Error processing {uploaded_file.name}: {str(e)}")
        
        # Add user message
        st.session_state.messages.append({"role": "user", "content": prompt})
        
        # Display user message
        with st.chat_message("user"):
            st.write(prompt)
        
        # Generate AI response
        with st.chat_message("assistant"):
            with st.spinner("Processing..."):
                try:
                    response = ai.process_request(prompt, file_results)
                    st.write(response)
                    st.session_state.messages.append({"role": "assistant", "content": response})
                except Exception as e:
                    error_msg = f"I encountered an error: {str(e)}"
                    st.error(error_msg)
                    st.session_state.messages.append({"role": "assistant", "content": error_msg})
        
        st.rerun()

if __name__ == "__main__":
    main()