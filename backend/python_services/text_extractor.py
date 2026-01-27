"""
Resume Text Extraction Module

A production-ready, ATS-safe text extraction module for PDF and DOCX files.
Extracts clean, readable text while preserving structure and formatting.

Features:
- PDF extraction using pdfplumber
- DOCX extraction using mammoth
- Text normalization (header/footer removal, page numbers, etc.)
- Bullet point preservation
- Section heading preservation
- Comprehensive error handling

Author: Senior Python NLP Engineer
"""

import os
import re
from pathlib import Path
from typing import Optional, Dict, Any
import logging

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


class TextExtractionError(Exception):
    """Custom exception for text extraction errors"""
    pass


class ResumeTextExtractor:
    """
    A deterministic, ATS-safe text extractor for resume files.
    
    Supports:
    - PDF files (.pdf)
    - DOCX files (.docx, .doc)
    """
    
    # Supported file extensions
    SUPPORTED_EXTENSIONS = {'.pdf', '.docx', '.doc'}
    
    # Common resume section headers (for preservation)
    SECTION_HEADERS = {
        'summary', 'objective', 'experience', 'education', 'skills',
        'certifications', 'projects', 'achievements', 'publications',
        'languages', 'interests', 'volunteer', 'awards', 'references',
        'professional summary', 'work experience', 'technical skills',
        'professional experience', 'career objective', 'qualifications'
    }
    
    # Patterns for unwanted content
    PATTERNS_TO_REMOVE = {
        # Page numbers
        'page_numbers': [
            r'\bPage\s+\d+\s+of\s+\d+\b',
            r'\b\d+\s+of\s+\d+\b',
            r'^\s*\d+\s*$',  # Standalone numbers
        ],
        # Common headers/footers
        'headers_footers': [
            r'Confidential|Proprietary|Draft',
            r'Resume of.*',
            r'CV of.*',
            r'Curriculum Vitae.*',
        ],
        # Extra whitespace
        'whitespace': [
            r'\n\s*\n\s*\n+',  # Multiple blank lines
            r'[ \t]+',  # Multiple spaces/tabs
        ]
    }
    
    # Bullet point markers to preserve
    BULLET_MARKERS = ['•', '●', '○', '■', '□', '▪', '▫', '–', '-', '*', '→', '»']
    
    def __init__(self):
        """Initialize the text extractor"""
        self._validate_dependencies()
    
    def _validate_dependencies(self) -> None:
        """
        Validate that required dependencies are installed.
        
        Raises:
            ImportError: If required dependencies are missing
        """
        try:
            import pdfplumber
            import mammoth
        except ImportError as e:
            logger.error(f"Missing required dependency: {e}")
            raise ImportError(
                "Required dependencies not installed. "
                "Please install: pip install pdfplumber mammoth"
            ) from e
    
    def extract_text(self, file_path: str) -> str:
        """
        Extract clean, readable text from a resume file.
        
        This is the main entry point for text extraction. It automatically
        detects the file type and uses the appropriate extraction method.
        
        Args:
            file_path: Path to the PDF or DOCX file
            
        Returns:
            Clean, normalized text content of the resume
            
        Raises:
            TextExtractionError: If extraction fails
            FileNotFoundError: If file doesn't exist
            ValueError: If file type is not supported
            
        Example:
            >>> extractor = ResumeTextExtractor()
            >>> text = extractor.extract_text("resume.pdf")
            >>> print(text)
        """
        try:
            # Validate file
            file_path_obj = self._validate_file(file_path)
            
            # Determine file type and extract
            extension = file_path_obj.suffix.lower()
            
            if extension == '.pdf':
                raw_text = self._extract_from_pdf(file_path)
            elif extension in {'.docx', '.doc'}:
                raw_text = self._extract_from_docx(file_path)
            else:
                raise ValueError(
                    f"Unsupported file type: {extension}. "
                    f"Supported types: {', '.join(self.SUPPORTED_EXTENSIONS)}"
                )
            
            # Normalize the extracted text
            normalized_text = self._normalize_text(raw_text)
            
            logger.info(f"Successfully extracted {len(normalized_text)} characters from {file_path}")
            
            return normalized_text
            
        except Exception as e:
            logger.error(f"Text extraction failed for {file_path}: {str(e)}")
            if isinstance(e, (TextExtractionError, FileNotFoundError, ValueError)):
                raise
            raise TextExtractionError(f"Failed to extract text: {str(e)}") from e
    
    def _validate_file(self, file_path: str) -> Path:
        """
        Validate that the file exists and is of a supported type.
        
        Args:
            file_path: Path to the file
            
        Returns:
            Path object for the validated file
            
        Raises:
            FileNotFoundError: If file doesn't exist
            ValueError: If file type is not supported
        """
        file_path_obj = Path(file_path)
        
        if not file_path_obj.exists():
            raise FileNotFoundError(f"File not found: {file_path}")
        
        if not file_path_obj.is_file():
            raise ValueError(f"Path is not a file: {file_path}")
        
        extension = file_path_obj.suffix.lower()
        if extension not in self.SUPPORTED_EXTENSIONS:
            raise ValueError(
                f"Unsupported file type: {extension}. "
                f"Supported types: {', '.join(self.SUPPORTED_EXTENSIONS)}"
            )
        
        return file_path_obj
    
    def _extract_from_pdf(self, file_path: str) -> str:
        """
        Extract text from a PDF file using pdfplumber.
        
        Args:
            file_path: Path to the PDF file
            
        Returns:
            Raw extracted text
            
        Raises:
            TextExtractionError: If PDF extraction fails
        """
        try:
            import pdfplumber
            
            text_parts = []
            
            with pdfplumber.open(file_path) as pdf:
                if not pdf.pages:
                    raise TextExtractionError("PDF file contains no pages")
                
                for page_num, page in enumerate(pdf.pages, 1):
                    try:
                        # Extract text from page
                        page_text = page.extract_text()
                        
                        if page_text:
                            text_parts.append(page_text)
                        else:
                            logger.warning(f"No text found on page {page_num}")
                    
                    except Exception as e:
                        logger.warning(f"Failed to extract page {page_num}: {str(e)}")
                        continue
            
            if not text_parts:
                raise TextExtractionError("No text could be extracted from PDF")
            
            # Join pages with double newline
            return '\n\n'.join(text_parts)
            
        except ImportError:
            raise TextExtractionError("pdfplumber not installed")
        except Exception as e:
            if isinstance(e, TextExtractionError):
                raise
            raise TextExtractionError(f"PDF extraction failed: {str(e)}") from e
    
    def _extract_from_docx(self, file_path: str) -> str:
        """
        Extract text from a DOCX file using mammoth.
        
        Args:
            file_path: Path to the DOCX file
            
        Returns:
            Raw extracted text
            
        Raises:
            TextExtractionError: If DOCX extraction fails
        """
        try:
            import mammoth
            
            with open(file_path, 'rb') as docx_file:
                # Extract text with basic styling
                result = mammoth.extract_raw_text(docx_file)
                
                if not result.value:
                    raise TextExtractionError("DOCX file appears to be empty")
                
                # Log any messages/warnings from mammoth
                if result.messages:
                    for message in result.messages:
                        logger.debug(f"Mammoth message: {message}")
                
                return result.value
            
        except ImportError:
            raise TextExtractionError("mammoth not installed")
        except Exception as e:
            if isinstance(e, TextExtractionError):
                raise
            raise TextExtractionError(f"DOCX extraction failed: {str(e)}") from e
    
    def _normalize_text(self, text: str) -> str:
        """
        Normalize extracted text by removing unwanted content and
        preserving important structure.
        
        Normalization steps:
        1. Remove headers/footers
        2. Remove page numbers
        3. Preserve bullet points
        4. Preserve section headings
        5. Normalize whitespace
        6. Remove empty lines (but keep one between sections)
        
        Args:
            text: Raw extracted text
            
        Returns:
            Normalized, clean text
        """
        if not text or not text.strip():
            return ""
        
        # Step 1: Preserve bullet points by normalizing them
        normalized = self._normalize_bullets(text)
        
        # Step 2: Remove page numbers
        for pattern in self.PATTERNS_TO_REMOVE['page_numbers']:
            normalized = re.sub(pattern, '', normalized, flags=re.IGNORECASE | re.MULTILINE)
        
        # Step 3: Remove common headers/footers
        for pattern in self.PATTERNS_TO_REMOVE['headers_footers']:
            normalized = re.sub(pattern, '', normalized, flags=re.IGNORECASE)
        
        # Step 4: Preserve and emphasize section headings
        normalized = self._emphasize_section_headings(normalized)
        
        # Step 5: Normalize whitespace
        # Replace multiple spaces with single space
        normalized = re.sub(r'[ \t]+', ' ', normalized)
        
        # Replace multiple newlines with maximum of 2
        normalized = re.sub(r'\n\s*\n\s*\n+', '\n\n', normalized)
        
        # Step 6: Clean up lines
        lines = normalized.split('\n')
        cleaned_lines = []
        
        for line in lines:
            # Strip leading/trailing whitespace
            cleaned_line = line.strip()
            
            # Skip empty lines unless they separate sections
            if cleaned_line or (cleaned_lines and cleaned_lines[-1]):
                cleaned_lines.append(cleaned_line)
        
        # Step 7: Join lines and ensure no more than one blank line between sections
        result = '\n'.join(cleaned_lines)
        result = re.sub(r'\n\n\n+', '\n\n', result)
        
        # Final cleanup
        return result.strip()
    
    def _normalize_bullets(self, text: str) -> str:
        """
        Normalize bullet points to a standard format.
        
        Args:
            text: Text containing various bullet markers
            
        Returns:
            Text with normalized bullet points
        """
        # Preserve bullets by ensuring they start with a standard marker
        lines = text.split('\n')
        normalized_lines = []
        
        for line in lines:
            stripped = line.strip()
            
            # Check if line starts with any bullet marker
            starts_with_bullet = False
            for marker in self.BULLET_MARKERS:
                if stripped.startswith(marker):
                    # Ensure consistent spacing after bullet
                    stripped = re.sub(
                        f'^{re.escape(marker)}\\s*',
                        f'{marker} ',
                        stripped
                    )
                    starts_with_bullet = True
                    break
            
            normalized_lines.append(stripped if starts_with_bullet else line.strip())
        
        return '\n'.join(normalized_lines)
    
    def _emphasize_section_headings(self, text: str) -> str:
        """
        Identify and preserve section headings.
        
        Args:
            text: Text that may contain section headings
            
        Returns:
            Text with preserved section headings
        """
        lines = text.split('\n')
        emphasized_lines = []
        
        for line in lines:
            stripped = line.strip()
            lower = stripped.lower()
            
            # Check if this line is a section heading
            is_heading = False
            
            # Check for exact matches
            if lower in self.SECTION_HEADERS:
                is_heading = True
            
            # Check for headings with colons
            elif ':' in lower:
                heading_part = lower.split(':')[0].strip()
                if heading_part in self.SECTION_HEADERS:
                    is_heading = True
            
            # Check for partial matches
            else:
                for header in self.SECTION_HEADERS:
                    if header in lower and len(stripped) < 50:  # Likely a heading
                        is_heading = True
                        break
            
            # Preserve heading with extra spacing
            if is_heading and stripped:
                # Ensure blank line before heading (if not first line)
                if emphasized_lines and emphasized_lines[-1]:
                    emphasized_lines.append('')
                emphasized_lines.append(stripped.upper())  # Emphasize in uppercase
                emphasized_lines.append('')  # Blank line after
            else:
                emphasized_lines.append(stripped)
        
        return '\n'.join(emphasized_lines)
    
    def extract_with_metadata(self, file_path: str) -> Dict[str, Any]:
        """
        Extract text along with metadata about the extraction.
        
        Args:
            file_path: Path to the file
            
        Returns:
            Dictionary containing:
                - text: Extracted text
                - file_name: Name of the file
                - file_type: Type of file (pdf/docx)
                - file_size: Size in bytes
                - char_count: Number of characters
                - word_count: Approximate word count
                - line_count: Number of lines
                
        Raises:
            TextExtractionError: If extraction fails
        """
        file_path_obj = self._validate_file(file_path)
        
        # Extract text
        text = self.extract_text(file_path)
        
        # Calculate metadata
        metadata = {
            'text': text,
            'file_name': file_path_obj.name,
            'file_type': file_path_obj.suffix.lower().lstrip('.'),
            'file_size': file_path_obj.stat().st_size,
            'char_count': len(text),
            'word_count': len(text.split()),
            'line_count': len(text.split('\n'))
        }
        
        return metadata


# Convenience function for simple usage
def extract_text(file_path: str) -> str:
    """
    Convenience function to extract text from a resume file.
    
    This is a simple wrapper around ResumeTextExtractor.extract_text()
    for quick, one-off extractions.
    
    Args:
        file_path: Path to the PDF or DOCX file
        
    Returns:
        Clean, normalized text content
        
    Raises:
        TextExtractionError: If extraction fails
        FileNotFoundError: If file doesn't exist
        ValueError: If file type is not supported
        
    Example:
        >>> from text_extractor import extract_text
        >>> text = extract_text("resume.pdf")
        >>> print(text)
    """
    extractor = ResumeTextExtractor()
    return extractor.extract_text(file_path)


# Example usage
if __name__ == "__main__":
    import sys
    
    if len(sys.argv) < 2:
        print("Usage: python text_extractor.py <file_path>")
        print("\nExample:")
        print("  python text_extractor.py resume.pdf")
        print("  python text_extractor.py resume.docx")
        sys.exit(1)
    
    file_path = sys.argv[1]
    
    try:
        # Extract text
        extractor = ResumeTextExtractor()
        result = extractor.extract_with_metadata(file_path)
        
        # Display results
        print(f"\n{'='*60}")
        print(f"File: {result['file_name']}")
        print(f"Type: {result['file_type'].upper()}")
        print(f"Size: {result['file_size']:,} bytes")
        print(f"{'='*60}\n")
        
        print(f"Statistics:")
        print(f"  - Characters: {result['char_count']:,}")
        print(f"  - Words: {result['word_count']:,}")
        print(f"  - Lines: {result['line_count']:,}")
        print(f"\n{'='*60}\n")
        
        print("Extracted Text:")
        print(f"\n{result['text']}\n")
        print(f"{'='*60}\n")
        
    except Exception as e:
        print(f"\n❌ Error: {str(e)}\n")
        sys.exit(1)
