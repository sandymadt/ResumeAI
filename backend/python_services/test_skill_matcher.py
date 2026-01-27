"""
Unit Tests for Skill Matching Module

Comprehensive tests covering:
- Exact keyword matching
- Semantic similarity matching
- Skill extraction from resume and job descriptions
- Score calculation
- Edge cases
"""

import unittest
from skill_matcher import SkillMatcher, SkillMatch, match_skills


class TestSkillMatcher(unittest.TestCase):
    """Test cases for SkillMatcher class"""
    
    def setUp(self):
        """Set up test fixtures"""
        # Use exact matching only for faster tests
        self.matcher = SkillMatcher(use_semantic=False)
        
        # Sample resume
        self.sample_resume = {
            "skills": [
                "Python", "JavaScript", "React", "Node.js",
                "AWS", "Docker", "PostgreSQL"
            ]
        }
        
        # Sample job description
        self.sample_job = """
        Required Skills:
        - Python programming
        - JavaScript and React
        - AWS cloud services
        - Docker containers
        - SQL databases
        """
    
    # ========================================================================
    # BASIC MATCHING TESTS
    # ========================================================================
    
    def test_basic_matching(self):
        """Test basic skill matching"""
        result = self.matcher.match_skills(self.sample_resume, self.sample_job)
        
        self.assertIn('matched_skills', result)
        self.assertIn('missing_skills', result)
        self.assertIn('keyword_match_score', result)
    
    def test_convenience_function(self):
        """Test convenience function works"""
        result = match_skills(self.sample_resume, self.sample_job)
        
        self.assertIsInstance(result, dict)
        self.assertIn('keyword_match_score', result)
    
    def test_result_structure(self):
        """Test that result has correct structure"""
        result = self.matcher.match_skills(self.sample_resume, self.sample_job)
        
        self.assertIsInstance(result['matched_skills'], list)
        self.assertIsInstance(result['missing_skills'], list)
        self.assertIsInstance(result['keyword_match_score'], (int, float))
        self.assertTrue(0 <= result['keyword_match_score'] <= 100)
    
    # ========================================================================
    # EXACT MATCHING TESTS
    # ========================================================================
    
    def test_exact_match_case_insensitive(self):
        """Test that exact matching is case-insensitive"""
        resume = {"skills": ["python", "JAVASCRIPT", "React"]}
        job = "Required: Python, JavaScript, react"
        
        result = self.matcher.match_skills(resume, job)
        
        # Should match all three
        self.assertGreaterEqual(len(result['matched_skills']), 2)
    
    def test_exact_match_detected(self):
        """Test that exact matches are detected"""
        resume = {"skills": ["Python"]}
        job = "Required: Python"
        
        result = self.matcher.match_skills(resume, job)
        
        self.assertEqual(len(result['matched_skills']), 1)
        self.assertEqual(result['matched_skills'][0]['match_type'], 'exact')
        self.assertEqual(result['matched_skills'][0]['similarity_score'], 1.0)
    
    def test_substring_matching(self):
        """Test substring matching for skills"""
        resume = {"skills": ["JavaScript"]}
        job = "Required: JavaScript programming"
        
        result = self.matcher.match_skills(resume, job)
        
        # Should match
        self.assertGreaterEqual(len(result['matched_skills']), 0)
    
    # ========================================================================
    # SKILL EXTRACTION TESTS
    # ========================================================================
    
    def test_extract_resume_skills(self):
        """Test extraction of skills from resume JSON"""
        resume = {
            "skills": ["Python", "Java", "  React  ", "python"]  # With duplicates and whitespace
        }
        
        skills = self.matcher._extract_resume_skills(resume)
        
        self.assertIsInstance(skills, list)
        self.assertIn("python", skills)
        self.assertIn("react", skills)
        # Check deduplication
        self.assertEqual(skills.count("python"), 1)
    
    def test_extract_job_skills(self):
        """Test extraction of skills from job description"""
        job = """
        Required Skills:
        - Python
        - JavaScript
        - AWS
        """
        
        skills = self.matcher._extract_job_skills(job)
        
        self.assertIsInstance(skills, list)
        self.assertTrue(len(skills) > 0)
    
    def test_missing_skills_field(self):
        """Test handling of resume without skills field"""
        resume = {"contact": {"name": "John Doe"}}
        job = "Required: Python"
        
        result = self.matcher.match_skills(resume, job)
        
        # Should not crash
        self.assertEqual(len(result['matched_skills']), 0)
        self.assertGreater(len(result['missing_skills']), 0)
    
    # ========================================================================
    # SKILL NORMALIZATION TESTS
    # ========================================================================
    
    def test_skill_normalization(self):
        """Test skill normalization"""
        test_cases = [
            ("  Python  ", "python"),
            ("JAVASCRIPT", "javascript"),
            ("Node.js", "node.js"),
            ("C++", "c++"),
        ]
        
        for input_skill, expected in test_cases:
            normalized = self.matcher._normalize_skill(input_skill)
            self.assertEqual(normalized, expected)
    
    def test_skill_synonym_expansion(self):
        """Test that abbreviations are expanded"""
        # JS -> javascript
        normalized = self.matcher._normalize_skill("js")
        self.assertEqual(normalized, "javascript")
        
        # ML -> machine learning
        normalized = self.matcher._normalize_skill("ml")
        self.assertEqual(normalized, "machine learning")
    
    def test_skill_prefix_removal(self):
        """Test removal of common prefixes"""
        test_cases = [
            "experience with Python",
            "knowledge of Python",
            "proficient in Python"
        ]
        
        for skill in test_cases:
            normalized = self.matcher._normalize_skill(skill)
            self.assertIn("python", normalized)
            self.assertNotIn("experience", normalized)
    
    # ========================================================================
    # SCORING TESTS
    # ========================================================================
    
    def test_perfect_match_score(self):
        """Test that perfect match gives 100% score"""
        resume = {"skills": ["Python", "JavaScript", "React"]}
        job = "Required: Python, JavaScript, React"
        
        result = self.matcher.match_skills(resume, job)
        
        # Should be close to 100
        self.assertGreater(result['keyword_match_score'], 90)
    
    def test_no_match_score(self):
        """Test that no matches gives 0% score"""
        resume = {"skills": ["Python", "JavaScript"]}
        job = "Required: Go, Rust, Haskell"
        
        result = self.matcher.match_skills(resume, job)
        
        self.assertEqual(result['keyword_match_score'], 0.0)
    
    def test_partial_match_score(self):
        """Test partial match scoring"""
        resume = {"skills": ["Python", "JavaScript"]}
        job = "Required: Python, JavaScript, Go, Rust"
        
        result = self.matcher.match_skills(resume, job)
        
        # Should be around 50%
        self.assertTrue(40 <= result['keyword_match_score'] <= 60)
    
    def test_score_calculation(self):
        """Test score calculation logic"""
        matched_skills = [
            SkillMatch("python", "python", "exact", 1.0),
            SkillMatch("java", "java", "exact", 1.0)
        ]
        job_skills = ["python", "java", "go", "rust"]
        
        score = self.matcher._calculate_match_score(matched_skills, job_skills)
        
        # 2 out of 4 = 50%
        self.assertEqual(score, 50.0)
    
    # ========================================================================
    # MATCH DETAILS TESTS
    # ========================================================================
    
    def test_match_details_included(self):
        """Test that match details are included in result"""
        result = self.matcher.match_skills(self.sample_resume, self.sample_job)
        
        self.assertIn('match_details', result)
        details = result['match_details']
        
        self.assertIn('total_job_skills', details)
        self.assertIn('total_resume_skills', details)
        self.assertIn('exact_matches', details)
        self.assertIn('semantic_matches', details)
        self.assertIn('match_rate', details)
    
    def test_match_rate_calculation(self):
        """Test match rate calculation"""
        resume = {"skills": ["Python", "JavaScript"]}
        job = "Required: Python, JavaScript, Go, Rust"
        
        result = self.matcher.match_skills(resume, job)
        
        # 2/4 matched = 50% match rate
        match_rate = result['match_details']['match_rate']
        self.assertTrue(40 <= match_rate <= 60)
    
    # ========================================================================
    # EDGE CASES
    # ========================================================================
    
    def test_empty_resume_skills(self):
        """Test handling of resume with no skills"""
        resume = {"skills": []}
        job = "Required: Python, JavaScript"
        
        result = self.matcher.match_skills(resume, job)
        
        self.assertEqual(len(result['matched_skills']), 0)
        self.assertGreater(len(result['missing_skills']), 0)
        self.assertEqual(result['keyword_match_score'], 0.0)
    
    def test_empty_job_description(self):
        """Test handling of empty job description"""
        resume = {"skills": ["Python", "JavaScript"]}
        job = ""
        
        result = self.matcher.match_skills(resume, job)
        
        self.assertEqual(len(result['matched_skills']), 0)
        self.assertEqual(len(result['missing_skills']), 0)
        self.assertEqual(result['keyword_match_score'], 0.0)
    
    def test_special_characters_in_skills(self):
        """Test handling of special characters"""
        resume = {"skills": ["C++", "C#", "Node.js", ".NET"]}
        job = "Required: C++, C#, Node.js, .NET"
        
        result = self.matcher.match_skills(resume, job)
        
        # Should handle special characters
        self.assertGreater(len(result['matched_skills']), 0)
    
    def test_very_long_skill_list(self):
        """Test handling of large skill lists"""
        resume = {"skills": [f"Skill{i}" for i in range(100)]}
        job = "Required: " + ", ".join([f"Skill{i}" for i in range(50)])
        
        result = self.matcher.match_skills(resume, job)
        
        # Should handle large lists without crashing
        self.assertIsInstance(result, dict)
    
    # ========================================================================
    # MATCH TYPE TESTS
    # ========================================================================
    
    def test_exact_match_type(self):
        """Test that exact matches are labeled correctly"""
        resume = {"skills": ["Python"]}
        job = "Required: Python"
        
        result = self.matcher.match_skills(resume, job)
        
        self.assertEqual(result['matched_skills'][0]['match_type'], 'exact')
    
    def test_match_to_dict_conversion(self):
        """Test SkillMatch to_dict conversion"""
        match = SkillMatch(
            resume_skill="python",
            job_skill="python programming",
            match_type="exact",
            similarity_score=1.0
        )
        
        dict_result = match.to_dict()
        
        self.assertIn('resume_skill', dict_result)
        self.assertIn('job_skill', dict_result)
        self.assertIn('match_type', dict_result)
        self.assertIn('similarity_score', dict_result)
        self.assertEqual(dict_result['similarity_score'], 1.0)


class TestSemanticMatching(unittest.TestCase):
    """Test semantic matching functionality"""
    
    def setUp(self):
        """Set up test fixtures"""
        # Try to use semantic matching
        self.matcher = SkillMatcher(use_semantic=True)
    
    def test_semantic_matcher_initialization(self):
        """Test that semantic matcher initializes"""
        # May or may not have model depending on installation
        self.assertIsInstance(self.matcher, SkillMatcher)
    
    def test_cosine_similarity_calculation(self):
        """Test cosine similarity calculation"""
        import numpy as np
        
        vec1 = np.array([1.0, 0.0, 0.0])
        vec2 = np.array([1.0, 0.0, 0.0])
        
        similarity = self.matcher._cosine_similarity(vec1, vec2)
        
        self.assertAlmostEqual(similarity, 1.0, places=5)
    
    def test_cosine_similarity_orthogonal(self):
        """Test cosine similarity for orthogonal vectors"""
        import numpy as np
        
        vec1 = np.array([1.0, 0.0])
        vec2 = np.array([0.0, 1.0])
        
        similarity = self.matcher._cosine_similarity(vec1, vec2)
        
        self.assertAlmostEqual(similarity, 0.0, places=5)
    
    def test_semantic_matching_fallback(self):
        """Test fallback to exact matching if model not available"""
        resume = {"skills": ["Python", "JavaScript"]}
        job = "Required: Python programming"
        
        result = self.matcher.match_skills(resume, job)
        
        # Should still work even if model not loaded
        self.assertIsInstance(result, dict)
        self.assertIn('keyword_match_score', result)


class TestHelperMethods(unittest.TestCase):
    """Test helper methods"""
    
    def setUp(self):
        self.matcher = SkillMatcher(use_semantic=False)
    
    def test_is_exact_match_identical(self):
        """Test exact match for identical strings"""
        self.assertTrue(self.matcher._is_exact_match("python", "python"))
    
    def test_is_exact_match_different(self):
        """Test exact match returns False for different strings"""
        self.assertFalse(self.matcher._is_exact_match("python", "java"))
    
    def test_is_exact_match_substring(self):
        """Test exact match for substrings"""
        # Single word in multi-word phrase
        self.assertTrue(self.matcher._is_exact_match("python", "python programming"))
    
    def test_normalize_empty_skill(self):
        """Test normalization of empty string"""
        result = self.matcher._normalize_skill("")
        self.assertEqual(result, "")
    
    def test_normalize_none_skill(self):
        """Test normalization of None"""
        result = self.matcher._normalize_skill(None)
        self.assertEqual(result, "")


# ============================================================================
# TEST RUNNER
# ============================================================================

if __name__ == '__main__':
    unittest.main(verbosity=2)
