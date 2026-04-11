"use client";
import { useState, useEffect } from "react";
import AuthGate from "@/components/AuthGate";
import MovieCard from "@/components/MovieCard";
import { getWatchlist, getHistory, getPreferences, getSearchHistory, removeFromWatchlist } from "@/lib/api";
import type { WatchlistItem, HistoryItem, UserPreferences } from "@/types";

export default function ProfilePage() {
  const [watchlist, setWatchlist] = useState<WatchlistItem[]>([]);
  const [history, setHistory] = useState<HistoryItem[]>([]);
  const [preferences, setPreferences] = useState<UserPreferences | null>(null);
  const [searchHistory, setSearchHistory] = useState<any[]>([]);
  const [activeTab, setActiveTab] = useState<"watchlist" | "history" | "searches">("watchlist");
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    async function fetchData() {
      try {
        const [wl, hist, prefs, searches] = await Promise.all([getWatchlist(), getHistory(), getPreferences(), getSearchHistory()]);
        setWatchlist(wl); setHistory(hist); setPreferences(prefs); setSearchHistory(searches);
      } catch (error) { console.error("Failed to fetch profile data:", error); }
      finally { setLoading(false); }
    }
    fetchData();
  }, []);

  const handleRemoveFromWatchlist = async (tmdbId: number) => {
    await removeFromWatchlist(tmdbId);
    setWatchlist((prev) => prev.filter((item) => item.tmdb_id !== tmdbId));
  };

  const tabs = [
    { key: "watchlist" as const, label: "Watchlist", count: watchlist.length },
    { key: "history" as const, label: "Watch History", count: history.length },
    { key: "searches" as const, label: "Recent Searches", count: searchHistory.length },
  ];

  return (
    <AuthGate>
      <div className="max-w-7xl mx-auto px-4 py-8">
        <h1 className="text-3xl font-bold text-white mb-8">My Profile</h1>
        {preferences && preferences.favorite_genres.length > 0 && (
          <div className="mb-8 p-4 bg-gray-900 rounded-lg">
            <h2 className="text-sm font-medium text-gray-400 mb-2">Your Taste</h2>
            <div className="flex gap-2 flex-wrap">{preferences.favorite_genres.map((genre) => <span key={genre} className="bg-red-600/20 text-red-400 px-3 py-1 rounded-full text-sm">{genre}</span>)}</div>
          </div>
        )}
        <div className="flex gap-1 mb-6 border-b border-gray-800">
          {tabs.map((tab) => <button key={tab.key} onClick={() => setActiveTab(tab.key)} className={`px-4 py-3 text-sm font-medium transition-colors ${activeTab === tab.key ? "text-red-500 border-b-2 border-red-500" : "text-gray-400 hover:text-white"}`}>{tab.label} ({tab.count})</button>)}
        </div>
        {loading ? <div className="animate-pulse text-gray-400 py-10 text-center">Loading...</div> : (
          <>
            {activeTab === "watchlist" && (
              <div className="grid grid-cols-2 sm:grid-cols-3 md:grid-cols-4 lg:grid-cols-5 gap-6">
                {watchlist.map((item) => (
                  <div key={item.tmdb_id} className="relative group">
                    <MovieCard tmdbId={item.tmdb_id} mediaType={item.media_type} title={item.title} posterPath={item.poster_path} />
                    <button onClick={(e) => { e.preventDefault(); handleRemoveFromWatchlist(item.tmdb_id); }} className="absolute top-2 right-2 bg-black/70 text-red-400 hover:text-red-300 w-6 h-6 rounded-full text-xs opacity-0 group-hover:opacity-100 transition-opacity flex items-center justify-center">X</button>
                  </div>
                ))}
                {watchlist.length === 0 && <p className="text-gray-500 col-span-full text-center py-10">Your watchlist is empty. Search for something to watch!</p>}
              </div>
            )}
            {activeTab === "history" && (
              <div className="grid grid-cols-2 sm:grid-cols-3 md:grid-cols-4 lg:grid-cols-5 gap-6">
                {history.map((item) => (
                  <div key={item.tmdb_id}><MovieCard tmdbId={item.tmdb_id} mediaType={item.media_type} title={item.title} posterPath={null} />{item.rating && <p className="text-yellow-400 text-xs mt-1">Rated: {item.rating}/5</p>}</div>
                ))}
                {history.length === 0 && <p className="text-gray-500 col-span-full text-center py-10">No watch history yet.</p>}
              </div>
            )}
            {activeTab === "searches" && (
              <div className="space-y-2">
                {searchHistory.map((item: any, index: number) => (
                  <div key={index} className="flex items-center justify-between p-3 bg-gray-900 rounded-lg">
                    <span className="text-gray-300">{item.query}</span>
                    <span className="text-gray-600 text-xs">{new Date(item.searched_at).toLocaleDateString()}</span>
                  </div>
                ))}
                {searchHistory.length === 0 && <p className="text-gray-500 text-center py-10">No search history yet.</p>}
              </div>
            )}
          </>
        )}
      </div>
    </AuthGate>
  );
}
