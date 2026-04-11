# MoodFlix

A mood-based movie and TV series discovery engine. Describe what you feel like watching in natural language and get AI-powered recommendations with personalized explanations.

## Tech Stack

- **Backend:** FastAPI + Python (uv)
- **Frontend:** Next.js (App Router) + Tailwind CSS
- **Search:** ChromaDB (vector embeddings) + OpenAI (re-ranking)
- **Data:** TMDB API
- **Auth:** Firebase Auth (Google sign-in)
- **User Data:** Firestore

## Setup

### Prerequisites

- Python 3.12+
- Node.js 18+
- uv (Python package manager)
- TMDB API key
- OpenAI API key
- Firebase project with Auth + Firestore enabled

### Backend

```bash
cd backend
cp .env.example .env
# Fill in your API keys in .env
uv sync
uv run uvicorn app.main:app --reload
```

### Frontend

```bash
cd frontend
cp .env.example .env.local
# Fill in your Firebase config in .env.local
npm install
npm run dev
```

### Initial Data Seeding

After starting the backend, trigger the initial TMDB sync:

```bash
curl -X POST http://localhost:8000/api/admin/sync/run \
  -H "Authorization: Bearer YOUR_TOKEN"
```

This will fetch popular movies/TV shows from TMDB and generate embeddings. The app is usable once the first batch completes.

## Architecture

See `docs/superpowers/specs/2026-04-10-moodflix-design.md` for the full design spec.
