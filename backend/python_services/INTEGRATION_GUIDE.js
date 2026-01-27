/**
 * Integration Guide: Python Text Extractor with Node.js Backend
 * 
 * This file shows how to integrate the Python text extraction module
 * with the existing Node.js Firebase Cloud Functions backend.
 */

const { spawn } = require('child_process');
const path = require('path');
const admin = require('firebase-admin');

/**
 * Extract text from a resume file using the Python module
 * 
 * @param {string} filePath - Absolute path to the PDF or DOCX file
 * @returns {Promise<string>} - Extracted and normalized text
 * @throws {Error} - If extraction fails
 */
async function extractResumeText(filePath) {
  return new Promise((resolve, reject) => {
    // Path to Python script
    const pythonScript = path.join(__dirname, '../python_services/text_extractor.py');
    
    // Spawn Python process
    const python = spawn('python', [pythonScript, filePath]);
    
    let outputData = '';
    let errorData = '';
    
    // Collect stdout
    python.stdout.on('data', (data) => {
      outputData += data.toString();
    });
    
    // Collect stderr
    python.stderr.on('data', (data) => {
      errorData += data.toString();
    });
    
    // Handle process completion
    python.on('close', (code) => {
      if (code === 0) {
        // Success - parse the extracted text from output
        // The script outputs structured data, extract just the text
        try {
          // Look for the "Extracted Text:" section in output
          const textMatch = outputData.match(/Extracted Text:\n\n([\s\S]+?)\n=+/);
          if (textMatch && textMatch[1]) {
            resolve(textMatch[1].trim());
          } else {
            // Fallback: return all output
            resolve(outputData);
          }
        } catch (e) {
          resolve(outputData); // Return raw output if parsing fails
        }
      } else {
        reject(new Error(`Text extraction failed (exit code ${code}): ${errorData}`));
      }
    });
    
    // Handle process errors
    python.on('error', (error) => {
      reject(new Error(`Failed to start Python process: ${error.message}`));
    });
  });
}

/**
 * Alternative: Use Python module directly via import (requires python-shell)
 * 
 * Install: npm install python-shell
 * 
 * @param {string} filePath - Path to resume file
 * @returns {Promise<object>} - Extraction result with metadata
 */
async function extractResumeTextWithMetadata(filePath) {
  const { PythonShell } = require('python-shell');
  
  const options = {
    mode: 'json',
    pythonPath: 'python', // or specific python3 path
    scriptPath: path.join(__dirname, '../python_services'),
    args: []
  };
  
  return new Promise((resolve, reject) => {
    // Create a temporary script to call our module
    const scriptCode = `
import json
from text_extractor import ResumeTextExtractor

extractor = ResumeTextExtractor()
result = extractor.extract_with_metadata("${filePath}")
print(json.dumps(result))
    `;
    
    PythonShell.runString(scriptCode, options, (err, results) => {
      if (err) {
        reject(err);
      } else {
        resolve(results[0]);
      }
    });
  });
}

/**
 * Firebase Cloud Function: Parse Resume
 * 
 * This function handles resume uploads and extracts text.
 * Integrates with the existing parseResume function.
 */
const functions = require('firebase-functions');

exports.parseResume = functions
  .runWith({
    timeoutSeconds: 120,
    memory: '512MB'
  })
  .https.onCall(async (data, context) => {
    try {
      // Ensure user is authenticated
      if (!context.auth) {
        throw new functions.https.HttpsError(
          'unauthenticated',
          'User must be authenticated'
        );
      }
      
      const { filePath, resumeId } = data;
      
      if (!filePath) {
        throw new functions.https.HttpsError(
          'invalid-argument',
          'File path is required'
        );
      }
      
      // Extract text using Python module
      console.log(`Extracting text from: ${filePath}`);
      const extractedText = await extractResumeText(filePath);
      
      console.log(`Extracted ${extractedText.length} characters`);
      
      // Store in Firestore
      if (resumeId) {
        await admin.firestore()
          .collection('resumes')
          .doc(resumeId)
          .update({
            extractedText: extractedText,
            parsedAt: admin.firestore.FieldValue.serverTimestamp(),
            status: 'parsed'
          });
      }
      
      return {
        success: true,
        text: extractedText,
        charCount: extractedText.length,
        wordCount: extractedText.split(/\s+/).length
      };
      
    } catch (error) {
      console.error('Parse resume error:', error);
      
      throw new functions.https.HttpsError(
        'internal',
        `Failed to parse resume: ${error.message}`
      );
    }
  });

/**
 * Helper: Download file from Firebase Storage and extract text
 * 
 * @param {string} storagePath - Path in Firebase Storage (e.g., 'resumes/user123/resume.pdf')
 * @returns {Promise<string>} - Extracted text
 */
async function extractFromStorage(storagePath) {
  const os = require('os');
  const fs = require('fs').promises;
  
  // Download file to temp directory
  const tempFilePath = path.join(os.tmpdir(), path.basename(storagePath));
  
  try {
    // Download from Storage
    await admin.storage()
      .bucket()
      .file(storagePath)
      .download({ destination: tempFilePath });
    
    // Extract text
    const text = await extractResumeText(tempFilePath);
    
    // Clean up temp file
    await fs.unlink(tempFilePath);
    
    return text;
    
  } catch (error) {
    // Ensure cleanup even on error
    try {
      await fs.unlink(tempFilePath);
    } catch (e) {
      // Ignore cleanup errors
    }
    
    throw error;
  }
}

/**
 * Complete Integration Example
 * 
 * This shows the full flow from upload to analysis
 */
exports.analyzeResumeComplete = functions
  .runWith({
    timeoutSeconds: 300,
    memory: '1GB'
  })
  .https.onCall(async (data, context) => {
    try {
      // 1. Authenticate
      if (!context.auth) {
        throw new functions.https.HttpsError('unauthenticated', 'Login required');
      }
      
      const { storagePath, jobDescription } = data;
      const userId = context.auth.uid;
      
      // 2. Extract text from resume
      console.log('Step 1: Extracting resume text...');
      const resumeText = await extractFromStorage(storagePath);
      
      // 3. Analyze with OpenAI (existing analyzeResume logic)
      console.log('Step 2: Analyzing with AI...');
      const analysis = await analyzeWithOpenAI(resumeText, jobDescription);
      
      // 4. Store results
      console.log('Step 3: Storing results...');
      const resultDoc = await admin.firestore()
        .collection('analyses')
        .add({
          userId: userId,
          resumePath: storagePath,
          resumeText: resumeText,
          jobDescription: jobDescription,
          analysis: analysis,
          createdAt: admin.firestore.FieldValue.serverTimestamp()
        });
      
      return {
        success: true,
        analysisId: resultDoc.id,
        ...analysis
      };
      
    } catch (error) {
      console.error('Complete analysis error:', error);
      throw new functions.https.HttpsError('internal', error.message);
    }
  });

/**
 * Batch Processing Example
 * 
 * Process multiple resumes efficiently
 */
async function batchExtractResumes(filePaths) {
  const results = [];
  
  for (const filePath of filePaths) {
    try {
      const text = await extractResumeText(filePath);
      results.push({
        filePath: filePath,
        success: true,
        text: text,
        wordCount: text.split(/\s+/).length
      });
    } catch (error) {
      results.push({
        filePath: filePath,
        success: false,
        error: error.message
      });
    }
  }
  
  return results;
}

// Export all functions
module.exports = {
  extractResumeText,
  extractResumeTextWithMetadata,
  extractFromStorage,
  batchExtractResumes
};

/**
 * TESTING THE INTEGRATION
 * 
 * 1. Install dependencies in functions folder:
 *    cd functions
 *    npm install python-shell  # Optional, for alternative method
 * 
 * 2. Ensure Python is available:
 *    python --version  # Should be Python 3.7+
 * 
 * 3. Test locally:
 *    const extractor = require('./resumeExtractor');
 *    const text = await extractor.extractResumeText('/path/to/resume.pdf');
 *    console.log(text);
 * 
 * 4. Deploy:
 *    firebase deploy --only functions
 */
