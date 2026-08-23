# AI Marks Entry System — Project Notes

## Overview
The project has four parts:
1. React frontend — Excel upload, review, confirmation.
2. FastAPI backend — validation, matching, confirmation APIs.
3. Mock examination portal — local portal used for demonstration.
4. Python automation — Playwright + Chromium submits confirmed marks.

## Flow
```text
Excel
  ↓
React (:5173)
  ↓ POST /api/upload
FastAPI (:8000)
  ↓
Validation
  ↓
Matched / Review / Unmatched
  ↓ POST /api/confirm
Confirmed marks
  ↓
automation.py
  ↓
Playwright + Chromium
  ↓
Mock Portal (:9000)
  ↓
Verify → Submit
```

## Technology
- React + TypeScript + Vite
- Python + FastAPI
- Pandas
- Playwright
- Chromium
- Excel (.xlsx/.xls)
- REST/JSON
- VS Code

## FastAPI endpoints
- `GET /` — API running message
- `GET /api/health` — health check
- `GET /api/students` — registered students
- `POST /api/upload` — upload and validate Excel
- `POST /api/confirm` — confirm only MATCHED records
- `GET /api/confirmed-marks` — return confirmed records

## Validation
The backend checks:
- `Enrollment No.`
- `Student Name`
- `Marks`
- Missing values
- Marks outside 0–40
- Duplicate enrollment numbers
- Unmatched enrollment numbers

## Frontend
`frontend/src/App.tsx`:
- fetches students
- uploads Excel through `/api/upload`
- displays counts and statuses
- filters records
- confirms marks through `/api/confirm`

## Automation
`backend/automation.py`:
1. Gets confirmed marks from FastAPI.
2. Opens Chromium with Playwright.
3. Opens the mock portal.
4. Logs in.
5. Selects the course.
6. Imports the required Excel file.
7. Verifies portal marks against confirmed records.
8. Submits the marks.

## Run commands

### FastAPI — Terminal 1
```powershell
cd C:\DAKSH\projectSIH\ai-marks-entry-system\backend
venv\Scripts\activate
uvicorn main:app --reload --port 8000
```

### Mock portal — Terminal 2
```powershell
cd C:\DAKSH\projectSIH\ai-marks-entry-system\mock-portal
python -m http.server 9000
```

### React — Terminal 3
```powershell
cd C:\DAKSH\projectSIH\ai-marks-entry-system\frontend
npm run dev
```

### Automation — Terminal 4
Run only after confirming marks in React:
```powershell
cd C:\DAKSH\projectSIH\ai-marks-entry-system\backend
venv\Scripts\activate
python automation.py
```

## URLs
- React: `http://localhost:5173`
- FastAPI: `http://127.0.0.1:8000`
- Swagger: `http://127.0.0.1:8000/docs`
- Mock portal: `http://localhost:9000`

## Important
`automation.py` must be run after confirmation. Otherwise `/api/confirmed-marks` may be empty and the script will show:
```text
Exception: No confirmed marks available.
```

## What to study for the demo
Understand:
- React components and state
- `useState` and `useEffect`
- TypeScript
- Vite
- FastAPI and REST APIs
- GET vs POST
- JSON and FormData
- CORS
- Pandas/Excel processing
- Validation logic
- Python virtual environments
- Uvicorn
- Playwright
- Chromium
- Browser automation
- Frontend ↔ backend communication
- Localhost and ports
