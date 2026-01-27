"""
Demo script for Resume Structuring Module

Demonstrates the resume structuring functionality with real examples.
"""

from resume_structurer import ResumeStructurer
import json


def demo_complete_resume():
    """Demo with a complete, well-formatted resume"""
    print("\n" + "="*70)
    print("DEMO 1: Complete Resume with All Sections")
    print("="*70)
    
    resume_text = """
John Doe
john.doe@email.com | +1-555-123-4567 | San Francisco, CA
linkedin.com/in/johndoe | github.com/johndoe

PROFESSIONAL SUMMARY
Senior Software Engineer with 5+ years of experience in full-stack web development.
Expertise in Python, JavaScript, React, and cloud technologies. Proven track record
of leading development teams and delivering scalable solutions.

TECHNICAL SKILLS
Python, JavaScript, TypeScript, React, Node.js, Express, Django, Flask
AWS, Docker, Kubernetes, PostgreSQL, MongoDB, Redis
Git, CI/CD, Agile, Scrum, REST API, GraphQL

WORK EXPERIENCE

Senior Software Engineer at Tech Corp
Jan 2020 - Present
• Lead team of 5 developers in building microservices architecture
• Implemented CI/CD pipeline reducing deployment time by 60%
• Mentored junior developers and conducted code reviews
• Technologies: Python, React, AWS, Docker, Kubernetes

Software Engineer at StartupXYZ
Jun 2018 - Dec 2019
• Developed RESTful APIs serving 1M+ daily requests
• Built real-time dashboard using React and WebSockets
• Integrated payment processing with Stripe
• Technologies: Node.js, MongoDB, React, AWS

Junior Developer at DevShop Inc
Jan 2017 - May 2018
• Maintained legacy Java applications
• Migrated database from MySQL to PostgreSQL
• Wrote unit and integration tests achieving 85% coverage

EDUCATION

Master of Science in Computer Science
Stanford University
2016

Bachelor of Science in Computer Engineering
University of California, Berkeley
2014
    """
    
    structurer = ResumeStructurer()
    result = structurer.structure(resume_text)
    
    print_structured_result(result)


def demo_simple_resume():
    """Demo with a simple resume (less structure)"""
    print("\n" + "="*70)
    print("DEMO 2: Simple Resume (Minimal Formatting)")
    print("="*70)
    
    resume_text = """
Jane Smith
jane.smith@email.com
(555) 987-6543

Skills: Python, Java, SQL, React, AWS

Experience:
Data Analyst at ABC Company, 2020-2023
Analyzed customer data and created dashboards

Software Intern at XYZ Corp, Summer 2019
Developed automated testing scripts

Education:
BS in Computer Science, MIT, 2020
    """
    
    structurer = ResumeStructurer()
    result = structurer.structure(resume_text)
    
    print_structured_result(result)


def demo_skill_extraction():
    """Demo focused on skill extraction"""
    print("\n" + "="*70)
    print("DEMO 3: Skill Extraction Examples")
    print("="*70)
    
    examples = [
        ("Comma-separated", "Skills: Python, JavaScript, React, Docker, AWS"),
        ("Bullet points", "Skills:\n• Python\n• JavaScript\n• React\n• Docker"),
        ("Mixed format", "Technical Skills:\nPython, JavaScript | React • Docker, AWS")
    ]
    
    structurer = ResumeStructurer()
    
    for name, text in examples:
        print(f"\n{name}:")
        print(f"Input: {text[:50]}...")
        doc = structurer.nlp(text)
        skills = structurer._extract_skills(text, doc)
        print(f"Extracted: {skills[:10]}")  # Show first 10


def demo_experience_parsing():
    """Demo focused on experience parsing"""
    print("\n" + "="*70)
    print("DEMO 4: Experience Entry Parsing")
    print("="*70)
    
    experience_text = """
Senior Software Engineer at Google
March 2020 - Present
• Led development of search ranking algorithm
• Improved query performance by 30%
• Managed team of 3 engineers

Software Engineer at Microsoft
Jan 2018 - Feb 2020
• Developed Azure cloud services
• Implemented automated testing framework
    """
    
    structurer = ResumeStructurer()
    doc = structurer.nlp(experience_text)
    experiences = structurer._extract_experience(experience_text, doc)
    
    print(f"\nFound {len(experiences)} experience entries:\n")
    for i, exp in enumerate(experiences, 1):
        print(f"Entry {i}:")
        print(f"  Title: {exp['title']}")
        print(f"  Company: {exp['company']}")
        print(f"  Dates: {exp['start_date']} - {exp['end_date']}")
        print(f"  Description: {exp['description'][:60]}...")
        print()


def demo_education_parsing():
    """Demo focused on education parsing"""
    print("\n" + "="*70)
    print("DEMO 5: Education Entry Parsing")
    print("="*70)
    
    education_text = """
PhD in Computer Science
Massachusetts Institute of Technology
2020

Master of Science in Artificial Intelligence
Stanford University
2016

Bachelor of Engineering in Computer Science
IIT Bombay
2014
    """
    
    structurer = ResumeStructurer()
    doc = structurer.nlp(education_text)
    education = structurer._extract_education(education_text, doc)
    
    print(f"\nFound {len(education)} education entries:\n")
    for i, edu in enumerate(education, 1):
        print(f"Entry {i}:")
        print(f"  Degree: {edu['degree']}")
        print(f"  Field: {edu['field']}")
        print(f"  Institution: {edu['institution']}")
        print(f"  Year: {edu['graduation_date']}")
        print()


def print_structured_result(result):
    """Pretty print structured resume result"""
    print("\n📋 STRUCTURED RESUME:\n")
    
    # Contact
    print("👤 CONTACT:")
    if result['contact']:
        for key, value in result['contact'].items():
            print(f"   {key}: {value}")
    else:
        print("   (no contact information detected)")
    
    # Summary
    print(f"\n📝 SUMMARY:")
    if result['summary']:
        print(f"   {result['summary'][:100]}...")
    else:
        print("   (no summary detected)")
    
    # Skills
    print(f"\n💪 SKILLS ({len(result['skills'])}):")
    if result['skills']:
        for i, skill in enumerate(result['skills'][:15], 1):  # Show first 15
            print(f"   {i}. {skill}")
        if len(result['skills']) > 15:
            print(f"   ... and {len(result['skills']) - 15} more")
    else:
        print("   (no skills detected)")
    
    # Experience
    print(f"\n💼 EXPERIENCE ({len(result['experience'])}):")
    if result['experience']:
        for i, exp in enumerate(result['experience'], 1):
            print(f"   {i}. {exp['title']} at {exp['company']}")
            print(f"      {exp['start_date']} - {exp['end_date']}")
    else:
        print("   (no experience detected)")
    
    # Education
    print(f"\n🎓 EDUCATION ({len(result['education'])}):")
    if result['education']:
        for i, edu in enumerate(result['education'], 1):
            print(f"   {i}. {edu['degree']} - {edu['field'] or '(no field)'}")
            print(f"      {edu['institution'] or '(no institution)'} ({edu['graduation_date']})")
    else:
        print("   (no education detected)")
    
    print("\n" + "-"*70)
    
    # JSON output
    print("\n📄 JSON OUTPUT:\n")
    print(json.dumps(result, indent=2))


def main():
    """Run all demos"""
    print("\n" + "="*70)
    print(" 🚀 RESUME STRUCTURING MODULE - DEMONSTRATION")
    print("="*70)
    
    demos = [
        ("Complete Resume", demo_complete_resume),
        ("Simple Resume", demo_simple_resume),
        ("Skill Extraction", demo_skill_extraction),
        ("Experience Parsing", demo_experience_parsing),
        ("Education Parsing", demo_education_parsing)
    ]
    
    for name, demo_func in demos:
        try:
            demo_func()
        except Exception as e:
            print(f"\n❌ Error in {name}: {e}")
    
    print("\n" + "="*70)
    print(" ✅ DEMONSTRATION COMPLETE")
    print("="*70 + "\n")


if __name__ == '__main__':
    main()
