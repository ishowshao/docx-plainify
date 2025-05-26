"""
Basic tests for the docx-plainify converter.
"""

import unittest
import tempfile
import os
from pathlib import Path

from docx_plainify.converter import DocxToYamlConverter


class TestDocxToYamlConverter(unittest.TestCase):
    """Test cases for DocxToYamlConverter."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.converter = DocxToYamlConverter()
    
    def test_converter_initialization(self):
        """Test converter initialization."""
        self.assertIsNotNone(self.converter)
        self.assertFalse(self.converter.describe_images)
        self.assertIsNone(self.converter.image_processor)
    
    def test_converter_with_images(self):
        """Test converter initialization with image processing."""
        converter = DocxToYamlConverter(describe_images=True, api_key="test_key")
        self.assertTrue(converter.describe_images)
        self.assertIsNotNone(converter.image_processor)
    
    def test_heading_level_extraction(self):
        """Test heading level extraction."""
        level = self.converter._get_heading_level("Heading 1")
        self.assertEqual(level, 1)
        
        level = self.converter._get_heading_level("Heading 3")
        self.assertEqual(level, 3)
        
        level = self.converter._get_heading_level("Normal")
        self.assertEqual(level, 1)  # Default level
    
    def test_text_extraction(self):
        """Test text extraction from elements."""
        # This is a basic test - in a real scenario, you'd need actual XML elements
        text = self.converter._extract_text_from_element(None)
        self.assertEqual(text, "")


if __name__ == '__main__':
    unittest.main() 