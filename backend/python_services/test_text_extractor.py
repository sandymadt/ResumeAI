"""
Unit Tests for Resume Text Extraction Module

Tests cover:
- File validation
- PDF extraction
- DOCX extraction
- Text normalization
- Error handling
- Edge cases
"""

import unittest
import os
import tempfile
from pathlib import Path
from unittest.mock import patch, MagicMock, mock_open
import sys

# Add parent directory to path for imports
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from text_extractor import (
    ResumeTextExtractor,
    TextExtractionError,
    extract_text
)


class TestResumeTextExtractor(unittest.TestCase):
    """Test cases for ResumeTextExtractor class"""
    
    def setUp(self):
        """Set up test fixtures"""
        self.extractor = ResumeTextExtractor()
        self.test_dir = tempfile.mkdtemp()
    
    def tearDown(self):
        """Clean up test files"""
        import shutil
        if os.path.exists(self.test_dir):
            shutil.rmtree(self.test_dir)
    
    # ========================================================================
    # FILE VALIDATION TESTS
    # ========================================================================
    
    def test_validate_file_not_found(self):
        """Test that FileNotFoundError is raised for non-existent files"""
        with self.assertRaises(FileNotFoundError):
            self.extractor._validate_file('/nonexistent/file.pdf')
    
    def test_validate_file_unsupported_type(self):
        """Test that ValueError is raised for unsupported file types"""
        # Create a temporary .txt file
        test_file = os.path.join(self.test_dir, 'test.txt')
        Path(test_file).touch()
        
        with self.assertRaises(ValueError) as context:
            self.extractor._validate_file(test_file)
        
        self.assertIn('Unsupported file type', str(context.exception))
    
    def test_validate_file_is_directory(self):
        """Test that ValueError is raised when path is a directory"""
        with self.assertRaises(ValueError) as context:
            self.extractor._validate_file(self.test_dir)
        
        self.assertIn('not a file', str(context.exception))
    
    def test_validate_file_success_pdf(self):
        """Test successful validation of PDF file"""
        test_file = os.path.join(self.test_dir, 'test.pdf')
        Path(test_file).touch()
        
        result = self.extractor._validate_file(test_file)
        self.assertIsInstance(result, Path)
        self.assertEqual(result.suffix, '.pdf')
    
    def test_validate_file_success_docx(self):
        """Test successful validation of DOCX file"""
        test_file = os.path.join(self.test_dir, 'test.docx')
        Path(test_file).touch()
        
        result = self.extractor._validate_file(test_file)
        self.assertIsInstance(result, Path)
        self.assertEqual(result.suffix, '.docx')
    
    # ========================================================================
    # TEXT NORMALIZATION TESTS
    # ========================================================================
    
    def test_normalize_text_empty(self):
        """Test normalization of empty text"""
        result = self.extractor._normalize_text('')
        self.assertEqual(result, '')
    
    def test_normalize_text_whitespace_only(self):
        """Test normalization of whitespace-only text"""
        result = self.extractor._normalize_text('   \n\n\t  ')
        self.assertEqual(result, '')
    
    def test_normalize_text_removes_multiple_spaces(self):
        """Test that multiple spaces are normalized to single space"""
        text = 'Hello    world    test'
        result = self.extractor._normalize_text(text)
        self.assertEqual(result, 'Hello world test')
    
    def test_normalize_text_removes_multiple_newlines(self):
        """Test that multiple newlines are normalized to double newline"""
        text = 'Line 1\n\n\n\n\nLine 2'
        result = self.extractor._normalize_text(text)
        self.assertEqual(result, 'Line 1\n\nLine 2')
    
    def test_normalize_text_removes_page_numbers(self):
        """Test that page numbers are removed"""
        test_cases = [
            ('Page 1 of 5\nContent here', 'Content'),
            ('Some text\n2 of 5\nContent', 'Content'),
            ('Content\n1\nMore content', 'Content')
        ]
        
        for text, expected_word in test_cases:
            result = self.extractor._normalize_text(text)
            # Page numbers should be removed
            self.assertNotIn('Page', result)
            # But content should remain
            if expected_word:
                self.assertIn(expected_word, result)
    
    def test_normalize_bullets_preserves_bullets(self):
        """Test that bullet points are preserved"""
        text = '• First point\n• Second point\n- Third point'
        result = self.extractor._normalize_bullets(text)
        
        self.assertIn('•', result)
        self.assertIn('First point', result)
        self.assertIn('Second point', result)
        self.assertIn('Third point', result)
    
    def test_normalize_bullets_standardizes_spacing(self):
        """Test that bullet spacing is standardized"""
        text = '•First point\n•  Second point with extra spaces'
        result = self.extractor._normalize_bullets(text)
        
        # Should have consistent spacing after bullets
        self.assertIn('• First point', result)
        self.assertIn('• Second point', result)
    
    def test_emphasize_section_headings(self):
        """Test that section headings are emphasized"""
        text = 'experience\nSoftware Engineer\neducation\nBS Computer Science'
        result = self.extractor._emphasize_section_headings(text)
        
        # Headings should be uppercase
        self.assertIn('EXPERIENCE', result)
        self.assertIn('EDUCATION', result)
        # Content should be preserved
        self.assertIn('Software Engineer', result)
        self.assertIn('BS Computer Science', result)
    
    def test_emphasize_section_headings_with_colons(self):
        """Test section headings with colons"""
        text = 'Skills:\nPython, JavaScript\nExperience:\nSoftware Engineer'
        result = self.extractor._emphasize_section_headings(text)
        
        self.assertIn('SKILLS:', result)
        self.assertIn('EXPERIENCE:', result)
    
    # ========================================================================
    # PDF EXTRACTION TESTS (Mocked)
    # ========================================================================
    
    @patch('pdfplumber.open')
    def test_extract_from_pdf_success(self, mock_pdf_open):
        """Test successful PDF extraction"""
        # Mock PDF with 2 pages
        mock_page1 = MagicMock()
        mock_page1.extract_text.return_value = 'Page 1 content'
        
        mock_page2 = MagicMock()
        mock_page2.extract_text.return_value = 'Page 2 content'
        
        mock_pdf = MagicMock()
        mock_pdf.pages = [mock_page1, mock_page2]
        mock_pdf.__enter__.return_value = mock_pdf
        mock_pdf.__exit__ = MagicMock()
        
        mock_pdf_open.return_value = mock_pdf
        
        result = self.extractor._extract_from_pdf('test.pdf')
        
        self.assertIn('Page 1 content', result)
        self.assertIn('Page 2 content', result)
    
    @patch('pdfplumber.open')
    def test_extract_from_pdf_empty_pages(self, mock_pdf_open):
        """Test PDF with no extractable text"""
        mock_page = MagicMock()
        mock_page.extract_text.return_value = None
        
        mock_pdf = MagicMock()
        mock_pdf.pages = [mock_page]
        mock_pdf.__enter__.return_value = mock_pdf
        mock_pdf.__exit__ = MagicMock()
        
        mock_pdf_open.return_value = mock_pdf
        
        with self.assertRaises(TextExtractionError) as context:
            self.extractor._extract_from_pdf('test.pdf')
        
        self.assertIn('No text could be extracted', str(context.exception))
    
    @patch('pdfplumber.open')
    def test_extract_from_pdf_no_pages(self, mock_pdf_open):
        """Test PDF with no pages"""
        mock_pdf = MagicMock()
        mock_pdf.pages = []
        mock_pdf.__enter__.return_value = mock_pdf
        mock_pdf.__exit__ = MagicMock()
        
        mock_pdf_open.return_value = mock_pdf
        
        with self.assertRaises(TextExtractionError) as context:
            self.extractor._extract_from_pdf('test.pdf')
        
        # Either error message is acceptable for an empty PDF
        error_msg = str(context.exception)
        self.assertTrue(
            'PDF file contains no pages' in error_msg or 
            'No text could be extracted' in error_msg
        )
    
    # ========================================================================
    # DOCX EXTRACTION TESTS (Mocked)
    # ========================================================================
    
    @patch('mammoth.extract_raw_text')
    @patch('builtins.open', new_callable=mock_open, read_data=b'fake docx content')
    def test_extract_from_docx_success(self, mock_file, mock_mammoth_extract):
        """Test successful DOCX extraction"""
        # Mock mammoth result
        mock_result = MagicMock()
        mock_result.value = 'Extracted DOCX content'
        mock_result.messages = []
        
        mock_mammoth_extract.return_value = mock_result
        
        result = self.extractor._extract_from_docx('test.docx')
        
        self.assertEqual(result, 'Extracted DOCX content')
    
    @patch('mammoth.extract_raw_text')
    @patch('builtins.open', new_callable=mock_open, read_data=b'fake docx content')
    def test_extract_from_docx_empty(self, mock_file, mock_mammoth_extract):
        """Test DOCX with no content"""
        mock_result = MagicMock()
        mock_result.value = ''
        mock_result.messages = []
        
        mock_mammoth_extract.return_value = mock_result
        
        with self.assertRaises(TextExtractionError) as context:
            self.extractor._extract_from_docx('test.docx')
        
        self.assertIn('appears to be empty', str(context.exception))
    
    # ========================================================================
    # INTEGRATION TESTS
    # ========================================================================
    
    def test_extract_with_metadata_structure(self):
        """Test that extract_with_metadata returns correct structure"""
        # Create a test PDF file (mock the extraction)
        test_file = os.path.join(self.test_dir, 'test.pdf')
        Path(test_file).write_text('dummy content')
        
        with patch.object(self.extractor, 'extract_text', return_value='Sample resume text'):
            result = self.extractor.extract_with_metadata(test_file)
        
        # Check structure
        self.assertIn('text', result)
        self.assertIn('file_name', result)
        self.assertIn('file_type', result)
        self.assertIn('file_size', result)
        self.assertIn('char_count', result)
        self.assertIn('word_count', result)
        self.assertIn('line_count', result)
        
        # Check values
        self.assertEqual(result['file_name'], 'test.pdf')
        self.assertEqual(result['file_type'], 'pdf')
        self.assertEqual(result['text'], 'Sample resume text')
        self.assertGreater(result['file_size'], 0)
    
    def test_convenience_function(self):
        """Test the convenience extract_text() function"""
        test_file = os.path.join(self.test_dir, 'test.pdf')
        Path(test_file).touch()
        
        with patch.object(ResumeTextExtractor, 'extract_text', return_value='Test content'):
            result = extract_text(test_file)
        
        self.assertEqual(result, 'Test content')
    
    # ========================================================================
    # ERROR HANDLING TESTS
    # ========================================================================
    
    def test_extract_text_wraps_exceptions(self):
        """Test that unexpected exceptions are wrapped in TextExtractionError"""
        test_file = os.path.join(self.test_dir, 'test.pdf')
        Path(test_file).touch()
        
        with patch.object(self.extractor, '_extract_from_pdf', side_effect=Exception('Unexpected error')):
            with self.assertRaises(TextExtractionError) as context:
                self.extractor.extract_text(test_file)
            
            self.assertIn('Failed to extract text', str(context.exception))
    
    def test_extract_text_preserves_known_exceptions(self):
        """Test that known exceptions are not wrapped"""
        # Test FileNotFoundError
        with self.assertRaises(FileNotFoundError):
            self.extractor.extract_text('/nonexistent/file.pdf')
        
        # Test ValueError for unsupported type
        test_file = os.path.join(self.test_dir, 'test.txt')
        Path(test_file).touch()
        
        with self.assertRaises(ValueError):
            self.extractor.extract_text(test_file)


class TestTextNormalizationEdgeCases(unittest.TestCase):
    """Test edge cases in text normalization"""
    
    def setUp(self):
        self.extractor = ResumeTextExtractor()
    
    def test_complex_resume_structure(self):
        """Test normalization of complex resume structure"""
        resume_text = """
        John Doe
        
        
        Professional Summary
        Experienced software engineer with 5+ years
        
        Experience
        • Led team of 5 developers
        • Increased performance by 40%
        
        Page 1 of 2
        
        Education
        BS Computer Science
        
        Skills
        Python, JavaScript, React
        """
        
        result = self.extractor._normalize_text(resume_text)
        
        # Check that content is preserved
        self.assertIn('John Doe', result)
        self.assertIn('PROFESSIONAL SUMMARY', result)
        self.assertIn('EXPERIENCE', result)
        self.assertIn('EDUCATION', result)
        self.assertIn('SKILLS', result)
        
        # Check that bullets are preserved
        self.assertIn('•', result)
        self.assertIn('Led team', result)
        
        # Check that page numbers are removed
        self.assertNotIn('Page 1 of 2', result)
        
        # Check that excessive whitespace is removed
        self.assertNotIn('\n\n\n', result)
    
    def test_special_characters_preserved(self):
        """Test that special characters in content are preserved"""
        text = 'Email: john@example.com\nPhone: +1 (555) 123-4567\nSkills: C++, .NET'
        result = self.extractor._normalize_text(text)
        
        self.assertIn('@', result)
        self.assertIn('+', result)
        self.assertIn('++', result)
        self.assertIn('.NET', result)
    
    def test_unicode_characters(self):
        """Test handling of unicode characters"""
        text = 'Name: José García\nSkills: Français, Español'
        result = self.extractor._normalize_text(text)
        
        # Check for the base content (may be uppercase due to section heading detection)
        self.assertIn('José', result)
        self.assertIn('García', result)
        # These may be uppercase due to heading detection
        self.assertTrue('Français' in result or 'FRANÇAIS' in result)
        self.assertTrue('Español' in result or 'ESPAÑOL' in result)


class TestSectionHeaderDetection(unittest.TestCase):
    """Test section header detection and emphasis"""
    
    def setUp(self):
        self.extractor = ResumeTextExtractor()
    
    def test_standard_section_headers(self):
        """Test detection of standard resume sections"""
        headers = [
            'Experience',
            'Education',
            'Skills',
            'Projects',
            'Summary',
            'Certifications'
        ]
        
        for header in headers:
            result = self.extractor._emphasize_section_headings(header)
            self.assertIn(header.upper(), result)
    
    def test_section_headers_with_variations(self):
        """Test detection of section header variations"""
        variations = [
            'Work Experience',
            'Professional Experience',
            'Technical Skills',
            'Professional Summary',
            'Career Objective'
        ]
        
        for variation in variations:
            result = self.extractor._emphasize_section_headings(variation)
            self.assertIn(variation.upper(), result)
    
    def test_non_headers_not_emphasized(self):
        """Test that regular content is not emphasized"""
        text = 'Developed software applications for clients'
        result = self.extractor._emphasize_section_headings(text)
        
        # Should remain as-is (not all uppercase)
        self.assertNotEqual(result, text.upper())


# ============================================================================
# TEST RUNNER
# ============================================================================

if __name__ == '__main__':
    # Run tests with verbose output
    unittest.main(verbosity=2)
