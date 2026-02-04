/**
 * analyzeResume - Main Business Logic
 * 
 * MOCK VERSION - Returns sample data for testing without OpenAI
 */

const { HttpsError } = require('firebase-functions/v2/https');

/**
 * Main handler function
 */
async function analyzeResumeHandler(request) {
    console.log('🚀 analyzeResume called (MOCK MODE)');

    // ============================================
    // 1. AUTHENTICATION CHECK
    // ============================================
    if (!request.auth) {
        throw new HttpsError(
            'unauthenticated',
            'You must be logged in to analyze resumes'
        );
    }

    const userId = request.auth.uid;
    console.log('✅ Authenticated user:', userId);

    // ============================================
    // 2. INPUT VALIDATION
    // ============================================
    const { resumeText, jobDescription, resumeId } = request.data;

    if (!resumeText || typeof resumeText !== 'string' || resumeText.trim().length < 50) {
        throw new HttpsError('invalid-argument', 'Resume text is missing or too short.');
    }

    if (!jobDescription || typeof jobDescription !== 'string' || jobDescription.trim().length < 20) {
        throw new HttpsError('invalid-argument', 'Job description is missing or too short.');
    }

    console.log('✅ Input validated');
    console.log('📄 Resume length:', resumeText.length);
    console.log('📋 Job description length:', jobDescription.length);

    // ============================================
    // 3. SIMULATE PROCESSING DELAY
    // ============================================
    console.log('🤖 Generating MOCK analysis...');
    await new Promise(resolve => setTimeout(resolve, 2000)); // 2 second delay

    // ============================================
    // 4. RETURN MOCK ANALYSIS RESULTS
    // ============================================
    const mockResult = {
        atsScore: 72,
        requiredKeywords: [
            'JavaScript', 'React', 'Node.js', 'TypeScript',
            'REST API', 'Git', 'Agile', 'Problem Solving',
            'Team Collaboration', 'CI/CD'
        ],
        matchedKeywords: [
            'JavaScript', 'React', 'Node.js', 'Git',
            'Team Collaboration', 'Problem Solving'
        ],
        missingKeywords: [
            'TypeScript', 'REST API', 'Agile', 'CI/CD'
        ],
        weakKeywords: [
            'Node.js', 'Git'
        ],
        sectionScores: {
            skills: 28,        // out of 40
            experience: 22,    // out of 30
            projects: 14,      // out of 20
            roleAlignment: 8   // out of 10
        },
        improvementSuggestions: [
            'Add TypeScript to your skill set - it\'s mentioned as a requirement in the job description',
            'Include specific examples of REST API development in your experience section',
            'Mention your experience with Agile methodologies and sprint planning',
            'Add details about CI/CD pipeline setup or usage (GitHub Actions, Jenkins, etc.)',
            'Quantify your Node.js achievements with metrics (e.g., "Improved API response time by 40%")',
            'Strengthen your Git experience by mentioning branching strategies or code review practices',
            'Add a projects section showcasing TypeScript-based applications',
            'Include keywords like "scalable", "performance optimization", and "best practices"'
        ],
        optimizedBullets: [
            'Architected and deployed 5+ production-ready React applications serving 50K+ monthly active users',
            'Developed RESTful APIs using Node.js and Express, reducing server response time by 35%',
            'Collaborated with cross-functional teams in Agile sprints to deliver features 20% faster',
            'Implemented CI/CD pipelines using GitHub Actions, automating deployment and reducing errors by 60%',
            'Migrated legacy JavaScript codebase to TypeScript, improving code maintainability and reducing bugs by 40%',
            'Led code reviews and established Git workflow best practices for a team of 8 developers',
            'Optimized React component rendering, achieving 50% improvement in page load performance',
            'Built scalable microservices architecture handling 1M+ API requests daily'
        ]
    };

    console.log('✅ MOCK Analysis complete');
    console.log('🎯 ATS Score:', mockResult.atsScore);

    return {
        success: true,
        ...mockResult,
        metadata: {
            userId,
            resumeId: resumeId || null,
            analyzedAt: new Date().toISOString(),
            model: 'mock-testing-mode',
            note: '⚠️ This is MOCK data for testing. Replace with real OpenAI integration.'
        }
    };
}

// ============================================
// EXPORTS
// ============================================
module.exports = {
    analyzeResumeHandler
};
