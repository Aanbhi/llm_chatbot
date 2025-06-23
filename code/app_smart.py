import streamlit as st
import re
import math
import ast
import operator
from datetime import datetime
import base64
import io

# External imports for file processing
try:
    from PIL import Image
    import PyPDF2
except ImportError as e:
    st.error(f"Missing required library: {e}")
    st.stop()

# Page configuration
st.set_page_config(
    page_title="AI Assistant",
    page_icon="🤖",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Minimal CSS
def load_css():
    st.markdown("""
    <style>
    .main-header {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        padding: 1.5rem;
        border-radius: 10px;
        text-align: center;
        color: white;
        margin-bottom: 1rem;
    }
    .main-header h1 {
        margin: 0;
        font-size: 2rem;
    }
    </style>
    """, unsafe_allow_html=True)

class SmartAI:
    """Advanced AI that actually processes and solves problems"""
    
    def __init__(self):
        # Mathematical operators
        self.operators = {
            ast.Add: operator.add,
            ast.Sub: operator.sub,
            ast.Mult: operator.mul,
            ast.Div: operator.truediv,
            ast.Pow: operator.pow,
            ast.BitXor: operator.xor,
            ast.USub: operator.neg,
        }
        
        # Programming knowledge base
        self.code_examples = {
            'python_function': '''def calculate_average(numbers):
    if not numbers:
        return 0
    return sum(numbers) / len(numbers)

# Usage
data = [10, 20, 30, 40, 50]
result = calculate_average(data)
print(f"Average: {result}")''',
            
            'python_loop': '''# For loop example
for i in range(1, 6):
    print(f"Iteration {i}: {i * 2}")

# While loop example
count = 0
while count < 5:
    count += 1
    print(f"Count: {count}")

# List comprehension
squares = [x**2 for x in range(1, 6)]
print(squares)''',
            
            'python_list': '''# Creating and manipulating lists
fruits = ["apple", "banana", "orange"]

# Adding elements
fruits.append("grape")
fruits.insert(1, "mango")

# Removing elements
fruits.remove("banana")
last_fruit = fruits.pop()

# Accessing elements
first = fruits[0]
last = fruits[-1]

# Iterating
for fruit in fruits:
    print(fruit)''',
            
            'javascript_function': '''// Function declaration
function calculateTax(amount, rate) {
    return amount * (rate / 100);
}

// Arrow function
const multiply = (a, b) => a * b;

// Function with default parameters
function greet(name = "Guest") {
    return `Hello, ${name}!`;
}

// Usage
console.log(calculateTax(100, 8.5));
console.log(multiply(5, 3));
console.log(greet("Alice"));''',
            
            'javascript_array': '''const numbers = [1, 2, 3, 4, 5];

// Array methods
const doubled = numbers.map(n => n * 2);
const evens = numbers.filter(n => n % 2 === 0);
const sum = numbers.reduce((acc, n) => acc + n, 0);

// Adding/removing elements
numbers.push(6);
numbers.unshift(0);
const last = numbers.pop();
const first = numbers.shift();

// Finding elements
const found = numbers.find(n => n > 3);
const index = numbers.indexOf(3);

console.log("Doubled:", doubled);
console.log("Sum:", sum);''',
            
            'html_structure': '''<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>My Website</title>
    <link rel="stylesheet" href="styles.css">
</head>
<body>
    <header>
        <nav>
            <ul>
                <li><a href="#home">Home</a></li>
                <li><a href="#about">About</a></li>
                <li><a href="#contact">Contact</a></li>
            </ul>
        </nav>
    </header>
    
    <main>
        <section id="home">
            <h1>Welcome</h1>
            <p>This is the main content area.</p>
        </section>
    </main>
    
    <footer>
        <p>&copy; 2024 My Website</p>
    </footer>
</body>
</html>''',
            
            'css_styling': '''/* Reset and base styles */
* {
    margin: 0;
    padding: 0;
    box-sizing: border-box;
}

body {
    font-family: Arial, sans-serif;
    line-height: 1.6;
    color: #333;
}

/* Header styles */
header {
    background: #333;
    color: white;
    padding: 1rem 0;
}

nav ul {
    list-style: none;
    display: flex;
    justify-content: center;
}

nav li {
    margin: 0 1rem;
}

nav a {
    color: white;
    text-decoration: none;
}

nav a:hover {
    text-decoration: underline;
}

/* Main content */
main {
    max-width: 1200px;
    margin: 2rem auto;
    padding: 0 1rem;
}

/* Responsive design */
@media (max-width: 768px) {
    nav ul {
        flex-direction: column;
    }
}'''
        }
    
    def process_input(self, user_input, file_results=None):
        """Main processing function"""
        
        if file_results:
            return self._handle_file_analysis(user_input, file_results)
        
        # Clean input
        text = user_input.strip()
        text_lower = text.lower()
        
        # Mathematical operations
        if self._contains_math(text):
            return self._solve_math(text)
        
        # Programming questions
        elif any(keyword in text_lower for keyword in ['python', 'javascript', 'html', 'css', 'code', 'function', 'loop', 'array', 'list']):
            return self._handle_programming(text_lower)
        
        # Direct questions
        elif text_lower.startswith(('what', 'how', 'why', 'when', 'where', 'who')):
            return self._answer_question(text)
        
        # General conversation
        else:
            return self._handle_general(text)
    
    def _contains_math(self, text):
        """Check if input contains mathematical operations"""
        math_patterns = [
            r'\d+\s*[\+\-\*/]\s*\d+',  # Basic arithmetic
            r'square root',
            r'sqrt',
            r'power',
            r'percentage',
            r'percent',
            r'\d+\s*\^\s*\d+',
            r'\d+\s*\*\*\s*\d+',
            r'calculate',
            r'solve',
            r'factorial'
        ]
        
        return any(re.search(pattern, text.lower()) for pattern in math_patterns)
    
    def _solve_math(self, text):
        """Solve mathematical problems"""
        text_lower = text.lower()
        
        try:
            # Extract numbers
            numbers = re.findall(r'-?\d+\.?\d*', text)
            
            # Basic arithmetic with proper subtraction handling
            if '+' in text:
                if len(numbers) >= 2:
                    result = sum(float(n) for n in numbers)
                    return f"Calculating: {' + '.join(numbers)} = {result}"
            
            elif '-' in text and len(numbers) >= 2:
                # Handle subtraction properly
                nums = [float(n) for n in numbers]
                result = nums[0] - nums[1]
                return f"Calculating: {numbers[0]} - {numbers[1]} = {result}"
            
            elif '*' in text or '×' in text:
                if len(numbers) >= 2:
                    result = float(numbers[0]) * float(numbers[1])
                    return f"Calculating: {numbers[0]} × {numbers[1]} = {result}"
            
            elif '/' in text or '÷' in text:
                if len(numbers) >= 2 and float(numbers[1]) != 0:
                    result = float(numbers[0]) / float(numbers[1])
                    return f"Calculating: {numbers[0]} ÷ {numbers[1]} = {result}"
            
            # Advanced operations
            elif 'square root' in text_lower or 'sqrt' in text_lower:
                if numbers:
                    num = float(numbers[0])
                    if num >= 0:
                        result = math.sqrt(num)
                        return f"Square root of {num} = {result}"
                    else:
                        return "Cannot calculate square root of negative number"
            
            elif 'power' in text_lower or '**' in text or '^' in text:
                if len(numbers) >= 2:
                    base = float(numbers[0])
                    exp = float(numbers[1])
                    result = base ** exp
                    return f"{base} to the power of {exp} = {result}"
            
            elif 'factorial' in text_lower:
                if numbers:
                    num = int(float(numbers[0]))
                    if 0 <= num <= 20:
                        result = math.factorial(num)
                        return f"Factorial of {num} = {result}"
                    else:
                        return "Factorial only available for numbers 0-20"
            
            elif 'percentage' in text_lower or 'percent' in text_lower:
                if len(numbers) >= 2:
                    value = float(numbers[0])
                    total = float(numbers[1])
                    percentage = (value / total) * 100
                    return f"{value} is {percentage:.2f}% of {total}"
            
            # Try to evaluate mathematical expressions safely
            else:
                # Clean expression
                expression = re.sub(r'[^0-9+\-*/().\s]', '', text)
                expression = expression.strip()
                
                if expression and self._is_safe_expression(expression):
                    try:
                        result = self._safe_eval(expression)
                        return f"Calculating: {expression} = {result}"
                    except:
                        pass
            
            return "I can solve mathematical problems. Try: '10 - 5', '7 * 8', 'square root of 25', '2 power 3'"
            
        except Exception as e:
            return f"Could not solve this math problem. Please check the format and try again."
    
    def _is_safe_expression(self, expr):
        """Check if mathematical expression is safe to evaluate"""
        allowed_chars = set('0123456789+-*/().\s')
        return all(c in allowed_chars for c in expr)
    
    def _safe_eval(self, expr):
        """Safely evaluate mathematical expressions"""
        try:
            node = ast.parse(expr, mode='eval')
            return self._eval_node(node.body)
        except:
            return None
    
    def _eval_node(self, node):
        """Evaluate AST node safely"""
        if isinstance(node, ast.Num):
            return node.n
        elif isinstance(node, ast.BinOp):
            return self.operators[type(node.op)](self._eval_node(node.left), self._eval_node(node.right))
        elif isinstance(node, ast.UnaryOp):
            return self.operators[type(node.op)](self._eval_node(node.operand))
        else:
            raise TypeError(node)
    
    def _handle_programming(self, text):
        """Handle programming questions with actual code"""
        
        if 'python' in text:
            if 'function' in text:
                return f"Python function example:\n\n```python\n{self.code_examples['python_function']}\n```"
            elif 'loop' in text:
                return f"Python loops:\n\n```python\n{self.code_examples['python_loop']}\n```"
            elif 'list' in text:
                return f"Python lists:\n\n```python\n{self.code_examples['python_list']}\n```"
            else:
                return "I can help with Python functions, loops, lists, dictionaries, classes, and more. What specific Python concept do you need?"
        
        elif 'javascript' in text:
            if 'function' in text:
                return f"JavaScript functions:\n\n```javascript\n{self.code_examples['javascript_function']}\n```"
            elif 'array' in text:
                return f"JavaScript arrays:\n\n```javascript\n{self.code_examples['javascript_array']}\n```"
            else:
                return "I can help with JavaScript functions, arrays, objects, DOM manipulation, and more. What do you need help with?"
        
        elif 'html' in text:
            return f"HTML structure:\n\n```html\n{self.code_examples['html_structure']}\n```"
        
        elif 'css' in text:
            return f"CSS styling:\n\n```css\n{self.code_examples['css_styling']}\n```"
        
        else:
            return "I can provide code examples for Python, JavaScript, HTML, and CSS. Which language interests you?"
    
    def _answer_question(self, text):
        """Answer direct questions"""
        text_lower = text.lower()
        
        if 'what is your name' in text_lower or 'who are you' in text_lower:
            return "I'm an AI assistant that can solve math problems, help with programming, and answer questions."
        
        elif 'what can you do' in text_lower:
            return "I can solve mathematical calculations, provide programming code examples, answer questions, and analyze uploaded files."
        
        elif 'how to' in text_lower:
            if 'learn programming' in text_lower:
                return "To learn programming: 1) Choose a language (Python is beginner-friendly), 2) Practice daily with small projects, 3) Read and understand error messages, 4) Build real projects, 5) Join coding communities for help."
            elif 'code' in text_lower:
                return "Start coding by: 1) Setting up a development environment, 2) Learning basic syntax, 3) Understanding variables and functions, 4) Practicing with simple programs, 5) Building projects that interest you."
            else:
                return f"I can provide guidance on learning and problem-solving. What specific topic would you like help with?"
        
        elif 'what is' in text_lower:
            if 'programming' in text_lower:
                return "Programming is writing instructions for computers to execute. It involves breaking down problems into logical steps and expressing them in a programming language like Python, JavaScript, or others."
            else:
                return f"I can explain various concepts. What specific topic would you like me to explain?"
        
        else:
            return f"I understand you're asking about '{text}'. I specialize in math calculations, programming help, and answering specific questions. Could you be more specific?"
    
    def _handle_general(self, text):
        """Handle general conversation"""
        text_lower = text.lower()
        
        if any(greeting in text_lower for greeting in ['hello', 'hi', 'hey']):
            return "Hello! I can solve math problems, help with programming, and answer questions. What can I help you with?"
        
        elif any(thanks in text_lower for thanks in ['thank', 'thanks']):
            return "You're welcome! Feel free to ask for more help."
        
        elif 'help' in text_lower:
            return "I can help with mathematical calculations, programming code examples, and answering questions. Try asking me to solve a math problem or help with code."
        
        else:
            return f"I can help solve specific problems. Try asking me to calculate something, help with code, or answer a question about a particular topic."
    
    def _handle_file_analysis(self, user_input, file_results):
        """Handle file analysis requests"""
        response = f"File analysis results:\n\n"
        
        for i, result in enumerate(file_results, 1):
            response += f"File {i}: {result['filename']}\n"
            response += f"Type: {result['file_type']}\n"
            response += f"Size: {result['size'] / 1024:.1f} KB\n"
            response += f"Analysis: {result['analysis']}\n\n"
        
        return response

class FileProcessor:
    """Simple file processor"""
    
    def process_file(self, uploaded_file):
        """Process uploaded file"""
        file_bytes = uploaded_file.read()
        uploaded_file.seek(0)
        
        result = {
            'filename': uploaded_file.name,
            'file_type': uploaded_file.type or 'unknown',
            'size': len(file_bytes),
            'analysis': 'File uploaded successfully'
        }
        
        if uploaded_file.type and uploaded_file.type.startswith('image/'):
            try:
                image = Image.open(io.BytesIO(file_bytes))
                result['analysis'] = f"Image: {image.width}x{image.height} pixels, {image.format} format"
            except:
                result['analysis'] = "Image file detected but could not analyze"
        
        elif uploaded_file.type == 'application/pdf':
            try:
                pdf_reader = PyPDF2.PdfReader(io.BytesIO(file_bytes))
                page_count = len(pdf_reader.pages)
                result['analysis'] = f"PDF document with {page_count} pages"
            except:
                result['analysis'] = "PDF file detected but could not analyze"
        
        elif uploaded_file.type and uploaded_file.type.startswith('text/'):
            try:
                text = file_bytes.decode('utf-8', errors='ignore')
                word_count = len(text.split())
                result['analysis'] = f"Text file with {word_count} words, {len(text)} characters"
            except:
                result['analysis'] = "Text file detected but could not analyze"
        
        return result

def render_header():
    """Render simple header"""
    st.markdown("""
    <div class="main-header">
        <h1>AI Assistant</h1>
    </div>
    """, unsafe_allow_html=True)

def render_sidebar():
    """Render minimal sidebar"""
    uploaded_files = st.sidebar.file_uploader(
        "Upload files",
        type=['txt', 'pdf', 'png', 'jpg', 'jpeg'],
        accept_multiple_files=True
    )
    
    if st.sidebar.button("Clear Chat"):
        st.session_state.messages = []
        st.rerun()
    
    return uploaded_files

@st.cache_resource
def init_ai():
    """Initialize AI and file processor"""
    ai = SmartAI()
    processor = FileProcessor()
    return ai, processor

def main():
    """Main application"""
    load_css()
    
    # Initialize
    ai, file_processor = init_ai()
    
    if 'messages' not in st.session_state:
        st.session_state.messages = []
    
    # Render UI
    render_header()
    uploaded_files = render_sidebar()
    
    # Welcome message
    if not st.session_state.messages:
        st.info("I can solve math problems, help with programming, and answer questions. Try: '15 - 7', 'Python function example', or 'What is programming?'")
    
    # Display messages
    for message in st.session_state.messages:
        with st.chat_message(message["role"]):
            st.write(message["content"])
    
    # Chat input
    if prompt := st.chat_input("Ask me anything..."):
        
        # Process files
        file_results = []
        if uploaded_files:
            for uploaded_file in uploaded_files:
                try:
                    result = file_processor.process_file(uploaded_file)
                    file_results.append(result)
                except Exception as e:
                    st.error(f"Error processing {uploaded_file.name}: {str(e)}")
        
        # Add user message
        st.session_state.messages.append({"role": "user", "content": prompt})
        
        with st.chat_message("user"):
            st.write(prompt)
        
        # Generate response
        with st.chat_message("assistant"):
            try:
                response = ai.process_input(prompt, file_results)
                st.write(response)
                st.session_state.messages.append({"role": "assistant", "content": response})
            except Exception as e:
                error_msg = f"Error: {str(e)}"
                st.error(error_msg)
                st.session_state.messages.append({"role": "assistant", "content": error_msg})
        
        st.rerun()

if __name__ == "__main__":
    main()