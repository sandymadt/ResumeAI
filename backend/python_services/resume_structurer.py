"""
Resume Structuring Module

A production-ready NLP module for converting raw resume text into structured JSON.
Uses spaCy with custom pipeline for intelligent extraction.

Features:
- Section detection (contact, summary, skills, experience, education)
- Entity extraction (skills, job titles, companies, dates)
- Rule-based + NLP hybrid approach
- No LLM usage
- Fully explainable extraction

Author: NLP Architect
"""

import re
from typing import Dict, List, Any, Optional, Tuple
from datetime import datetime
import logging

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


class ResumeStructurer:
    """
    Intelligent resume structurer using spaCy NLP pipeline.
    
    Converts raw resume text into structured JSON with mandatory sections:
    - contact
    - summary
    - skills
    - experience
    - education
    """
    
    # Section header patterns (case-insensitive)
    SECTION_PATTERNS = {
        'contact': [
            'contact', 'contact information', 'personal information',
            'personal details', 'contact details'
        ],
        'summary': [
            'summary', 'professional summary', 'profile', 'objective',
            'career objective', 'professional profile', 'about me',
            'about', 'career summary', 'executive summary'
        ],
        'skills': [
            'skills', 'technical skills', 'core competencies', 'competencies',
            'expertise', 'core skills', 'key skills', 'technologies',
            'technical expertise', 'areas of expertise', 'proficiencies'
        ],
        'experience': [
            'experience', 'work experience', 'professional experience',
            'employment', 'employment history', 'work history',
            'professional background', 'career history'
        ],
        'education': [
            'education', 'educational background', 'academic background',
            'qualifications', 'academic qualifications', 'academics',
            'educational qualifications'
        ]
    }
    
    # Common technical skills (for skill detection)
    COMMON_SKILLS = {
        # Programming Languages
        'python', 'java', 'javascript', 'typescript', 'c++', 'c#', 'ruby',
        'php', 'swift', 'kotlin', 'go', 'rust', 'scala', 'r', 'matlab',
        'perl', 'shell', 'bash', 'powershell',
        
        # Web Technologies
        'html', 'css', 'react', 'angular', 'vue', 'node.js', 'express',
        'django', 'flask', 'spring', 'asp.net', 'jquery', 'bootstrap',
        'tailwind', 'sass', 'webpack', 'babel',
        
        # Databases
        'sql', 'mysql', 'postgresql', 'mongodb', 'redis', 'cassandra',
        'oracle', 'sqlite', 'dynamodb', 'elasticsearch', 'neo4j',
        
        # Cloud & DevOps
        'aws', 'azure', 'gcp', 'docker', 'kubernetes', 'jenkins', 'gitlab',
        'github actions', 'terraform', 'ansible', 'chef', 'puppet',
        'ci/cd', 'devops',
        
        # Data Science & ML
        'machine learning', 'deep learning', 'nlp', 'tensorflow', 'pytorch',
        'keras', 'scikit-learn', 'pandas', 'numpy', 'spark', 'hadoop',
        'tableau', 'power bi', 'data analysis', 'statistics',
        
        # Other
        'git', 'linux', 'agile', 'scrum', 'jira', 'rest api', 'graphql',
        'microservices', 'testing', 'unit testing', 'tdd', 'api'
    }
    
    # Common job title keywords
    JOB_TITLE_KEYWORDS = {
        'engineer', 'developer', 'architect', 'manager', 'lead', 'senior',
        'junior', 'principal', 'staff', 'analyst', 'consultant', 'specialist',
        'designer', 'director', 'coordinator', 'administrator', 'scientist',
        'researcher', 'associate', 'intern', 'trainee', 'head', 'chief',
        'vp', 'vice president', 'cto', 'ceo', 'cfo'
    }
    
    # Education degree patterns
    DEGREE_PATTERNS = {
        'bachelor', 'master', 'phd', 'doctorate', 'mba', 'ms', 'bs', 'ba',
        'ma', 'btech', 'mtech', 'bsc', 'msc', 'be', 'me', 'associate',
        'diploma', 'certification', 'certificate'
    }
    
    def __init__(self):
        """Initialize the resume structurer with spaCy model"""
        self.nlp = self._load_spacy_model()
    
    def _load_spacy_model(self):
        """Load spaCy model with custom pipeline components"""
        try:
            import spacy
            
            # Try to load English model
            try:
                nlp = spacy.load('en_core_web_sm')
                logger.info("Loaded spaCy model: en_core_web_sm")
            except OSError:
                # If model not found, create blank English model
                logger.warning("spaCy model not found, creating blank English model")
                nlp = spacy.blank('en')
            
            return nlp
            
        except ImportError:
            raise ImportError(
                "spaCy not installed. Please install: pip install spacy"
            )
    
    def structure(self, resume_text: str) -> Dict[str, Any]:
        """
        Convert raw resume text into structured JSON.
        
        Args:
            resume_text: Raw resume text (from text extraction module)
            
        Returns:
            Structured dictionary with sections:
            {
                "contact": {...},
                "summary": "...",
                "skills": [...],
                "experience": [...],
                "education": [...]
            }
        """
        if not resume_text or not resume_text.strip():
            return self._empty_structure()
        
        # Process text with spaCy
        doc = self.nlp(resume_text)
        
        # Detect sections
        sections = self._detect_sections(resume_text)
        
        # Extract structured data
        structure = {
            'contact': self._extract_contact(sections.get('contact', ''), doc),
            'summary': self._extract_summary(sections.get('summary', '')),
            'skills': self._extract_skills(sections.get('skills', ''), doc),
            'experience': self._extract_experience(sections.get('experience', ''), doc),
            'education': self._extract_education(sections.get('education', ''), doc)
        }
        
        logger.info(f"Structured resume with {len(structure['skills'])} skills, "
                   f"{len(structure['experience'])} experiences, "
                   f"{len(structure['education'])} education entries")
        
        return structure
    
    def _empty_structure(self) -> Dict[str, Any]:
        """Return empty structure template"""
        return {
            'contact': {},
            'summary': '',
            'skills': [],
            'experience': [],
            'education': []
        }
    
    def _detect_sections(self, text: str) -> Dict[str, str]:
        """
        Detect resume sections using hybrid rule-based + NLP approach.
        
        Args:
            text: Raw resume text
            
        Returns:
            Dictionary mapping section names to their content
        """
        lines = text.split('\n')
        sections = {}
        current_section = None
        section_content = []
        
        for line in lines:
            line_stripped = line.strip()
            if not line_stripped:
                continue
            
            # Check if line is a section header
            detected_section = self._identify_section_header(line_stripped)
            
            if detected_section:
                # Save previous section
                if current_section and section_content:
                    sections[current_section] = '\n'.join(section_content)
                
                # Start new section
                current_section = detected_section
                section_content = []
            else:
                # Add to current section content
                if current_section:
                    section_content.append(line_stripped)
        
        # Save last section
        if current_section and section_content:
            sections[current_section] = '\n'.join(section_content)
        
        # If no sections detected, try to infer from content
        if not sections:
            sections = self._infer_sections(text)
        
        return sections
    
    def _identify_section_header(self, line: str) -> Optional[str]:
        """
        Identify if a line is a section header.
        
        Uses rules:
        1. Line length < 50 characters
        2. Matches known section patterns
        3. May end with colon
        
        Args:
            line: Single line of text
            
        Returns:
            Section name if detected, None otherwise
        """
        if len(line) > 50:
            return None
        
        line_lower = line.lower().strip(':').strip()
        
        # Check each section pattern
        for section_name, patterns in self.SECTION_PATTERNS.items():
            for pattern in patterns:
                # Strict match only (with optional trailing punctuation already stripped)
                # to avoid false positives such as:
                # "Experienced engineer" being misclassified as "experience" header.
                if line_lower == pattern:
                    return section_name
        
        return None
    
    def _infer_sections(self, text: str) -> Dict[str, str]:
        """
        Infer sections when no clear headers are found.
        
        Uses heuristics:
        - First paragraph often contains contact/summary
        - Lists of skills
        - Experience with dates
        - Education with degrees
        """
        sections = {}
        paragraphs = text.split('\n\n')
        
        for para in paragraphs:
            para_lower = para.lower()
            
            # Check for email/phone (contact section)
            if '@' in para or 'phone' in para_lower or 'email' in para_lower:
                sections['contact'] = para
            
            # Check for skills keywords
            elif any(skill in para_lower for skill in list(self.COMMON_SKILLS)[:20]):
                sections['skills'] = para
            
            # Check for education degrees
            elif any(degree in para_lower for degree in self.DEGREE_PATTERNS):
                sections['education'] = para
            
            # Check for experience (dates, company indicators)
            elif re.search(r'\d{4}|\b(jan|feb|mar|apr|may|jun|jul|aug|sep|oct|nov|dec)\b', para_lower):
                sections['experience'] = para
        
        return sections
    
    def _extract_contact(self, section_text: str, doc) -> Dict[str, Any]:
        """
        Extract contact information.
        
        Looks for:
        - Name (first entity or capitalized words)
        - Email
        - Phone
        - Location
        - LinkedIn/GitHub
        """
        contact = {}
        
        if not section_text:
            # Try to find email/phone in entire doc
            full_text = doc.text
        else:
            full_text = section_text
        
        # Extract email
        email_pattern = r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b'
        emails = re.findall(email_pattern, full_text)
        if emails:
            contact['email'] = emails[0]
        
        # Extract phone (various formats)
        phone_patterns = [
            r'(?:\+?\d{1,3}[-.\s]?)?\(?\d{3}\)?[-.\s]?\d{3}[-.\s]?\d{4}',  # US format (optional country code)
            r'\+?\d{10,}',  # Simple long number
            r'\(\d{3}\)\s*\d{3}-\d{4}'  # (123) 456-7890
        ]
        for pattern in phone_patterns:
            phones = re.findall(pattern, full_text)
            if phones:
                contact['phone'] = phones[0]
                break
        
        # Extract name (use NER if available, otherwise first line)
        if hasattr(doc, 'ents'):
            for ent in doc.ents:
                if ent.label_ == 'PERSON':
                    contact['name'] = ent.text
                    break
        
        if 'name' not in contact and section_text:
            # Use first line as name if it looks like a name
            first_line = section_text.split('\n')[0].strip()
            if first_line and len(first_line.split()) <= 4 and first_line[0].isupper():
                contact['name'] = first_line
        
        # Extract LinkedIn
        linkedin_pattern = r'linkedin\.com/in/[\w-]+'
        linkedin = re.search(linkedin_pattern, full_text.lower())
        if linkedin:
            contact['linkedin'] = linkedin.group(0)
        
        # Extract GitHub
        github_pattern = r'github\.com/[\w-]+'
        github = re.search(github_pattern, full_text.lower())
        if github:
            contact['github'] = github.group(0)
        
        # Extract location (city, state)
        if hasattr(doc, 'ents'):
            for ent in doc.ents:
                if ent.label_ in ['GPE', 'LOC']:
                    contact['location'] = ent.text
                    break
        
        return contact
    
    def _extract_summary(self, section_text: str) -> str:
        """
        Extract professional summary.
        
        Returns the summary text as-is, cleaned of extra whitespace.
        """
        if not section_text:
            return ''
        
        # Clean and return
        summary = ' '.join(section_text.split())
        return summary
    
    def _extract_skills(self, section_text: str, doc) -> List[str]:
        """
        Extract skills using hybrid NLP + pattern matching.
        
        Approaches:
        1. Match against known skills list
        2. Extract noun phrases as potential skills
        3. Look for bulleted lists
        4. Deduplicate and normalize
        """
        skills = set()
        
        if not section_text:
            section_text = doc.text
        
        text_lower = section_text.lower()
        
        # Approach 1: Match known skills
        for skill in self.COMMON_SKILLS:
            if skill in text_lower:
                skills.add(skill.title())
        
        # Approach 2: Extract from bullet points and comma-separated lists
        lines = section_text.split('\n')
        for line in lines:
            line_clean = line.strip().lstrip('•●○■□▪▫–-*').strip()
            
            # Split by commas, semicolons, pipes
            potential_skills = re.split(r'[,;|]', line_clean)
            
            for skill in potential_skills:
                skill = skill.strip()
                # Valid skills: 2-30 chars, not too many words
                if 2 <= len(skill) <= 30 and len(skill.split()) <= 4:
                    # If contains alphanumeric and not all lowercase
                    if any(c.isalnum() for c in skill):
                        skills.add(skill)
        
        # Approach 3: Use spaCy noun chunks (if parser is available)
        if hasattr(doc, 'noun_chunks'):
            skill_doc = self.nlp(section_text)
            try:
                for chunk in skill_doc.noun_chunks:
                    chunk_text = chunk.text.strip()
                    # Filter reasonable length chunks
                    if 2 <= len(chunk_text) <= 30 and len(chunk_text.split()) <= 3:
                        # Check if looks like a skill (contains tech keyword or is capitalized)
                        if (any(word.lower() in text_lower for word in chunk_text.split()) or
                            chunk_text[0].isupper()):
                            skills.add(chunk_text)
            except ValueError:
                # Happens with blank spaCy pipelines (no dependency parser loaded).
                # In that case we gracefully skip noun_chunk-based extraction.
                pass
        
        # Clean and deduplicate
        cleaned_skills = []
        for skill in sorted(skills):
            # Remove duplicates (case-insensitive)
            if not any(s.lower() == skill.lower() for s in cleaned_skills):
                cleaned_skills.append(skill)
        
        return cleaned_skills[:50]  # Limit to 50 skills
    
    def _extract_experience(self, section_text: str, doc) -> List[Dict[str, Any]]:
        """
        Extract work experience entries.
        
        Each entry contains:
        - title: Job title
        - company: Company name
        - start_date: Start date
        - end_date: End date (or "Present")
        - description: Job description/responsibilities
        """
        experiences = []
        
        if not section_text:
            return experiences
        
        # Split into potential job entries (by double newline or date patterns)
        entries = self._split_experience_entries(section_text)
        
        for entry in entries:
            exp_data = self._parse_experience_entry(entry, doc)
            if exp_data:
                experiences.append(exp_data)
        
        return experiences
    
    def _split_experience_entries(self, text: str) -> List[str]:
        """Split experience section into individual job entries"""
        # Try to split by double newlines first
        entries = text.split('\n\n')
        
        # If only one entry, try to split by date patterns
        if len(entries) == 1:
            # Look for date ranges as separators
            date_pattern = r'\b\d{4}\s*[-–—]\s*(?:\d{4}|present|current)\b'
            matches = list(re.finditer(date_pattern, text, re.IGNORECASE))
            
            if len(matches) > 1:
                # Split at each date occurrence
                split_entries = []
                last_end = 0
                for match in matches:
                    if last_end > 0:
                        split_entries.append(text[last_end:match.start()].strip())
                    last_end = match.start()
                if last_end < len(text):
                    split_entries.append(text[last_end:].strip())
                
                if split_entries:
                    return split_entries
        
        return [e.strip() for e in entries if e.strip()]
    
    def _parse_experience_entry(self, entry_text: str, doc) -> Optional[Dict[str, Any]]:
        """Parse a single experience entry"""
        lines = [l.strip() for l in entry_text.split('\n') if l.strip()]
        
        if not lines:
            return None
        
        exp_data = {
            'title': '',
            'company': '',
            'start_date': '',
            'end_date': '',
            'description': ''
        }
        
        # First line often contains title and/or company
        first_line = lines[0]
        
        # Extract dates from entry
        dates = self._extract_dates(entry_text)
        if dates:
            exp_data['start_date'] = dates[0]
            exp_data['end_date'] = dates[1] if len(dates) > 1 else dates[0]
        
        # Try to identify title and company
        # Common patterns:
        # "Job Title at Company"
        # "Job Title | Company"
        # "Job Title, Company"
        if ' at ' in first_line.lower():
            parts = first_line.split(' at ', 1)
            exp_data['title'] = parts[0].strip()
            exp_data['company'] = parts[1].strip()
        elif ' | ' in first_line:
            parts = first_line.split(' | ', 1)
            exp_data['title'] = parts[0].strip()
            exp_data['company'] = parts[1].strip()
        elif ',' in first_line:
            parts = first_line.split(',', 1)
            # Check if first part looks like a job title
            if any(keyword in parts[0].lower() for keyword in self.JOB_TITLE_KEYWORDS):
                exp_data['title'] = parts[0].strip()
                exp_data['company'] = parts[1].strip()
            else:
                exp_data['title'] = first_line
        else:
            exp_data['title'] = first_line
        
        # If second line exists and no company yet, might be company
        if len(lines) > 1 and not exp_data['company']:
            second_line = lines[1]
            # Check if it looks like a company (not a date, not starting with bullet)
            if not re.match(r'\d{4}', second_line) and not second_line[0] in '•●○■□▪▫–-*':
                exp_data['company'] = second_line
        
        # Extract description (remaining content, especially bullet points)
        desc_lines = []
        for line in lines[1:] if len(lines) > 1 else []:
            # Skip date lines
            if re.match(r'\b\d{4}\s*[-–—]', line):
                continue
            # Skip if it's the company line we already extracted
            if line == exp_data['company']:
                continue
            desc_lines.append(line)
        
        if desc_lines:
            exp_data['description'] = '\n'.join(desc_lines)
        
        # Only return if we have at least a title or company
        if exp_data['title'] or exp_data['company']:
            return exp_data
        
        return None
    
    def _extract_education(self, section_text: str, doc) -> List[Dict[str, Any]]:
        """
        Extract education entries.
        
        Each entry contains:
        - degree: Degree type (BS, MS, PhD, etc.)
        - field: Field of study
        - institution: School/University name
        - graduation_date: Graduation year
        """
        education_entries = []
        
        if not section_text:
            return education_entries
        
        # Split into entries
        entries = section_text.split('\n\n')
        entries = [e for e in entries if e.strip()]
        
        for entry in entries:
            entry = entry.strip()
            if not entry:
                continue
            
            edu_data = {
                'degree': '',
                'field': '',
                'institution': '',
                'graduation_date': ''
            }
            
            # Extract degree
            entry_lower = entry.lower()
            for degree in self.DEGREE_PATTERNS:
                if degree in entry_lower:
                    # Try to get full degree name
                    degree_match = re.search(
                        r'\b(bachelor|master|phd|doctorate|mba|[bm]\.?[sca]\.?|[bm]\.?tech|associate|diploma)\b.*?(?=\bin\b|$)',
                        entry,
                        re.IGNORECASE
                    )
                    if degree_match:
                        edu_data['degree'] = degree_match.group(0).strip()
                    else:
                        edu_data['degree'] = degree.upper()
                    break
            
            # Extract field of study (often after "in" or degree name)
            field_match = re.search(
                r'\bin\b\s+([A-Z][A-Za-z\s&]+?)(?:\n|,|\b(?:from|at)\b|$)',
                entry
            )
            if field_match:
                edu_data['field'] = field_match.group(1).strip()
            
            # Extract institution (often after "from" or on separate line)
            inst_patterns = [
                r'\b(?:from|at)\b\s+([A-Z][A-Za-z\s&.,]+?)(?:\n|,|$)',
                r'\n([A-Z][A-Za-z\s&.,]+?University)',
                r'\n([A-Z][A-Za-z\s&.,]+?College)',
                r'\n([A-Z][A-Za-z\s&.,]+?Institute)'
            ]
            for pattern in inst_patterns:
                inst_match = re.search(pattern, entry)
                if inst_match:
                    edu_data['institution'] = inst_match.group(1).strip()
                    break
            
            # If no institution found, use university/college names from NER
            if not edu_data['institution'] and hasattr(doc, 'ents'):
                entry_doc = self.nlp(entry)
                for ent in entry_doc.ents:
                    if ent.label_ == 'ORG' and any(word in ent.text.lower() for word in ['university', 'college', 'institute', 'school']):
                        edu_data['institution'] = ent.text
                        break
            
            # Extract graduation year
            dates = self._extract_dates(entry)
            if dates:
                # Usually the later date or standalone year is graduation
                # Filter out just years (not month-year)
                years = [d for d in dates if d.isdigit() and len(d) == 4]
                if years:
                    edu_data['graduation_date'] = years[-1]
                else:
                    edu_data['graduation_date'] = dates[-1]
            
            # Only add if we have at least degree or institution
            if edu_data['degree'] or edu_data['institution']:
                education_entries.append(edu_data)
        
        return education_entries
    
    def _extract_dates(self, text: str) -> List[str]:
        """
        Extract dates from text.
        
        Handles formats:
        - 2020 - 2023
        - Jan 2020 - Dec 2023
        - 2020 - Present
        - 2020
        """
        dates = []
        
        # Pattern 1: Year range (2020 - 2023 or 2020-2023)
        year_range = re.findall(
            r'\b(\d{4})\s*[-–—]\s*(\d{4}|present|current)\b',
            text,
            re.IGNORECASE
        )
        for start, end in year_range:
            dates.append(start)
            dates.append(end.title() if end.lower() in ['present', 'current'] else end)
        
        # Pattern 2: Month Year - Month Year
        month_year = re.findall(
            r'\b(jan|feb|mar|apr|may|jun|jul|aug|sep|oct|nov|dec)[a-z]*\.?\s+(\d{4})',
            text,
            re.IGNORECASE
        )
        for month, year in month_year:
            dates.append(f"{month.title()} {year}")
        
        # Pattern 3: Standalone years
        if not dates:
            years = re.findall(r'\b(20\d{2}|19\d{2})\b', text)
            dates.extend(years)
        
        return dates
    
    def extract_metadata(self, resume_text: str) -> Dict[str, Any]:
        """
        Extract metadata along with structure.
        
        Returns:
            Dictionary with structure + metadata
        """
        structure = self.structure(resume_text)
        
        metadata = {
            'structure': structure,
            'metadata': {
                'total_skills': len(structure['skills']),
                'total_experience': len(structure['experience']),
                'total_education': len(structure['education']),
                'has_contact': bool(structure['contact']),
                'has_summary': bool(structure['summary']),
                'extraction_timestamp': datetime.now().isoformat()
            }
        }
        
        return metadata


# Convenience function
def structure_resume(resume_text: str) -> Dict[str, Any]:
    """
    Convenience function to structure a resume.
    
    Args:
        resume_text: Raw resume text
        
    Returns:
        Structured dictionary with sections
    """
    structurer = ResumeStructurer()
    return structurer.structure(resume_text)


if __name__ == '__main__':
    # Example usage
    import sys
    
    if len(sys.argv) > 1:
        # Read from file
        with open(sys.argv[1], 'r', encoding='utf-8') as f:
            text = f.read()
    else:
        # Example text
        text = """
        John Doe
        john.doe@email.com | +1 (555) 123-4567 | San Francisco, CA
        
        Summary
        Senior Software Engineer with 5+ years of experience in full-stack development.
        
        Skills
        Python, JavaScript, React, Node.js, AWS, Docker, PostgreSQL
        
        Experience
        
        Senior Software Engineer at Tech Corp
        Jan 2020 - Present
        • Led development of microservices architecture
        • Improved system performance by 40%
        
        Software Engineer at StartupXYZ
        Jun 2018 - Dec 2019
        • Developed RESTful APIs using Python and Flask
        • Implemented CI/CD pipelines
        
        Education
        
        Master of Science in Computer Science
        Stanford University
        2018
        
        Bachelor of Science in Computer Engineering
        UC Berkeley
        2016
        """
    
    # Structure the resume
    structurer = ResumeStructurer()
    result = structurer.structure(text)
    
    # Pretty print
    import json
    print(json.dumps(result, indent=2))
