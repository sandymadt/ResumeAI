/**
 * Firebase Cloud Functions - Entry Point
 * 
 * RESPONSIBILITIES:
 * - Initialize Firebase Admin
 * - Export callable functions
 * - Route requests to business logic
 * 
 * NO BUSINESS LOGIC HERE - Keep it clean!
 */

const { initializeApp } = require('firebase-admin/app');
const { onCall } = require('firebase-functions/v2/https');
const { analyzeResumeHandler } = require('./analyzeResume');

// Initialize Firebase Admin SDK
initializeApp();

/**
 * analyzeResume - Callable Function
 * 
 * FLOW:
 * Frontend → Firebase Auth → This Function → analyzeResumeHandler → OpenAI → Response
 * 
 * CALLABLE FUNCTIONS:
 * - Automatically authenticate user
 * - Handle CORS automatically
 * - JSON serialization
 * - Error handling built-in
 * 
 * INTERVIEW NOTES:
 * "We use Firebase callable functions instead of HTTP functions because they:
 * 1. Automatically include the authenticated user context
 * 2. Handle CORS and serialization
 * 3. Provide better error handling
 * 4. Simplify frontend integration (httpsCallable)"
 */
exports.analyzeResume = onCall(
    {
        // Resource allocation
        timeoutSeconds: 300, // 5 minutes max
        memory: '512MiB',

        // Region (optional - defaults to us-central1)
        // region: 'us-central1',
    },
    analyzeResumeHandler
);

console.log('✅ Firebase Cloud Functions initialized');
console.log('📦 Exported functions: analyzeResume');
