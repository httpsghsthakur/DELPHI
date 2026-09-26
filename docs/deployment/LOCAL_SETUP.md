# DELPHI Local Setup Guide

This guide is for running DELPHI locally outside of Docker for development purposes.

## Prerequisites
- Python 3.11+
- Node.js 20+
- SQLite (built-in)

## Backend Setup

1. **Virtual Environment:**
   ```bash
   python -m venv venv
   source venv/bin/activate  # Or venv\Scripts\activate on Windows
   ```

2. **Install Dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

3. **Environment Configuration:**
   ```bash
   cp .env.example .env
   ```
   
4. **Run the API:**
   ```bash
   uvicorn delphi.api.main:app --reload --port 8000
   ```

## Frontend Setup

1. **Install Dependencies:**
   ```bash
   cd frontend
   npm install
   ```

2. **Run Development Server:**
   ```bash
   npm run dev
   ```
   The dashboard will be available at http://localhost:5173.

## Testing & Quality
- Backend Tests: `pytest`
- Frontend Tests: `cd frontend && npm run test`
- Frontend Typecheck: `cd frontend && npm run typecheck`
