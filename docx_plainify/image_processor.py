"""
Image processing module for generating semantic descriptions using LLM.
"""

import logging
import base64
import io
from typing import Optional

from PIL import Image
from langchain_openai import ChatOpenAI
from langchain.schema import HumanMessage


class ImageProcessor:
    """
    Processes images and generates semantic descriptions using LLM.
    """
    
    def __init__(self, api_key: Optional[str] = None):
        """
        Initialize the image processor.
        
        Args:
            api_key: OpenAI API key for LLM calls
        """
        self.api_key = api_key
        self.logger = logging.getLogger(__name__)
        
        if api_key:
            try:
                self.llm = ChatOpenAI(
                    model="gpt-4o",
                    api_key=api_key,
                    max_tokens=500,
                    temperature=0.1
                )
            except Exception as e:
                self.logger.error(f"Failed to initialize OpenAI client: {str(e)}")
                self.llm = None
        else:
            self.llm = None
            self.logger.warning("No API key provided. Image descriptions will not be generated.")
    
    def describe_image(self, image_data: bytes) -> str:
        """
        Generate a semantic description of an image.
        
        Args:
            image_data: Raw image data as bytes
            
        Returns:
            Text description of the image
        """
        if not self.llm:
            return "Image description not available (no API key provided)"
        
        try:
            # Convert image data to base64
            base64_image = base64.b64encode(image_data).decode('utf-8')
            
            # Prepare the prompt
            prompt = """
            Please provide a clear, concise description of this image. Focus on:
            1. The main subject or content of the image
            2. Important visual elements, data, or information shown
            3. The type of image (chart, diagram, photo, etc.)
            4. Any text or labels visible in the image
            
            Keep the description factual and suitable for AI processing.
            """
            
            # Create message with image
            message = HumanMessage(
                content=[
                    {"type": "text", "text": prompt},
                    {
                        "type": "image_url",
                        "image_url": {
                            "url": f"data:image/jpeg;base64,{base64_image}"
                        }
                    }
                ]
            )
            
            # Get response from LLM
            response = self.llm.invoke([message])
            description = response.content.strip()
            
            self.logger.info("Successfully generated image description")
            return description
            
        except Exception as e:
            self.logger.error(f"Error generating image description: {str(e)}")
            return f"Error generating image description: {str(e)}"
    
    def _validate_image(self, image_data: bytes) -> bool:
        """
        Validate that the image data is valid.
        
        Args:
            image_data: Raw image data
            
        Returns:
            True if image is valid
        """
        try:
            image = Image.open(io.BytesIO(image_data))
            image.verify()
            return True
        except Exception:
            return False 