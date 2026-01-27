"""
Impact Scoring Module

A production-ready module for evaluating resume impact and quality.
Uses spaCy dependency parsing and rule-based scoring logic.

Features:
- Quantified achievement detection (%, numbers, metrics)
- Ownership verb analysis (led, built, designed)
- Outcome-driven bullet identification
- STAR structure indicators
- Fully explainable scoring

No LLM usage - Pure NLP and rule-based logic

Author: NLP Engineer
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
class BulletAnalysis:
    """Analysis of a single bullet point"""
    text: str
    has_quantification: bool
    has_ownership_verb: bool
    has_outcome: bool
    has_star_structure: bool
    impact_score: float
    findings: List[str]
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            'text': self.text[:80] + '...' if len(self.text) > 80 else self.text,
            'has_quantification': self.has_quantification,
            'has_ownership_verb': self.has_ownership_verb,
            'has_outcome': self.has_outcome,
            'has_star_structure': self.has_star_structure,
            'impact_score': round(self.impact_score, 2),
            'findings': self.findings
        }


class ImpactScorer:
    """
    Evaluates resume impact using NLP and rule-based scoring.
    
    Scoring criteria:
    1. Quantified achievements (30 points)
    2. Ownership verbs (25 points)
    3. Outcome-driven content (25 points)
    4. STAR structure (20 points)
    """
    
    # Strong ownership verbs
    OWNERSHIP_VERBS = {
        # Leadership
        'led', 'managed', 'directed', 'supervised', 'coordinated', 'oversaw',
        'headed', 'spearheaded', 'championed', 'drove', 'orchestrated',
        
        # Creation/Building
        'built', 'created', 'developed', 'designed', 'established', 'launched',
        'founded', 'initiated', 'pioneered', 'architected', 'engineered',
        'implemented', 'deployed', 'constructed',
        
        # Achievement
        'achieved', 'accomplished', 'delivered', 'exceeded', 'surpassed',
        'attained', 'secured', 'won', 'earned', 'generated',
        
        # Improvement
        'improved', 'enhanced', 'optimized', 'streamlined', 'refined',
        'upgraded', 'modernized', 'transformed', 'revolutionized', 'increased',
        'boosted', 'accelerated', 'maximized', 'strengthened',
        
        # Problem-solving
        'solved', 'resolved', 'fixed', 'debugged', 'troubleshot',
        'eliminated', 'reduced', 'minimized', 'prevented'
    }
    
    # Outcome/result keywords
    OUTCOME_KEYWORDS = {
        'result', 'resulting', 'outcome', 'impact', 'effect', 'achievement',
        'success', 'successful', 'gain', 'revenue', 'profit', 'savings',
        'efficiency', 'performance', 'productivity', 'quality', 'satisfaction',
        'growth', 'improvement', 'reduction', 'increase', 'decrease'
    }
    
    # STAR structure indicators
    STAR_INDICATORS = {
        'situation': ['faced', 'encountered', 'challenged', 'needed', 'required'],
        'task': ['tasked', 'responsible', 'assigned', 'charged', 'goal'],
        'action': list(OWNERSHIP_VERBS),  # Action verbs
        'result': ['resulting', 'achieved', 'delivered', 'completed', 'accomplished']
    }
    
    # Score weights
    WEIGHTS = {
        'quantification': 30,
        'ownership_verbs': 25,
        'outcomes': 25,
        'star_structure': 20
    }
    
    def __init__(self):
        """Initialize impact scorer with spaCy"""
        self.nlp = self._load_spacy()
    
    def _load_spacy(self):
        """Load spaCy model for NLP analysis"""
        try:
            import spacy
            
            try:
                nlp = spacy.load('en_core_web_sm')
                logger.info("Loaded spaCy model: en_core_web_sm")
                return nlp
            except OSError:
                logger.warning("spaCy model not found, creating blank model")
                nlp = spacy.blank('en')
                return nlp
                
        except ImportError:
            raise ImportError("spaCy not installed. Please install: pip install spacy")
    
    def score_impact(self, resume_json: Dict[str, Any]) -> Dict[str, Any]:
        """
        Score resume impact based on achievement quality.
        
        Args:
            resume_json: Structured resume JSON with 'experience' field
            
        Returns:
            {
                "impact_score": 0-100,
                "strengths": [...],
                "weak_points": [...],
                "bullet_analyses": [...],
                "score_breakdown": {...}
            }
        """
        # Extract bullets from experience
        bullets = self._extract_bullets(resume_json)
        
        if not bullets:
            return self._empty_result("No experience bullets found")
        
        logger.info(f"Analyzing {len(bullets)} bullets")
        
        # Analyze each bullet
        analyses = [self._analyze_bullet(bullet) for bullet in bullets]
        
        # Calculate scores
        score_breakdown = self._calculate_scores(analyses)
        
        # Identify strengths and weaknesses
        strengths, weak_points = self._identify_strengths_weaknesses(analyses, score_breakdown)
        
        # Calculate overall impact score
        impact_score = sum(score_breakdown.values())
        
        result = {
            'impact_score': round(impact_score, 2),
            'strengths': strengths,
            'weak_points': weak_points,
            'bullet_analyses': [a.to_dict() for a in analyses],
            'score_breakdown': score_breakdown,
            'summary': {
                'total_bullets': len(bullets),
                'quantified_bullets': sum(1 for a in analyses if a.has_quantification),
                'ownership_verb_bullets': sum(1 for a in analyses if a.has_ownership_verb),
                'outcome_driven_bullets': sum(1 for a in analyses if a.has_outcome),
                'star_structured_bullets': sum(1 for a in analyses if a.has_star_structure)
            }
        }
        
        logger.info(f"Impact scoring complete. Score: {impact_score}/100")
        
        return result
    
    def _extract_bullets(self, resume_json: Dict[str, Any]) -> List[str]:
        """Extract bullet points from experience descriptions"""
        bullets = []
        
        if 'experience' not in resume_json:
            return bullets
        
        for exp in resume_json['experience']:
            if 'description' in exp and exp['description']:
                # Split by newlines and extract bullet points
                lines = exp['description'].split('\n')
                for line in lines:
                    line = line.strip()
                    # Check if line starts with bullet marker
                    if line and line[0] in '•●○■□▪▫–-*':
                        bullet = line.lstrip('•●○■□▪▫–-*').strip()
                        if bullet:
                            bullets.append(bullet)
        
        return bullets
    
    def _analyze_bullet(self, bullet: str) -> BulletAnalysis:
        """
        Analyze a single bullet point for impact.
        
        Checks:
        1. Quantification (numbers, percentages, metrics)
        2. Ownership verbs (strong action verbs)
        3. Outcome-driven (results, impact)
        4. STAR structure indicators
        """
        findings = []
        
        # Process with spaCy
        doc = self.nlp(bullet)
        
        # Check quantification
        has_quantification, quant_findings = self._check_quantification(bullet)
        findings.extend(quant_findings)
        
        # Check ownership verbs
        has_ownership, verb_findings = self._check_ownership_verbs(bullet, doc)
        findings.extend(verb_findings)
        
        # Check outcomes
        has_outcome, outcome_findings = self._check_outcomes(bullet, doc)
        findings.extend(outcome_findings)
        
        # Check STAR structure
        has_star, star_findings = self._check_star_structure(bullet)
        findings.extend(star_findings)
        
        # Calculate bullet-level impact score
        bullet_score = 0
        if has_quantification:
            bullet_score += 30
        if has_ownership:
            bullet_score += 25
        if has_outcome:
            bullet_score += 25
        if has_star:
            bullet_score += 20
        
        return BulletAnalysis(
            text=bullet,
            has_quantification=has_quantification,
            has_ownership_verb=has_ownership,
            has_outcome=has_outcome,
            has_star_structure=has_star,
            impact_score=bullet_score,
            findings=findings
        )
    
    def _check_quantification(self, bullet: str) -> Tuple[bool, List[str]]:
        """
        Check for quantified achievements.
        
        Looks for:
        - Percentages (40%, 40 percent)
        - Numbers (1M, 5000, $100K)
        - Metrics (3x, 2.5x improvement)
        - Time periods (6 months, 2 years)
        """
        findings = []
        has_quant = False
        
        # Pattern 1: Percentages
        percent_pattern = r'\d+\.?\d*\s*(?:%|percent)'
        percent_matches = re.findall(percent_pattern, bullet, re.IGNORECASE)
        if percent_matches:
            has_quant = True
            findings.append(f"✓ Quantified with percentage: {percent_matches[0]}")
        
        # Pattern 2: Large numbers (with K, M, B suffixes)
        number_pattern = r'(?:\$|£|€)?\s*\d+(?:\.\d+)?\s*(?:K|M|B|million|billion|thousand)'
        number_matches = re.findall(number_pattern, bullet, re.IGNORECASE)
        if number_matches:
            has_quant = True
            findings.append(f"✓ Quantified with metric: {number_matches[0]}")
        
        # Pattern 3: Regular numbers (>10 to avoid false positives)
        large_num_pattern = r'\b(?:[1-9]\d{2,}|[1-9]\d{1}(?:,\d{3})*)\b'
        large_num_matches = re.findall(large_num_pattern, bullet)
        if large_num_matches:
            has_quant = True
            findings.append(f"✓ Quantified with number: {large_num_matches[0]}")
        
        # Pattern 4: Multipliers (3x, 2.5x)
        multiplier_pattern = r'\d+\.?\d*\s*[xX]'
        multiplier_matches = re.findall(multiplier_pattern, bullet)
        if multiplier_matches:
            has_quant = True
            findings.append(f"✓ Quantified with multiplier: {multiplier_matches[0]}")
        
        # Pattern 5: Time periods
        time_pattern = r'\d+\s*(?:months?|years?|weeks?|days?)'
        time_matches = re.findall(time_pattern, bullet, re.IGNORECASE)
        if time_matches:
            has_quant = True
            findings.append(f"✓ Quantified with time period: {time_matches[0]}")
        
        if not has_quant:
            findings.append("✗ No quantification found - add numbers, percentages, or metrics")
        
        return has_quant, findings
    
    def _check_ownership_verbs(self, bullet: str, doc) -> Tuple[bool, List[str]]:
        """
        Check for strong ownership/action verbs.
        
        Uses spaCy to find verbs and checks against ownership verb list.
        """
        findings = []
        has_ownership = False
        
        # Get first word (should be action verb in good bullets)
        words = bullet.split()
        if not words:
            return False, ["✗ Empty bullet point"]
        
        first_word = words[0].lower()
        
        # Check if first word is ownership verb
        if first_word in self.OWNERSHIP_VERBS:
            has_ownership = True
            findings.append(f"✓ Strong action verb: '{first_word}'")
        else:
            # Check if any verb in sentence is ownership verb
            verb_found = False
            if hasattr(doc, 'pos_'):
                for token in doc:
                    if token.pos_ == 'VERB' and token.lemma_.lower() in self.OWNERSHIP_VERBS:
                        verb_found = True
                        findings.append(f"✓ Contains ownership verb: '{token.lemma_}'")
                        has_ownership = True
                        break
            
            if not verb_found:
                findings.append(f"✗ Weak opening verb: '{first_word}' - use strong action verbs (led, built, improved)")
        
        return has_ownership, findings
    
    def _check_outcomes(self, bullet: str, doc) -> Tuple[bool, List[str]]:
        """
        Check for outcome/result-driven content.
        
        Looks for:
        - Result keywords (resulted, achieved, improved)
        - Impact words (impact, effect, outcome)
        - Business metrics (revenue, profit, efficiency)
        """
        findings = []
        has_outcome = False
        
        bullet_lower = bullet.lower()
        
        # Check for outcome keywords
        found_keywords = []
        for keyword in self.OUTCOME_KEYWORDS:
            if keyword in bullet_lower:
                found_keywords.append(keyword)
                has_outcome = True
        
        if found_keywords:
            findings.append(f"✓ Outcome-driven: mentions {', '.join(found_keywords[:3])}")
        
        # Check for "resulting in" or "led to" patterns
        result_patterns = [
            r'result(?:ing|ed)\s+in',
            r'led\s+to',
            r'(?:improv|increas|enhanc|boost)(?:ed|ing)\s+\w+\s+by',
            r'achieved',
            r'delivered'
        ]
        
        for pattern in result_patterns:
            if re.search(pattern, bullet_lower):
                has_outcome = True
                findings.append(f"✓ Shows clear results/outcomes")
                break
        
        if not has_outcome:
            findings.append("✗ No clear outcome stated - describe the result or impact")
        
        return has_outcome, findings
    
    def _check_star_structure(self, bullet: str) -> Tuple[bool, List[str]]:
        """
        Check for STAR (Situation, Task, Action, Result) structure.
        
        A bullet with STAR structure typically:
        - Has context (situation/task)
        - Shows action taken
        - States the result
        """
        findings = []
        star_components = {
            'situation': False,
            'task': False,
            'action': False,
            'result': False
        }
        
        bullet_lower = bullet.lower()
        
        # Check for situation indicators
        for indicator in self.STAR_INDICATORS['situation']:
            if indicator in bullet_lower:
                star_components['situation'] = True
                break
        
        # Check for task indicators
        for indicator in self.STAR_INDICATORS['task']:
            if indicator in bullet_lower:
                star_components['task'] = True
                break
        
        # Check for action (ownership verbs)
        words = bullet.split()
        if words:
            first_word = words[0].lower()
            if first_word in self.OWNERSHIP_VERBS:
                star_components['action'] = True
        
        # Check for result indicators
        for indicator in self.STAR_INDICATORS['result']:
            if indicator in bullet_lower:
                star_components['result'] = True
                break
        
        # Also check if has outcome keywords (implies result)
        if any(keyword in bullet_lower for keyword in self.OUTCOME_KEYWORDS):
            star_components['result'] = True
        
        # Count components
        components_present = sum(star_components.values())
        
        # Need at least Action + Result, or 3+ components
        has_star = (
            (star_components['action'] and star_components['result']) or
            components_present >= 3
        )
        
        if has_star:
            present = [k for k, v in star_components.items() if v]
            findings.append(f"✓ STAR structure: includes {', '.join(present)}")
        else:
            findings.append("✗ Weak structure - add context (what/why) and clear results")
        
        return has_star, findings
    
    def _calculate_scores(self, analyses: List[BulletAnalysis]) -> Dict[str, float]:
        """Calculate weighted scores for each criterion"""
        if not analyses:
            return {k: 0.0 for k in self.WEIGHTS.keys()}
        
        # Calculate percentage of bullets meeting each criterion
        total = len(analyses)
        
        quantified_pct = sum(1 for a in analyses if a.has_quantification) / total
        ownership_pct = sum(1 for a in analyses if a.has_ownership_verb) / total
        outcome_pct = sum(1 for a in analyses if a.has_outcome) / total
        star_pct = sum(1 for a in analyses if a.has_star_structure) / total
        
        # Apply weights
        return {
            'quantification': round(quantified_pct * self.WEIGHTS['quantification'], 2),
            'ownership_verbs': round(ownership_pct * self.WEIGHTS['ownership_verbs'], 2),
            'outcomes': round(outcome_pct * self.WEIGHTS['outcomes'], 2),
            'star_structure': round(star_pct * self.WEIGHTS['star_structure'], 2)
        }
    
    def _identify_strengths_weaknesses(
        self,
        analyses: List[BulletAnalysis],
        score_breakdown: Dict[str, float]
    ) -> Tuple[List[str], List[str]]:
        """Identify strengths and weaknesses based on analysis"""
        strengths = []
        weak_points = []
        
        # Check each criterion
        if score_breakdown['quantification'] >= 20:
            pct = (score_breakdown['quantification'] / self.WEIGHTS['quantification']) * 100
            strengths.append(f"Strong quantification: {int(pct)}% of bullets include metrics")
        elif score_breakdown['quantification'] < 10:
            weak_points.append("Weak quantification: Few bullets include numbers or percentages")
        
        if score_breakdown['ownership_verbs'] >= 18:
            pct = (score_breakdown['ownership_verbs'] / self.WEIGHTS['ownership_verbs']) * 100
            strengths.append(f"Strong action verbs: {int(pct)}% of bullets use ownership verbs")
        elif score_breakdown['ownership_verbs'] < 12:
            weak_points.append("Weak action verbs: Use more powerful verbs (led, built, achieved)")
        
        if score_breakdown['outcomes'] >= 18:
            pct = (score_breakdown['outcomes'] / self.WEIGHTS['outcomes']) * 100
            strengths.append(f"Outcome-driven: {int(pct)}% of bullets show results")
        elif score_breakdown['outcomes'] < 12:
            weak_points.append("Weak outcomes: Bullets should clearly state results and impact")
        
        if score_breakdown['star_structure'] >= 14:
            pct = (score_breakdown['star_structure'] / self.WEIGHTS['star_structure']) * 100
            strengths.append(f"Good structure: {int(pct)}% of bullets follow STAR format")
        elif score_breakdown['star_structure'] < 8:
            weak_points.append("Weak structure: Bullets lack context and clear results (STAR format)")
        
        # Overall strengths
        high_impact_bullets = [a for a in analyses if a.impact_score >= 80]
        if len(high_impact_bullets) >= len(analyses) * 0.5:
            strengths.append(f"High-impact content: {len(high_impact_bullets)} strong bullets")
        
        # Overall weaknesses
        low_impact_bullets = [a for a in analyses if a.impact_score < 40]
        if len(low_impact_bullets) >= len(analyses) * 0.3:
            weak_points.append(f"Low-impact content: {len(low_impact_bullets)} bullets need improvement")
        
        return strengths, weak_points
    
    def _empty_result(self, reason: str) -> Dict[str, Any]:
        """Return empty result with reason"""
        return {
            'impact_score': 0.0,
            'strengths': [],
            'weak_points': [reason],
            'bullet_analyses': [],
            'score_breakdown': {k: 0.0 for k in self.WEIGHTS.keys()},
            'summary': {
                'total_bullets': 0,
                'quantified_bullets': 0,
                'ownership_verb_bullets': 0,
                'outcome_driven_bullets': 0,
                'star_structured_bullets': 0
            }
        }


def score_impact(resume_json: Dict[str, Any]) -> Dict[str, Any]:
    """
    Convenience function to score resume impact.
    
    Args:
        resume_json: Structured resume JSON
        
    Returns:
        Impact score result with strengths and weaknesses
    """
    scorer = ImpactScorer()
    return scorer.score_impact(resume_json)


if __name__ == '__main__':
    # Example usage
    import json
    
    sample_resume = {
        "experience": [
            {
                "title": "Senior Engineer",
                "company": "Tech Corp",
                "description": """
• Led development of microservices architecture serving 1M users, improving system reliability by 40%
• Built automated deployment pipeline, reducing release time from 2 hours to 15 minutes
• Responsible for managing team of 3 developers
• Worked on various API improvements
                """
            }
        ]
    }
    
    scorer = ImpactScorer()
    result = scorer.score_impact(sample_resume)
    
    print(json.dumps(result, indent=2))
