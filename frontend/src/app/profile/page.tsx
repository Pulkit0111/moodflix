"use client";
import { useState, useEffect } from "react";
import AuthGate from "@/components/AuthGate";
import MovieCard from "@/components/MovieCard";
import TasteDNA from "@/components/TasteDNA";
import { getWatchlist, getHistory, getPreferences, getSearchHistory, removeFromWatchlist, getTasteDNA } from "@/lib/api";
import type { WatchlistItem, HistoryItem, UserPreferences, TasteDNA as TasteDNAType } from "@/types";

export default function ProfilePage() {
  const [watchlist, setWatchlist] = useState<WatchlistItem[]>([]);
  const [history, setHistory] = useState<HistoryItem[]>([]);
  const [preferences, setPreferences] = useState<UserPreferences | null>(null);
  const [searchHistory, setSearchHistory] = useState<any[]>([]);
  const [tasteDna, setTasteDna] = useState<TasteDNAType | null>(null);
  const [activeTab, setActiveTab] = useState<"watchlist" | "history" | "searches">("watchlist");
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    async function fetchData() {
      try {
        const [wlRes, histRes, prefsRes, searchRes, tasteRes] = await Promise.allSettled([
          getWatchlist(), getHistory(), getPreferences(), getSearchHistory(), getTasteDNA(),
        ]);
        if (wlRes.status === "fulfilled") setWatchlist(wlRes.value);
        if (histRes.status === "fulfilled") setHistory(histRes.value);
        if (prefsRes.status === "fulfilled") setPreferences(prefsRes.value);
        if (searchRes.status === "fulfilled") setSearchHistory(searchRes.value);
        if (tasteRes.status === "fulfilled" && !tasteRes.value.status) setTasteDna(tasteRes.value as TasteDNAType);
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
    { key: "history" as const, label: "History", count: history.length },
    { key: "searches" as const, label: "Searches", count: searchHistory.length },
  ];

  return (
    <AuthGate>
      <div className="max-w-7xl mx-auto px-6 py-10">
        <h1 className="text-2xl font-light text-white mb-8 tracking-wide">My Profile</h1>

        {/* Taste DNA */}
        {tasteDna && <TasteDNA data={tasteDna} />}

        {/* Taste preferences fallback */}
        {!tasteDna && preferences && preferences.favorite_genres.length > 0 && (
          <div className="mb-8 p-5 border border-[#1a1a1a] rounded-xl">
            <h2 className="text-label mb-3">YOUR TASTE</h2>
            <div className="flex gap-2 flex-wrap">{preferences.favorite_genres.map((genre) => <span key={genre} className="text-xs text-[#888] border border-[#222] px-3 py-1.5 rounded-full">{genre}</span>)}</div>
          </div>
        )}

        {/* Tabs */}
        <div className="flex gap-1 mb-8 border-b border-[#1a1a1a]">
          {tabs.map((tab) => (
            <button key={tab.key} onClick={() => setActiveTab(tab.key)}
              className={`px-4 py-3 text-xs tracking-wider transition-colors ${activeTab === tab.key ? "text-white border-b-2 border-white" : "text-[#555] hover:text-[#999]"}`}>
              {tab.label.toUpperCase()} ({tab.count})
            </button>
          ))}
        </div>

        {loading ? <div className="animate-pulse text-[#444] py-10 text-center">Loading...</div> : (
          <>
            {activeTab === "watchlist" && (
              <div className="grid grid-cols-2 sm:grid-cols-3 md:grid-cols-4 lg:grid-cols-5 gap-6">
                {watchlist.map((item) => (
                  <div key={item.tmdb_id} className="relative group">
                    <MovieCard tmdbId={item.tmdb_id} mediaType={item.media_type} title={item.title} posterPath={item.poster_path} />
                    <button onClick={(e) => { e.preventDefault(); handleRemoveFromWatchlist(item.tmdb_id); }}
                      className="absolute top-2 right-2 bg-black/70 text-[#888] hover:text-white w-6 h-6 rounded-full text-xs opacity-0 group-hover:opacity-100 transition-opacity flex items-center justify-center">&times;</button>
                  </div>
                ))}
                {watchlist.length === 0 && <p className="text-[#555] col-span-full text-center py-10 text-sm font-light">Your watchlist is empty</p>}
              </div>
            )}
            {activeTab === "history" && (
              <div className="grid grid-cols-2 sm:grid-cols-3 md:grid-cols-4 lg:grid-cols-5 gap-6">
                {history.map((item) => (
                  <div key={item.tmdb_id}><MovieCard tmdbId={item.tmdb_id} mediaType={item.media_type} title={item.title} posterPath={null} />{item.rating && <p className="text-[#888] text-xs mt-1">Rated: {item.rating}/5</p>}</div>
                ))}
                {history.length === 0 && <p className="text-[#555] col-span-full text-center py-10 text-sm font-light">No watch history yet</p>}
              </div>
            )}
            {activeTab === "searches" && (
              <div className="space-y-2">
                {searchHistory.map((item: any, index: number) => (
                  <div key={index} className="flex items-center justify-between p-3 border border-[#1a1a1a] rounded-lg">
                    <span className="text-sm text-[#a0a0a0] font-light">{item.query}</span>
                    <span className="text-[#444] text-xs">{new Date(item.searched_at).toLocaleDateString()}</span>
                  </div>
                ))}
                {searchHistory.length === 0 && <p className="text-[#555] text-center py-10 text-sm font-light">No search history yet</p>}
              </div>
            )}
          </>
        )}
      </div>
    </AuthGate>
  );
}
