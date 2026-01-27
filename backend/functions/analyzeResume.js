/**
 * analyzeResume - Main Business Logic
 * 
 * THIS IS THE ONLY BACKEND LOGIC FILE
 * 
 * RESPONSIBILITIES:
 * 1. Input validation
 * 2. OpenAI client initialization (secure)
 * 3. ATS prompt construction
 * 4. OpenAI API call
 * 5. JSON parsing & validation
 * 6. Error handling
 * 
 * NO EMULATOR - PRODUCTION ONLY
 */

const { HttpsError } = require('firebase-functions/v2/https');
const { defineSecret } = require('firebase-functions/params');
const OpenAI = require('openai');

// Define secret (loaded from Google Cloud Secret Manager)
const OPENAI_API_KEY = defineSecret('OPENAI_API_KEY');

/**
 * Main handler function
 * 
 * @param {Object} request - Firebase callable request object
 * @param {Object} request.data - Request payload
 * @param {string} request.data.resumeText - Full resume text
 * @param {string} request.data.jobDescription - Job description
 * @param {string|null} request.data.resumeId - Optional resume ID
 * @param {Object} request.auth - Firebase auth context
 * @returns {Promise<Object>} ATS analysis results
 */
async function analyzeResumeHandler(request) {
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

    // Validate resume text
    if (!resumeText || typeof resumeText !== 'string') {
        throw new HttpsError('invalid-argument', 'Resume text is required and must be a string');
    }

    if (resumeText.trim().length < 100) {
        throw new HttpsError('invalid-argument', 'Resume text is too short (minimum 100 characters)');
    }

    if (resumeText.length > 50000) {
        throw new HttpsError('invalid-argument', 'Resume text is too long (maximum 50,000 characters)');
    }

    // Validate job description
    if (!jobDescription || typeof jobDescription !== 'string') {
        throw new HttpsError('invalid-argument', 'Job description is required and must be a string');
    }

    if (jobDescription.trim().length < 50) {
        throw new HttpsError('invalid-argument', 'Job description is too short (minimum 50 characters)');
    }

    if (jobDescription.length > 20000) {
        throw new HttpsError('invalid-argument', 'Job description is too long (maximum 20,000 characters)');
    }

    console.log('✅ Input validated');
    console.log(`📄 Resume: ${resumeText.length} chars`);
    console.log(`📋 Job Description: ${jobDescription.length} chars`);

    // ============================================
    // 3. INITIALIZE OPENAI CLIENT (SECURE)
    // ============================================
    const openai = new OpenAI({
        apiKey: OPENAI_API_KEY.value(), // Access secret securely
    });

    console.log('✅ OpenAI client initialized');

    // ============================================
    // 4. BUILD ATS PROMPT
    // ============================================
    const systemPrompt = `You are an expert ATS (Applicant Tracking System) analyzer. 

Your task is to analyze a resume against a job description and provide a comprehensive, structured analysis.

SCORING SYSTEM (Total = 100 points):
- Skills Match: 40 points
- Experience Relevance: 30 points
- Projects Relevance: 20 points
- Role Alignment: 10 points

ATS ANALYSIS RULES:
1. Extract ALL required keywords from the job description (skills, tools, technologies, qualifications)
2. Match resume keywords (both exact matches and contextual/semantic matches)
3. Identify missing critical keywords
4. Identify weak keywords (mentioned but not demonstrated)
5. Calculate precise scores for each section
6. Provide actionable improvement suggestions
7. Rewrite bullet points in ATS-friendly language (action verbs, quantifiable metrics)

BE STRICT AND REALISTIC. An average resume should score 40-60.

You MUST respond with ONLY valid JSON in this EXACT structure:
{
  "atsScore": <number 0-100>,
  "requiredKeywords": [<array of strings>],
  "matchedKeywords": [<array of strings>],
  "missingKeywords": [<array of strings>],
  "weakKeywords": [<array of strings>],
  "sectionScores": {
    "skills": <number 0-40>,
    "experience": <number 0-30>,
    "projects": <number 0-20>,
    "roleAlignment": <number 0-10>
  },
  "improvementSuggestions": [<array of strings, 5-10 actionable items>],
  "optimizedBullets": [<array of strings, 5-10 rewritten bullet points>]
}

CRITICAL: Return ONLY the JSON object. No markdown, no explanation, no extra text.`;

    const userPrompt = `Analyze this resume against the job description:

JOB DESCRIPTION:
${jobDescription}

RESUME:
${resumeText}

Provide the ATS analysis in the specified JSON format.`;

    console.log('✅ ATS prompt constructed');

    // ============================================
    // 5. CALL OPENAI API
    // ============================================
    let analysisResult;

    try {
        console.log('🤖 Calling OpenAI API...');

        const completion = await openai.chat.completions.create({
            model: 'gpt-4-turbo-preview', // or 'gpt-3.5-turbo' for cost savings
            messages: [
                { role: 'system', content: systemPrompt },
                { role: 'user', content: userPrompt }
            ],
            temperature: 0.3, // Lower = more consistent
            max_tokens: 2000,
            response_format: { type: 'json_object' }, // Force JSON output
        });

        console.log('✅ OpenAI response received');
        console.log('📊 Tokens used:', completion.usage);

        const rawResponse = completion.choices[0].message.content;
        console.log('📝 Raw response length:', rawResponse.length);

        // ============================================
        // 6. PARSE & VALIDATE JSON
        // ============================================
        try {
            analysisResult = JSON.parse(rawResponse);
            console.log('✅ JSON parsed successfully');
        } catch (parseError) {
            console.error('❌ JSON parse error:', parseError);
            throw new HttpsError(
                'internal',
                'Failed to parse AI response. Please try again.'
            );
        }

        // Validate required fields
        const requiredFields = [
            'atsScore',
            'requiredKeywords',
            'matchedKeywords',
            'missingKeywords',
            'weakKeywords',
            'sectionScores',
            'improvementSuggestions',
            'optimizedBullets'
        ];

        for (const field of requiredFields) {
            if (!(field in analysisResult)) {
                throw new HttpsError(
                    'internal',
                    `AI response missing required field: ${field}`
                );
            }
        }

        // Validate sectionScores
        if (!analysisResult.sectionScores.skills ||
            !analysisResult.sectionScores.experience ||
            !analysisResult.sectionScores.projects ||
            !analysisResult.sectionScores.roleAlignment) {
            throw new HttpsError('internal', 'Invalid section scores in AI response');
        }

        console.log('✅ Response validated');
        console.log('🎯 ATS Score:', analysisResult.atsScore);

    } catch (openAiError) {
        console.error('❌ OpenAI API error:', openAiError);

        // Handle specific OpenAI errors
        if (openAiError.status === 401) {
            throw new HttpsError('internal', 'OpenAI API key is invalid');
        }

        if (openAiError.status === 429) {
            throw new HttpsError('resource-exhausted', 'API rate limit exceeded. Please try again in a moment.');
        }

        if (openAiError.code === 'ETIMEDOUT' || openAiError.code === 'ECONNREFUSED') {
            throw new HttpsError('unavailable', 'OpenAI service is temporarily unavailable');
        }

        // Generic error
        throw new HttpsError(
            'internal',
            `Analysis failed: ${openAiError.message || 'Unknown error'}`
        );
    }

    // ============================================
    // 7. RETURN STRUCTURED RESPONSE
    // ============================================
    const response = {
        success: true,
        ...analysisResult,
        metadata: {
            userId,
            resumeId: resumeId || null,
            analyzedAt: new Date().toISOString(),
            model: 'gpt-4-turbo-preview'
        }
    };

    console.log('✅ Analysis completed successfully');
    return response;
}

// ============================================
// EXPORTS
// ============================================
module.exports = {
    analyzeResumeHandler,
    OPENAI_API_KEY // Export secret definition for index.js
};
