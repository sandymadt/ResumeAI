"""
Formatting & Readability Module

A production-ready module for evaluating resume formatting and ATS optimization.
Uses deterministic rule-based scoring logic.

Features:
- Section ordering validation
- Bullet density analysis
- Line length optimization
- White-space balance checking
- ATS-safe formatting verification

No AI models or LLM usage - Pure deterministic logic

Author: Resume Formatting Expert
"""

import re
from typing import Dict, List, Any, Tuple
from dataclasses import dataclass
import logging

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


@dataclass
class FormattingIssue:
    """Represents a formatting issue"""
    category: str
    severity: str  # 'critical', 'warning', 'info'
    message: str
    recommendation: str
    
    def to_dict(self) -> Dict[str, str]:
        return {
            'category': self.category,
            'severity': self.severity,
            'message': self.message,
            'recommendation': self.recommendation
        }


class FormattingAnalyzer:
    """
    Analyzes resume formatting and readability for ATS optimization.
    
    Scoring criteria:
    1. Section ordering (20 points)
    2. Bullet density (25 points)
    3. Line length (20 points)
    4. White-space balance (20 points)
    5. ATS-safe formatting (15 points)
    """
    
    # Optimal section order (ATS-friendly)
    OPTIMAL_SECTION_ORDER = [
        'contact',
        'summary',
        'experience',
        'skills',
        'education'
    ]
    
    # Alternative acceptable orders
    ACCEPTABLE_ORDERS = [
        ['contact', 'summary', 'skills', 'experience', 'education'],
        ['contact', 'experience', 'skills', 'education', 'summary'],
        ['contact', 'summary', 'experience', 'education', 'skills']
    ]
    
    # Optimal metrics
    OPTIMAL_BULLETS_PER_JOB = (3, 6)  # Min, Max
    OPTIMAL_LINE_LENGTH = (50, 120)   # Characters
    OPTIMAL_TOTAL_BULLETS = (8, 20)   # Total across all jobs
    
    # Score weights
    WEIGHTS = {
        'section_order': 20,
        'bullet_density': 25,
        'line_length': 20,
        'whitespace': 20,
        'ats_safe': 15
    }
    
    def __init__(self):
        """Initialize formatting analyzer"""
        self.issues = []
        self.recommendations = []
    
    def analyze_formatting(self, resume_json: Dict[str, Any]) -> Dict[str, Any]:
        """
        Analyze resume formatting.
        
        Args:
            resume_json: Structured resume JSON
            
        Returns:
            {
                "formatting_score": 0-100,
                "formatting_issues": [...],
                "formatting_recommendations": [...],
                "score_breakdown": {...}
            }
        """
        # Reset state
        self.issues = []
        self.recommendations = []
        
        # Run all checks
        scores = {}
        scores['section_order'] = self._check_section_order(resume_json)
        scores['bullet_density'] = self._check_bullet_density(resume_json)
        scores['line_length'] = self._check_line_length(resume_json)
        scores['whitespace'] = self._check_whitespace(resume_json)
        scores['ats_safe'] = self._check_ats_safe(resume_json)
        
        # Calculate total score
        formatting_score = sum(scores.values())
        
        result = {
            'formatting_score': round(formatting_score, 2),
            'formatting_issues': [issue.to_dict() for issue in self.issues],
            'formatting_recommendations': self.recommendations,
            'score_breakdown': scores
        }
        
        logger.info(f"Formatting analysis complete. Score: {formatting_score}/100, "
                   f"Issues: {len(self.issues)}")
        
        return result
    
    def _check_section_order(self, resume_json: Dict[str, Any]) -> float:
        """
        Check if sections are in optimal order.
        
        Optimal order: Contact → Summary → Experience → Skills → Education
        """
        max_score = self.WEIGHTS['section_order']
        
        # Get sections present in resume
        sections_present = [s for s in self.OPTIMAL_SECTION_ORDER if s in resume_json]
        
        if not sections_present:
            self._add_issue('section_order', 'critical',
                          "No standard sections found",
                          "Include standard sections: Contact, Experience, Education")
            return 0.0
        
        # Check if matches optimal order
        if sections_present == self.OPTIMAL_SECTION_ORDER[:len(sections_present)]:
            self._add_recommendation("✓ Sections in optimal ATS-friendly order")
            return max_score
        
        # Check if matches any acceptable order
        for acceptable in self.ACCEPTABLE_ORDERS:
            acceptable_subset = [s for s in acceptable if s in sections_present]
            if sections_present == acceptable_subset:
                self._add_recommendation("✓ Sections in acceptable order")
                return max_score * 0.9
        
        # Sections are out of order
        self._add_issue('section_order', 'warning',
                       f"Sections not in optimal order: {', '.join(sections_present)}",
                       f"Recommended order: {', '.join(self.OPTIMAL_SECTION_ORDER)}")
        
        # Partial credit based on how many are in correct relative position
        correct_positions = sum(
            1 for i, s in enumerate(sections_present)
            if i == 0 or sections_present.index(s) > sections_present.index(sections_present[i-1])
        )
        score = (correct_positions / len(sections_present)) * max_score * 0.7
        
        return round(score, 2)
    
    def _check_bullet_density(self, resume_json: Dict[str, Any]) -> float:
        """
        Check bullet point density.
        
        Optimal: 3-6 bullets per job, 8-20 total
        """
        max_score = self.WEIGHTS['bullet_density']
        
        if 'experience' not in resume_json or not resume_json['experience']:
            self._add_issue('bullet_density', 'critical',
                          "No experience section found",
                          "Add experience section with bullet points")
            return 0.0
        
        experiences = resume_json['experience']
        bullets_per_job = []
        total_bullets = 0
        
        for exp in experiences:
            if 'description' in exp and exp['description']:
                # Count bullet points
                bullet_count = len([
                    line for line in exp['description'].split('\n')
                    if line.strip() and line.strip()[0] in '•●○■□▪▫–-*'
                ])
                bullets_per_job.append(bullet_count)
                total_bullets += bullet_count
        
        if not bullets_per_job:
            self._add_issue('bullet_density', 'warning',
                          "No bullet points found in experience",
                          "Use bullet points (•) to list achievements")
            return max_score * 0.2
        
        # Check total bullets
        min_total, max_total = self.OPTIMAL_TOTAL_BULLETS
        total_score = 0.0
        
        if min_total <= total_bullets <= max_total:
            total_score = 0.5
            self._add_recommendation(f"✓ Good total bullet count: {total_bullets}")
        elif total_bullets < min_total:
            self._add_issue('bullet_density', 'warning',
                          f"Too few bullets: {total_bullets} (recommended: {min_total}-{max_total})",
                          "Add more bullet points describing your achievements")
            total_score = (total_bullets / min_total) * 0.5
        else:  # too many
            self._add_issue('bullet_density', 'info',
                          f"Many bullets: {total_bullets} (recommended: {min_total}-{max_total})",
                          "Consider condensing to most impactful achievements")
            total_score = 0.4
        
        # Check bullets per job
        min_per_job, max_per_job = self.OPTIMAL_BULLETS_PER_JOB
        jobs_in_range = sum(1 for count in bullets_per_job if min_per_job <= count <= max_per_job)
        per_job_score = (jobs_in_range / len(bullets_per_job)) * 0.5
        
        if jobs_in_range == len(bullets_per_job):
            self._add_recommendation("✓ All jobs have optimal bullet count (3-6)")
        elif jobs_in_range < len(bullets_per_job) / 2:
            self._add_issue('bullet_density', 'warning',
                          f"{len(bullets_per_job) - jobs_in_range} jobs have suboptimal bullet count",
                          "Aim for 3-6 bullets per job position")
        
        score = (total_score + per_job_score) * max_score
        return round(score, 2)
    
    def _check_line_length(self, resume_json: Dict[str, Any]) -> float:
        """
        Check line length optimization.
        
        Optimal: 50-120 characters per line
        """
        max_score = self.WEIGHTS['line_length']
        
        # Extract all text lines
        all_lines = self._extract_all_lines(resume_json)
        
        if not all_lines:
            return max_score * 0.5  # Neutral score if no content
        
        min_len, max_len = self.OPTIMAL_LINE_LENGTH
        
        # Check each line
        optimal_lines = 0
        too_short = 0
        too_long = 0
        
        for line in all_lines:
            line_len = len(line)
            
            if min_len <= line_len <= max_len:
                optimal_lines += 1
            elif line_len < min_len:
                too_short += 1
            else:
                too_long += 1
        
        total_lines = len(all_lines)
        optimal_ratio = optimal_lines / total_lines
        
        # Score based on optimal ratio
        score = optimal_ratio * max_score
        
        # Add recommendations
        if optimal_ratio >= 0.8:
            self._add_recommendation(f"✓ Good line length: {int(optimal_ratio*100)}% of lines optimal")
        else:
            if too_short > total_lines * 0.2:
                self._add_issue('line_length', 'info',
                              f"{too_short} lines too short (< {min_len} chars)",
                              "Expand bullet points with more detail")
            if too_long > total_lines * 0.2:
                self._add_issue('line_length', 'warning',
                              f"{too_long} lines too long (> {max_len} chars)",
                              "Break long lines into multiple bullets")
        
        return round(score, 2)
    
    def _check_whitespace(self, resume_json: Dict[str, Any]) -> float:
        """
        Check white-space balance.
        
        Ensures sections aren't too dense or too sparse.
        """
        max_score = self.WEIGHTS['whitespace']
        
        # Check each section's content density
        section_scores = []
        
        # Experience section density
        if 'experience' in resume_json and resume_json['experience']:
            exp_density = self._calculate_section_density(resume_json['experience'])
            if 0.3 <= exp_density <= 0.7:
                section_scores.append(1.0)
                self._add_recommendation("✓ Experience section has good density")
            else:
                section_scores.append(0.6)
                if exp_density < 0.3:
                    self._add_issue('whitespace', 'info',
                                  "Experience section seems sparse",
                                  "Add more details or consolidate positions")
                else:
                    self._add_issue('whitespace', 'info',
                                  "Experience section seems dense",
                                  "Add spacing between positions")
        
        # Skills section
        if 'skills' in resume_json and resume_json['skills']:
            skill_count = len(resume_json['skills'])
            if 5 <= skill_count <= 20:
                section_scores.append(1.0)
                self._add_recommendation(f"✓ Skills section well-balanced ({skill_count} skills)")
            else:
                section_scores.append(0.7)
                if skill_count < 5:
                    self._add_issue('whitespace', 'warning',
                                  f"Few skills listed ({skill_count})",
                                  "Add more relevant skills (aim for 8-15)")
                else:
                    self._add_issue('whitespace', 'info',
                                  f"Many skills listed ({skill_count})",
                                  "Focus on most relevant skills")
        
        # Summary section
        if 'summary' in resume_json and resume_json['summary']:
            summary_len = len(resume_json['summary'])
            if 100 <= summary_len <= 300:
                section_scores.append(1.0)
                self._add_recommendation("✓ Summary length optimal")
            else:
                section_scores.append(0.7)
                if summary_len < 100:
                    self._add_issue('whitespace', 'info',
                                  "Summary is brief",
                                  "Expand to 2-3 sentences highlighting key strengths")
                else:
                    self._add_issue('whitespace', 'info',
                                  "Summary is lengthy",
                                  "Condense to 2-3 impactful sentences")
        
        # Calculate average score
        if section_scores:
            avg_score = sum(section_scores) / len(section_scores)
            score = avg_score * max_score
        else:
            score = max_score * 0.5
        
        return round(score, 2)
    
    def _check_ats_safe(self, resume_json: Dict[str, Any]) -> float:
        """
        Check for ATS-safe formatting.
        
        ATS systems prefer:
        - Plain text formatting
- Standard section names
        - No tables, images, columns
        - No special characters in headers
        """
        max_score = self.WEIGHTS['ats_safe']
        score = max_score
        
        # Check 1: Standard section names
        required_sections = ['contact', 'experience', 'education']
        missing_sections = [s for s in required_sections if s not in resume_json]
        
        if missing_sections:
            score -= (len(missing_sections) / len(required_sections)) * (max_score * 0.4)
            self._add_issue('ats_safe', 'critical',
                          f"Missing required sections: {', '.join(missing_sections)}",
                          "Include all standard sections for ATS parsing")
        else:
            self._add_recommendation("✓ All required sections present")
        
        # Check 2: Contact information completeness
        if 'contact' in resume_json:
            contact = resume_json['contact']
            required_contact = ['email', 'phone']
            missing_contact = [f for f in required_contact if f not in contact or not contact[f]]
            
            if not missing_contact:
                self._add_recommendation("✓ Complete contact information")
            else:
                score -= (len(missing_contact) / len(required_contact)) * (max_score * 0.3)
                self._add_issue('ats_safe', 'critical',
                              f"Missing contact: {', '.join(missing_contact)}",
                              "Ensure email and phone are clearly listed")
        
        # Check 3: Content structure
        if 'experience' in resume_json and resume_json['experience']:
            for i, exp in enumerate(resume_json['experience']):
                # Check for required fields
                if not exp.get('title'):
                    score -= max_score * 0.1
                    self._add_issue('ats_safe', 'warning',
                                  f"Experience entry {i+1} missing job title",
                                  "Ensure each position has a clear job title")
                
                if not exp.get('company'):
                    score -= max_score * 0.1
                    self._add_issue('ats_safe', 'warning',
                                  f"Experience entry {i+1} missing company name",
                                  "Ensure each position includes company name")
        
        # Check 4: Avoid problematic characters in skills
        if 'skills' in resume_json and resume_json['skills']:
            problematic_chars = re.compile(r'[^\w\s\+\-\.\#]')
            problem_skills = [s for s in resume_json['skills'] if problematic_chars.search(s)]
            
            if problem_skills and len(problem_skills) > len(resume_json['skills']) * 0.2:
                score -= max_score * 0.1
                self._add_issue('ats_safe', 'info',
                              f"{len(problem_skills)} skills contain special characters",
                              "Use standard alphanumeric characters for skills")
        
        # Ensure score doesn't go below 0
        score = max(0, score)
        
        if score >= max_score * 0.9:
            self._add_recommendation("✓ Resume is ATS-safe")
        
        return round(score, 2)
    
    def _extract_all_lines(self, resume_json: Dict[str, Any]) -> List[str]:
        """Extract all text lines from resume"""
        lines = []
        
        # Summary
        if 'summary' in resume_json and resume_json['summary']:
            lines.append(resume_json['summary'])
        
        # Experience bullets
        if 'experience' in resume_json:
            for exp in resume_json['experience']:
                if 'description' in exp and exp['description']:
                    for line in exp['description'].split('\n'):
                        line = line.strip().lstrip('•●○■□▪▫–-*').strip()
                        if line:
                            lines.append(line)
        
        # Skills (treat as single line)
        if 'skills' in resume_json and resume_json['skills']:
            lines.append(', '.join(resume_json['skills']))
        
        return lines
    
    def _calculate_section_density(self, section_content: Any) -> float:
        """
        Calculate density of a section.
        
        Returns value between 0 (sparse) and 1 (dense)
        """
        if isinstance(section_content, list):
            # For experience/education - check content richness
            if not section_content:
                return 0.0
            
            total_chars = 0
            for item in section_content:
                if isinstance(item, dict):
                    for value in item.values():
                        if isinstance(value, str):
                            total_chars += len(value)
            
            # Normalize by number of items
            avg_chars = total_chars / len(section_content)
            # Optimal is around 200-500 chars per item
            density = min(avg_chars / 500, 1.0)
            return density
        
        return 0.5  # Default neutral
    
    def _add_issue(self, category: str, severity: str, message: str, recommendation: str):
        """Add a formatting issue"""
        issue = FormattingIssue(category, severity, message, recommendation)
        self.issues.append(issue)
    
    def _add_recommendation(self, recommendation: str):
        """Add a formatting recommendation"""
        self.recommendations.append(recommendation)


def analyze_formatting(resume_json: Dict[str, Any]) -> Dict[str, Any]:
    """
    Convenience function to analyze resume formatting.
    
    Args:
        resume_json: Structured resume JSON
        
    Returns:
        Formatting analysis result
    """
    analyzer = FormattingAnalyzer()
    return analyzer.analyze_formatting(resume_json)


if __name__ == '__main__':
    # Example usage
    import json
    
    sample_resume = {
        "contact": {
            "name": "John Doe",
            "email": "john@email.com",
            "phone": "555-1234"
        },
        "summary": "Experienced software engineer with 5+ years in full-stack development",
        "experience": [
            {
                "title": "Senior Engineer",
                "company": "Tech Corp",
                "description": """• Led development of microservices architecture
• Improved system reliability by 40%
• Built automated deployment pipeline
• Mentored junior developers"""
            }
        ],
        "skills": ["Python", "JavaScript", "React", "AWS", "Docker"],
        "education": [
            {
                "degree": "BS Computer Science",
                "institution": "MIT",
                "graduation_date": "2020"
            }
        ]
    }
    
    analyzer = FormattingAnalyzer()
    result = analyzer.analyze_formatting(sample_resume)
    
    print(json.dumps(result, indent=2))
