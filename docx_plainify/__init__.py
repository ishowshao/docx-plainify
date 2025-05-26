"""
docx-plainify: Convert .docx files to structured YAML format for AI processing.
"""

__version__ = "1.0.0"
__author__ = "docx-plainify"

from .converter import DocxToYamlConverter
from .image_processor import ImageProcessor

__all__ = ["DocxToYamlConverter", "ImageProcessor"] 