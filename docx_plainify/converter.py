"""
Core converter module for transforming DOCX files to structured YAML format.
"""

import logging
import os
import tempfile
from typing import List, Dict, Any, Optional, Union
from pathlib import Path

import yaml
from docx import Document
from docx.document import Document as DocumentType
from docx.text.paragraph import Paragraph
from docx.table import Table
from docx.oxml.text.paragraph import CT_P
from docx.oxml.table import CT_Tbl
from docx.oxml import parse_xml
from docx.shared import Inches

from .image_processor import ImageProcessor


class DocxToYamlConverter:
    """
    Converts DOCX files to structured YAML format while preserving document structure.
    """
    
    def __init__(self, describe_images: bool = False, api_key: Optional[str] = None):
        """
        Initialize the converter.
        
        Args:
            describe_images: Whether to generate descriptions for images using LLM
            api_key: OpenAI API key for image description (if describe_images is True)
        """
        self.describe_images = describe_images
        self.image_processor = ImageProcessor(api_key) if describe_images else None
        self.logger = logging.getLogger(__name__)
        
    def convert_file(self, input_path: str, output_path: str) -> None:
        """
        Convert a DOCX file to YAML format.
        
        Args:
            input_path: Path to input DOCX file
            output_path: Path to output YAML file
        """
        try:
            self.logger.info(f"Starting conversion of {input_path}")
            
            # Load the document
            doc = Document(input_path)
            
            # Convert to structured data
            structured_data = self._convert_document(doc)
            
            # Write to YAML file
            self._write_yaml(structured_data, output_path)
            
            self.logger.info(f"Conversion completed successfully. Output saved to {output_path}")
            
        except Exception as e:
            self.logger.error(f"Error converting file: {str(e)}")
            raise
    
    def _convert_document(self, doc: DocumentType) -> List[Dict[str, Any]]:
        """
        Convert document content to structured data.
        
        Args:
            doc: python-docx Document object
            
        Returns:
            List of structured elements
        """
        elements = []
        
        # Process document elements in order
        for element in doc.element.body:
            if isinstance(element, CT_P):
                # Paragraph element
                paragraph = Paragraph(element, doc)
                converted = self._convert_paragraph(paragraph)
                if converted:
                    elements.append(converted)
                    
            elif isinstance(element, CT_Tbl):
                # Table element
                table = Table(element, doc)
                converted = self._convert_table(table)
                if converted:
                    elements.append(converted)
            else:
                # Other elements - extract text if available
                text_content = self._extract_text_from_element(element)
                if text_content and text_content.strip():
                    elements.append({
                        "type": "paragraph",
                        "text": text_content.strip()
                    })
        
        # Merge consecutive list items
        elements = self._merge_consecutive_lists(elements)
        
        # Process images if enabled
        if self.describe_images and self.image_processor:
            image_elements = self._process_images(doc)
            # Insert image elements at appropriate positions
            # For simplicity, we'll append them at the end
            # In a more sophisticated implementation, we'd track their positions
            elements.extend(image_elements)
        
        return elements
    
    def _convert_paragraph(self, paragraph: Paragraph) -> Optional[Dict[str, Any]]:
        """
        Convert a paragraph to structured format.
        
        Args:
            paragraph: python-docx Paragraph object
            
        Returns:
            Structured paragraph data or None if empty
        """
        text = paragraph.text.strip()
        if not text:
            return None
        
        # Check if it's a heading
        if paragraph.style.name.startswith('Heading'):
            return {
                "type": "heading",
                "text": text,
                "level": self._get_heading_level(paragraph.style.name)
            }
        
        # Check if it's a list item
        if self._is_list_paragraph(paragraph):
            return self._convert_list_item(paragraph)
        
        # Regular paragraph
        return {
            "type": "paragraph",
            "text": text
        }
    
    def _convert_table(self, table: Table) -> Optional[Dict[str, Any]]:
        """
        Convert a table to structured format.
        
        Args:
            table: python-docx Table object
            
        Returns:
            Structured table data or None if empty
        """
        if not table.rows:
            return None
        
        # Get headers from first row
        headers = []
        first_row = table.rows[0]
        for cell in first_row.cells:
            headers.append(cell.text.strip())
        
        if not any(headers):
            return None
        
        # Convert data rows
        rows = []
        for row in table.rows[1:]:
            row_data = {}
            for i, cell in enumerate(row.cells):
                if i < len(headers):
                    cell_content = self._process_cell_content(cell)
                    row_data[headers[i]] = cell_content
            
            if any(row_data.values()):  # Only add non-empty rows
                rows.append(row_data)
        
        return {
            "type": "table",
            "rows": rows
        }
    
    def _process_cell_content(self, cell) -> Union[str, List[Dict[str, Any]]]:
        """
        Process cell content, which may contain complex structures.
        
        Args:
            cell: Table cell object
            
        Returns:
            Cell content as string or structured data
        """
        # For now, return simple text
        # In a more sophisticated implementation, we'd parse nested structures
        text = cell.text.strip()
        
        # Check if cell contains multiple paragraphs or lists
        paragraphs = cell.paragraphs
        if len(paragraphs) > 1:
            # Multiple paragraphs - create structured content
            content = []
            for para in paragraphs:
                if para.text.strip():
                    if self._is_list_paragraph(para):
                        list_item = self._convert_list_item(para)
                        if list_item:
                            content.append(list_item)
                    else:
                        content.append({
                            "type": "paragraph",
                            "text": para.text.strip()
                        })
            return content if content else text
        
        return text
    
    def _convert_list_item(self, paragraph: Paragraph) -> Optional[Dict[str, Any]]:
        """
        Convert a list item paragraph.
        
        Args:
            paragraph: Paragraph that is part of a list
            
        Returns:
            List structure or None
        """
        # This is a simplified implementation
        # A more sophisticated version would handle nested lists properly
        text = paragraph.text.strip()
        if not text:
            return None
        
        # Clean list markers
        cleaned_text = self._clean_list_text(text)
        
        return {
            "type": "list",
            "items": [{"text": cleaned_text}]
        }
    
    def _is_list_paragraph(self, paragraph: Paragraph) -> bool:
        """
        Check if a paragraph is part of a list.
        
        Args:
            paragraph: Paragraph to check
            
        Returns:
            True if paragraph is a list item
        """
        # Check for numbering or bullet formatting
        if paragraph._element.pPr is not None:
            numPr = paragraph._element.pPr.numPr
            if numPr is not None:
                return True
        
        # Check for common list indicators in text
        text = paragraph.text.strip()
        if text.startswith(('•', '-', '*', '1.', '2.', '3.', '4.', '5.')):
            return True
        
        return False
    
    def _get_heading_level(self, style_name: str) -> int:
        """
        Extract heading level from style name.
        
        Args:
            style_name: Style name like 'Heading 1'
            
        Returns:
            Heading level as integer
        """
        try:
            return int(style_name.split()[-1])
        except (ValueError, IndexError):
            return 1
    
    def _extract_text_from_element(self, element) -> str:
        """
        Extract text from an XML element.
        
        Args:
            element: XML element
            
        Returns:
            Extracted text
        """
        try:
            # Try to get text content from the element
            if hasattr(element, 'text'):
                return element.text or ""
            
            # Fallback: try to extract from child elements
            text_parts = []
            for child in element:
                if hasattr(child, 'text') and child.text:
                    text_parts.append(child.text)
            
            return " ".join(text_parts)
        except Exception:
            return ""
    
    def _process_images(self, doc: DocumentType) -> List[Dict[str, Any]]:
        """
        Process images in the document.
        
        Args:
            doc: Document object
            
        Returns:
            List of image elements with descriptions
        """
        image_elements = []
        
        try:
            # Extract images from document
            for rel in doc.part.rels.values():
                if "image" in rel.target_ref:
                    # Get image data
                    image_data = rel.target_part.blob
                    
                    # Generate description using LLM
                    description = self.image_processor.describe_image(image_data)
                    
                    image_elements.append({
                        "type": "image",
                        "name": rel.target_ref.split('/')[-1],
                        "description": description
                    })
        
        except Exception as e:
            self.logger.warning(f"Error processing images: {str(e)}")
        
        return image_elements
    
    def _merge_consecutive_lists(self, elements: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """
        Merge consecutive list elements into single list structures.
        
        Args:
            elements: List of document elements
            
        Returns:
            List with merged consecutive lists
        """
        if not elements:
            return elements
        
        merged = []
        current_list = None
        
        for element in elements:
            if element.get("type") == "list":
                if current_list is None:
                    # Start a new list
                    current_list = {
                        "type": "list",
                        "items": element["items"].copy()
                    }
                else:
                    # Extend the current list
                    current_list["items"].extend(element["items"])
            else:
                # Not a list element
                if current_list is not None:
                    # Save the current list and reset
                    merged.append(current_list)
                    current_list = None
                merged.append(element)
        
        # Don't forget the last list if it exists
        if current_list is not None:
            merged.append(current_list)
        
        return merged

    def _clean_list_text(self, text: str) -> str:
        """
        Remove list markers from text.
        
        Args:
            text: Raw list item text
            
        Returns:
            Cleaned text without list markers
        """
        import re
        
        # Remove bullet points
        text = re.sub(r'^[•◦▪▫‣⁃\-\*\+]\s*', '', text)
        
        # Remove numbered list markers
        text = re.sub(r'^\d+[\.\)]\s*', '', text)
        
        # Remove lettered list markers
        text = re.sub(r'^[a-zA-Z][\.\)]\s*', '', text)
        
        # Remove roman numeral markers
        text = re.sub(r'^[ivxlcdm]+[\.\)]\s*', '', text, flags=re.IGNORECASE)
        
        return text.strip()

    def _write_yaml(self, data: List[Dict[str, Any]], output_path: str) -> None:
        """
        Write structured data to YAML file.
        
        Args:
            data: Structured data to write
            output_path: Output file path
        """
        try:
            with open(output_path, 'w', encoding='utf-8') as f:
                yaml.dump(data, f, default_flow_style=False, 
                         allow_unicode=True, sort_keys=False, indent=2)
        except Exception as e:
            self.logger.error(f"Error writing YAML file: {str(e)}")
            raise 