/**
 * analyzeResume - Main Business Logic
 * 
 * MOCK VERSION - Returns sample data for testing without OpenAI
 */

const { HttpsError } = require('firebase-functions/v2/https');
const { getFirestore, FieldValue } = require('firebase-admin/firestore');

/**
 * Main handler function
 */
async function analyzeResumeHandler(request) {
    const db = getFirestore();
    console.log('🚀 analyzeResume called');

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
    // 4. DYNAMIC ATS CALCULATION (Improved Mock)
    // ============================================
    console.log('🤖 Calculating dynamic ATS score...');

    // A simple list of common tech keywords to look for if JD is generic
    const commonTechKeywords = [
        'JavaScript', 'React', 'Node.js', 'Python', 'Java', 'SQL', 'Git',
        'Cloud', 'AWS', 'Docker', 'Kubernetes', 'TypeScript', 'HTML', 'CSS',
        'Agile', 'DevOps', 'CI/CD', 'API', 'REST', 'GraphQL', 'Machine Learning'
    ];

    // Extract potential keywords from JD (simple words > 4 chars)
    const jdWords = jobDescription.toLowerCase().match(/\b\w{4,}\b/g) || [];
    const resumeWords = resumeText.toLowerCase().match(/\b\w{4,}\b/g) || [];
    const resumeFullText = resumeText.toLowerCase();

    // Find matches
    const potentialKeywords = Array.from(new Set([...jdWords.filter(w => commonTechKeywords.map(k => k.toLowerCase()).includes(w))]));
    const matchedKeywords = potentialKeywords.filter(kw => resumeWords.includes(kw));
    const missingKeywords = potentialKeywords.filter(kw => !resumeWords.includes(kw));

    // Section Scoring
    const sections = {
        experience: ['experience', 'work history', 'employment'],
        skills: ['skills', 'technologies', 'competencies'],
        education: ['education', 'academic', 'degree'],
        projects: ['projects', 'portfolio']
    };

    const sectionScores = {
        experience: sections.experience.some(s => resumeFullText.includes(s)) ? 25 : 5,
        skills: sections.skills.some(s => resumeFullText.includes(s)) ? 35 : 10,
        projects: sections.projects.some(s => resumeFullText.includes(s)) ? 18 : 5,
        roleAlignment: matchedKeywords.length > 5 ? 10 : 5
    };

    // Calculate Final ATS Score (0-100)
    // Weights: Keywords (40%), Sections (60%)
    const keywordScore = potentialKeywords.length > 0
        ? (matchedKeywords.length / potentialKeywords.length) * 40
        : 20;

    const baseSectionScore = (sectionScores.experience + sectionScores.skills + sectionScores.projects + sectionScores.roleAlignment);
    const finalAtsScore = Math.min(Math.round(keywordScore + (baseSectionScore * 0.6)), 98);

    const dynamicResult = {
        atsScore: finalAtsScore,
        requiredKeywords: potentialKeywords.map(k => k.charAt(0).toUpperCase() + k.slice(1)),
        matchedKeywords: matchedKeywords.map(k => k.charAt(0).toUpperCase() + k.slice(1)),
        missingKeywords: missingKeywords.map(k => k.charAt(0).toUpperCase() + k.slice(1)),
        weakKeywords: missingKeywords.slice(0, 2).map(k => k.charAt(0).toUpperCase() + k.slice(1)),
        sectionScores: {
            skills: Math.round(sectionScores.skills * (finalAtsScore / 100)),
            experience: Math.round(sectionScores.experience * (finalAtsScore / 100)),
            projects: Math.round(sectionScores.projects * (finalAtsScore / 100)),
            roleAlignment: sectionScores.roleAlignment
        },
        improvementSuggestions: [
            `Increase your score by adding these missing keywords: ${missingKeywords.slice(0, 3).join(', ')}`,
            sectionScores.experience < 20 ? 'Your experience section seems weak or missing. Add more professional history.' : 'Strengthen your experience with more quantifiable metrics.',
            sectionScores.projects < 10 ? 'Add a "Projects" section to showcase practical applications of your skills.' : 'Good use of projects to demonstrate competency.',
            'Ensure your contact information is at the very top for better parsing.'
        ],
        optimizedBullets: [
            'Optimized existing experience bullet to include keywords and metrics',
            'Rewrote summary to better align with the job requirements',
            'Formatted skills section for better ATS readability'
        ]
    };

    console.log('✅ Dynamic Analysis complete');
    console.log('🎯 Calculated ATS Score:', dynamicResult.atsScore);

    const finalResponse = {
        success: true,
        ...dynamicResult,
        metadata: {
            userId,
            resumeId: resumeId || null,
            analyzedAt: new Date().toISOString(),
            model: 'dynamic-heuristic-engine',
            note: '🚀 This score is dynamically calculated based on keyword density and section analysis.'
        }
    };

    // ============================================
    // 5. PERSIST TO FIRESTORE
    // ============================================
    try {
        console.log('💾 Saving analysis to Firestore...');

        // Use the resume name from the first line of the text if possible
        let resumeName = resumeText.split('\n')[0].trim().substring(0, 50) || 'Resume';

        // If this is a re-analysis (resumeId exists), mark it as an edited version
        if (resumeId) {
            resumeName = `${resumeName} (Edited)`;
        }

        const analysisData = {
            userId,
            resumeName,
            jobTitle: jdWords[0] ? jdWords[0].charAt(0).toUpperCase() + jdWords[0].slice(1) : 'Target Role',
            company: 'Target Company',
            atsScore: dynamicResult.atsScore,
            result: dynamicResult,
            createdAt: FieldValue.serverTimestamp(),
            updatedAt: FieldValue.serverTimestamp(),
            metadata: finalResponse.metadata,
            isReAnalysis: !!resumeId,
            originalResumeId: resumeId || null
        };

        const docRef = await db.collection('analyses').add(analysisData);
        console.log('✅ Analysis saved with ID:', docRef.id);

        // Include the ID in the response
        finalResponse.analysisId = docRef.id;
    } catch (saveError) {
        console.error('❌ Error saving to Firestore:', saveError);
        // We still return the result even if save fails, but log it
    }

    return finalResponse;
}

// ============================================
// EXPORTS
// ============================================
module.exports = {
    analyzeResumeHandler
};
