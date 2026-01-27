"""
Skill Matching Module

A production-ready skill matching system for ATS keyword analysis.
Combines exact keyword matching with semantic similarity using transformer models.

Features:
- Exact keyword matching (case-insensitive)
- Semantic similarity using sentence-transformers (MiniLM)
- Cosine similarity scoring
- Explainable match scores
- Optimized for ATS realism

No LLM usage - Uses lightweight embedding models

Author: ML Engineer
"""

import re
from typing import Dict, List, Any, Tuple, Set
import numpy as np
from dataclasses import dataclass
import logging

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


@dataclass
class SkillMatch:
    """Represents a matched skill with similarity score"""
    resume_skill: str
    job_skill: str
    match_type: str  # 'exact' or 'semantic'
    similarity_score: float
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            'resume_skill': self.resume_skill,
            'job_skill': self.job_skill,
            'match_type': self.match_type,
            'similarity_score': round(self.similarity_score, 3)
        }


class SkillMatcher:
    """
    Intelligent skill matcher using exact and semantic matching.
    
    Combines:
    1. Exact keyword matching (case-insensitive)
    2. Semantic similarity using sentence-transformers
    3. Abbreviation/synonym handling
    """
    
    # Common skill abbreviations and synonyms
    SKILL_SYNONYMS = {
        'js': 'javascript',
        'ts': 'typescript',
        'py': 'python',
        'db': 'database',
        'api': 'application programming interface',
        'ml': 'machine learning',
        'ai': 'artificial intelligence',
        'nlp': 'natural language processing',
        'cv': 'computer vision',
        'ci/cd': 'continuous integration continuous deployment',
        'k8s': 'kubernetes',
        'aws': 'amazon web services',
        'gcp': 'google cloud platform',
        'sql': 'structured query language',
        'nosql': 'not only sql',
        'rest': 'representational state transfer',
        'orm': 'object relational mapping',
        'ui': 'user interface',
        'ux': 'user experience',
        'qa': 'quality assurance',
        'devops': 'development operations'
    }
    
    # Semantic similarity threshold for matches
    SEMANTIC_THRESHOLD = 0.7  # 70% similarity
    
    def __init__(self, use_semantic: bool = True):
        """
        Initialize skill matcher.
        
        Args:
            use_semantic: Whether to use semantic matching (requires sentence-transformers)
        """
        self.use_semantic = use_semantic
        self.model = None
        
        if use_semantic:
            self.model = self._load_model()
    
    def _load_model(self):
        """Load sentence-transformers model"""
        try:
            from sentence_transformers import SentenceTransformer
            
            # Use MiniLM - lightweight and fast
            model_name = 'all-MiniLM-L6-v2'
            logger.info(f"Loading sentence-transformers model: {model_name}")
            model = SentenceTransformer(model_name)
            logger.info("Model loaded successfully")
            return model
            
        except ImportError:
            logger.warning("sentence-transformers not installed. Falling back to exact matching only.")
            self.use_semantic = False
            return None
        except Exception as e:
            logger.error(f"Error loading model: {e}")
            self.use_semantic = False
            return None
    
    def match_skills(
        self,
        resume_json: Dict[str, Any],
        job_description: str
    ) -> Dict[str, Any]:
        """
        Match skills between resume and job description.
        
        Args:
            resume_json: Structured resume JSON with 'skills' field
            job_description: Raw job description text
            
        Returns:
            Dictionary with:
            {
                "matched_skills": [...],
                "missing_skills": [...],
                "keyword_match_score": 0-100
            }
        """
        # Extract skills
        resume_skills = self._extract_resume_skills(resume_json)
        job_skills = self._extract_job_skills(job_description)
        
        logger.info(f"Resume skills: {len(resume_skills)}, Job skills: {len(job_skills)}")
        
        # Perform matching
        matched_skills, missing_skills = self._perform_matching(resume_skills, job_skills)
        
        # Calculate keyword match score
        keyword_score = self._calculate_match_score(matched_skills, job_skills)
        
        result = {
            'matched_skills': [match.to_dict() for match in matched_skills],
            'missing_skills': missing_skills,
            'keyword_match_score': round(keyword_score, 2),
            'match_details': {
                'total_job_skills': len(job_skills),
                'total_resume_skills': len(resume_skills),
                'exact_matches': len([m for m in matched_skills if m.match_type == 'exact']),
                'semantic_matches': len([m for m in matched_skills if m.match_type == 'semantic']),
                'match_rate': round(len(matched_skills) / len(job_skills) * 100, 2) if job_skills else 0
            }
        }
        
        logger.info(f"Matching complete. Score: {keyword_score}/100, "
                   f"Matched: {len(matched_skills)}, Missing: {len(missing_skills)}")
        
        return result
    
    def _extract_resume_skills(self, resume_json: Dict[str, Any]) -> List[str]:
        """Extract and normalize skills from resume JSON"""
        skills = []
        
        # Get skills from 'skills' field
        if 'skills' in resume_json and resume_json['skills']:
            skills.extend(resume_json['skills'])
        
        # Normalize skills
        normalized = []
        for skill in skills:
            # Clean and lowercase
            cleaned = self._normalize_skill(skill)
            if cleaned:
                normalized.append(cleaned)
        
        # Remove duplicates while preserving order
        unique_skills = list(dict.fromkeys(normalized))
        
        return unique_skills
    
    def _extract_job_skills(self, job_description: str) -> List[str]:
        """Extract skills from job description text"""
        # Common patterns for skill sections in job descriptions
        skill_section_patterns = [
            r'(?:required skills|skills required|technical skills|qualifications)[:\s]*(.+?)(?:\n\n|required|preferred|$)',
            r'(?:must have|requirements)[:\s]*(.+?)(?:\n\n|nice to have|preferred|$)',
            r'(?:experience with|proficiency in|knowledge of)[:\s]*(.+?)(?:\n|$)'
        ]
        
        skills = set()
        
        # Try to extract from skill sections
        for pattern in skill_section_patterns:
            matches = re.findall(pattern, job_description, re.IGNORECASE | re.DOTALL)
            for match in matches:
                # Split by common delimiters
                skill_items = re.split(r'[,;•\n]', match)
                for item in skill_items:
                    cleaned = self._normalize_skill(item)
                    if cleaned and len(cleaned) > 1:
                        skills.add(cleaned)
        
        # Also extract known technical terms (if no skills found in sections)
        if not skills:
            # Look for programming languages, frameworks, tools
            tech_patterns = [
                r'\b(python|java|javascript|typescript|c\+\+|c#|ruby|php|go|rust|swift|kotlin)\b',
                r'\b(react|angular|vue|node\.js|django|flask|spring|express)\b',
                r'\b(aws|azure|gcp|docker|kubernetes|jenkins|git)\b',
                r'\b(sql|mysql|postgresql|mongodb|redis|elasticsearch)\b',
                r'\b(machine learning|deep learning|ai|nlp|data science)\b'
            ]
            
            for pattern in tech_patterns:
                matches = re.findall(pattern, job_description, re.IGNORECASE)
                for match in matches:
                    cleaned = self._normalize_skill(match)
                    if cleaned:
                        skills.add(cleaned)
        
        return list(skills)
    
    def _normalize_skill(self, skill: str) -> str:
        """Normalize a skill string"""
        if not skill:
            return ''
        
        # Convert to lowercase and strip
        skill = skill.lower().strip()
        
        # Remove common prefixes/suffixes
        skill = re.sub(r'^(experience with|knowledge of|proficient in|strong|excellent)\s+', '', skill)
        skill = re.sub(r'\s+(experience|skills?|proficiency)$', '', skill)
        
        # Remove parentheses content
        skill = re.sub(r'\([^)]*\)', '', skill)
        
        # Clean up whitespace and special characters
        skill = re.sub(r'[^\w\s\+\-\.]', '', skill)
        skill = ' '.join(skill.split())
        
        # Expand abbreviations
        if skill in self.SKILL_SYNONYMS:
            skill = self.SKILL_SYNONYMS[skill]
        
        return skill
    
    def _perform_matching(
        self,
        resume_skills: List[str],
        job_skills: List[str]
    ) -> Tuple[List[SkillMatch], List[str]]:
        """
        Perform exact and semantic matching.
        
        Returns:
            (matched_skills, missing_skills)
        """
        matched_skills = []
        matched_job_skills = set()
        
        # First pass: Exact matching
        for job_skill in job_skills:
            for resume_skill in resume_skills:
                if self._is_exact_match(resume_skill, job_skill):
                    match = SkillMatch(
                        resume_skill=resume_skill,
                        job_skill=job_skill,
                        match_type='exact',
                        similarity_score=1.0
                    )
                    matched_skills.append(match)
                    matched_job_skills.add(job_skill)
                    break
        
        # Second pass: Semantic matching for unmatched job skills
        if self.use_semantic and self.model:
            unmatched_job_skills = [s for s in job_skills if s not in matched_job_skills]
            
            if unmatched_job_skills and resume_skills:
                semantic_matches = self._semantic_matching(
                    resume_skills,
                    unmatched_job_skills
                )
                matched_skills.extend(semantic_matches)
                matched_job_skills.update([m.job_skill for m in semantic_matches])
        
        # Identify missing skills
        missing_skills = [s for s in job_skills if s not in matched_job_skills]
        
        return matched_skills, missing_skills
    
    def _is_exact_match(self, skill1: str, skill2: str) -> bool:
        """Check if two skills are an exact match"""
        # Direct equality
        if skill1 == skill2:
            return True
        
        # One is substring of the other (with word boundaries)
        if skill1 in skill2 or skill2 in skill1:
            # Check if it's a meaningful substring (not just partial word)
            words1 = set(skill1.split())
            words2 = set(skill2.split())
            # If either skill is a single word and it's in the other, it's a match
            if len(words1) == 1 and words1.issubset(words2):
                return True
            if len(words2) == 1 and words2.issubset(words1):
                return True
        
        return False
    
    def _semantic_matching(
        self,
        resume_skills: List[str],
        job_skills: List[str]
    ) -> List[SkillMatch]:
        """
        Perform semantic similarity matching.
        
        Uses sentence-transformers to find semantically similar skills.
        """
        if not self.model:
            return []
        
        matches = []
        
        try:
            # Encode all skills
            resume_embeddings = self.model.encode(resume_skills)
            job_embeddings = self.model.encode(job_skills)
            
            # Calculate cosine similarities
            for i, job_skill in enumerate(job_skills):
                job_embedding = job_embeddings[i]
                
                best_match_idx = -1
                best_similarity = 0.0
                
                for j, resume_embedding in enumerate(resume_embeddings):
                    # Cosine similarity
                    similarity = self._cosine_similarity(job_embedding, resume_embedding)
                    
                    if similarity > best_similarity:
                        best_similarity = similarity
                        best_match_idx = j
                
                # Only add if above threshold
                if best_similarity >= self.SEMANTIC_THRESHOLD:
                    match = SkillMatch(
                        resume_skill=resume_skills[best_match_idx],
                        job_skill=job_skill,
                        match_type='semantic',
                        similarity_score=float(best_similarity)
                    )
                    matches.append(match)
        
        except Exception as e:
            logger.error(f"Error in semantic matching: {e}")
        
        return matches
    
    def _cosine_similarity(self, vec1: np.ndarray, vec2: np.ndarray) -> float:
        """Calculate cosine similarity between two vectors"""
        dot_product = np.dot(vec1, vec2)
        norm1 = np.linalg.norm(vec1)
        norm2 = np.linalg.norm(vec2)
        
        if norm1 == 0 or norm2 == 0:
            return 0.0
        
        return dot_product / (norm1 * norm2)
    
    def _calculate_match_score(
        self,
        matched_skills: List[SkillMatch],
        job_skills: List[str]
    ) -> float:
        """
        Calculate overall keyword match score (0-100).
        
        Score is weighted:
        - Exact matches: 100% weight
        - Semantic matches: Weighted by similarity score
        """
        if not job_skills:
            return 0.0
        
        total_weight = 0.0
        
        for match in matched_skills:
            if match.match_type == 'exact':
                total_weight += 1.0
            else:  # semantic
                total_weight += match.similarity_score
        
        # Calculate percentage
        score = (total_weight / len(job_skills)) * 100
        
        # Cap at 100
        return min(score, 100.0)


def match_skills(resume_json: Dict[str, Any], job_description: str) -> Dict[str, Any]:
    """
    Convenience function to match skills.
    
    Args:
        resume_json: Structured resume JSON
        job_description: Job description text
        
    Returns:
        Match result with matched_skills, missing_skills, and score
    """
    matcher = SkillMatcher()
    return matcher.match_skills(resume_json, job_description)


if __name__ == '__main__':
    # Example usage
    import json
    
    # Sample resume
    sample_resume = {
        "skills": [
            "Python", "JavaScript", "React", "Node.js",
            "AWS", "Docker", "PostgreSQL", "MongoDB",
            "Machine Learning", "TensorFlow"
        ]
    }
    
    # Sample job description
    sample_job = """
    We are looking for a Senior Software Engineer with the following skills:
    
    Required Skills:
    - Python programming
    - JavaScript and React
    - AWS cloud services
    - Docker and Kubernetes
    - SQL databases (PostgreSQL preferred)
    - RESTful API development
    
    Nice to Have:
    - Machine Learning experience
    - Go programming language
    - GraphQL
    """
    
    # Match skills
    matcher = SkillMatcher()
    result = matcher.match_skills(sample_resume, sample_job)
    
    # Print results
    print(json.dumps(result, indent=2))
