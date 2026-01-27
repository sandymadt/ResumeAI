"""
Sample Usage Examples for Resume Text Extraction Module

This script demonstrates various ways to use the text extraction module.
"""

import os
from pathlib import Path
from text_extractor import ResumeTextExtractor, extract_text, TextExtractionError


def example_1_quick_extraction():
    """Example 1: Quick text extraction using convenience function"""
    print("\n" + "="*60)
    print("Example 1: Quick Extraction")
    print("="*60)
    
    # This assumes you have a sample resume file
    # Replace with your actual file path
    sample_file = "sample_resume.pdf"
    
    if not os.path.exists(sample_file):
        print(f"⚠️  Sample file '{sample_file}' not found")
        print("   Please provide a resume file to test")
        return
    
    try:
        # Simple one-liner extraction
        text = extract_text(sample_file)
        
        print(f"✅ Successfully extracted text")
        print(f"\nFirst 500 characters:")
        print("-" * 60)
        print(text[:500])
        print("-" * 60)
        
    except FileNotFoundError:
        print("❌ File not found")
    except ValueError as e:
        print(f"❌ Invalid file type: {e}")
    except TextExtractionError as e:
        print(f"❌ Extraction failed: {e}")


def example_2_with_metadata():
    """Example 2: Extract text with metadata"""
    print("\n" + "="*60)
    print("Example 2: Extraction with Metadata")
    print("="*60)
    
    sample_file = "sample_resume.pdf"
    
    if not os.path.exists(sample_file):
        print(f"⚠️  Sample file '{sample_file}' not found")
        return
    
    try:
        extractor = ResumeTextExtractor()
        result = extractor.extract_with_metadata(sample_file)
        
        print(f"✅ Extraction successful!\n")
        print(f"📄 File Information:")
        print(f"   Name: {result['file_name']}")
        print(f"   Type: {result['file_type'].upper()}")
        print(f"   Size: {result['file_size']:,} bytes")
        print(f"\n📊 Content Statistics:")
        print(f"   Characters: {result['char_count']:,}")
        print(f"   Words: {result['word_count']:,}")
        print(f"   Lines: {result['line_count']:,}")
        
        # Basic analysis
        avg_word_length = result['char_count'] / result['word_count'] if result['word_count'] > 0 else 0
        print(f"   Avg word length: {avg_word_length:.1f} chars")
        
        # Content preview
        print(f"\n📝 Content Preview:")
        print("-" * 60)
        lines = result['text'].split('\n')
        for i, line in enumerate(lines[:10], 1):
            if line.strip():
                print(f"   {i}. {line[:70]}")
        print("-" * 60)
        
    except Exception as e:
        print(f"❌ Error: {e}")


def example_3_batch_processing():
    """Example 3: Batch process multiple files"""
    print("\n" + "="*60)
    print("Example 3: Batch Processing")
    print("="*60)
    
    # Look for resume files in current directory
    resume_dir = Path(".")
    resume_files = list(resume_dir.glob("*.pdf")) + list(resume_dir.glob("*.docx"))
    
    if not resume_files:
        print("⚠️  No resume files found (*.pdf or *.docx)")
        print("   Please add some resume files to test batch processing")
        return
    
    print(f"Found {len(resume_files)} resume files\n")
    
    extractor = ResumeTextExtractor()
    results = []
    
    for resume_file in resume_files:
        try:
            print(f"Processing: {resume_file.name}...", end=" ")
            
            result = extractor.extract_with_metadata(str(resume_file))
            
            results.append({
                'file': resume_file.name,
                'status': 'success',
                'words': result['word_count'],
                'chars': result['char_count']
            })
            
            print(f"✅ ({result['word_count']} words)")
            
        except Exception as e:
            results.append({
                'file': resume_file.name,
                'status': 'failed',
                'error': str(e)
            })
            print(f"❌ Failed")
    
    # Summary
    print(f"\n{'='*60}")
    print("Batch Processing Summary")
    print('='*60)
    
    successful = [r for r in results if r['status'] == 'success']
    failed = [r for r in results if r['status'] == 'failed']
    
    print(f"✅ Successful: {len(successful)}")
    print(f"❌ Failed: {len(failed)}")
    
    if successful:
        total_words = sum(r['words'] for r in successful)
        avg_words = total_words / len(successful)
        print(f"\n📊 Statistics:")
        print(f"   Total words extracted: {total_words:,}")
        print(f"   Average words per resume: {avg_words:.0f}")


def example_4_error_handling():
    """Example 4: Comprehensive error handling"""
    print("\n" + "="*60)
    print("Example 4: Error Handling")
    print("="*60)
    
    test_cases = [
        ("nonexistent_file.pdf", "Non-existent file"),
        ("text_extractor.py", "Wrong file type"),
        ("sample_resume.pdf", "Valid file (if exists)")
    ]
    
    extractor = ResumeTextExtractor()
    
    for file_path, description in test_cases:
        print(f"\nTest: {description}")
        print(f"File: {file_path}")
        
        try:
            text = extractor.extract_text(file_path)
            print(f"✅ Success! Extracted {len(text)} characters")
            
        except FileNotFoundError:
            print("❌ Error: File not found")
            
        except ValueError as e:
            print(f"❌ Error: Invalid file type")
            print(f"   Details: {e}")
            
        except TextExtractionError as e:
            print(f"❌ Error: Extraction failed")
            print(f"   Details: {e}")
            
        except Exception as e:
            print(f"❌ Error: Unexpected error")
            print(f"   Details: {e}")


def example_5_text_analysis():
    """Example 5: Basic text analysis after extraction"""
    print("\n" + "="*60)
    print("Example 5: Text Analysis")
    print("="*60)
    
    sample_file = "sample_resume.pdf"
    
    if not os.path.exists(sample_file):
        print(f"⚠️  Sample file '{sample_file}' not found")
        return
    
    try:
        text = extract_text(sample_file)
        
        # Basic analysis
        print("📊 Resume Analysis:\n")
        
        # Section detection
        sections = [
            'SUMMARY', 'EXPERIENCE', 'EDUCATION', 'SKILLS',
            'PROJECTS', 'CERTIFICATIONS', 'AWARDS'
        ]
        
        found_sections = []
        for section in sections:
            if section in text.upper():
                found_sections.append(section)
        
        print(f"✅ Sections found ({len(found_sections)}):")
        for section in found_sections:
            print(f"   • {section}")
        
        # Bullet point detection
        bullet_count = sum(1 for line in text.split('\n') if line.strip().startswith('•'))
        print(f"\n📍 Bullet points: {bullet_count}")
        
        # Common keywords
        keywords = ['python', 'javascript', 'java', 'react', 'node', 'aws', 'docker']
        found_keywords = [kw for kw in keywords if kw.lower() in text.lower()]
        
        if found_keywords:
            print(f"\n🔑 Technical keywords found:")
            for kw in found_keywords:
                print(f"   • {kw.title()}")
        
        # Email detection
        import re
        emails = re.findall(r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b', text)
        if emails:
            print(f"\n📧 Email: {emails[0]}")
        
        # Phone detection
        phones = re.findall(r'\+?[\d\s()-]{10,}', text)
        if phones:
            print(f"📱 Phone: {phones[0].strip()}")
        
    except Exception as e:
        print(f"❌ Error: {e}")


def main():
    """Run all examples"""
    print("\n" + "="*60)
    print(" Resume Text Extraction Module - Sample Usage")
    print("="*60)
    
    # Run examples
    example_1_quick_extraction()
    example_2_with_metadata()
    example_3_batch_processing()
    example_4_error_handling()
    example_5_text_analysis()
    
    print("\n" + "="*60)
    print("All examples completed!")
    print("="*60 + "\n")


if __name__ == "__main__":
    main()
