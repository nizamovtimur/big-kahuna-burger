"""
Simple input sanitization service for basic text cleaning.
"""
import re
from typing import Any, Dict, List, Optional


class InputSanitizer:
    """Service for basic sanitization of user inputs."""
    
    # Control characters and potentially problematic characters
    DANGEROUS_CHARS = r'[\x00\x08\x0b\x0c\x0e\x1f\x7f<>/"\'\;\:\|=\+]'

    @classmethod
    def sanitize_text(cls, text: str) -> str:
        """
        Basic text sanitization - remove control characters and normalize.
        
        Args:
            text: Input text to sanitize
            
        Returns:
            Sanitized text
        """
        if not text or not isinstance(text, str):
            return ""
        
        # Remove dangerous characters and null bytes
        text = re.sub(cls.DANGEROUS_CHARS, '', text)
        
        # Normalize whitespace
        text = re.sub(r'\s+', ' ', text)
        
        return text.strip()
    
    @classmethod
    def sanitize_html(cls, html_content: str) -> str:
        """
        Basic HTML sanitization - remove control characters.
        
        Args:
            html_content: HTML content to sanitize
            
        Returns:
            Sanitized HTML content
        """
        if not html_content or not isinstance(html_content, str):
            return ""
        
        # Remove control characters and null bytes
        html_content = re.sub(cls.DANGEROUS_CHARS, '', html_content)
        
        # Normalize whitespace
        html_content = re.sub(r'\s+', ' ', html_content)
        
        return html_content.strip()
    
    @classmethod
    def sanitize_user_input(cls, user_input: Any) -> str:
        """
        Basic sanitization of user input for AI processing.
        
        Args:
            user_input: User input to sanitize
            
        Returns:
            Sanitized string safe for AI processing
        """
        if not user_input:
            return ""
        
        # Convert to string if not already
        text = str(user_input)
        
        # Basic text sanitization
        text = cls.sanitize_text(text)
        
        return text
    
    @classmethod
    def sanitize_sql_query(cls, query: str) -> str:
        """
        Basic SQL query sanitization - remove control characters.
        
        Args:
            query: SQL query to sanitize
            
        Returns:
            Sanitized SQL query
        """
        if not query or not isinstance(query, str):
            return ""
        
        # Remove control characters and null bytes
        query = re.sub(cls.DANGEROUS_CHARS, '', query)
        
        # Normalize whitespace
        query = re.sub(r'\s+', ' ', query)
        
        return query.strip()
    
    @classmethod
    def validate_file_upload(cls, filename: str, content_type: str, file_size: int) -> bool:
        """
        Basic file upload validation.
        
        Args:
            filename: Name of the uploaded file
            content_type: MIME type of the file
            file_size: Size of the file in bytes
            
        Returns:
            True if file is safe to process
        """
        # Check file size (max 10MB)
        if file_size > 10 * 1024 * 1024:
            raise ValueError("File size exceeds 10MB limit")
        
        # Basic filename sanitization
        if not filename or not isinstance(filename, str):
            raise ValueError("Invalid filename")
        
        # Remove control characters from filename
        filename = re.sub(cls.DANGEROUS_CHARS, '', filename)
        if not filename.strip():
            raise ValueError("Filename contains only control characters")
        
        return True


# Global instance
input_sanitizer = InputSanitizer()
