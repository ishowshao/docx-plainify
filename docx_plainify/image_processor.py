"""
Image processing module for generating semantic descriptions using LLM.
"""

import logging
import base64
import io
import os
from typing import Optional

from PIL import Image
from langchain_openai import AzureChatOpenAI
from langchain.schema import HumanMessage


class ImageProcessor:
    """
    Processes images and generates semantic descriptions using LLM.
    """
    
    def __init__(self, api_key: Optional[str] = None):
        """
        Initialize the image processor.
        
        Args:
            api_key: Deprecated parameter, Azure OpenAI uses environment variables
        """
        self.logger = logging.getLogger(__name__)
        
        # Check for required Azure OpenAI environment variables
        azure_endpoint = os.environ.get("AZURE_OPENAI_ENDPOINT")
        azure_deployment = os.environ.get("AZURE_OPENAI_DEPLOYMENT_NAME")
        azure_api_version = os.environ.get("AZURE_OPENAI_API_VERSION")
        
        if azure_endpoint and azure_deployment and azure_api_version:
            try:
                self.llm = AzureChatOpenAI(
                    azure_endpoint=azure_endpoint,
                    azure_deployment=azure_deployment,
                    openai_api_version=azure_api_version,
                    max_tokens=500,
                    temperature=0.1
                )
                self.logger.info("Successfully initialized Azure OpenAI client")
            except Exception as e:
                self.logger.error(f"Failed to initialize Azure OpenAI client: {str(e)}")
                self.llm = None
        else:
            self.llm = None
            missing_vars = []
            if not azure_endpoint:
                missing_vars.append("AZURE_OPENAI_ENDPOINT")
            if not azure_deployment:
                missing_vars.append("AZURE_OPENAI_DEPLOYMENT_NAME")
            if not azure_api_version:
                missing_vars.append("AZURE_OPENAI_API_VERSION")
            
            self.logger.warning(f"Missing Azure OpenAI environment variables: {', '.join(missing_vars)}. Image descriptions will not be generated.")
    
    def describe_image(self, image_data: bytes) -> str:
        """
        Generate a semantic description of an image.
        
        Args:
            image_data: Raw image data as bytes
            
        Returns:
            Text description of the image
        """
        if not self.llm:
            return "Image description not available (Azure OpenAI not configured)"
        
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