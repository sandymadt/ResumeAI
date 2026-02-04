# Resume Analysis History - Complete Flow

## Overview
Every resume analysis (initial and re-analysis) is automatically saved to your Scan History in Firestore.

## How It Works

### 1. Initial Analysis
**Location**: New Analysis Page (`/new-analysis`)

**Flow**:
1. User uploads resume and provides job description
2. Click "Analyze Resume Now"
3. Backend `analyzeResume` function:
   - Calculates ATS score
   - Generates improvement suggestions
   - **Automatically saves to Firestore** with:
     - Resume name (from first line of resume)
     - Job title (extracted from job description)
     - ATS score
     - All analysis results
     - Timestamp
4. User is redirected to Analysis Results page
5. **Confirmation**: "Saved to History" badge appears on results page

### 2. Editing & Re-Analysis
**Location**: Resume Editor (`/resume-editor`)

**Flow**:
1. User makes changes to resume text in the editor
2. Click the **"Re-Analyze"** button (blue button under Resume Score)
3. System:
   - Extracts current text from editor
   - Sends to backend with same job description
   - Backend saves as **NEW entry** with:
     - Resume name + "(Edited)" suffix
     - Updated ATS score
     - New analysis results
     - `isReAnalysis: true` flag
     - Link to original analysis ID
4. **Confirmation**: Toast message shows "✓ Analysis saved to history!"
5. Score updates immediately in the editor

### 3. Viewing History
**Location**: Scan History Page (`/history`)

**Features**:
- All analyses listed chronologically (newest first)
- **Edited versions** show purple "EDITED" badge
- Each entry displays:
  - ATS Score (color-coded)
  - Resume name
  - Job title and company
  - Timestamp
  - Matched/missing keywords count
- Click "View" to reload that analysis

### 4. Version Tracking

**Original Analysis**:
```
Resume Name: "John Doe - Software Engineer"
isReAnalysis: false
originalResumeId: null
```

**After Editing**:
```
Resume Name: "John Doe - Software Engineer (Edited)"
isReAnalysis: true
originalResumeId: "abc123..." (links to original)
```

## Key Points

✅ **Automatic Saving**: Every analysis is saved automatically - no manual action needed
✅ **Version History**: Each re-analysis creates a new entry, preserving your optimization journey
✅ **Visual Indicators**: Edited versions clearly marked with purple badge
✅ **Persistent Storage**: All data stored in Firestore, accessible from any device
✅ **Score Tracking**: Compare scores across versions to see improvement

## User Actions Required

**NONE** - The system automatically saves:
- When you complete initial analysis
- When you click "Re-Analyze" in the editor
- When you make any changes and re-scan

## Accessing Your History

1. **From Navigation**: Click "History" in the main menu
2. **From Editor**: Click "Version History" button in top bar
3. **From Results Page**: Click "Re-Scan" to create new version

## Troubleshooting

**If history is empty**:
1. Ensure you're logged in (history is per-user)
2. Complete at least one analysis
3. Check Firebase emulators are running
4. Check browser console for errors

**If re-analysis doesn't save**:
1. Ensure resume text is at least 100 characters
2. Ensure job description is available
3. Check network tab for failed API calls
4. Verify Firebase connection

## Technical Details

**Backend**: `backend/functions/analyzeResume.js`
- Line 142-168: Firestore persistence logic
- Automatically called by both initial and re-analysis

**Frontend**:
- `NewAnalysis.jsx`: Initial analysis trigger
- `ResumeEditor.jsx`: Re-analysis trigger (line 163-195)
- `ScanHistory.jsx`: Display all saved analyses

**Database**: Firestore collection `analyses`
- Each document = one analysis
- Indexed by userId and createdAt
- Contains full analysis results
