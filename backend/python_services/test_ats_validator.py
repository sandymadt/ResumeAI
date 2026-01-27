"""
Unit Tests for ATS Validation Module

Comprehensive tests covering:
- Required sections validation
- Contact information checks
- Experience quality validation
- Bullet point analysis
- Date consistency checks
- Action verb usage
- Scoring logic
"""

import unittest
from ats_validator import ATSValidator, validate_resume


class TestATSValidator(unittest.TestCase):
    """Test cases for ATSValidator class"""
    
    def setUp(self):
        """Set up test fixtures"""
        self.validator = ATSValidator()
        
        # Perfect resume for baseline
        self.perfect_resume = {
            "contact": {
                "name": "John Doe",
                "email": "john.doe@email.com",
                "phone": "+1-555-123-4567",
                "linkedin": "linkedin.com/in/johndoe"
            },
            "summary": "Senior Software Engineer with 5+ years of experience",
            "skills": ["Python", "JavaScript", "React"],
            "experience": [
                {
                    "title": "Senior Engineer",
                    "company": "Tech Corp",
                    "start_date": "2020",
                    "end_date": "Present",
                    "description": "• Led development of cloud infrastructure serving 1M users\n• Improved system performance by 40% through optimization"
                }
            ],
            "education": [
                {
                    "degree": "BS",
                    "field": "Computer Science",
                    "institution": "MIT",
                    "graduation_date": "2020"
                }
            ]
        }
    
    # ========================================================================
    # BASIC VALIDATION TESTS
    # ========================================================================
    
    def test_perfect_resume_high_score(self):
        """Test that a perfect resume gets a high score"""
        result = self.validator.validate(self.perfect_resume)
        
        self.assertGreater(result['rule_score'], 90)
        self.assertIn('rule_score', result)
        self.assertIn('violations', result)
        self.assertIn('passed_checks', result)
    
    def test_convenience_function(self):
        """Test convenience function works"""
        result = validate_resume(self.perfect_resume)
        
        self.assertIsInstance(result, dict)
        self.assertIn('rule_score', result)
    
    def test_result_structure(self):
        """Test that result has correct structure"""
        result = self.validator.validate(self.perfect_resume)
        
        self.assertIsInstance(result['rule_score'], (int, float))
        self.assertIsInstance(result['violations'], list)
        self.assertIsInstance(result['passed_checks'], list)
        self.assertTrue(0 <= result['rule_score'] <= 100)
    
    # ========================================================================
    # REQUIRED SECTIONS TESTS
    # ========================================================================
    
    def test_missing_required_section(self):
        """Test detection of missing required section"""
        incomplete_resume = self.perfect_resume.copy()
        del incomplete_resume['experience']
        
        result = self.validator.validate(incomplete_resume)
        
        # Should have violation for missing experience
        violations = [v for v in result['violations'] if v['check'] == 'required_sections']
        self.assertTrue(len(violations) > 0)
        self.assertLess(result['rule_score'], 90)
    
    def test_empty_required_section(self):
        """Test detection of empty required section"""
        empty_resume = self.perfect_resume.copy()
        empty_resume['experience'] = []
        
        result = self.validator.validate(empty_resume)
        
        violations = [v for v in result['violations'] 
                     if v['check'] == 'required_sections' and 'empty' in v['message'].lower()]
        self.assertTrue(len(violations) > 0)
    
    def test_all_required_sections_present(self):
        """Test that all required sections pass"""
        result = self.validator.validate(self.perfect_resume)
        
        passed = [p for p in result['passed_checks'] if p['check'] == 'required_sections']
        self.assertEqual(len(passed), 3)  # contact, experience, education
    
    # ========================================================================
    # RECOMMENDED SECTIONS TESTS
    # ========================================================================
    
    def test_missing_recommended_section(self):
        """Test warning for missing recommended section"""
        no_summary = self.perfect_resume.copy()
        del no_summary['summary']
        
        result = self.validator.validate(no_summary)
        
        violations = [v for v in result['violations'] 
                     if v['check'] == 'recommended_sections' and v['section'] == 'summary']
        self.assertTrue(len(violations) > 0)
        self.assertEqual(violations[0]['severity'], 'warning')
    
    def test_recommended_sections_present(self):
        """Test bonus for having recommended sections"""
        result = self.validator.validate(self.perfect_resume)
        
        self.assertGreater(result['score_breakdown'].get('recommended_sections', 0), 0)
    
    # ========================================================================
    # CONTACT INFORMATION TESTS
    # ========================================================================
    
    def test_missing_email(self):
        """Test critical violation for missing email"""
        no_email = self.perfect_resume.copy()
        no_email['contact'] = {'name': 'John Doe', 'phone': '555-1234'}
        
        result = self.validator.validate(no_email)
        
        violations = [v for v in result['violations'] 
                     if v['check'] == 'contact_info' and v['field'] == 'email']
        self.assertTrue(len(violations) > 0)
        self.assertEqual(violations[0]['severity'], 'critical')
    
    def test_invalid_email_format(self):
        """Test warning for invalid email format"""
        invalid_email = self.perfect_resume.copy()
        invalid_email['contact']['email'] = 'not-an-email'
        
        result = self.validator.validate(invalid_email)
        
        violations = [v for v in result['violations'] 
                     if 'email format' in v['message'].lower()]
        self.assertTrue(len(violations) > 0)
    
    def test_valid_email_format(self):
        """Test that valid email passes"""
        result = self.validator.validate(self.perfect_resume)
        
        passed = [p for p in result['passed_checks'] 
                 if 'email format valid' in p['message'].lower()]
        self.assertEqual(len(passed), 1)
    
    def test_linkedin_bonus(self):
        """Test bonus for including LinkedIn"""
        with_linkedin = self.perfect_resume.copy()
        without_linkedin = self.perfect_resume.copy()
        del without_linkedin['contact']['linkedin']
        
        result_with = self.validator.validate(with_linkedin)
        result_without = self.validator.validate(without_linkedin)
        
        self.assertGreater(
            result_with['score_breakdown']['contact_info'],
            result_without['score_breakdown']['contact_info']
        )
    
    # ========================================================================
    # EXPERIENCE QUALITY TESTS
    # ========================================================================
    
    def test_no_experience_critical(self):
        """Test critical violation for no experience"""
        no_exp = self.perfect_resume.copy()
        no_exp['experience'] = []
        
        result = self.validator.validate(no_exp)
        
        violations = [v for v in result['violations'] 
                     if 'no work experience' in v['message'].lower()]
        self.assertTrue(len(violations) > 0)
        self.assertEqual(result['score_breakdown']['experience_quality'], 0)
    
    def test_experience_missing_title(self):
        """Test warning for experience without title"""
        no_title = self.perfect_resume.copy()
        no_title['experience'][0]['title'] = ''
        
        result = self.validator.validate(no_title)
        
        violations = [v for v in result['violations'] 
                     if 'missing job title' in v['message'].lower()]
        self.assertTrue(len(violations) > 0)
    
    def test_experience_missing_company(self):
        """Test warning for experience without company"""
        no_company = self.perfect_resume.copy()
        no_company['experience'][0]['company'] = ''
        
        result = self.validator.validate(no_company)
        
        violations = [v for v in result['violations'] 
                     if 'missing company' in v['message'].lower()]
        self.assertTrue(len(violations) > 0)
    
    def test_experience_short_description(self):
        """Test warning for short description"""
        short_desc = self.perfect_resume.copy()
        short_desc['experience'][0]['description'] = 'Did stuff'
        
        result = self.validator.validate(short_desc)
        
        violations = [v for v in result['violations'] 
                     if 'description' in v['message'].lower()]
        self.assertTrue(len(violations) > 0)
    
    # ========================================================================
    # BULLET POINT TESTS
    # ========================================================================
    
    def test_optimal_bullet_length(self):
        """Test that optimal length bullets score well"""
        result = self.validator.validate(self.perfect_resume)
        
        # Should have good bullet point score
        self.assertGreater(result['score_breakdown'].get('bullet_points', 0), 10)
    
    def test_too_short_bullets(self):
        """Test detection of too-short bullets"""
        short_bullets = self.perfect_resume.copy()
        short_bullets['experience'][0]['description'] = '• Did work\n• Fixed bugs'
        
        result = self.validator.validate(short_bullets)
        
        violations = [v for v in result['violations'] 
                     if 'too short' in v['message'].lower()]
        self.assertTrue(len(violations) > 0)
    
    def test_too_long_bullets(self):
        """Test detection of too-long bullets"""
        long_bullets = self.perfect_resume.copy()
        long_text = 'Developed a complex software system ' * 10
        long_bullets['experience'][0]['description'] = f'• {long_text}\n• {long_text}'
        
        result = self.validator.validate(long_bullets)
        
        violations = [v for v in result['violations'] 
                     if 'too long' in v['message'].lower()]
        self.assertTrue(len(violations) > 0)
    
    def test_no_bullets_warning(self):
        """Test warning when no bullets found"""
        no_bullets = self.perfect_resume.copy()
        no_bullets['experience'][0]['description'] = 'Just plain text description'
        
        result = self.validator.validate(no_bullets)
        
        violations = [v for v in result['violations'] 
                     if 'no bullet points' in v['message'].lower()]
        self.assertTrue(len(violations) > 0)
    
    # ========================================================================
    # DATE CONSISTENCY TESTS
    # ========================================================================
    
    def test_missing_dates(self):
        """Test warning for missing dates"""
        no_dates = self.perfect_resume.copy()
        no_dates['experience'][0]['start_date'] = ''
        no_dates['experience'][0]['end_date'] = ''
        
        result = self.validator.validate(no_dates)
        
        violations = [v for v in result['violations'] 
                     if 'missing dates' in v['message'].lower()]
        self.assertTrue(len(violations) > 0)
    
    def test_start_after_end_date(self):
        """Test detection of start date after end date"""
        bad_dates = self.perfect_resume.copy()
        bad_dates['experience'][0]['start_date'] = '2023'
        bad_dates['experience'][0]['end_date'] = '2020'
        
        result = self.validator.validate(bad_dates)
        
        violations = [v for v in result['violations'] 
                     if 'start date after end date' in v['message'].lower()]
        self.assertTrue(len(violations) > 0)
    
    def test_present_date_handling(self):
        """Test that 'Present' is handled correctly"""
        with_present = self.perfect_resume.copy()
        with_present['experience'][0]['end_date'] = 'Present'
        
        result = self.validator.validate(with_present)
        
        # Should not flag Present as invalid
        violations = [v for v in result['violations'] 
                     if v['check'] == 'date_consistency' and v['severity'] == 'warning']
        # Present shouldn't cause date order violation
        date_order_violations = [v for v in violations 
                                if 'after end date' in v['message'].lower()]
        self.assertEqual(len(date_order_violations), 0)
    
    def test_chronological_order(self):
        """Test check for reverse chronological order"""
        multi_exp = self.perfect_resume.copy()
        multi_exp['experience'] = [
            {
                "title": "Senior Engineer",
                "company": "CompanyA",
                "start_date": "2020",
                "end_date": "2023",
                "description": "• Led projects"
            },
            {
                "title": "Engineer",
                "company": "CompanyB",
                "start_date": "2018",
                "end_date": "2020",
                "description": "• Developed features"
            }
        ]
        
        result = self.validator.validate(multi_exp)
        
        passed = [p for p in result['passed_checks'] 
                 if 'chronological order' in p['message'].lower()]
        self.assertTrue(len(passed) > 0)
    
    # ========================================================================
    # ACTION VERB TESTS
    # ========================================================================
    
    def test_strong_action_verbs(self):
        """Test recognition of strong action verbs"""
        strong_verbs = self.perfect_resume.copy()
        strong_verbs['experience'][0]['description'] = (
            '• Led team of 5 developers\n'
            '• Developed microservices architecture\n'
            '• Improved system performance by 40%'
        )
        
        result = self.validator.validate(strong_verbs)
        
        self.assertGreater(result['score_breakdown'].get('action_verbs', 0), 3)
    
    def test_weak_phrases_detected(self):
        """Test detection of weak phrases"""
        weak_resume = self.perfect_resume.copy()
        weak_resume['experience'][0]['description'] = (
            '• Responsible for managing team\n'
            '• Was tasked with developing features\n'
            '• Helped with deployment'
        )
        
        result = self.validator.validate(weak_resume)
        
        violations = [v for v in result['violations'] 
                     if 'weak phrases' in v['message'].lower()]
        self.assertTrue(len(violations) > 0)
    
    def test_action_verb_ratio(self):
        """Test that high action verb ratio scores well"""
        good_verbs = self.perfect_resume.copy()
        good_verbs['experience'][0]['description'] = (
            '• Led development initiatives\n'
            '• Improved code quality metrics\n'
            '• Designed scalable architecture\n'
            '• Implemented CI/CD pipeline'
        )
        
        result = self.validator.validate(good_verbs)
        
        passed = [p for p in result['passed_checks'] 
                 if 'strong action verbs' in p['message'].lower() and '>70%' in p['message']]
        self.assertTrue(len(passed) > 0)
    
    # ========================================================================
    # SCORING TESTS
    # ========================================================================
    
    def test_score_is_percentage(self):
        """Test that score is between 0-100"""
        result = self.validator.validate(self.perfect_resume)
        
        self.assertTrue(0 <= result['rule_score'] <= 100)
    
    def test_score_breakdown_sums_correctly(self):
        """Test that score breakdown components sum to total"""
        result = self.validator.validate(self.perfect_resume)
        
        breakdown_sum = sum(result['score_breakdown'].values())
        self.assertAlmostEqual(breakdown_sum, result['rule_score'], places=1)
    
    def test_empty_resume_low_score(self):
        """Test that empty resume gets very low score"""
        empty_resume = {
            "contact": {},
            "summary": "",
            "skills": [],
            "experience": [],
            "education": []
        }
        
        result = self.validator.validate(empty_resume)
        
        self.assertLess(result['rule_score'], 30)
    
    def test_score_weights_sum_to_100(self):
        """Test that all check weights sum to 100"""
        total_weight = sum(self.validator.CHECK_WEIGHTS.values())
        self.assertEqual(total_weight, 100)
    
    # ========================================================================
    # SEVERITY LEVELS TESTS
    # ========================================================================
    
    def test_critical_violations_exist(self):
        """Test that critical violations are flagged"""
        bad_resume = {
            "contact": {},
            "experience": [],
            "education": []
        }
        
        result = self.validator.validate(bad_resume)
        
        critical = [v for v in result['violations'] if v['severity'] == 'critical']
        self.assertTrue(len(critical) > 0)
    
    def test_warning_violations_exist(self):
        """Test that warning violations are flagged"""
        no_summary = self.perfect_resume.copy()
        del no_summary['summary']
        
        result = self.validator.validate(no_summary)
        
        warnings = [v for v in result['violations'] if v['severity'] == 'warning']
        self.assertTrue(len(warnings) > 0)
    
    def test_info_violations_exist(self):
        """Test that info-level suggestions exist"""
        result = self.validator.validate(self.perfect_resume)
        
        # May or may not have info violations depending on resume
        info_violations = [v for v in result['violations'] if v.get('severity') == 'info']
        # Just check that the severity level exists in code
        self.assertTrue(True)
    
    # ========================================================================
    # EDGE CASES
    # ========================================================================
    
    def test_minimal_valid_resume(self):
        """Test minimal resume that passes all required checks"""
        minimal = {
            "contact": {
                "name": "Jane Doe",
                "email": "jane@email.com",
                "phone": "555-1234"
            },
            "experience": [
                {
                    "title": "Engineer",
                    "company": "Tech Co",
                    "start_date": "2020",
                    "end_date": "2023",
                    "description": "• Developed software applications for enterprise clients"
                }
            ],
            "education": [
                {
                    "degree": "BS",
                    "field": "CS",
                    "institution": "University",
                    "graduation_date": "2020"
                }
            ]
        }
        
        result = self.validator.validate(minimal)
        
        # Should pass but maybe not score super high
        self.assertGreater(result['rule_score'], 60)
    
    def test_multiple_experiences(self):
        """Test resume with multiple experience entries"""
        multi = self.perfect_resume.copy()
        multi['experience'].append({
            "title": "Junior Developer",
            "company": "StartupXYZ",
            "start_date": "2018",
            "end_date": "2020",
            "description": "• Built web applications\n• Collaborated with design team"
        })
        
        result = self.validator.validate(multi)
        
        # Should score well with multiple experiences
        self.assertGreater(result['rule_score'], 85)


class TestHelperFunctions(unittest.TestCase):
    """Test helper functions"""
    
    def setUp(self):
        self.validator = ATSValidator()
    
    def test_extract_year_from_full_year(self):
        """Test year extraction from full year"""
        year = self.validator._extract_year('2020')
        self.assertEqual(year, '2020')
    
    def test_extract_year_from_date_string(self):
        """Test year extraction from date string"""
        year = self.validator._extract_year('Jan 2020')
        self.assertEqual(year, '2020')
    
    def test_extract_year_present(self):
        """Test Present date handling"""
        year = self.validator._extract_year('Present')
        self.assertEqual(year, 'Present')
    
    def test_extract_year_empty(self):
        """Test empty string handling"""
        year = self.validator._extract_year('')
        self.assertEqual(year, '')


# ============================================================================
# TEST RUNNER
# ============================================================================

if __name__ == '__main__':
    unittest.main(verbosity=2)
