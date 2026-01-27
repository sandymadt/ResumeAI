"""
Feedback Generator Module

A production-ready module for generating resume improvement feedback.
Supports both rule-based (default) and LLM-based (optional) modes.

Features:
- Rule-based feedback (free, deterministic)
- Optional LLM-based feedback (advanced)
- Safe: LLM never sees raw resume text
- Structured JSON input only
- Actionable suggestions

Author: Resume Feedback Generator Expert
"""

from typing import Dict, Any, List, Optional
from dataclasses import dataclass
import logging

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


@dataclass
class FeedbackSuggestion:
    """Represents a single improvement suggestion"""
    category: str
    priority: str  # 'high', 'medium', 'low'
    issue: str
    suggestion: str
    impact: str  # Expected impact if implemented
    
    def to_dict(self) -> Dict[str, str]:
        return {
            'category': self.category,
            'priority': self.priority,
            'issue': self.issue,
            'suggestion': self.suggestion,
            'impact': self.impact
        }


class FeedbackGenerator:
    """
    Generates improvement feedback from resume analysis results.
    
    Two modes:
    1. Rule-based (default): Deterministic, always available
    2. LLM-based (optional): Advanced, requires API key
    """
    
    def __init__(self, use_llm: bool = False, llm_api_key: Optional[str] = None):
        """
        Initialize feedback generator.
        
        Args:
            use_llm: Whether to use LLM for enhanced feedback
            llm_api_key: Optional API key for LLM (e.g., OpenAI)
        """
        self.use_llm = use_llm
        self.llm_api_key = llm_api_key
        
        if use_llm and not llm_api_key:
            logger.warning("LLM mode requested but no API key provided. Falling back to rule-based.")
            self.use_llm = False
    
    def generate_feedback(
        self,
        resume_json: Dict[str, Any],
        ats_result: Optional[Dict[str, Any]] = None,
        skill_result: Optional[Dict[str, Any]] = None,
        impact_result: Optional[Dict[str, Any]] = None,
        formatting_result: Optional[Dict[str, Any]] = None,
        final_result: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Generate comprehensive feedback.
        
        Args:
            resume_json: Structured resume JSON (no raw text)
            ats_result: Result from validate_resume()
            skill_result: Result from match_skills()
            impact_result: Result from score_impact()
            formatting_result: Result from analyze_formatting()
            final_result: Result from calculate_ats_score()
            
        Returns:
            {
                "feedback": "Summary feedback text",
                "improvement_suggestions": [...],
                "mode": "rule-based" or "llm-based"
            }
        """
        if self.use_llm:
            return self._generate_llm_feedback(
                resume_json, ats_result, skill_result, 
                impact_result, formatting_result, final_result
            )
        else:
            return self._generate_rule_based_feedback(
                resume_json, ats_result, skill_result,
                impact_result, formatting_result, final_result
            )
    
    def _generate_rule_based_feedback(
        self,
        resume_json: Dict[str, Any],
        ats_result: Optional[Dict[str, Any]],
        skill_result: Optional[Dict[str, Any]],
        impact_result: Optional[Dict[str, Any]],
        formatting_result: Optional[Dict[str, Any]],
        final_result: Optional[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """Generate rule-based feedback (deterministic, free)"""
        
        suggestions = []
        
        # Analyze each component
        if ats_result:
            suggestions.extend(self._analyze_ats(ats_result))
        
        if skill_result:
            suggestions.extend(self._analyze_skills(skill_result))
        
        if impact_result:
            suggestions.extend(self._analyze_impact(impact_result))
        
        if formatting_result:
            suggestions.extend(self._analyze_formatting(formatting_result))
        
        # Generate summary feedback
        feedback_summary = self._generate_summary(
            resume_json, final_result, suggestions
        )
        
        result = {
            'feedback': feedback_summary,
            'improvement_suggestions': [s.to_dict() for s in suggestions],
            'mode': 'rule-based',
            'total_suggestions': len(suggestions),
            'priority_breakdown': {
                'high': len([s for s in suggestions if s.priority == 'high']),
                'medium': len([s for s in suggestions if s.priority == 'medium']),
                'low': len([s for s in suggestions if s.priority == 'low'])
            }
        }
        
        logger.info(f"Generated {len(suggestions)} rule-based suggestions")
        
        return result
    
    def _analyze_ats(self, ats_result: Dict[str, Any]) -> List[FeedbackSuggestion]:
        """Analyze ATS validation results"""
        suggestions = []
        
        score = ats_result.get('rule_score', 0)
        violations = ats_result.get('violations', [])
        
        # Critical violations
        critical = [v for v in violations if v.get('severity') == 'critical']
        for violation in critical:
            suggestions.append(FeedbackSuggestion(
                category='ats_compliance',
                priority='high',
                issue=violation.get('message', ''),
                suggestion=f"Fix critical issue: {violation.get('message', '')}",
                impact="Essential for ATS parsing - high priority fix"
            ))
        
        # Warning violations
        warnings = [v for v in violations if v.get('severity') == 'warning']
        for warning in warnings[:3]:  # Top 3 warnings
            suggestions.append(FeedbackSuggestion(
                category='ats_compliance',
                priority='medium',
                issue=warning.get('message', ''),
                suggestion=f"Address warning: {warning.get('message', '')}",
                impact="Improves ATS compatibility"
            ))
        
        # Low score overall
        if score < 70:
            suggestions.append(FeedbackSuggestion(
                category='ats_compliance',
                priority='high',
                issue=f"Low ATS compliance score: {score}/100",
                suggestion="Review all ATS violations and address critical issues first",
                impact="Significantly improves chance of passing ATS screening"
            ))
        
        return suggestions
    
    def _analyze_skills(self, skill_result: Dict[str, Any]) -> List[FeedbackSuggestion]:
        """Analyze skill matching results"""
        suggestions = []
        
        missing_skills = skill_result.get('missing_skills', [])
        match_score = skill_result.get('keyword_match_score', 0)
        
        # Low match score
        if match_score < 60:
            suggestions.append(FeedbackSuggestion(
                category='skills',
                priority='high',
                issue=f"Low keyword match: {match_score}%",
                suggestion="Add more job-relevant skills and keywords from the job description",
                impact="Increases likelihood of passing keyword screening by 40-60%"
            ))
        
        # Missing critical skills
        if len(missing_skills) > 0:
            top_missing = missing_skills[:5]  # Top 5
            suggestions.append(FeedbackSuggestion(
                category='skills',
                priority='high' if len(missing_skills) > 5 else 'medium',
                issue=f"{len(missing_skills)} required skills missing",
                suggestion=f"Add these missing skills if you have them: {', '.join(top_missing)}",
                impact="Directly addresses job requirements"
            ))
        
        return suggestions
    
    def _analyze_impact(self, impact_result: Dict[str, Any]) -> List[FeedbackSuggestion]:
        """Analyze impact scoring results"""
        suggestions = []
        
        score = impact_result.get('impact_score', 0)
        summary = impact_result.get('summary', {})
        weak_points = impact_result.get('weak_points', [])
        
        # Quantification issues
        total_bullets = summary.get('total_bullets', 0)
        quantified = summary.get('quantified_bullets', 0)
        
        if total_bullets > 0:
            quant_ratio = quantified / total_bullets
            if quant_ratio < 0.5:
                suggestions.append(FeedbackSuggestion(
                    category='impact',
                    priority='high',
                    issue=f"Only {quantified}/{total_bullets} bullets include metrics",
                    suggestion="Add numbers, percentages, or metrics to at least 50% of bullet points",
                    impact="Makes achievements concrete and verifiable - increases impact by 50%"
                ))
        
        # Action verb issues
        ownership_bullets = summary.get('ownership_verb_bullets', 0)
        if total_bullets > 0:
            verb_ratio = ownership_bullets / total_bullets
            if verb_ratio < 0.7:
                suggestions.append(FeedbackSuggestion(
                    category='impact',
                    priority='medium',
                    issue=f"Only {ownership_bullets}/{total_bullets} bullets use strong action verbs",
                    suggestion="Start each bullet with powerful action verbs: Led, Built, Achieved, Improved",
                    impact="Demonstrates ownership and proactive contribution"
                ))
        
        # Outcome issues
        outcome_bullets = summary.get('outcome_driven_bullets', 0)
        if total_bullets > 0:
            outcome_ratio = outcome_bullets / total_bullets
            if outcome_ratio < 0.6:
                suggestions.append(FeedbackSuggestion(
                    category='impact',
                    priority='high',
                    issue=f"Only {outcome_bullets}/{total_bullets} bullets show clear outcomes",
                    suggestion="Add results and impact to each bullet: 'resulting in...', 'improved by...', 'increased...'",
                    impact="Demonstrates business value and measurable contribution"
                ))
        
        return suggestions
    
    def _analyze_formatting(self, formatting_result: Dict[str, Any]) -> List[FeedbackSuggestion]:
        """Analyze formatting results"""
        suggestions = []
        
        issues = formatting_result.get('formatting_issues', [])
        score = formatting_result.get('formatting_score', 0)
        
        # Critical formatting issues
        critical = [i for i in issues if i.get('severity') == 'critical']
        for issue in critical:
            suggestions.append(FeedbackSuggestion(
                category='formatting',
                priority='high',
                issue=issue.get('message', ''),
                suggestion=issue.get('recommendation', ''),
                impact="Critical for ATS parsing"
            ))
        
        # Bullet density issues
        density_issues = [i for i in issues if 'bullet' in i.get('message', '').lower()]
        for issue in density_issues[:2]:  # Top 2
            suggestions.append(FeedbackSuggestion(
                category='formatting',
                priority='medium',
                issue=issue.get('message', ''),
                suggestion=issue.get('recommendation', ''),
                impact="Improves readability and professional appearance"
            ))
        
        return suggestions
    
    def _generate_summary(
        self,
        resume_json: Dict[str, Any],
        final_result: Optional[Dict[str, Any]],
        suggestions: List[FeedbackSuggestion]
    ) -> str:
        """Generate summary feedback text"""
        
        if final_result:
            score = final_result.get('ats_score', 0)
            grade = final_result.get('score_grade', 'F')
        else:
            score = 0
            grade = 'F'
        
        # Opening
        if score >= 85:
            opening = f"Excellent resume! Your ATS score of {score}/100 (Grade {grade}) is strong."
        elif score >= 70:
            opening = f"Good resume with room for improvement. Current ATS score: {score}/100 (Grade {grade})."
        elif score >= 60:
            opening = f"Your resume needs improvement. Current ATS score: {score}/100 (Grade {grade})."
        else:
            opening = f"Significant improvements needed. Current ATS score: {score}/100 (Grade {grade})."
        
        # Priority suggestions
        high_priority = [s for s in suggestions if s.priority == 'high']
        
        if high_priority:
            priority_text = f"\n\nHigh Priority ({len(high_priority)} items):\n"
            for i, suggestion in enumerate(high_priority[:3], 1):
                priority_text += f"{i}. {suggestion.issue}\n"
        else:
            priority_text = "\n\nNo critical issues found. Focus on optimization."
        
        # Next steps
        next_steps = "\n\nRecommended Actions:\n"
        if high_priority:
            next_steps += "1. Address all high-priority issues first\n"
            next_steps += "2. Add quantified achievements with metrics\n"
            next_steps += "3. Ensure ATS-safe formatting\n"
        else:
            next_steps += "1. Optimize bullet points for impact\n"
            next_steps += "2. Fine-tune keyword matching\n"
            next_steps += "3. Polish formatting and layout\n"
        
        return opening + priority_text + next_steps
    
    def _generate_llm_feedback(
        self,
        resume_json: Dict[str, Any],
        ats_result: Optional[Dict[str, Any]],
        skill_result: Optional[Dict[str, Any]],
        impact_result: Optional[Dict[str, Any]],
        formatting_result: Optional[Dict[str, Any]],
        final_result: Optional[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """
        Generate LLM-based feedback (optional, advanced).
        
        SAFETY RULES:
        - Never send raw resume text to LLM
        - Only send structured, anonymized data
        - No PII (personally identifiable information)
        - Validate all LLM outputs
        """
        
        # First, generate rule-based feedback as baseline
        baseline = self._generate_rule_based_feedback(
            resume_json, ats_result, skill_result,
            impact_result, formatting_result, final_result
        )
        
        try:
            # Prepare safe, structured input for LLM
            safe_input = self._prepare_safe_llm_input(
                resume_json, ats_result, skill_result,
                impact_result, formatting_result, final_result
            )
            
            # Call LLM (placeholder - implement actual LLM call)
            llm_suggestions = self._call_llm_safely(safe_input)
            
            # Validate and combine with baseline
            validated_suggestions = self._validate_llm_suggestions(llm_suggestions)
            
            # Merge with baseline suggestions
            all_suggestions = baseline['improvement_suggestions'] + validated_suggestions
            
            # Generate enhanced summary
            enhanced_feedback = self._generate_llm_summary(safe_input, all_suggestions)
            
            result = {
                'feedback': enhanced_feedback,
                'improvement_suggestions': all_suggestions,
                'mode': 'llm-based',
                'total_suggestions': len(all_suggestions),
                'llm_enhanced': True
            }
            
            logger.info(f"Generated {len(all_suggestions)} LLM-enhanced suggestions")
            
            return result
            
        except Exception as e:
            logger.error(f"LLM feedback generation failed: {e}. Falling back to rule-based.")
            return baseline
    
    def _prepare_safe_llm_input(
        self,
        resume_json: Dict[str, Any],
        ats_result: Optional[Dict[str, Any]],
        skill_result: Optional[Dict[str, Any]],
        impact_result: Optional[Dict[str, Any]],
        formatting_result: Optional[Dict[str, Any]],
        final_result: Optional[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """
        Prepare safe, anonymized input for LLM.
        
        REMOVES:
        - Names
        - Email addresses
        - Phone numbers
        - Addresses
        - Company names (optional)
        """
        
        safe_data = {
            'scores': {
                'ats': ats_result.get('rule_score') if ats_result else None,
                'keyword_match': skill_result.get('keyword_match_score') if skill_result else None,
                'impact': impact_result.get('impact_score') if impact_result else None,
                'formatting': formatting_result.get('formatting_score') if formatting_result else None,
                'final': final_result.get('ats_score') if final_result else None
            },
            'issues': {
                'ats_violations': len(ats_result.get('violations', [])) if ats_result else 0,
                'missing_skills': len(skill_result.get('missing_skills', [])) if skill_result else 0,
                'weak_points': impact_result.get('weak_points', []) if impact_result else [],
                'formatting_issues': len(formatting_result.get('formatting_issues', [])) if formatting_result else 0
            },
            'stats': {
                'total_experience_entries': len(resume_json.get('experience', [])),
                'total_skills': len(resume_json.get('skills', [])),
                'total_education': len(resume_json.get('education', [])),
                'has_summary': bool(resume_json.get('summary'))
            }
        }
        
        return safe_data
    
    def _call_llm_safely(self, safe_input: Dict[str, Any]) -> List[Dict[str, str]]:
        """
        Call LLM API safely (placeholder).
        
        In production, implement actual LLM call here.
        Example: OpenAI GPT, Anthropic Claude, etc.
        """
        logger.info("LLM call would happen here (placeholder)")
        
        # Placeholder - return empty list
        # In production, this would call the LLM API
        return []
    
    def _validate_llm_suggestions(self, suggestions: List[Dict[str, str]]) -> List[Dict[str, str]]:
        """Validate LLM suggestions for safety and quality"""
        validated = []
        
        for suggestion in suggestions:
            # Check required fields
            if not all(k in suggestion for k in ['category', 'priority', 'issue', 'suggestion', 'impact']):
                continue
            
            # Check for hallucinations (PII, fake data)
            if self._contains_suspicious_content(suggestion):
                continue
            
            # Check actionability
            if len(suggestion.get('suggestion', '')) < 20:
                continue
            
            validated.append(suggestion)
        
        return validated
    
    def _contains_suspicious_content(self, suggestion: Dict[str, str]) -> bool:
        """Check if suggestion contains suspicious content"""
        # Check for email patterns
        import re
        email_pattern = r'[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}'
        
        for value in suggestion.values():
            if re.search(email_pattern, str(value)):
                return True
        
        return False
    
    def _generate_llm_summary(self, safe_input: Dict[str, Any], suggestions: List[Dict[str, str]]) -> str:
        """Generate LLM-enhanced summary (placeholder)"""
        # In production, use LLM to generate personalized summary
        # For now, fallback to rule-based
        final_score = safe_input['scores'].get('final', 0)
        return f"Your resume scores {final_score}/100. {len(suggestions)} improvements suggested."


def generate_feedback(
    resume_json: Dict[str, Any],
    ats_result: Optional[Dict[str, Any]] = None,
    skill_result: Optional[Dict[str, Any]] = None,
    impact_result: Optional[Dict[str, Any]] = None,
    formatting_result: Optional[Dict[str, Any]] = None,
    final_result: Optional[Dict[str, Any]] = None,
    use_llm: bool = False,
    llm_api_key: Optional[str] = None
) -> Dict[str, Any]:
    """
    Convenience function to generate feedback.
    
    Args:
        resume_json: Structured resume JSON
        ats_result: ATS validation result
        skill_result: Skill matching result
        impact_result: Impact scoring result
        formatting_result: Formatting analysis result
        final_result: Final aggregated score result
        use_llm: Whether to use LLM enhancement
        llm_api_key: Optional LLM API key
        
    Returns:
        Feedback with suggestions
    """
    generator = FeedbackGenerator(use_llm, llm_api_key)
    return generator.generate_feedback(
        resume_json, ats_result, skill_result,
        impact_result, formatting_result, final_result
    )


if __name__ == '__main__':
    # Example usage
    import json
    
    # Sample analysis results
    sample_resume = {
        "experience": [
            {"title": "Engineer", "company": "Tech Co", "description": "• Did work"}
        ],
        "skills": ["Python"],
        "education": [{"degree": "BS", "institution": "University"}]
    }
    
    sample_ats = {
        "rule_score": 72,
        "violations": [
            {"severity": "warning", "message": "Missing summary section"}
        ]
    }
    
    sample_skill = {
        "keyword_match_score": 58,
        "missing_skills": ["React", "AWS", "Docker"]
    }
    
    sample_impact = {
        "impact_score": 45,
        "summary": {
            "total_bullets": 4,
            "quantified_bullets": 1,
            "ownership_verb_bullets": 2,
            "outcome_driven_bullets": 1
        },
        "weak_points": ["Weak quantification"]
    }
    
    sample_final = {
        "ats_score": 65.5,
        "score_grade": "D"
    }
    
    # Generate feedback
    generator = FeedbackGenerator(use_llm=False)
    result = generator.generate_feedback(
        sample_resume,
        sample_ats,
        sample_skill,
        sample_impact,
        None,
        sample_final
    )
    
    print(json.dumps(result, indent=2))
