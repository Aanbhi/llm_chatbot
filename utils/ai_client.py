import os
import json
from openai import OpenAI

class AIClient:
    """Client for interacting with OpenAI API"""
    
    def __init__(self):
        api_key = os.getenv("OPENAI_API_KEY", "default_key")
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
                error_msg += "\n\nPlease check that your OPENAI_API_KEY environment variable is set correctly."
            elif "rate limit" in str(e).lower():
                error_msg += "\n\nRate limit exceeded. Please wait a moment before trying again."
            elif "connection" in str(e).lower():
                error_msg += "\n\nConnection error. Please check your internet connection."
            
            return error_msg
    
    def summarize_text(self, text, max_length=200):
        """Summarize long text content"""
        try:
            prompt = f"Please provide a concise summary of the following text in about {max_length} words:\n\n{text}"
            
            response = self.client.chat.completions.create(
                model=self.text_model,
                messages=[{"role": "user", "content": prompt}],
                max_tokens=max_length * 2,  # Allow some buffer
                temperature=0.5
            )
            
            return response.choices[0].message.content
            
        except Exception as e:
            return f"Error summarizing text: {str(e)}"
    
    def analyze_image_with_context(self, base64_image, context=""):
        """Analyze image with additional context"""
        try:
            prompt = "Analyze this image in detail. "
            if context:
                prompt += f"Additional context: {context}"
            
            response = self.client.chat.completions.create(
                model=self.vision_model,
                messages=[
                    {
                        "role": "user",
                        "content": [
                            {"type": "text", "text": prompt},
                            {
                                "type": "image_url",
                                "image_url": {"url": f"data:image/jpeg;base64,{base64_image}"}
                            }
                        ]
                    }
                ],
                max_tokens=500,
                temperature=0.7
            )
            
            return response.choices[0].message.content
            
        except Exception as e:
            return f"Error analyzing image: {str(e)}"