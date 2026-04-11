import { getIdToken } from "./firebase";
import type { SearchResponse, Genre, WatchlistItem, HistoryItem, UserPreferences } from "@/types";

const API_URL = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000";

async function apiFetch(path: string, options: RequestInit = {}) {
  const token = await getIdToken();
  const headers: Record<string, string> = {
    "Content-Type": "application/json",
    ...((options.headers as Record<string, string>) || {}),
  };
  if (token) { headers["Authorization"] = `Bearer ${token}`; }
  const response = await fetch(`${API_URL}${path}`, { ...options, headers });
  if (!response.ok) { throw new Error(`API error: ${response.status} ${response.statusText}`); }
  return response.json();
}

export async function search(query: string): Promise<SearchResponse> {
  return apiFetch("/api/search", { method: "POST", body: JSON.stringify({ query }) });
}
export async function getTrending(page: number = 1) { return apiFetch(`/api/trending?page=${page}`); }
export async function getTopRated(mediaType: string = "movie", page: number = 1) { return apiFetch(`/api/top-rated?media_type=${mediaType}&page=${page}`); }
export async function getGenres(mediaType: string = "movie"): Promise<Genre[]> { return apiFetch(`/api/genres?media_type=${mediaType}`); }
export async function browse(genreId: number, mediaType: string = "movie", page: number = 1) { return apiFetch(`/api/browse?genre=${genreId}&media_type=${mediaType}&page=${page}`); }
export async function getDetails(mediaType: string, tmdbId: number) { return apiFetch(`/api/title/${mediaType}/${tmdbId}`); }
export async function getSimilar(mediaType: string, tmdbId: number) { return apiFetch(`/api/title/${mediaType}/${tmdbId}/similar`); }
export async function getProfile() { return apiFetch("/api/user/profile"); }
export async function getWatchlist(): Promise<WatchlistItem[]> { return apiFetch("/api/user/watchlist"); }
export async function addToWatchlist(tmdbId: number, mediaType: string, title: string, posterPath: string | null) {
  return apiFetch("/api/user/watchlist", { method: "POST", body: JSON.stringify({ tmdb_id: tmdbId, media_type: mediaType, title, poster_path: posterPath }) });
}
export async function removeFromWatchlist(tmdbId: number) { return apiFetch(`/api/user/watchlist/${tmdbId}`, { method: "DELETE" }); }
export async function getHistory(): Promise<HistoryItem[]> { return apiFetch("/api/user/history"); }
export async function addToHistory(tmdbId: number, mediaType: string, title: string, rating?: number) {
  return apiFetch("/api/user/history", { method: "POST", body: JSON.stringify({ tmdb_id: tmdbId, media_type: mediaType, title, rating }) });
}
export async function getPreferences(): Promise<UserPreferences> { return apiFetch("/api/user/preferences"); }
export async function updatePreferences(prefs: UserPreferences) { return apiFetch("/api/user/preferences", { method: "PUT", body: JSON.stringify(prefs) }); }
export async function getSearchHistory() { return apiFetch("/api/user/search-history"); }
