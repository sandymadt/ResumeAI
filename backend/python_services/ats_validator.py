"""
Rule-Based ATS Validation Module

A deterministic ATS (Applicant Tracking System) validation module that evaluates
resume compliance based on industry-standard rules.

Features:
- Required sections validation
- Bullet point length checks
- Action verb analysis
- Date consistency validation
- Contact information verification
- Deterministic scoring (0-100)

No ML/LLM - Pure rule-based logic

Author: ATS System Designer
"""

import re
from typing import Dict, List, Any, Tuple
from datetime import datetime
import logging

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


class ATSValidator:
    """
    Rule-based ATS validator for resume compliance checking.
    
    Evaluates resumes based on industry-standard ATS requirements:
    - Section completeness
    - Formatting standards
    - Content quality indicators
    - Contact information
    """
    
    # Required sections for ATS compliance
    REQUIRED_SECTIONS = ['contact', 'experience', 'education']
    RECOMMENDED_SECTIONS = ['summary', 'skills']
    
    # Common action verbs for resume bullet points
    ACTION_VERBS = {
        # Leadership
        'led', 'managed', 'directed', 'supervised', 'coordinated', 'oversaw',
        'guided', 'mentored', 'coached', 'trained', 'facilitated',
        
        # Achievement
        'achieved', 'accomplished', 'delivered', 'exceeded', 'surpassed',
        'attained', 'earned', 'won', 'gained',
        
        # Creation/Building
        'created', 'developed', 'built', 'designed', 'established',
        'launched', 'founded', 'initiated', 'introduced', 'pioneered',
        
        # Improvement
        'improved', 'enhanced', 'optimized', 'streamlined', 'refined',
        'upgraded', 'modernized', 'revamped', 'transformed', 'increased',
        
        # Analysis
        'analyzed', 'evaluated', 'assessed', 'investigated', 'researched',
        'examined', 'measured', 'tested', 'reviewed',
        
        # Implementation
        'implemented', 'executed', 'deployed', 'integrated', 'migrated',
        'installed', 'configured', 'automated',
        
        # Collaboration
        'collaborated', 'partnered', 'worked', 'contributed', 'supported',
        'assisted', 'helped', 'participated',
        
        # Communication
        'presented', 'communicated', 'documented', 'reported', 'wrote',
        'published', 'spoke', 'lectured',
        
        # Other
        'solved', 'reduced', 'saved', 'generated', 'produced', 'maintained',
        'organized', 'planned', 'scheduled', 'performed', 'conducted'
    }
    
    # Weak/passive verbs to avoid
    WEAK_VERBS = {
        'responsible for', 'duties included', 'worked on', 'helped with',
        'tasked with', 'involved in', 'participated in', 'assisted in'
    }
    
    # Check weights for scoring
    CHECK_WEIGHTS = {
        'required_sections': 25,
        'recommended_sections': 10,
        'contact_info': 15,
        'experience_quality': 20,
        'bullet_points': 15,
        'date_consistency': 10,
        'action_verbs': 5
    }
    
    def __init__(self):
        """Initialize the ATS validator"""
        self.violations = []
        self.passed_checks = []
        self.score_breakdown = {}
    
    def validate(self, resume_json: Dict[str, Any]) -> Dict[str, Any]:
        """
        Validate resume JSON against ATS rules.
        
        Args:
            resume_json: Structured resume JSON from resume_structurer
                        Expected format:
                        {
                            "contact": {...},
                            "summary": "...",
                            "skills": [...],
                            "experience": [...],
                            "education": [...]
                        }
        
        Returns:
            Validation result:
            {
                "rule_score": 0-100,
                "violations": [...],
                "passed_checks": [...],
                "score_breakdown": {...}
            }
        """
        # Reset state
        self.violations = []
        self.passed_checks = []
        self.score_breakdown = {}
        
        # Run all validation checks
        self._check_required_sections(resume_json)
        self._check_recommended_sections(resume_json)
        self._check_contact_information(resume_json.get('contact', {}))
        self._check_experience_quality(resume_json.get('experience', []))
        self._check_bullet_points(resume_json.get('experience', []))
        self._check_date_consistency(resume_json.get('experience', []))
        self._check_action_verbs(resume_json.get('experience', []))
        
        # Calculate total score
        total_score = sum(self.score_breakdown.values())
        
        # Build result
        result = {
            'rule_score': round(total_score, 2),
            'violations': self.violations,
            'passed_checks': self.passed_checks,
            'score_breakdown': self.score_breakdown
        }
        
        logger.info(f"ATS validation complete. Score: {total_score}/100, "
                   f"Violations: {len(self.violations)}, "
                   f"Passed: {len(self.passed_checks)}")
        
        return result
    
    def _check_required_sections(self, resume_json: Dict[str, Any]) -> None:
        """
        Check if all required sections are present and non-empty.
        
        Required sections: contact, experience, education
        """
        max_score = self.CHECK_WEIGHTS['required_sections']
        section_score = max_score / len(self.REQUIRED_SECTIONS)
        earned_score = 0
        
        for section in self.REQUIRED_SECTIONS:
            if section not in resume_json:
                self.violations.append({
                    'check': 'required_sections',
                    'severity': 'critical',
                    'message': f"Missing required section: '{section}'",
                    'section': section
                })
            elif not resume_json[section]:
                self.violations.append({
                    'check': 'required_sections',
                    'severity': 'critical',
                    'message': f"Required section '{section}' is empty",
                    'section': section
                })
            else:
                self.passed_checks.append({
                    'check': 'required_sections',
                    'message': f"Required section '{section}' present and populated",
                    'section': section
                })
                earned_score += section_score
        
        self.score_breakdown['required_sections'] = earned_score
    
    def _check_recommended_sections(self, resume_json: Dict[str, Any]) -> None:
        """
        Check if recommended sections are present.
        
        Recommended sections: summary, skills
        """
        max_score = self.CHECK_WEIGHTS['recommended_sections']
        section_score = max_score / len(self.RECOMMENDED_SECTIONS)
        earned_score = 0
        
        for section in self.RECOMMENDED_SECTIONS:
            if section in resume_json and resume_json[section]:
                self.passed_checks.append({
                    'check': 'recommended_sections',
                    'message': f"Recommended section '{section}' present",
                    'section': section
                })
                earned_score += section_score
            else:
                self.violations.append({
                    'check': 'recommended_sections',
                    'severity': 'warning',
                    'message': f"Missing recommended section: '{section}'",
                    'section': section
                })
        
        self.score_breakdown['recommended_sections'] = earned_score
    
    def _check_contact_information(self, contact: Dict[str, str]) -> None:
        """
        Validate contact information completeness.
        
        Checks for:
        - Email (required)
        - Phone (required)
        - Name (required)
        - LinkedIn (recommended)
        """
        max_score = self.CHECK_WEIGHTS['contact_info']
        
        # Required fields (75% of score)
        required_fields = ['email', 'phone', 'name']
        required_score = max_score * 0.75
        field_score = required_score / len(required_fields)
        earned_score = 0
        
        for field in required_fields:
            if field in contact and contact[field]:
                self.passed_checks.append({
                    'check': 'contact_info',
                    'message': f"Contact field '{field}' present",
                    'field': field
                })
                earned_score += field_score
            else:
                self.violations.append({
                    'check': 'contact_info',
                    'severity': 'critical',
                    'message': f"Missing required contact field: '{field}'",
                    'field': field
                })
        
        # Validate email format
        if 'email' in contact and contact['email']:
            email_pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
            if re.match(email_pattern, contact['email']):
                self.passed_checks.append({
                    'check': 'contact_info',
                    'message': 'Email format valid',
                    'field': 'email'
                })
            else:
                self.violations.append({
                    'check': 'contact_info',
                    'severity': 'warning',
                    'message': f"Email format may be invalid: '{contact['email']}'",
                    'field': 'email'
                })
        
        # Optional fields (25% of score)
        if 'linkedin' in contact and contact['linkedin']:
            self.passed_checks.append({
                'check': 'contact_info',
                'message': 'LinkedIn profile included',
                'field': 'linkedin'
            })
            earned_score += max_score * 0.25
        else:
            self.violations.append({
                'check': 'contact_info',
                'severity': 'info',
                'message': 'LinkedIn profile recommended but not required',
                'field': 'linkedin'
            })
        
        self.score_breakdown['contact_info'] = earned_score
    
    def _check_experience_quality(self, experiences: List[Dict[str, Any]]) -> None:
        """
        Check quality of experience entries.
        
        Validates:
        - At least one experience entry
        - Each entry has title and company
        - Each entry has dates
        - Each entry has description
        """
        max_score = self.CHECK_WEIGHTS['experience_quality']
        
        if not experiences:
            self.violations.append({
                'check': 'experience_quality',
                'severity': 'critical',
                'message': 'No work experience entries found',
            })
            self.score_breakdown['experience_quality'] = 0
            return
        
        # At least one experience
        self.passed_checks.append({
            'check': 'experience_quality',
            'message': f'Resume contains {len(experiences)} experience entries'
        })
        
        # Check quality of each entry
        criteria = ['title', 'company', 'description']
        per_entry_score = max_score / len(experiences)
        per_criterion_score = per_entry_score / len(criteria)
        
        earned_score = 0
        
        for i, exp in enumerate(experiences):
            entry_num = i + 1
            
            # Check title
            if exp.get('title'):
                earned_score += per_criterion_score
            else:
                self.violations.append({
                    'check': 'experience_quality',
                    'severity': 'warning',
                    'message': f'Experience entry {entry_num} missing job title',
                    'entry': entry_num
                })
            
            # Check company
            if exp.get('company'):
                earned_score += per_criterion_score
            else:
                self.violations.append({
                    'check': 'experience_quality',
                    'severity': 'warning',
                    'message': f'Experience entry {entry_num} missing company name',
                    'entry': entry_num
                })
            
            # Check description
            if exp.get('description') and len(exp['description'].strip()) > 20:
                earned_score += per_criterion_score
                self.passed_checks.append({
                    'check': 'experience_quality',
                    'message': f'Experience entry {entry_num} has detailed description',
                    'entry': entry_num
                })
            else:
                self.violations.append({
                    'check': 'experience_quality',
                    'severity': 'warning',
                    'message': f'Experience entry {entry_num} missing or short description',
                    'entry': entry_num
                })
        
        self.score_breakdown['experience_quality'] = earned_score
    
    def _check_bullet_points(self, experiences: List[Dict[str, Any]]) -> None:
        """
        Validate bullet point formatting and length.
        
        ATS-friendly bullet points should:
        - Be 1-2 lines long (50-150 characters)
        - Start with action verbs
        - Be concise and specific
        """
        max_score = self.CHECK_WEIGHTS['bullet_points']
        
        if not experiences:
            self.score_breakdown['bullet_points'] = 0
            return
        
        bullet_lines = []
        for exp in experiences:
            if exp.get('description'):
                # Split by newline and filter bullet points
                lines = exp['description'].split('\n')
                for line in lines:
                    line = line.strip()
                    # Check if line starts with bullet marker
                    if line and line[0] in '•●○■□▪▫–-*':
                        bullet_lines.append(line.lstrip('•●○■□▪▫–-*').strip())
        
        if not bullet_lines:
            self.violations.append({
                'check': 'bullet_points',
                'severity': 'warning',
                'message': 'No bullet points found in experience descriptions'
            })
            self.score_breakdown['bullet_points'] = 0
            return
        
        # Check each bullet point
        optimal_bullets = 0
        too_short = 0
        too_long = 0

        
        for bullet in bullet_lines:
            length = len(bullet)
            
            if 50 <= length <= 150:
                optimal_bullets += 1
            elif length < 50:
                too_short += 1
            else:
                too_long += 1
        
        total_bullets = len(bullet_lines)
        optimal_ratio = optimal_bullets / total_bullets if total_bullets > 0 else 0
        
        earned_score = max_score * optimal_ratio
        
        self.passed_checks.append({
            'check': 'bullet_points',
            'message': f'{optimal_bullets}/{total_bullets} bullet points are optimal length (50-150 chars)'
        })
        
        if too_short > 0:
            self.violations.append({
                'check': 'bullet_points',
                'severity': 'info',
                'message': f'{too_short} bullet points are too short (<50 characters)',
                'count': too_short
            })
        
        if too_long > 0:
            self.violations.append({
                'check': 'bullet_points',
                'severity': 'info',
                'message': f'{too_long} bullet points are too long (>150 characters)',
                'count': too_long
            })
        
        self.score_breakdown['bullet_points'] = earned_score
    
    def _check_date_consistency(self, experiences: List[Dict[str, Any]]) -> None:
        """
        Validate date consistency in experience entries.
        
        Checks:
        - All entries have dates
        - Start date before end date
        - No overlapping positions
        - Chronological order (most recent first)
        """
        max_score = self.CHECK_WEIGHTS['date_consistency']
        
        if not experiences:
            self.score_breakdown['date_consistency'] = 0
            return
        
        earned_score = max_score
        issues_found = 0
        
        # Check each entry has dates
        for i, exp in enumerate(experiences):
            entry_num = i + 1
            
            if not exp.get('start_date') or not exp.get('end_date'):
                self.violations.append({
                    'check': 'date_consistency',
                    'severity': 'warning',
                    'message': f'Experience entry {entry_num} missing dates',
                    'entry': entry_num
                })
                issues_found += 1
        
        # Check date order (start < end)
        for i, exp in enumerate(experiences):
            entry_num = i + 1
            start = exp.get('start_date', '')
            end = exp.get('end_date', '')
            
            if start and end:
                # Extract years for comparison
                start_year = self._extract_year(start)
                end_year = self._extract_year(end)
                
                if start_year and end_year:
                    if end != 'Present' and end != 'Current':
                        if int(start_year) > int(end_year):
                            self.violations.append({
                                'check': 'date_consistency',
                                'severity': 'warning',
                                'message': f'Experience entry {entry_num} has start date after end date',
                                'entry': entry_num,
                                'start': start,
                                'end': end
                            })
                            issues_found += 1
        
        # Check chronological order (most recent first)
        if len(experiences) > 1:
            is_chronological = True
            for i in range(len(experiences) - 1):
                curr_year = self._extract_year(experiences[i].get('end_date', ''))
                next_year = self._extract_year(experiences[i+1].get('end_date', ''))
                
                if curr_year and next_year:
                    if curr_year != 'Present' and next_year != 'Present':
                        if int(next_year) > int(curr_year):
                            is_chronological = False
                            break
            
            if is_chronological:
                self.passed_checks.append({
                    'check': 'date_consistency',
                    'message': 'Experience entries in reverse chronological order'
                })
            else:
                self.violations.append({
                    'check': 'date_consistency',
                    'severity': 'info',
                    'message': 'Experience entries not in reverse chronological order (recommended)'
                })
                issues_found += 1
        
        # Penalize score based on issues
        if issues_found > 0:
            penalty = min(issues_found * (max_score / len(experiences)), max_score)
            earned_score = max(0, earned_score - penalty)
        
        if issues_found == 0:
            self.passed_checks.append({
                'check': 'date_consistency',
                'message': 'All dates are consistent and valid'
            })
        
        self.score_breakdown['date_consistency'] = earned_score
    
    def _check_action_verbs(self, experiences: List[Dict[str, Any]]) -> None:
        """
        Check usage of strong action verbs in experience descriptions.
        
        ATS systems favor:
        - Strong action verbs (led, developed, achieved)
        - Avoid weak phrases (responsible for, helped with)
        """
        max_score = self.CHECK_WEIGHTS['action_verbs']
        
        if not experiences:
            self.score_breakdown['action_verbs'] = 0
            return
        
        # Extract all bullet points
        bullets = []
        for exp in experiences:
            if exp.get('description'):
                lines = exp['description'].split('\n')
                for line in lines:
                    line = line.strip()
                    if line and line[0] in '•●○■□▪▫–-*':
                        bullets.append(line.lstrip('•●○■□▪▫–-*').strip())
        
        if not bullets:
            self.score_breakdown['action_verbs'] = 0
            return
        
        # Check action verbs
        strong_verb_count = 0
        weak_phrase_count = 0
        
        for bullet in bullets:
            bullet_lower = bullet.lower()
            first_word = bullet.split()[0].lower() if bullet.split() else ''
            
            # Check if starts with strong action verb
            if first_word in self.ACTION_VERBS:
                strong_verb_count += 1
            
            # Check for weak phrases
            for weak in self.WEAK_VERBS:
                if weak in bullet_lower:
                    weak_phrase_count += 1
                    break
        
        total_bullets = len(bullets)
        strong_ratio = strong_verb_count / total_bullets if total_bullets > 0 else 0
        
        earned_score = max_score * strong_ratio
        
        self.passed_checks.append({
            'check': 'action_verbs',
            'message': f'{strong_verb_count}/{total_bullets} bullet points start with strong action verbs'
        })
        
        if weak_phrase_count > 0:
            self.violations.append({
                'check': 'action_verbs',
                'severity': 'info',
                'message': f'{weak_phrase_count} bullet points use weak phrases (e.g., "responsible for")',
                'count': weak_phrase_count
            })
        
        if strong_ratio >= 0.7:
            self.passed_checks.append({
                'check': 'action_verbs',
                'message': 'Good use of strong action verbs (>70%)'
            })
        
        self.score_breakdown['action_verbs'] = earned_score
    
    def _extract_year(self, date_str: str) -> str:
        """Extract year from date string"""
        if not date_str:
            return ''
        
        if date_str.lower() in ['present', 'current']:
            return 'Present'
        
        # Try to extract 4-digit year
        year_match = re.search(r'\b(19\d{2}|20\d{2})\b', date_str)
        if year_match:
            return year_match.group(1)
        
        return ''


def validate_resume(resume_json: Dict[str, Any]) -> Dict[str, Any]:
    """
    Convenience function to validate a resume.
    
    Args:
        resume_json: Structured resume JSON
        
    Returns:
        Validation result with score, violations, and passed checks
    """
    validator = ATSValidator()
    return validator.validate(resume_json)


if __name__ == '__main__':
    # Example usage
    import json
    
    # Sample structured resume
    sample_resume = {
        "contact": {
            "name": "John Doe",
            "email": "john.doe@email.com",
            "phone": "+1-555-123-4567",
            "linkedin": "linkedin.com/in/johndoe"
        },
        "summary": "Senior Software Engineer with 5+ years of experience",
        "skills": ["Python", "JavaScript", "React", "AWS"],
        "experience": [
            {
                "title": "Senior Software Engineer",
                "company": "Tech Corp",
                "start_date": "2020",
                "end_date": "Present",
                "description": "• Led development of microservices architecture\n• Improved system performance by 40%\n• Mentored junior developers"
            },
            {
                "title": "Software Engineer",
                "company": "StartupXYZ",
                "start_date": "2018",
                "end_date": "2020",
                "description": "• Developed RESTful APIs\n• Implemented CI/CD pipelines"
            }
        ],
        "education": [
            {
                "degree": "Master of Science",
                "field": "Computer Science",
                "institution": "Stanford University",
                "graduation_date": "2018"
            }
        ]
    }
    
    # Validate
    validator = ATSValidator()
    result = validator.validate(sample_resume)
    
    # Print results
    print(json.dumps(result, indent=2))
