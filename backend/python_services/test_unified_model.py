"""
Test script for the Unified Resume Analysis Model

This script demonstrates how to use the unified model and validates
that all services are working correctly.
"""

import sys
import json
from pathlib import Path

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent))

from unified_model import UnifiedResumeAnalyzer, analyze_resume


def test_basic_usage():
    """Test 1: Basic usage with sample data"""
    print("="*70)
    print("TEST 1: Basic Usage")
    print("="*70)
    
    # Sample resume text
    sample_resume = """
    John Doe
    Software Engineer
    Email: john.doe@email.com
    Phone: +1-555-123-4567
    LinkedIn: linkedin.com/in/johndoe
    
    PROFESSIONAL SUMMARY
    Senior Software Engineer with 5+ years of experience in full-stack development.
    
    SKILLS
    Python, JavaScript, React, Node.js, AWS, Docker, Git
    
    EXPERIENCE
    
    Senior Software Engineer | Tech Corp | 2020 - Present
    • Led development of microservices architecture using Python and Docker
    • Improved system performance by 40% through optimization
    • Mentored 5 junior developers on best practices
    • Implemented CI/CD pipelines reducing deployment time by 60%
    
    Software Engineer | StartupXYZ | 2018 - 2020
    • Developed RESTful APIs using Node.js and Express
    • Built responsive web applications with React
    • Collaborated with cross-functional teams
    
    EDUCATION
    
    Master of Science in Computer Science
    Stanford University | 2018
    """
    
    try:
        result = analyze_resume(
            resume_text=sample_resume,
            enable_detailed_logging=True
        )
        
        print("\n✅ Analysis completed successfully!")
        print(f"   ATS Score: {result['ats_score']}/100")
        print(f"   Grade: {result['metadata']['grade']}")
        print(f"   Duration: {result['metadata'].get('analysis_duration_seconds', 0)}s")
        
        return True
    except Exception as e:
        print(f"\n❌ Test failed: {str(e)}")
        return False


def test_with_job_description():
    """Test 2: Analysis with job description"""
    print("\n" + "="*70)
    print("TEST 2: Analysis with Job Description")
    print("="*70)
    
    sample_resume = """
    Jane Smith
    Full Stack Developer
    jane.smith@email.com | 555-9876
    
    SKILLS
    Python, React, TypeScript, AWS, PostgreSQL
    
    EXPERIENCE
    Full Stack Developer | WebCo | 2019-Present
    • Built scalable web applications using React and Python
    • Designed RESTful APIs and microservices
    • Managed AWS infrastructure
    """
    
    job_description = """
    We are seeking a Senior Full Stack Developer with:
    - 3+ years of Python and React experience
    - TypeScript proficiency
    - AWS cloud experience
    - Docker and Kubernetes knowledge
    - PostgreSQL database skills
    """
    
    try:
        result = analyze_resume(
            resume_text=sample_resume,
            job_description=job_description,
            enable_detailed_logging=False
        )
        
        print("\n✅ Analysis completed successfully!")
        print(f"   ATS Score: {result['ats_score']}/100")
        print(f"   Matched Skills: {len(result['matched_skills'])}")
        print(f"   Missing Skills: {len(result['missing_skills'])}")
        
        if result['missing_skills']:
            print(f"\n   Missing: {', '.join(result['missing_skills'][:5])}")
        
        return True
    except Exception as e:
        print(f"\n❌ Test failed: {str(e)}")
        return False


def test_class_usage():
    """Test 3: Using the UnifiedResumeAnalyzer class"""
    print("\n" + "="*70)
    print("TEST 3: Class-Based Usage")
    print("="*70)
    
    sample_resume = """
    Alex Johnson
    Data Scientist
    alex@email.com
    
    SKILLS
    Python, Machine Learning, TensorFlow, SQL, Pandas
    
    EXPERIENCE
    Data Scientist | DataCorp | 2020-Present
    • Developed machine learning models with 95% accuracy
    • Analyzed large datasets using Python and SQL
    • Created data visualizations for stakeholders
    """
    
    try:
        # Initialize analyzer
        analyzer = UnifiedResumeAnalyzer(
            use_llm_feedback=False,
            enable_detailed_logging=False
        )
        
        # Analyze
        result = analyzer.analyze(resume_text=sample_resume)
        
        print("\n✅ Analysis completed successfully!")
        print(f"   ATS Score: {result['ats_score']}/100")
        print(f"   Strengths: {len(result['strengths'])}")
        print(f"   Suggestions: {len(result['improvement_suggestions'])}")
        
        if result['strengths']:
            print(f"\n   Top Strength: {result['strengths'][0]}")
        
        return True
    except Exception as e:
        print(f"\n❌ Test failed: {str(e)}")
        return False


def test_output_format():
    """Test 4: Validate output format"""
    print("\n" + "="*70)
    print("TEST 4: Output Format Validation")
    print("="*70)
    
    sample_resume = """
    Test User
    test@email.com
    
    SKILLS
    Python, Java
    
    EXPERIENCE
    Developer | Company | 2020-2023
    • Developed software applications
    """
    
    try:
        result = analyze_resume(
            resume_text=sample_resume,
            enable_detailed_logging=False
        )
        
        # Validate required fields
        required_fields = [
            'ats_score',
            'section_scores',
            'matched_skills',
            'missing_skills',
            'strengths',
            'improvement_suggestions',
            'feedback',
            'detailed_results',
            'metadata'
        ]
        
        missing_fields = []
        for field in required_fields:
            if field not in result:
                missing_fields.append(field)
        
        if missing_fields:
            print(f"\n❌ Missing fields: {', '.join(missing_fields)}")
            return False
        
        print("\n✅ All required fields present!")
        print(f"   Fields validated: {len(required_fields)}")
        
        # Validate section scores
        section_scores = result['section_scores']
        required_sections = [
            'ats_compliance',
            'keyword_matching',
            'impact_quality',
            'formatting'
        ]
        
        for section in required_sections:
            if section not in section_scores:
                print(f"\n❌ Missing section score: {section}")
                return False
        
        print(f"   Section scores validated: {len(required_sections)}")
        
        return True
    except Exception as e:
        print(f"\n❌ Test failed: {str(e)}")
        return False


def test_error_handling():
    """Test 5: Error handling"""
    print("\n" + "="*70)
    print("TEST 5: Error Handling")
    print("="*70)
    
    try:
        # Test with empty text
        result = analyze_resume(
            resume_text="",
            enable_detailed_logging=False
        )
        
        # Should return error output
        if result['metadata'].get('error'):
            print("\n✅ Error handling works correctly!")
            print(f"   Error message: {result['metadata']['error_message'][:50]}...")
            return True
        else:
            print("\n❌ Should have returned error for empty text")
            return False
            
    except Exception as e:
        print(f"\n⚠️  Exception raised (acceptable): {str(e)[:50]}...")
        return True


def run_all_tests():
    """Run all tests"""
    print("\n" + "="*70)
    print("       UNIFIED RESUME ANALYSIS MODEL - TEST SUITE")
    print("="*70)
    
    tests = [
        ("Basic Usage", test_basic_usage),
        ("Job Description Matching", test_with_job_description),
        ("Class-Based Usage", test_class_usage),
        ("Output Format", test_output_format),
        ("Error Handling", test_error_handling)
    ]
    
    results = []
    
    for test_name, test_func in tests:
        try:
            result = test_func()
            results.append((test_name, result))
        except Exception as e:
            print(f"\n❌ {test_name} crashed: {str(e)}")
            results.append((test_name, False))
    
    # Summary
    print("\n" + "="*70)
    print("TEST SUMMARY")
    print("="*70)
    
    passed = sum(1 for _, result in results if result)
    total = len(results)
    
    for test_name, result in results:
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"{status} - {test_name}")
    
    print("\n" + "="*70)
    print(f"Results: {passed}/{total} tests passed")
    print("="*70)
    
    return passed == total


if __name__ == '__main__':
    success = run_all_tests()
    sys.exit(0 if success else 1)
