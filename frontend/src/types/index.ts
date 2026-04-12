export interface MediaSummary {
  tmdb_id: number;
  media_type: "movie" | "tv";
  title: string;
  poster_path: string | null;
  vote_average: number;
  release_year: number | null;
  mood_tags?: string[];
}

export interface SearchResult extends MediaSummary {
  match_reason: string;
}

export interface SearchResponse {
  query: string;
  results: SearchResult[];
}

export interface Genre {
  id: number;
  name: string;
}

export interface WatchlistItem {
  tmdb_id: number;
  media_type: string;
  title: string;
  poster_path: string | null;
  added_at: string;
}

export interface HistoryItem {
  tmdb_id: number;
  media_type: string;
  title: string;
  watched_at: string;
  rating: number | null;
}

export interface UserPreferences {
  favorite_genres: string[];
  disliked_genres: string[];
  preferred_decades: string[];
}

export interface ChatMessage {
  role: "user" | "assistant";
  content: string;
}

export interface ChatRecommendation extends MediaSummary {
  pitch: string;
}

export interface MoodPlaylist {
  id: string;
  name: string;
  description: string;
  mood_key: string;
  items: MediaSummary[];
  generated_at: string;
}

export interface TasteDNA {
  top_moods: { mood: string; percentage: number }[];
  genre_breakdown: { genre: string; count: number }[];
  preferred_eras: { era: string; count: number }[];
  director_affinities: string[];
  summary: string;
}
