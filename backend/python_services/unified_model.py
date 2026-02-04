"""
Unified Resume Analysis Model

A single, comprehensive model that combines all resume analysis services:
- Text Extraction
- Resume Structuring
- ATS Validation
- Skill Matching
- Impact Scoring
- Formatting Analysis
- Score Aggregation
- Feedback Generation

This unified model provides a clean, simple API for complete resume analysis.

Author: AI Backend Architect
Version: 2.0.0
"""

from typing import Dict, Any, Optional, List
import logging
from pathlib import Path
import traceback
from datetime import datetime

# Import all individual components
# Support both relative imports (when used as module) and absolute imports (when run directly)
try:
    from .text_extractor import ResumeTextExtractor, TextExtractionError, extract_text
    from .resume_structurer import ResumeStructurer, structure_resume
    from .ats_validator import ATSValidator, validate_resume
    from .skill_matcher import SkillMatcher, match_skills
    from .impact_scorer import ImpactScorer, score_impact
    from .formatting_analyzer import FormattingAnalyzer, analyze_formatting
    from .score_aggregator import ScoreAggregator, calculate_ats_score
    from .feedback_generator import FeedbackGenerator, generate_feedback
except ImportError:
    # Fallback to absolute imports for standalone usage
    from text_extractor import ResumeTextExtractor, TextExtractionError, extract_text
    from resume_structurer import ResumeStructurer, structure_resume
    from ats_validator import ATSValidator, validate_resume
    from skill_matcher import SkillMatcher, match_skills
    from impact_scorer import ImpactScorer, score_impact
    from formatting_analyzer import FormattingAnalyzer, analyze_formatting
    from score_aggregator import ScoreAggregator, calculate_ats_score
    from feedback_generator import FeedbackGenerator, generate_feedback

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


class UnifiedResumeAnalyzer:
    """
    Unified Resume Analysis Model
    
    A comprehensive, all-in-one model that combines all resume analysis services
    into a single, easy-to-use interface.
    
    Features:
    - Single initialization for all services
    - One method to analyze everything
    - Automatic orchestration of all modules
    - Standardized output format
    - Built-in error handling
    - Production-ready logging
    
    Usage:
        analyzer = UnifiedResumeAnalyzer()
        result = analyzer.analyze(resume_path="resume.pdf", job_description="...")
        print(f"ATS Score: {result['ats_score']}/100")
    """
    
    def __init__(
        self,
        use_llm_feedback: bool = False,
        llm_api_key: Optional[str] = None,
        enable_detailed_logging: bool = True
    ):
        """
        Initialize the unified resume analyzer.
        
        Args:
            use_llm_feedback: Whether to use LLM for enhanced feedback generation
            llm_api_key: Optional API key for LLM-based feedback
            enable_detailed_logging: Enable detailed step-by-step logging
        """
        self.use_llm_feedback = use_llm_feedback
        self.llm_api_key = llm_api_key
        self.enable_detailed_logging = enable_detailed_logging
        
        # Initialize all service components
        self._initialize_services()
        
        logger.info("✅ Unified Resume Analyzer initialized successfully")
    
    def _initialize_services(self):
        """Initialize all individual service components"""
        try:
            self.text_extractor = ResumeTextExtractor()
            self.resume_structurer = ResumeStructurer()
            self.ats_validator = ATSValidator()
            self.skill_matcher = SkillMatcher()
            self.impact_scorer = ImpactScorer()
            self.formatting_analyzer = FormattingAnalyzer()
            self.score_aggregator = ScoreAggregator()
            self.feedback_generator = FeedbackGenerator()
            
            if self.enable_detailed_logging:
                logger.info("All service components initialized:")
                logger.info("  ✓ Text Extractor")
                logger.info("  ✓ Resume Structurer")
                logger.info("  ✓ ATS Validator")
                logger.info("  ✓ Skill Matcher")
                logger.info("  ✓ Impact Scorer")
                logger.info("  ✓ Formatting Analyzer")
                logger.info("  ✓ Score Aggregator")
                logger.info("  ✓ Feedback Generator")
        
        except Exception as e:
            logger.error(f"Failed to initialize services: {str(e)}")
            raise
    
    def analyze(
        self,
        resume_path: Optional[str] = None,
        resume_text: Optional[str] = None,
        job_description: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Complete resume analysis - the main API endpoint.
        
        This single method orchestrates all analysis services and returns
        a comprehensive analysis result.
        
        Args:
            resume_path: Path to resume file (PDF or DOCX)
            resume_text: Raw resume text (alternative to resume_path)
            job_description: Optional job description for skill matching
            
        Returns:
            Comprehensive analysis result with:
            - ats_score: Overall ATS score (0-100)
            - section_scores: Breakdown by category
            - matched_skills: Skills found in both resume and JD
            - missing_skills: Skills in JD but not in resume
            - strengths: Identified strengths
            - improvement_suggestions: Prioritized suggestions
            - feedback: Overall feedback text
            - metadata: Analysis metadata
            
        Example:
            result = analyzer.analyze(
                resume_path="resume.pdf",
                job_description="Looking for Python developer..."
            )
        """
        start_time = datetime.now()
        
        try:
            if self.enable_detailed_logging:
                logger.info("="*70)
                logger.info("🚀 Starting Unified Resume Analysis")
                logger.info("="*70)
            
            # Validate inputs
            if not resume_path and not resume_text:
                raise ValueError("Either resume_path or resume_text must be provided")
            
            # Step 1: Extract text
            text = self._step_extract_text(resume_path, resume_text)
            
            # Step 2: Structure resume
            resume_json = self._step_structure_resume(text)
            
            # Step 3: Run all analysis modules
            ats_result = self._step_validate_ats(resume_json)
            skill_result = self._step_analyze_skills(resume_json, job_description)
            impact_result = self._step_score_impact(resume_json)
            formatting_result = self._step_analyze_formatting(resume_json)
            
            # Step 4: Aggregate scores
            final_score = self._step_aggregate_scores(
                ats_result, skill_result, impact_result, formatting_result
            )
            
            # Step 5: Generate feedback
            feedback_result = self._step_generate_feedback(
                resume_json, ats_result, skill_result,
                impact_result, formatting_result, final_score
            )
            
            # Step 6: Build unified output
            output = self._build_output(
                resume_json, ats_result, skill_result, impact_result,
                formatting_result, final_score, feedback_result
            )
            
            # Add timing metadata
            end_time = datetime.now()
            duration = (end_time - start_time).total_seconds()
            output['metadata']['analysis_duration_seconds'] = round(duration, 2)
            output['metadata']['analyzed_at'] = end_time.isoformat()
            
            if self.enable_detailed_logging:
                logger.info("="*70)
                logger.info(f"✅ Analysis Complete - Score: {output['ats_score']}/100")
                logger.info(f"⏱️  Duration: {duration:.2f}s")
                logger.info("="*70)
            
            return output
            
        except Exception as e:
            logger.error(f"❌ Analysis failed: {str(e)}")
            logger.error(traceback.format_exc())
            return self._build_error_output(str(e))
    
    # ========================================================================
    # Individual Analysis Steps
    # ========================================================================
    
    def _step_extract_text(
        self,
        resume_path: Optional[str],
        resume_text: Optional[str]
    ) -> str:
        """Step 1: Extract text from resume"""
        if self.enable_detailed_logging:
            logger.info("📄 Step 1/6: Extracting text...")
        
        try:
            if resume_text:
                text = resume_text
            else:
                text = self.text_extractor.extract_text(resume_path)
            
            if not text or len(text.strip()) < 50:
                raise ValueError("Resume text too short or empty")
            
            if self.enable_detailed_logging:
                logger.info(f"   ✓ Extracted {len(text)} characters")
            
            return text
            
        except TextExtractionError as e:
            raise Exception(f"Text extraction failed: {str(e)}")
        except Exception as e:
            raise Exception(f"Unexpected error during text extraction: {str(e)}")
    
    def _step_structure_resume(self, text: str) -> Dict[str, Any]:
        """Step 2: Structure resume into JSON"""
        if self.enable_detailed_logging:
            logger.info("🏗️  Step 2/6: Structuring resume...")
        
        try:
            resume_json = structure_resume(text)
            
            if not resume_json:
                raise ValueError("Resume structuring produced empty result")
            
            sections_found = len(resume_json.keys())
            if self.enable_detailed_logging:
                logger.info(f"   ✓ Found {sections_found} sections")
            
            return resume_json
            
        except Exception as e:
            raise Exception(f"Resume structuring failed: {str(e)}")
    
    def _step_validate_ats(self, resume_json: Dict[str, Any]) -> Dict[str, Any]:
        """Step 3a: ATS validation"""
        if self.enable_detailed_logging:
            logger.info("📋 Step 3/6: Running ATS validation...")
        
        try:
            result = self.ats_validator.validate(resume_json)
            
            if self.enable_detailed_logging:
                score = result.get('rule_score', 0)
                violations = len(result.get('violations', []))
                logger.info(f"   ✓ ATS Score: {score}/100, Violations: {violations}")
            
            return result
            
        except Exception as e:
            logger.warning(f"ATS validation failed: {e}")
            return {
                'rule_score': 0,
                'violations': [],
                'passed_checks': [],
                'score_breakdown': {}
            }
    
    def _step_analyze_skills(
        self,
        resume_json: Dict[str, Any],
        job_description: Optional[str]
    ) -> Dict[str, Any]:
        """Step 4/6: Skill matching"""
        if self.enable_detailed_logging:
            logger.info("🎯 Step 4/6: Analyzing skills...")
        
        try:
            if job_description:
                result = match_skills(resume_json, job_description)
                
                if self.enable_detailed_logging:
                    matched = len(result.get('matched_skills', []))
                    missing = len(result.get('missing_skills', []))
                    logger.info(f"   ✓ Matched: {matched}, Missing: {missing}")
                
                return result
            else:
                # No job description - return neutral result
                resume_skills = len(resume_json.get('skills', []))
                
                if self.enable_detailed_logging:
                    logger.info(f"   ⚠️  No job description provided (found {resume_skills} resume skills)")
                
                return {
                    'keyword_match_score': 50,
                    'matched_skills': [],
                    'missing_skills': [],
                    'match_details': {
                        'total_job_skills': 0,
                        'total_resume_skills': resume_skills
                    }
                }
                
        except Exception as e:
            logger.warning(f"Skill matching failed: {e}")
            return {
                'keyword_match_score': 0,
                'matched_skills': [],
                'missing_skills': [],
                'match_details': {}
            }
    
    def _step_score_impact(self, resume_json: Dict[str, Any]) -> Dict[str, Any]:
        """Step 5/6: Impact scoring"""
        if self.enable_detailed_logging:
            logger.info("💪 Step 5/6: Scoring impact...")
        
        try:
            result = score_impact(resume_json)
            
            if self.enable_detailed_logging:
                score = result.get('impact_score', 0)
                strengths = len(result.get('strengths', []))
                logger.info(f"   ✓ Impact Score: {score}/100, Strengths: {strengths}")
            
            return result
            
        except Exception as e:
            logger.warning(f"Impact scoring failed: {e}")
            return {
                'impact_score': 0,
                'strengths': [],
                'weak_points': []
            }
    
    def _step_analyze_formatting(self, resume_json: Dict[str, Any]) -> Dict[str, Any]:
        """Step 5/6: Formatting analysis"""
        if self.enable_detailed_logging:
            logger.info("🎨 Step 5/6: Analyzing formatting...")
        
        try:
            result = analyze_formatting(resume_json)
            
            if self.enable_detailed_logging:
                score = result.get('formatting_score', 0)
                issues = len(result.get('formatting_issues', []))
                logger.info(f"   ✓ Formatting Score: {score}/100, Issues: {issues}")
            
            return result
            
        except Exception as e:
            logger.warning(f"Formatting analysis failed: {e}")
            return {
                'formatting_score': 0,
                'formatting_issues': [],
                'formatting_recommendations': []
            }
    
    def _step_aggregate_scores(
        self,
        ats_result: Dict[str, Any],
        skill_result: Dict[str, Any],
        impact_result: Dict[str, Any],
        formatting_result: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Step 6/6: Aggregate final score"""
        if self.enable_detailed_logging:
            logger.info("🧮 Step 6/6: Calculating final score...")
        
        try:
            result = calculate_ats_score(
                rule_score=ats_result.get('rule_score'),
                keyword_score=skill_result.get('keyword_match_score'),
                impact_score=impact_result.get('impact_score'),
                formatting_score=formatting_result.get('formatting_score')
            )
            
            if self.enable_detailed_logging:
                final_score = result.get('ats_score', 0)
                grade = result.get('score_grade', 'F')
                logger.info(f"   ✓ Final ATS Score: {final_score}/100 (Grade: {grade})")
            
            return result
            
        except Exception as e:
            logger.warning(f"Score aggregation failed: {e}")
            return {
                'ats_score': 0,
                'section_scores': {},
                'score_grade': 'F'
            }
    
    def _step_generate_feedback(
        self,
        resume_json: Dict[str, Any],
        ats_result: Dict[str, Any],
        skill_result: Dict[str, Any],
        impact_result: Dict[str, Any],
        formatting_result: Dict[str, Any],
        final_result: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Generate comprehensive feedback"""
        if self.enable_detailed_logging:
            logger.info("💬 Generating feedback...")
        
        try:
            result = generate_feedback(
                resume_json,
                ats_result,
                skill_result,
                impact_result,
                formatting_result,
                final_result,
                use_llm=self.use_llm_feedback,
                llm_api_key=self.llm_api_key
            )
            
            if self.enable_detailed_logging:
                suggestions = len(result.get('improvement_suggestions', []))
                logger.info(f"   ✓ Generated {suggestions} improvement suggestions")
            
            return result
            
        except Exception as e:
            logger.warning(f"Feedback generation failed: {e}")
            return {
                'feedback': 'Unable to generate detailed feedback.',
                'improvement_suggestions': []
            }
    
    # ========================================================================
    # Output Building
    # ========================================================================
    
    def _build_output(
        self,
        resume_json: Dict[str, Any],
        ats_result: Dict[str, Any],
        skill_result: Dict[str, Any],
        impact_result: Dict[str, Any],
        formatting_result: Dict[str, Any],
        final_result: Dict[str, Any],
        feedback_result: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Build standardized output format"""
        return {
            # Core ATS score (0-100)
            'ats_score': round(final_result.get('ats_score', 0), 2),
            
            # Detailed section scores
            'section_scores': {
                'ats_compliance': round(ats_result.get('rule_score', 0), 2),
                'keyword_matching': round(skill_result.get('keyword_match_score', 0), 2),
                'impact_quality': round(impact_result.get('impact_score', 0), 2),
                'formatting': round(formatting_result.get('formatting_score', 0), 2)
            },
            
            # Skill matching results
            'matched_skills': [
                {
                    'resume_skill': m.get('resume_skill', ''),
                    'job_skill': m.get('job_skill', ''),
                    'match_type': m.get('match_type', 'exact'),
                    'confidence': round(m.get('similarity_score', 1.0), 2)
                }
                for m in skill_result.get('matched_skills', [])
            ],
            
            'missing_skills': skill_result.get('missing_skills', []),
            
            # Strengths identified
            'strengths': self._extract_strengths(
                ats_result, skill_result, impact_result, formatting_result
            ),
            
            # Improvement suggestions (prioritized)
            'improvement_suggestions': [
                {
                    'category': s.get('category', 'general'),
                    'priority': s.get('priority', 'medium'),
                    'title': s.get('issue', ''),
                    'description': s.get('suggestion', ''),
                    'expected_impact': s.get('impact', '')
                }
                for s in feedback_result.get('improvement_suggestions', [])
            ],
            
            # Overall feedback
            'feedback': feedback_result.get('feedback', ''),
            
            # Detailed results (for advanced users)
            'detailed_results': {
                'ats_violations': ats_result.get('violations', []),
                'ats_passed_checks': ats_result.get('passed_checks', []),
                'impact_strengths': impact_result.get('strengths', []),
                'impact_weak_points': impact_result.get('weak_points', []),
                'formatting_issues': formatting_result.get('formatting_issues', []),
                'formatting_recommendations': formatting_result.get('formatting_recommendations', [])
            },
            
            # Metadata
            'metadata': {
                'analysis_version': '2.0.0',
                'model_type': 'unified',
                'grade': final_result.get('score_grade', 'F'),
                'total_suggestions': len(feedback_result.get('improvement_suggestions', [])),
                'has_job_description': skill_result.get('match_details', {}).get('total_job_skills', 0) > 0,
                'resume_sections_found': list(resume_json.keys()),
                'llm_feedback_enabled': self.use_llm_feedback
            }
        }
    
    def _extract_strengths(
        self,
        ats_result: Dict[str, Any],
        skill_result: Dict[str, Any],
        impact_result: Dict[str, Any],
        formatting_result: Dict[str, Any]
    ) -> List[str]:
        """Extract strengths from all analysis results"""
        strengths = []
        
        # From ATS validation
        rule_score = ats_result.get('rule_score', 0)
        if rule_score >= 80:
            strengths.append(f"✓ Excellent ATS compliance ({rule_score}/100)")
        elif rule_score >= 60:
            strengths.append(f"✓ Good ATS compliance ({rule_score}/100)")
        
        passed_checks = ats_result.get('passed_checks', [])
        if len(passed_checks) > 10:
            strengths.append(f"✓ Passes {len(passed_checks)} ATS quality checks")
        
        # From skill matching
        match_score = skill_result.get('keyword_match_score', 0)
        if match_score >= 75:
            strengths.append(f"✓ Excellent keyword match ({match_score}%)")
        elif match_score >= 50:
            strengths.append(f"✓ Good keyword match ({match_score}%)")
        
        # From impact scoring
        impact_strengths = impact_result.get('strengths', [])
        for strength in impact_strengths[:3]:  # Top 3
            strengths.append(f"✓ {strength}")
        
        # From formatting
        formatting_score = formatting_result.get('formatting_score', 0)
        if formatting_score >= 80:
            strengths.append(f"✓ Well-formatted resume ({formatting_score}/100)")
        
        return strengths[:10]  # Max 10 strengths
    
    def _build_error_output(self, error_message: str) -> Dict[str, Any]:
        """Build error output in case of failure"""
        return {
            'ats_score': 0,
            'section_scores': {
                'ats_compliance': 0,
                'keyword_matching': 0,
                'impact_quality': 0,
                'formatting': 0
            },
            'matched_skills': [],
            'missing_skills': [],
            'strengths': [],
            'improvement_suggestions': [
                {
                    'category': 'error',
                    'priority': 'high',
                    'title': 'Analysis Failed',
                    'description': f'Unable to analyze resume: {error_message}',
                    'expected_impact': 'Please check the resume file and try again'
                }
            ],
            'feedback': f'Resume analysis failed: {error_message}',
            'detailed_results': {},
            'metadata': {
                'analysis_version': '2.0.0',
                'model_type': 'unified',
                'grade': 'F',
                'error': True,
                'error_message': error_message
            }
        }


# ============================================================================
# Convenience function for quick usage
# ============================================================================

def analyze_resume(
    resume_path: Optional[str] = None,
    resume_text: Optional[str] = None,
    job_description: Optional[str] = None,
    use_llm_feedback: bool = False,
    llm_api_key: Optional[str] = None,
    enable_detailed_logging: bool = True
) -> Dict[str, Any]:
    """
    Quick convenience function for resume analysis.
    
    This is the simplest way to use the unified model - just call this function!
    
    Args:
        resume_path: Path to resume file (PDF or DOCX)
        resume_text: Raw resume text (alternative to resume_path)
        job_description: Optional job description for skill matching
        use_llm_feedback: Whether to use LLM for enhanced feedback
        llm_api_key: Optional API key for LLM-based feedback
        enable_detailed_logging: Enable detailed logging
        
    Returns:
        Comprehensive analysis result
        
    Example:
        # Analyze from file
        result = analyze_resume(resume_path="resume.pdf")
        
        # Analyze with job description
        result = analyze_resume(
            resume_path="resume.pdf",
            job_description="Looking for Python developer..."
        )
        
        # Analyze from text
        result = analyze_resume(
            resume_text="John Doe\\nSoftware Engineer...",
            job_description="..."
        )
    """
    analyzer = UnifiedResumeAnalyzer(
        use_llm_feedback=use_llm_feedback,
        llm_api_key=llm_api_key,
        enable_detailed_logging=enable_detailed_logging
    )
    
    return analyzer.analyze(
        resume_path=resume_path,
        resume_text=resume_text,
        job_description=job_description
    )


if __name__ == '__main__':
    # Example usage and testing
    import json
    import sys
    
    print("="*70)
    print("          UNIFIED RESUME ANALYSIS MODEL v2.0")
    print("="*70)
    print()
    
    if len(sys.argv) > 1:
        resume_file = sys.argv[1]
        job_desc = sys.argv[2] if len(sys.argv) > 2 else None
        
        print(f"Analyzing: {resume_file}")
        if job_desc:
            print(f"Job Description: {job_desc[:100]}...")
        print()
        
        # Run analysis
        result = analyze_resume(
            resume_path=resume_file,
            job_description=job_desc
        )
        
        # Print results
        print(json.dumps(result, indent=2))
        
        print()
        print("="*70)
        print(f"FINAL SCORE: {result['ats_score']}/100 ({result['metadata']['grade']})")
        print("="*70)
    else:
        print("Usage: python unified_model.py <resume_path> [job_description]")
        print()
        print("Example:")
        print('  python unified_model.py resume.pdf "Looking for Python developer..."')
        print()
        print("Or use in your code:")
        print("  from unified_model import analyze_resume")
        print('  result = analyze_resume(resume_path="resume.pdf")')
