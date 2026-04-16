# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Commands

### Backend
```bash
cd backend
uv sync                                        # install dependencies
uv run uvicorn app.main:app --reload           # dev server on :8000
uv run pytest                                  # run all tests
uv run pytest tests/test_search_service.py     # run single test file
uv run ruff check .                            # lint
python run_sync.py                             # manually trigger TMDB sync (~20 min)
```

### Frontend
```bash
cd frontend
npm install
npm run dev          # dev server on :3000
npm run build        # production build
npm run lint         # ESLint
```

### Environment setup
- `backend/.env` — copy from `.env.example`. Requires: `TMDB_API_KEY`, `OPENAI_API_KEY`, `FIREBASE_SERVICE_ACCOUNT_PATH`
- `frontend/.env.local` — copy from `.env.example`. Requires Firebase client config vars.

## Architecture

MoodFlix is a mood-based movie/TV recommender. The frontend is Next.js App Router (`"use client"` throughout), the backend is FastAPI. They communicate via REST + one SSE streaming endpoint for chat.

### Authentication flow
Firebase Auth (Google sign-in only). The frontend calls `getIdToken()` and attaches `Authorization: Bearer {token}` to every API request. The backend verifies this token via `verify_firebase_token` FastAPI dependency. User profiles are auto-created in Firestore on the first `/api/user/profile` call.

### Data stores
- **ChromaDB** (`./data/chroma_db`) — vector store for all movie/TV titles. Each document stores embeddings + metadata: `title`, `genres`, `release_year`, `vote_average`, `poster_path`, `mood_tags`. This is the source for all search and similarity queries.
- **Firestore** — user data only: profiles, watchlist, watch history, preferences, search history.
- **No relational DB.** TMDB is the source of truth for media metadata; it is synced into ChromaDB via the worker.

### TMDB sync worker
`backend/app/workers/tmdb_sync.py` — runs daily at 3 AM via APScheduler. Fetches popular + top-rated + regional cinema (15 languages) from TMDB, classifies mood tags via GPT (10 titles/batch), generates OpenAI embeddings, then upserts into ChromaDB. State is tracked in `sync_state.json`. Can be triggered manually via `python run_sync.py` or `POST /api/admin/sync/run`.

### Search pipeline
`POST /api/search` → embed query with `text-embedding-3-small` → ChromaDB vector search (50 candidates) → GPT rerank to 10 results with `match_reason` per title. User context (preferences + last 20 watched) is injected into the rerank prompt. Optional `filter_text` (e.g. "only comedies") is passed as a constraint to GPT.

### Mood playlists
10 hardcoded mood keys (e.g. `cozy-rainy-day`, `adrenaline-rush`). Each has a text definition that gets embedded → ChromaDB search (30 candidates) → GPT curates to 12-15. Results are cached in-memory for 24 hours in `PlaylistService`.

### AI Chat (streaming)
`POST /api/chat` streams SSE. `ChatService` maintains multi-turn conversation context. After 3+ user messages it performs a ChromaDB candidate search and injects results into the GPT stream prompt. The frontend reads the stream via `ReadableStreamDefaultReader`.

### Frontend API layer
`frontend/src/lib/api.ts` — single module wrapping all backend calls. Has a module-level `Map` cache (5-min TTL) for all GET requests. Handles token injection, 502 retries (800ms backoff), and cache invalidation on mutations (e.g. watchlist add/remove clears the watchlist cache key).

### Frontend state
- `ChatContext` — controls chat panel open/close globally, used by Navbar and home page CTA.
- `ToastContext` — 3-second auto-dismiss toasts.
- `useAuth` — wraps Firebase `onAuthStateChanged`, returns `{ user, loading }`.
- `useSearch` — manages search query execution and deduplicates results by `tmdb_id`.

## Backend router map

| Router | Prefix | Responsibility |
|---|---|---|
| browse | `/api` | trending, top-rated, genres, browse-by-genre |
| search | `/api/search` | semantic search |
| detail | `/api/title` | title details + similar titles (ChromaDB) |
| user | `/api/user` | profile, watchlist, history, preferences, search history, taste-dna |
| playlist | `/api/playlists` | mood playlist list + generation |
| chat | `/api/chat` | streaming AI chat |
| pitch | `/api/pitch`, `/api/pitches` | single + batch personalized pitches |
| taste | `/api/user/taste-dna` | taste profile from watch history |
| admin | `/api/admin/sync` | sync status + manual trigger |

## Key design decisions

- **`allow_origins=["*"]` with `allow_credentials=False`** in CORS — required because wildcard origin and credentials cannot be combined (Starlette constraint).
- **`"use client"` on all pages** — no RSC data fetching; all data loading is done client-side in `useEffect`. This is intentional given the auth-gated nature of most content.
- **ChromaDB is the search source, not TMDB** — search never calls TMDB live. All queries go through the local vector store populated by the sync worker.
- **Mood tags are a controlled vocabulary** — 20 fixed tags (e.g. `cozy`, `mind-bending`, `bittersweet`). Tags are assigned by GPT during sync. Search reranking and playlist generation use these tags as a signal.
- **Next.js 16 / React 19** — contains breaking changes from older versions. Before modifying frontend patterns, check `node_modules/next/dist/docs/` for current API.
