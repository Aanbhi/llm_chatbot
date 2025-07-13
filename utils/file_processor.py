import base64
import io
import magic
import chardet
from PIL import Image
import PyPDF2
import streamlit as st

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
