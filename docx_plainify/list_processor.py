"""
Enhanced list processing module for handling nested lists and complex list structures.
"""

import logging
from typing import List, Dict, Any, Optional
from docx.text.paragraph import Paragraph
from docx.document import Document as DocumentType


class ListProcessor:
    """
    Processes lists and nested lists from DOCX documents.
    """
    
    def __init__(self):
        self.logger = logging.getLogger(__name__)
    
    def process_lists(self, doc: DocumentType) -> List[Dict[str, Any]]:
        """
        Process all lists in the document and group them properly.
        
        Args:
            doc: Document object
            
        Returns:
            List of processed list structures
        """
        paragraphs = []
        for element in doc.element.body:
            if hasattr(element, 'tag') and 'p' in element.tag:
                paragraphs.append(Paragraph(element, doc))
        
        list_groups = self._group_list_items(paragraphs)
        return [self._convert_list_group(group) for group in list_groups]
    
    def _group_list_items(self, paragraphs: List[Paragraph]) -> List[List[Paragraph]]:
        """
        Group consecutive list items together.
        
        Args:
            paragraphs: List of all paragraphs
            
        Returns:
            Groups of consecutive list paragraphs
        """
        groups = []
        current_group = []
        
        for para in paragraphs:
            if self._is_list_paragraph(para):
                current_group.append(para)
            else:
                if current_group:
                    groups.append(current_group)
                    current_group = []
        
        # Don't forget the last group
        if current_group:
            groups.append(current_group)
        
        return groups
    
    def _convert_list_group(self, paragraphs: List[Paragraph]) -> Dict[str, Any]:
        """
        Convert a group of list paragraphs to structured format.
        
        Args:
            paragraphs: Group of list paragraphs
            
        Returns:
            Structured list data
        """
        items = []
        current_level = 0
        level_stack = []
        
        for para in paragraphs:
            level = self._get_list_level(para)
            text = para.text.strip()
            
            # Remove common list markers
            text = self._clean_list_text(text)
            
            if not text:
                continue
            
            item = {"text": text}
            
            if level > current_level:
                # Starting a nested level
                if items:
                    # Add children to the last item
                    if "children" not in items[-1]:
                        items[-1]["children"] = []
                    level_stack.append(items)
                    items = items[-1]["children"]
                current_level = level
            elif level < current_level:
                # Going back to a higher level
                while level_stack and level < current_level:
                    items = level_stack.pop()
                    current_level -= 1
            
            items.append(item)
        
        # Build the final structure
        while level_stack:
            items = level_stack.pop()
        
        return {
            "type": "list",
            "items": items
        }
    
    def _is_list_paragraph(self, paragraph: Paragraph) -> bool:
        """
        Check if a paragraph is part of a list.
        
        Args:
            paragraph: Paragraph to check
            
        Returns:
            True if paragraph is a list item
        """
        # Check for numbering properties
        if paragraph._element.pPr is not None:
            numPr = paragraph._element.pPr.numPr
            if numPr is not None:
                return True
        
        # Check for common list indicators in text
        text = paragraph.text.strip()
        list_indicators = [
            '•', '◦', '▪', '▫', '‣', '⁃',  # Bullet points
            '-', '*', '+',  # Dash/asterisk bullets
        ]
        
        # Check for bullet points
        for indicator in list_indicators:
            if text.startswith(indicator):
                return True
        
        # Check for numbered lists
        import re
        if re.match(r'^\d+\.', text) or re.match(r'^\d+\)', text):
            return True
        
        # Check for lettered lists
        if re.match(r'^[a-zA-Z]\.', text) or re.match(r'^[a-zA-Z]\)', text):
            return True
        
        # Check for roman numerals
        if re.match(r'^[ivxlcdm]+\.', text.lower()) or re.match(r'^[ivxlcdm]+\)', text.lower()):
            return True
        
        return False
    
    def _get_list_level(self, paragraph: Paragraph) -> int:
        """
        Determine the nesting level of a list item.
        
        Args:
            paragraph: List paragraph
            
        Returns:
            Nesting level (0-based)
        """
        # Try to get level from numbering properties
        if paragraph._element.pPr is not None:
            numPr = paragraph._element.pPr.numPr
            if numPr is not None and numPr.ilvl is not None:
                return int(numPr.ilvl.val)
        
        # Fallback: estimate level from indentation
        # Count leading spaces/tabs
        text = paragraph.text
        leading_spaces = len(text) - len(text.lstrip())
        
        # Estimate level based on indentation (assuming 4 spaces per level)
        estimated_level = leading_spaces // 4
        
        return max(0, estimated_level)
    
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