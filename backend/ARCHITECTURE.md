# 🏗️ Backend Architecture

## 📐 System Architecture Diagram

```
┌─────────────────────────────────────────────────────────────────┐
│                         FRONTEND (React)                         │
│                                                                  │
│  ┌──────────────┐         ┌──────────────┐                     │
│  │ AnalysisPage │────────▶│analysisService│                     │
│  └──────────────┘         └───────┬──────┘                     │
│                                    │                             │
│                          httpsCallable('analyzeResume')          │
└────────────────────────────────────┼──────────────────────────────┘
                                     │
                                     │ HTTPS + Auth
                                     ▼
┌─────────────────────────────────────────────────────────────────┐
│                   FIREBASE CLOUD FUNCTIONS                       │
│                                                                  │
│  ┌────────────────────────────────────────────────────────────┐ │
│  │  index.js (Entry Point)                                    │ │
│  │  ┌──────────────────────────────────────────────────────┐  │ │
│  │  │ exports.analyzeResume = onCall(...)                  │  │ │
│  │  └────────────────────┬─────────────────────────────────┘  │ │
│  └───────────────────────┼────────────────────────────────────┘ │
│                          │                                       │
│                          ▼                                       │
│  ┌────────────────────────────────────────────────────────────┐ │
│  │  analyzeResume.js (Business Logic)                         │ │
│  │                                                             │ │
│  │  1️⃣  Authentication Check                                  │ │
│  │  2️⃣  Input Validation                                      │ │
│  │  3️⃣  OpenAI Client Init (with Secret)                      │ │
│  │  4️⃣  ATS Prompt Construction                               │ │
│  │  5️⃣  OpenAI API Call                                       │ │
│  │  6️⃣  JSON Parsing & Validation                             │ │
│  │  7️⃣  Return Structured Response                            │ │
│  └────────────────────┬───────────────────────────────────────┘ │
└───────────────────────┼─────────────────────────────────────────┘
                        │
                        │ API Request
                        ▼
┌─────────────────────────────────────────────────────────────────┐
│                      OPENAI GPT-4 API                            │
│                                                                  │
│  ┌────────────────────────────────────────────────────────────┐ │
│  │  System Prompt: "You are an ATS analyzer..."               │ │
│  │  User Prompt: Resume + Job Description                     │ │
│  │                                                             │ │
│  │  ──▶ AI Processing ──▶ JSON Response                       │ │
│  └────────────────────────────────────────────────────────────┘ │
└───────────────────────┬─────────────────────────────────────────┘
                        │
                        │ Structured JSON
                        ▼
┌─────────────────────────────────────────────────────────────────┐
│                         RESPONSE FLOW                            │
│                                                                  │
│  {                                                               │
│    "atsScore": 75,                                              │
│    "matchedKeywords": [...],                                     │
│    "missingKeywords": [...],                                     │
│    "sectionScores": {...},                                       │
│    "improvementSuggestions": [...],                              │
│    "optimizedBullets": [...]                                     │
│  }                                                               │
└───────────────────────┬─────────────────────────────────────────┘
                        │
                        │ Return to Frontend
                        ▼
┌─────────────────────────────────────────────────────────────────┐
│                      FRONTEND DISPLAY                            │
│                                                                  │
│  ┌──────────────┐                                               │
│  │AnalysisResults│  ──▶  Beautiful UI with Scores & Insights    │
│  └──────────────┘                                               │
└─────────────────────────────────────────────────────────────────┘
```

---

## 🔐 Security Architecture

```
┌──────────────────────────────────────────────────────────┐
│                    SECURITY LAYERS                        │
└──────────────────────────────────────────────────────────┘

1. AUTHENTICATION
   ┌──────────────────────────────────────┐
   │ Firebase Auth                         │
   │ • User must be logged in              │
   │ • Token automatically included        │
   │ • Verified by Cloud Functions         │
   └──────────────────────────────────────┘

2. API KEY MANAGEMENT
   ┌──────────────────────────────────────┐
   │ Google Cloud Secret Manager           │
   │ • API key stored securely             │
   │ • Never in code or Git                │
   │ • Accessed at runtime only            │
   └──────────────────────────────────────┘

3. INPUT VALIDATION
   ┌──────────────────────────────────────┐
   │ Backend Validation                    │
   │ • Type checking                       │
   │ • Length limits                       │
   │ • Sanitization                        │
   └──────────────────────────────────────┘

4. RATE LIMITING
   ┌──────────────────────────────────────┐
   │ Firebase Quotas                       │
   │ • Max invocations/day                 │
   │ • Timeout limits                      │
   │ • Memory limits                       │
   └──────────────────────────────────────┘
```

---

## 📊 Data Flow

```
USER ACTION                    BACKEND PROCESSING              AI ANALYSIS
─────────────                  ──────────────────              ───────────

1. Upload Resume     ──────▶   Validate Input       ──────▶   Extract Text
   
2. Enter Job Desc    ──────▶   Check Auth           ──────▶   Parse Keywords
   
3. Click "Analyze"   ──────▶   Build Prompt         ──────▶   Match Resume
   
4. Wait...           ◀──────   Call OpenAI          ──────▶   Calculate Score
   
5. View Results      ◀──────   Parse JSON           ◀──────   Return Analysis
```

---

## 🗂️ File Responsibilities

```
backend/
│
├── firebase.json              # Firebase config (no emulator)
├── .firebaserc               # Project link
├── .gitignore                # Never commit secrets!
│
├── README.md                 # Full documentation
├── SETUP.md                  # Environment setup
├── QUICKSTART.md             # Fast setup guide
│
├── deploy.sh                 # Bash deployment script
├── deploy.ps1                # PowerShell deployment script
│
└── functions/
    ├── package.json          # Dependencies
    │                         #  - firebase-admin
    │                         #  - firebase-functions
    │                         #  - openai
    │
    ├── index.js              # Entry point
    │                         #  - Initialize Firebase
    │                         #  - Export analyzeResume
    │                         #  - Configure resources
    │
    └── analyzeResume.js      # ⭐ MAIN BUSINESS LOGIC
                              #  - Auth check
                              #  - Input validation
                              #  - OpenAI integration
                              #  - ATS prompt engineering
                              #  - Error handling
```

---

## 🔄 Request/Response Cycle

### REQUEST
```javascript
{
  resumeText: "John Doe, Software Engineer...",
  jobDescription: "We are seeking a React developer...",
  resumeId: "optional-resume-id"
}
```

### PROCESSING
1. **Authenticate**: Check if user is logged in
2. **Validate**: Ensure inputs are correct
3. **Initialize**: Create OpenAI client
4. **Prompt**: Build ATS analysis prompt
5. **Call AI**: Send to GPT-4
6. **Parse**: Extract JSON from response
7. **Validate**: Check response structure
8. **Return**: Send to frontend

### RESPONSE
```javascript
{
  success: true,
  atsScore: 75,
  requiredKeywords: ["React", "Node.js", "AWS"],
  matchedKeywords: ["React", "JavaScript"],
  missingKeywords: ["AWS", "Docker"],
  weakKeywords: ["Node.js"],
  sectionScores: {
    skills: 32,
    experience: 25,
    projects: 15,
    roleAlignment: 8
  },
  improvementSuggestions: [
    "Add AWS experience to your resume",
    "Quantify your React projects with metrics",
    ...
  ],
  optimizedBullets: [
    "Architected scalable React applications serving 100K+ users",
    ...
  ],
  metadata: {
    userId: "firebase-user-id",
    resumeId: null,
    analyzedAt: "2024-01-23T12:00:00.000Z",
    model: "gpt-4-turbo-preview"
  }
}
```

---

## 🎯 ATS Scoring Algorithm

```
TOTAL SCORE: 100 POINTS
├── Skills Match (40 points)
│   ├── Required skills found: +40
│   ├── Partial match: +20-35
│   └── Missing critical skills: -10 each
│
├── Experience Relevance (30 points)
│   ├── Highly relevant experience: +30
│   ├── Some relevant experience: +15-25
│   └── Unrelated experience: +5-10
│
├── Projects Relevance (20 points)
│   ├── Matching projects: +20
│   ├── Related projects: +10-15
│   └── No projects: 0
│
└── Role Alignment (10 points)
    ├── Perfect fit: +10
    ├── Good fit: +5-8
    └── Poor fit: +1-3
```

---

## 🚀 Deployment Flow

```
DEVELOPER                    FIREBASE                         PRODUCTION
─────────                    ────────                         ──────────

1. Code Changes
   ├── index.js
   └── analyzeResume.js
          │
          │
          ▼
2. Install Dependencies
   npm install
          │
          │
          ▼
3. Configure Secrets
   firebase functions:config:set openai.key="..."
          │
          │
          ▼
4. Deploy
   firebase deploy --only functions
          │
          ├────────────────────▶  Build Functions
          │                       
          │                       Validate Code
          │                       
          │                       Upload to Cloud
          │                       
          │ ◀────────────────────  Deploy Success
          │
          ▼
5. Live in Production
   https://us-central1-resumeready-34a35.cloudfunctions.net/analyzeResume
```

---

## 💡 Key Design Decisions

### 1. Why Callable Functions over HTTP?
- ✅ Automatic authentication
- ✅ CORS handled
- ✅ Type-safe
- ✅ Better error handling

### 2. Why Single Business Logic File?
- ✅ Easy to understand
- ✅ Interview-friendly
- ✅ No over-engineering
- ✅ Single responsibility

### 3. Why GPT-4 over GPT-3.5?
- ✅ Better accuracy
- ✅ Consistent JSON output
- ✅ Contextual understanding
- ✅ Worth the cost for quality

### 4. Why Secret Manager over Config?
- ✅ More secure
- ✅ Easier rotation
- ✅ Audit logging
- ✅ Production best practice

---

**This architecture is production-ready, scalable, and interview-friendly!** ✅
