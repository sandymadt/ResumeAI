"""
Final Score Aggregator Module

A production-ready module for calculating final ATS scores by aggregating
scores from all analysis modules.

Features:
- Weighted score aggregation
- Configurable weight tuning
- Deterministic and reproducible
- Clear section breakdown

No AI models or LLM usage - Pure deterministic aggregation

Author: ATS Scoring Engine Designer
"""

from typing import Dict, Any, Optional, List
import logging

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


class ScoreAggregator:
    """
    Aggregates scores from all resume analysis modules into final ATS score.
    
    Default weights:
    - Rule Checks (ATS Validation): 25%
    - Keyword Matching (Skill Match): 35%
    - Impact Score: 25%
    - Formatting: 15%
    """
    
    # Default weights (should sum to 1.0)
    DEFAULT_WEIGHTS = {
        'rule_checks': 0.25,      # ATS validation
        'keyword_matching': 0.35,  # Skill matching
        'impact_score': 0.25,      # Impact quality
        'formatting': 0.15         # Formatting & readability
    }
    
    def __init__(self, weights: Optional[Dict[str, float]] = None):
        """
        Initialize score aggregator.
        
        Args:
            weights: Optional custom weights dict. Must sum to 1.0.
                    Keys: 'rule_checks', 'keyword_matching', 'impact_score', 'formatting'
        """
        if weights is None:
            self.weights = self.DEFAULT_WEIGHTS.copy()
        else:
            self._validate_weights(weights)
            self.weights = weights
    
    def aggregate(
        self,
        rule_score: Optional[float] = None,
        keyword_score: Optional[float] = None,
        impact_score: Optional[float] = None,
        formatting_score: Optional[float] = None
    ) -> Dict[str, Any]:
        """
        Aggregate scores into final ATS score.
        
        Args:
            rule_score: ATS validation score (0-100)
            keyword_score: Skill matching score (0-100)
            impact_score: Impact quality score (0-100)
            formatting_score: Formatting score (0-100)
            
        Returns:
            {
                "ats_score": 0-100,
                "section_scores": {
                    "rule_checks": score,
                    "keyword_matching": score,
                    "impact_score": score,
                    "formatting": score
                },
                "weighted_contributions": {...},
                "score_grade": "A/B/C/D/F",
                "missing_scores": [...]
            }
        """
        # Collect scores
        section_scores = {
            'rule_checks': rule_score,
            'keyword_matching': keyword_score,
            'impact_score': impact_score,
            'formatting': formatting_score
        }
        
        # Track missing scores
        missing_scores = [k for k, v in section_scores.items() if v is None]
        
        # Calculate weighted contributions
        weighted_contributions = {}
        total_weight_used = 0.0
        weighted_sum = 0.0
        
        for section, score in section_scores.items():
            if score is not None:
                # Ensure score is in valid range
                score = max(0.0, min(100.0, float(score)))
                section_scores[section] = score
                
                # Calculate weighted contribution
                weight = self.weights[section]
                contribution = score * weight
                weighted_contributions[section] = round(contribution, 2)
                
                weighted_sum += contribution
                total_weight_used += weight
        
        # Calculate final ATS score
        if total_weight_used > 0:
            # If some scores missing, normalize by available weight
            ats_score = weighted_sum / total_weight_used * (total_weight_used / 1.0)
            # Alternative: scale up to 100 - ats_score = weighted_sum / total_weight_used
            # But we use the first approach to penalize missing scores
        else:
            ats_score = 0.0
        
        # Determine grade
        score_grade = self._calculate_grade(ats_score)
        
        result = {
            'ats_score': round(ats_score, 2),
            'section_scores': section_scores,
            'weighted_contributions': weighted_contributions,
            'score_grade': score_grade,
            'weights_used': self.weights,
            'missing_scores': missing_scores
        }
        
        logger.info(f"Score aggregation complete. Final ATS Score: {ats_score:.2f}/100 ({score_grade})")
        
        return result
    
    def aggregate_from_results(
        self,
        ats_result: Optional[Dict[str, Any]] = None,
        skill_result: Optional[Dict[str, Any]] = None,
        impact_result: Optional[Dict[str, Any]] = None,
        formatting_result: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Aggregate scores from module result dictionaries.
        
        Convenience method that extracts scores from result dicts.
        
        Args:
            ats_result: Result from validate_resume()
            skill_result: Result from match_skills()
            impact_result: Result from score_impact()
            formatting_result: Result from analyze_formatting()
            
        Returns:
            Aggregated score result
        """
        # Extract scores from results
        rule_score = ats_result.get('rule_score') if ats_result else None
        keyword_score = skill_result.get('keyword_match_score') if skill_result else None
        impact_score = impact_result.get('impact_score') if impact_result else None
        formatting_score = formatting_result.get('formatting_score') if formatting_result else None
        
        return self.aggregate(rule_score, keyword_score, impact_score, formatting_score)
    
    def _validate_weights(self, weights: Dict[str, float]):
        """Validate that weights are correct"""
        required_keys = set(self.DEFAULT_WEIGHTS.keys())
        provided_keys = set(weights.keys())
        
        if required_keys != provided_keys:
            raise ValueError(
                f"Weights must contain exactly these keys: {required_keys}. "
                f"Got: {provided_keys}"
            )
        
        total_weight = sum(weights.values())
        if not (0.99 <= total_weight <= 1.01):  # Allow small floating point error
            raise ValueError(
                f"Weights must sum to 1.0. Got: {total_weight}. "
                f"Weights: {weights}"
            )
        
        for key, value in weights.items():
            if not (0 <= value <= 1):
                raise ValueError(
                    f"Weight '{key}' must be between 0 and 1. Got: {value}"
                )
    
    def _calculate_grade(self, score: float) -> str:
        """
        Calculate letter grade from score.
        
        A: 90-100 (Excellent)
        B: 80-89  (Good)
        C: 70-79  (Fair)
        D: 60-69  (Poor)
        F: 0-59   (Fail)
        """
        if score >= 90:
            return 'A'
        elif score >= 80:
            return 'B'
        elif score >= 70:
            return 'C'
        elif score >= 60:
            return 'D'
        else:
            return 'F'
    
    def get_recommendations(self, result: Dict[str, Any]) -> List[str]:
        """
        Get recommendations based on aggregated score.
        
        Args:
            result: Result from aggregate() or aggregate_from_results()
            
        Returns:
            List of recommendations
        """
        recommendations = []
        section_scores = result['section_scores']
        
        # Check each section
        if section_scores.get('rule_checks') is not None:
            if section_scores['rule_checks'] < 70:
                recommendations.append(
                    "⚠️ ATS Compliance: Address critical violations to improve ATS parsing"
                )
            elif section_scores['rule_checks'] >= 90:
                recommendations.append("✓ ATS Compliance: Excellent - resume is ATS-friendly")
        
        if section_scores.get('keyword_matching') is not None:
            if section_scores['keyword_matching'] < 60:
                recommendations.append(
                    "⚠️ Keyword Match: Add more job-relevant skills and keywords"
                )
            elif section_scores['keyword_matching'] >= 80:
                recommendations.append("✓ Keyword Match: Strong alignment with job requirements")
        
        if section_scores.get('impact_score') is not None:
            if section_scores['impact_score'] < 50:
                recommendations.append(
                    "⚠️ Impact: Add quantified achievements and stronger action verbs"
                )
            elif section_scores['impact_score'] >= 75:
                recommendations.append("✓ Impact: Strong achievement-focused content")
        
        if section_scores.get('formatting') is not None:
            if section_scores['formatting'] < 70:
                recommendations.append(
                    "⚠️ Formatting: Improve layout and structure for better readability"
                )
            elif section_scores['formatting'] >= 85:
                recommendations.append("✓ Formatting: Clean, professional layout")
        
        # Overall recommendation
        ats_score = result['ats_score']
        if ats_score >= 85:
            recommendations.insert(0, "🎉 Overall: Excellent resume! Ready for submission")
        elif ats_score >= 70:
            recommendations.insert(0, "👍 Overall: Good resume with room for improvement")
        elif ats_score >= 60:
            recommendations.insert(0, "⚡ Overall: Needs improvement - focus on weak areas")
        else:
            recommendations.insert(0, "❌ Overall: Significant improvements needed")
        
        return recommendations


def calculate_ats_score(
    rule_score: Optional[float] = None,
    keyword_score: Optional[float] = None,
    impact_score: Optional[float] = None,
    formatting_score: Optional[float] = None,
    weights: Optional[Dict[str, float]] = None
) -> Dict[str, Any]:
    """
    Convenience function to calculate final ATS score.
    
    Args:
        rule_score: ATS validation score (0-100)
        keyword_score: Skill matching score (0-100)
        impact_score: Impact quality score (0-100)
        formatting_score: Formatting score (0-100)
        weights: Optional custom weights
        
    Returns:
        Aggregated score result
    """
    aggregator = ScoreAggregator(weights)
    return aggregator.aggregate(rule_score, keyword_score, impact_score, formatting_score)


if __name__ == '__main__':
    # Example usage
    import json
    
    # Sample scores from different modules
    sample_scores = {
        'rule_score': 85.0,        # From ATS validator
        'keyword_score': 72.0,     # From skill matcher
        'impact_score': 68.5,      # From impact scorer
        'formatting_score': 78.0   # From formatting analyzer
    }
    
    # Create aggregator
    aggregator = ScoreAggregator()
    
    # Calculate final score
    result = aggregator.aggregate(**sample_scores)
    
    # Get recommendations
    recommendations = aggregator.get_recommendations(result)
    result['recommendations'] = recommendations
    
    # Print result
    print(json.dumps(result, indent=2))
    
    print("\n" + "="*60)
    print("SCORE BREAKDOWN:")
    print("="*60)
    for section, score in result['section_scores'].items():
        contribution = result['weighted_contributions'].get(section, 0)
        weight = result['weights_used'][section]
        print(f"{section:20s}: {score:5.1f}/100 (weight: {weight:.0%}) → {contribution:5.2f} points")
    
    print(f"\nFinal ATS Score: {result['ats_score']}/100 ({result['score_grade']})")
    
    print("\n" + "="*60)
    print("RECOMMENDATIONS:")
    print("="*60)
    for rec in recommendations:
        print(f"• {rec}")
