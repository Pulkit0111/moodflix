# MoodFlix AI Features + Clean Minimal Redesign

## Context

MoodFlix is a mood-first movie/TV discovery app. The current MVP has basic browsing (trending, top-rated), AI-powered semantic search (embeddings + GPT reranking), watchlist, watch history, and a profile page. The UI is a dark Netflix-like theme with red accents.

This spec adds 7 AI features that lean into the mood-first identity and redesigns the entire UI to a clean minimal aesthetic (Letterboxd meets Apple TV+).

## Design Decisions

- **UI**: Clean Minimal -- pure blacks (#0a0a0a), subtle borders (#1a1a1a), white text, letter-spaced uppercase labels, no red accents
- **Homepage**: Search hero + quick mood pills below + "For You" section + mood playlists + trending
- **AI Chat**: Slide-over panel (right side, dismissible), not full page
- **Identity**: Mood-first discovery. Every feature reinforces "how are you feeling?"

---

## Feature Specifications

### F1: AI Mood Playlists

Auto-generated collections like "Cozy Rainy Day", "Adrenaline Rush", "Post-Breakup Comfort".

**Backend**:
- New `PlaylistService` queries ChromaDB by mood embedding, retrieves 30 candidates, GPT selects 10-15 best fits
- 8-12 predefined moods with curated descriptions
- New router: `GET /api/playlists`, `GET /api/playlists/{mood_key}`
- Cache in Firestore (`playlist_cache/{mood_key}`, 24h TTL)

**Frontend**:
- `PlaylistCard` component: horizontal card with playlist name + stacked poster thumbnails
- New page: `/playlist/[mood]` showing full playlist grid
- Playlist cards section on homepage between hero and trending

**Files**: New: `backend/app/services/playlist_service.py`, `backend/app/routers/playlist.py`, `frontend/src/components/PlaylistCard.tsx`, `frontend/src/app/playlist/[mood]/page.tsx`. Modify: `backend/app/main.py`, `frontend/src/app/page.tsx`, `frontend/src/lib/api.ts`

### F2: Vibe Map (Quick Mood Buttons)

Mood pill buttons on homepage for one-tap mood-based search.

**Frontend only** -- reuses existing search pipeline:
- `MoodPills` component: row of bordered pills (Thrilling, Cozy, Nostalgic, Mind-bending, Feel-good, Dark, Romantic, Epic)
- Click navigates to `/search?q={mood_query}`

**Files**: New: `frontend/src/components/MoodPills.tsx`. Modify: `frontend/src/app/page.tsx`

### F3: AI Movie Matchmaker Chat

Conversational AI slide-over panel. Asks follow-up questions, narrows down, recommends with personalized pitches.

**Backend**:
- New `ChatService` with streaming via SSE
- System prompt positions AI as "MoodFlix AI matchmaker"
- Multi-turn: when intent is clear, internally calls `search_service.retrieve_candidates()` and injects into GPT context
- Returns recommendations as JSON blocks within conversational response
- New router: `POST /api/chat` returns `StreamingResponse`

**Frontend**:
- `ChatPanel`: fixed right panel (w-[420px]), z-50, slide-in animation
- Message bubbles (user/assistant), typing indicator, inline `ChatMovieCard` components
- `useChat` hook manages state + SSE streaming
- `ChatContext` provides global open/close state
- Mounted in root layout, triggered from homepage + navbar

**Files**: New: `backend/app/services/chat_service.py`, `backend/app/routers/chat.py`, `frontend/src/components/ChatPanel.tsx`, `frontend/src/components/ChatMovieCard.tsx`, `frontend/src/hooks/useChat.ts`, `frontend/src/contexts/ChatContext.tsx`. Modify: `backend/app/main.py`, `frontend/src/app/layout.tsx`, `frontend/src/app/page.tsx`, `frontend/src/components/Navbar.tsx`, `frontend/src/lib/api.ts`

### F4: "Why You'll Love This" Cards

Personalized AI pitch per movie based on user's taste.

**Backend**:
- New `PitchService` calls GPT with movie info + user preferences/history
- Batch endpoint for efficiency: `POST /api/pitches`
- Single endpoint: `GET /api/pitch/{media_type}/{tmdb_id}`
- Cache in Firestore (`users/{uid}/pitch_cache/{media_type}_{tmdb_id}`, 7-day TTL)

**Frontend**:
- Pitch displayed on MovieCard (truncated italic line) and detail page hero (highlighted quote)
- Homepage: batch-fetch pitches for visible items after auth
- Load asynchronously to avoid blocking render

**Files**: New: `backend/app/services/pitch_service.py`, `backend/app/routers/pitch.py`. Modify: `backend/app/main.py`, `frontend/src/components/MovieCard.tsx`, `frontend/src/app/title/[type]/[id]/page.tsx`, `frontend/src/app/page.tsx`, `frontend/src/lib/api.ts`

### F5: AI Taste DNA Profile

Visual taste fingerprint analyzing user's watch history.

**Backend**:
- New `TasteService` fetches history, looks up ChromaDB metadata (genres, mood_tags), calls GPT to analyze
- Returns: top_moods (with percentages), genre_breakdown, preferred_eras, director_affinities, summary text
- Minimum 5 items in history required
- New router: `GET /api/user/taste-dna`
- Cache in Firestore (`users/{uid}/taste_dna`, 24h TTL)

**Frontend**:
- `TasteDNA` component: horizontal mood bars (CSS-only), genre pills with counts, era segments, director names, GPT summary
- Replaces the simple "Your Taste" section on profile page

**Files**: New: `backend/app/services/taste_service.py`, `backend/app/routers/taste.py`, `frontend/src/components/TasteDNA.tsx`. Modify: `backend/app/main.py`, `frontend/src/app/profile/page.tsx`, `frontend/src/lib/api.ts`

### F6: AI Mood Tags on Every Title

During sync, GPT classifies 3-5 mood tags per title from a controlled vocabulary.

**Backend**:
- Enhance `embedding_gen.py`: add `classify_mood_tags()` that batches 10 titles per GPT call
- Store as `mood_tags` (comma-separated string) in ChromaDB metadata
- Backfill function for existing 500 items
- Search service returns mood_tags with results
- Detail endpoint looks up mood_tags from ChromaDB

**Frontend**:
- Mood tag pills on MovieCard (2-3 tags, subtle bordered pills)
- All mood tags on detail page alongside genre tags

**Controlled vocabulary**: heartwarming, slow-burn, mind-bending, adrenaline-rush, cozy, dark, nostalgic, feel-good, romantic, epic, thrilling, cerebral, bittersweet, whimsical, intense, melancholic, uplifting, suspenseful, quirky, emotional

**Files**: Modify: `backend/app/workers/embedding_gen.py`, `backend/app/services/search_service.py`, `backend/app/routers/detail.py`, `frontend/src/components/MovieCard.tsx`, `frontend/src/app/title/[type]/[id]/page.tsx`, `frontend/src/components/Carousel.tsx`

### F7: Smart Mood Filters

Natural language filter bar on search results.

**Backend**:
- Add `filter_text: str | None` to `SearchRequest` model
- Pass filter_text to GPT reranker as additional constraint

**Frontend**:
- `SmartFilter` component: text input below search bar on results page
- Placeholder: "Refine: under 2 hours, won't make me cry, good for a date..."
- Example filter pills that auto-populate
- Debounced re-search on input (500ms)

**Files**: New: `frontend/src/components/SmartFilter.tsx`. Modify: `backend/app/models/search.py`, `backend/app/services/search_service.py`, `backend/app/routers/search.py`, `frontend/src/hooks/useSearch.ts`, `frontend/src/app/search/page.tsx`, `frontend/src/lib/api.ts`

---

## UI Redesign Specification

### Design Tokens
- Surface: `#0a0a0a`, Elevated: `#111111`
- Border: `#1a1a1a`, Subtle: `#141414`
- Text: primary `#ffffff`, secondary `#a0a0a0`, tertiary `#666666`
- Accent: `#ffffff` (white on black for primary actions)
- No red accents anywhere

### Typography
- Headings: lighter weights (font-light/extralight), increased letter-spacing
- Labels: uppercase, `tracking-widest`, `text-xs`, `text-gray-500`
- Body: font-normal (400 weight)

### Components to Redesign
- **Navbar**: "MOODFLIX" letter-spaced logo, white/gray palette, ghost border buttons
- **SearchBar**: Subtle border, no red focus ring, ghost submit button
- **MovieCard**: No colored badges, subtle hover (scale-[1.02]), mood tag pills
- **Carousel**: Uppercase section titles, thinner arrow buttons
- **All buttons**: Ghost border style (white border on transparent) or solid white on black
- **All pages**: More darkspace, breathing room, refined typography

---

## Data Model Changes

### ChromaDB Metadata (add field)
- `mood_tags`: comma-separated string (e.g., "dark,intense,mind-bending")

### New Firestore Collections
- `playlist_cache/{mood_key}` -- playlist data + `generated_at`
- `users/{uid}/pitch_cache/{media_type}_{tmdb_id}` -- pitch string + `generated_at` (7d TTL)
- `users/{uid}/taste_dna` -- analysis object + `generated_at` (24h TTL)

### New Backend Config
- `mood_classification_model: str = "gpt-4o-mini"`
- `chat_model: str = "gpt-4o-mini"`

---

## New Files (16)

**Backend (8)**: `models/chat.py`, `models/playlist.py`, `models/taste.py`, `services/playlist_service.py`, `services/chat_service.py`, `services/pitch_service.py`, `services/taste_service.py`, `routers/playlist.py`, `routers/chat.py`, `routers/pitch.py`, `routers/taste.py`

**Frontend (8)**: `components/MoodPills.tsx`, `components/PlaylistCard.tsx`, `components/ChatPanel.tsx`, `components/ChatMovieCard.tsx`, `components/SmartFilter.tsx`, `components/TasteDNA.tsx`, `contexts/ChatContext.tsx`, `hooks/useChat.ts`, `app/playlist/[mood]/page.tsx`

## Modified Files (21)

**Backend (9)**: `config.py`, `main.py`, `models/media.py`, `models/search.py`, `services/search_service.py`, `routers/search.py`, `routers/detail.py`, `workers/embedding_gen.py`

**Frontend (12)**: `types/index.ts`, `lib/api.ts`, `app/globals.css`, `app/layout.tsx`, `app/page.tsx`, `app/search/page.tsx`, `app/profile/page.tsx`, `app/title/[type]/[id]/page.tsx`, `components/MovieCard.tsx`, `components/SearchBar.tsx`, `components/Navbar.tsx`, `components/Carousel.tsx`

---

## Implementation Order

1. **Foundation**: ChromaDB mood tags + models + search wiring
2. **Backend services** (parallel): Playlist, Chat, Pitch, Taste, Smart Filter
3. **Run mood tag backfill** on existing 500 items
4. **Global styles**: Design tokens + typography
5. **Frontend features** (parallel): MoodPills, PlaylistCard, ChatPanel, SmartFilter, TasteDNA, pitch integration, mood tag display
6. **UI redesign pass**: All components + pages

## Verification

1. **Mood tags**: Run backfill, verify ChromaDB items have mood_tags metadata
2. **Search**: Search for a mood, verify results include mood_tags and match_reason
3. **Playlists**: Hit `GET /api/playlists`, verify 8-12 playlists with items
4. **Chat**: Open panel, have multi-turn conversation, verify streaming + inline recommendations
5. **Pitches**: Visit detail page, verify personalized "Why you'll love this" appears
6. **Taste DNA**: Add 5+ items to history, visit profile, verify taste analysis renders
7. **Smart filters**: Search, type a filter like "under 2 hours", verify results change
8. **UI**: Verify no red accents remain, all pages use new design tokens
