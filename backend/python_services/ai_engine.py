"""
Unified AI Engine for Resume Analysis

A production-ready orchestration engine that combines all analysis modules
into a single, cohesive AI service.

Features:
- Single API endpoint for complete resume analysis
- Orchestrates all modules internally
- Standardized JSON output
- Error handling and logging
- Node.js compatible (black box design)

Flow:
Resume → Parsing → Structuring → Scoring → Feedback → Unified Output

Author: Backend AI Architect
"""

from typing import Dict, Any, Optional
import logging
from pathlib import Path
import traceback

# Import all analysis modules
from .text_extractor import extract_text, TextExtractionError
from .resume_structurer import structure_resume
from .ats_validator import validate_resume
from .skill_matcher import match_skills
from .impact_scorer import score_impact
from .formatting_analyzer import analyze_formatting
from .score_aggregator import calculate_ats_score
from .feedback_generator import generate_feedback

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


class ResumeAnalysisEngine:
    """
    Unified AI Engine for complete resume analysis.
    
    Orchestrates all modules to provide a single, cohesive analysis service.
    Designed to be used as a black box by external services (e.g., Node.js).
    """
    
    def __init__(self, use_llm_feedback: bool = False, llm_api_key: Optional[str] = None):
        """
        Initialize the resume analysis engine.
        
        Args:
            use_llm_feedback: Whether to use LLM for enhanced feedback
            llm_api_key: Optional LLM API key for advanced feedback
        """
        self.use_llm_feedback = use_llm_feedback
        self.llm_api_key = llm_api_key
        logger.info("Resume Analysis Engine initialized")
    
    def analyze_resume(
        self,
        resume_path: str,
        job_description: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Complete resume analysis pipeline.
        
        This is the MAIN API endpoint - everything happens through this single call.
        
        Args:
            resume_path: Path to resume file (PDF or DOCX)
            job_description: Optional job description for skill matching
            
        Returns:
            Standardized analysis result in unified format
        """
        try:
            logger.info(f"Starting resume analysis for: {resume_path}")
            
            # Step 1: Extract text from resume
            logger.info("Step 1/6: Extracting text...")
            text = self._extract_text(resume_path)
            
            # Step 2: Structure resume into JSON
            logger.info("Step 2/6: Structuring resume...")
            resume_json = self._structure_resume(text)
            
            # Step 3: Run all analysis modules in parallel
            logger.info("Step 3/6: Running ATS validation...")
            ats_result = self._validate_ats(resume_json)
            
            logger.info("Step 4/6: Analyzing skills...")
            skill_result = self._analyze_skills(resume_json, job_description)
            
            logger.info("Step 5/6: Scoring impact...")
            impact_result = self._score_impact(resume_json)
            
            logger.info("Step 5/6: Analyzing formatting...")
            formatting_result = self._analyze_formatting(resume_json)
            
            # Step 4: Aggregate final score
            logger.info("Step 6/6: Calculating final score...")
            final_result = self._aggregate_scores(
                ats_result, skill_result, impact_result, formatting_result
            )
            
            # Step 5: Generate feedback
            logger.info("Step 6/6: Generating feedback...")
            feedback_result = self._generate_feedback(
                resume_json, ats_result, skill_result,
                impact_result, formatting_result, final_result
            )
            
            # Step 6: Build unified output
            output = self._build_unified_output(
                resume_json, ats_result, skill_result, impact_result,
                formatting_result, final_result, feedback_result
            )
            
            logger.info(f"Analysis complete. Final ATS Score: {output['ats_score']}/100")
            
            return output
            
        except Exception as e:
            logger.error(f"Analysis failed: {str(e)}\n{traceback.format_exc()}")
            return self._build_error_output(str(e))
    
    def _extract_text(self, resume_path: str) -> str:
        """Step 1: Extract text from resume file"""
        try:
            text = extract_text(resume_path)
            if not text or len(text.strip()) < 50:
                raise ValueError("Resume text too short or empty")
            return text
        except TextExtractionError as e:
            raise Exception(f"Text extraction failed: {str(e)}")
        except Exception as e:
            raise Exception(f"Unexpected error during text extraction: {str(e)}")
    
    def _structure_resume(self, text: str) -> Dict[str, Any]:
        """Step 2: Structure resume into JSON"""
        try:
            resume_json = structure_resume(text)
            if not resume_json:
                raise ValueError("Resume structuring produced empty result")
            return resume_json
        except Exception as e:
            raise Exception(f"Resume structuring failed: {str(e)}")
    
    def _validate_ats(self, resume_json: Dict[str, Any]) -> Dict[str, Any]:
        """Step 3a: ATS validation"""
        try:
            return validate_resume(resume_json)
        except Exception as e:
            logger.warning(f"ATS validation failed: {e}")
            return {'rule_score': 0, 'violations': [], 'passed_checks': []}
    
    def _analyze_skills(
        self,
        resume_json: Dict[str, Any],
        job_description: Optional[str]
    ) -> Dict[str, Any]:
        """Step 3b: Skill matching"""
        try:
            if job_description:
                return match_skills(resume_json, job_description)
            else:
                # No job description provided - return neutral result
                return {
                    'keyword_match_score': 50,
                    'matched_skills': [],
                    'missing_skills': [],
                    'match_details': {
                        'total_job_skills': 0,
                        'total_resume_skills': len(resume_json.get('skills', []))
                    }
                }
        except Exception as e:
            logger.warning(f"Skill matching failed: {e}")
            return {
                'keyword_match_score': 0,
                'matched_skills': [],
                'missing_skills': []
            }
    
    def _score_impact(self, resume_json: Dict[str, Any]) -> Dict[str, Any]:
        """Step 3c: Impact scoring"""
        try:
            return score_impact(resume_json)
        except Exception as e:
            logger.warning(f"Impact scoring failed: {e}")
            return {
                'impact_score': 0,
                'strengths': [],
                'weak_points': []
            }
    
    def _analyze_formatting(self, resume_json: Dict[str, Any]) -> Dict[str, Any]:
        """Step 3d: Formatting analysis"""
        try:
            return analyze_formatting(resume_json)
        except Exception as e:
            logger.warning(f"Formatting analysis failed: {e}")
            return {
                'formatting_score': 0,
                'formatting_issues': [],
                'formatting_recommendations': []
            }
    
    def _aggregate_scores(
        self,
        ats_result: Dict[str, Any],
        skill_result: Dict[str, Any],
        impact_result: Dict[str, Any],
        formatting_result: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Step 4: Aggregate final score"""
        try:
            return calculate_ats_score(
                rule_score=ats_result.get('rule_score'),
                keyword_score=skill_result.get('keyword_match_score'),
                impact_score=impact_result.get('impact_score'),
                formatting_score=formatting_result.get('formatting_score')
            )
        except Exception as e:
            logger.warning(f"Score aggregation failed: {e}")
            return {
                'ats_score': 0,
                'section_scores': {},
                'score_grade': 'F'
            }
    
    def _generate_feedback(
        self,
        resume_json: Dict[str, Any],
        ats_result: Dict[str, Any],
        skill_result: Dict[str, Any],
        impact_result: Dict[str, Any],
        formatting_result: Dict[str, Any],
        final_result: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Step 5: Generate feedback"""
        try:
            return generate_feedback(
                resume_json,
                ats_result,
                skill_result,
                impact_result,
                formatting_result,
                final_result,
                use_llm=self.use_llm_feedback,
                llm_api_key=self.llm_api_key
            )
        except Exception as e:
            logger.warning(f"Feedback generation failed: {e}")
            return {
                'feedback': 'Unable to generate detailed feedback.',
                'improvement_suggestions': []
            }
    
    def _build_unified_output(
        self,
        resume_json: Dict[str, Any],
        ats_result: Dict[str, Any],
        skill_result: Dict[str, Any],
        impact_result: Dict[str, Any],
        formatting_result: Dict[str, Any],
        final_result: Dict[str, Any],
        feedback_result: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Step 6: Build unified output in standardized format.
        
        This is the contract with Node.js - must be stable!
        """
        return {
            # Core score (0-100)
            'ats_score': final_result.get('ats_score', 0),
            
            # Section scores breakdown
            'section_scores': {
                'ats_compliance': ats_result.get('rule_score', 0),
                'keyword_matching': skill_result.get('keyword_match_score', 0),
                'impact_quality': impact_result.get('impact_score', 0),
                'formatting': formatting_result.get('formatting_score', 0)
            },
            
            # Skill matching results
            'matched_skills': [
                {
                    'resume_skill': m.get('resume_skill', ''),
                    'job_skill': m.get('job_skill', ''),
                    'match_type': m.get('match_type', 'exact'),
                    'confidence': m.get('similarity_score', 1.0)
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
            
            # Overall feedback text
            'feedback': feedback_result.get('feedback', ''),
            
            # Metadata
            'metadata': {
                'analysis_version': '1.0.0',
                'grade': final_result.get('score_grade', 'F'),
                'total_suggestions': len(feedback_result.get('improvement_suggestions', [])),
                'has_job_description': skill_result.get('match_details', {}).get('total_job_skills', 0) > 0,
                'resume_sections_found': list(resume_json.keys())
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
        if ats_result.get('rule_score', 0) >= 80:
            strengths.append("Strong ATS compliance - resume is well-structured")
        
        passed_checks = ats_result.get('passed_checks', [])
        if len(passed_checks) > 10:
            strengths.append(f"Passes {len(passed_checks)} ATS quality checks")
        
        # From skill matching
        match_score = skill_result.get('keyword_match_score', 0)
        if match_score >= 75:
            strengths.append(f"Excellent keyword match ({match_score}%) with job requirements")
        
        # From impact scoring
        impact_strengths = impact_result.get('strengths', [])
        strengths.extend(impact_strengths[:3])  # Top 3
        
        # From formatting
        formatting_recs = formatting_result.get('formatting_recommendations', [])
        positive_recs = [r for r in formatting_recs if r.startswith('✓')]
        strengths.extend(positive_recs[:3])  # Top 3
        
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
            'metadata': {
                'analysis_version': '1.0.0',
                'grade': 'F',
                'error': True,
                'error_message': error_message
            }
        }


# ============================================================================
# Convenience function for single-call API
# ============================================================================

def analyze_resume(
    resume_path: str,
    job_description: Optional[str] = None,
    use_llm_feedback: bool = False,
    llm_api_key: Optional[str] = None
) -> Dict[str, Any]:
    """
    Single API endpoint for complete resume analysis.
    
    This is the main function that Node.js (or any external service) should call.
    Everything happens internally - this is a black box.
    
    Args:
        resume_path: Path to resume file (PDF or DOCX)
        job_description: Optional job description for skill matching
        use_llm_feedback: Whether to use LLM for enhanced feedback
        llm_api_key: Optional LLM API key
        
    Returns:
        Standardized JSON with analysis results
        
    Example:
        result = analyze_resume("resume.pdf", job_description="...")
        print(f"ATS Score: {result['ats_score']}/100")
    """
    engine = ResumeAnalysisEngine(use_llm_feedback, llm_api_key)
    return engine.analyze_resume(resume_path, job_description)


if __name__ == '__main__':
    # Example usage
    import json
    import sys
    
    if len(sys.argv) > 1:
        resume_file = sys.argv[1]
    else:
        print("Usage: python ai_engine.py <resume_path> [job_description]")
        print("\nUsing sample resume for demo...")
        resume_file = "sample_resume.pdf"
    
    job_desc = None
    if len(sys.argv) > 2:
        job_desc = sys.argv[2]
    
    print("="*70)
    print("          UNIFIED AI ENGINE - Resume Analysis")
    print("="*70)
    print(f"\nAnalyzing: {resume_file}")
    if job_desc:
        print(f"Job Description: {job_desc[:100]}...")
    print()
    
    # Run analysis
    result = analyze_resume(resume_file, job_desc)
    
    # Print results
    print(json.dumps(result, indent=2))
    
    print("\n" + "="*70)
    print(f"FINAL ATS SCORE: {result['ats_score']}/100 ({result['metadata']['grade']})")
    print("="*70)
