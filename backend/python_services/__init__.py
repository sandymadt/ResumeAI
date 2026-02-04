"""
Resume Analysis Python Services

A production-ready AI-powered resume analysis system with complete pipeline:
text extraction, structuring, ATS validation, skill matching, impact scoring,
formatting analysis, score aggregation, and feedback generation.

Main API:
    - analyze_resume: Single endpoint for complete resume analysis (BLACK BOX)
    - ResumeAnalysisEngine: Unified orchestration engine

Individual Modules (for advanced usage):
    - text_extractor: Extract clean text from PDF/DOCX files
    - resume_structurer: Convert raw text into structured JSON
    - ats_validator: Validate resume ATS compliance
    - skill_matcher: Match skills between resume and job description
    - impact_scorer: Evaluate resume impact and achievement quality
    - formatting_analyzer: Check formatting and readability
    - score_aggregator: Calculate final ATS score
    - feedback_generator: Generate improvement suggestions

Main Exports:
    🔥 analyze_resume: ONE-CALL API for complete analysis
    🔥 ResumeAnalysisEngine: Orchestration engine
    
    Individual module functions (advanced):
    - extract_text, structure_resume, validate_resume, match_skills,
      score_impact, analyze_formatting, calculate_ats_score, generate_feedback
"""

# ============================================================================
# PRIMARY API - Use these for black-box operation
# ============================================================================

# 🔥 NEW: Unified Model (Recommended)
from .unified_model import (
    UnifiedResumeAnalyzer,
    analyze_resume as unified_analyze_resume
)

# Legacy: Original AI Engine (Still supported)
from .ai_engine import (
    analyze_resume,
    ResumeAnalysisEngine
)

# ============================================================================
# Individual modules - For advanced/custom workflows
# ============================================================================

from .text_extractor import (
    extract_text,
    ResumeTextExtractor,
    TextExtractionError
)

from .resume_structurer import (
    structure_resume,
    ResumeStructurer
)

from .ats_validator import (
    validate_resume,
    ATSValidator
)

from .skill_matcher import (
    match_skills,
    SkillMatcher
)

from .impact_scorer import (
    score_impact,
    ImpactScorer
)

from .formatting_analyzer import (
    analyze_formatting,
    FormattingAnalyzer
)

from .score_aggregator import (
    calculate_ats_score,
    ScoreAggregator
)

from .feedback_generator import (
    generate_feedback,
    FeedbackGenerator
)

__version__ = '1.0.0'
__author__ = 'Senior NLP Engineer'

__all__ = [
    # ========================================================================
    # PRIMARY API - Recommended for most use cases
    # ========================================================================
    # 🔥 NEW: Unified Model (Simplest and most powerful)
    'UnifiedResumeAnalyzer',      # 🔥 NEW! Single class for everything
    'unified_analyze_resume',     # 🔥 NEW! One-call convenience function
    
    # Legacy: Original AI Engine (Still supported)
    'analyze_resume',             # Original one-call API
    'ResumeAnalysisEngine',       # Original orchestration engine
    
    # ========================================================================
    # Individual modules - For advanced workflows
    # ========================================================================
    # Text extraction
    'extract_text',
    'ResumeTextExtractor',
    'TextExtractionError',
    # Resume structuring
    'structure_resume',
    'ResumeStructurer',
    # ATS validation
    'validate_resume',
    'ATSValidator',
    # Skill matching
    'match_skills',
    'SkillMatcher',
    # Impact scoring
    'score_impact',
    'ImpactScorer',
    # Formatting analysis
    'analyze_formatting',
    'FormattingAnalyzer',
    # Score aggregation
    'calculate_ats_score',
    'ScoreAggregator',
    # Feedback generation
    'generate_feedback',
    'FeedbackGenerator'
]
