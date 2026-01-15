# Quick Start Guide

## Running the Application

### In Two Terminal Windows:

**Terminal 1 - Backend (MUST RUN FIRST):**
```bash
cd /Users/udirno/Desktop/website/portfolio/argument-explorer/backend
source venv/bin/activate
export ANTHROPIC_API_KEY=your_anthropic_api_key_here
uvicorn main:app --reload --port 8000
```

Wait for: `INFO: Uvicorn running on http://0.0.0.0:8000`

**Terminal 2 - Frontend:**
```bash
cd /Users/udirno/Desktop/website/portfolio/argument-explorer/frontend
python3 -m http.server 8080
```

**Then open in browser:**
- Go to: `http://localhost:8080`
- Enter a question and click "Analyze"

## Troubleshooting

**Button doesn't work?**
1. Make sure backend is running (check Terminal 1)
2. Open browser console (F12) and check for errors
3. Verify backend is on port 8000: Visit `http://localhost:8000/` (should show JSON)

**Port already in use?**
```bash
lsof -ti:8000 | xargs kill -9
```

**API Key error?**
Make sure you export the API key in the SAME terminal where you run uvicorn.
