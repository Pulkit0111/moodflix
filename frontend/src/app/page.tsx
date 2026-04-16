"use client";
import { useState, useEffect } from "react";
import SearchBar from "@/components/SearchBar";
import MoodPills from "@/components/MoodPills";
import Carousel from "@/components/Carousel";
import PlaylistCard from "@/components/PlaylistCard";
import SkeletonCard from "@/components/SkeletonCard";
import { getTrending, getTopRated, getPlaylists } from "@/lib/api";
import { useChat } from "@/contexts/ChatContext";
import type { MoodPlaylist } from "@/types";

export default function Home() {
  const [trending, setTrending] = useState<any[]>([]);
  const [topMovies, setTopMovies] = useState<any[]>([]);
  const [topTV, setTopTV] = useState<any[]>([]);
  const [playlists, setPlaylists] = useState<MoodPlaylist[]>([]);
  const [loading, setLoading] = useState(true);
  const { openChat } = useChat();

  useEffect(() => {
    async function fetchData() {
      try {
        const [trendingRes, moviesRes, tvRes, playlistRes] = await Promise.allSettled([
          getTrending(), getTopRated("movie"), getTopRated("tv"), getPlaylists(),
        ]);
        if (trendingRes.status === "fulfilled") setTrending(trendingRes.value);
        if (moviesRes.status === "fulfilled") setTopMovies(moviesRes.value);
        if (tvRes.status === "fulfilled") setTopTV(tvRes.value);
        if (playlistRes.status === "fulfilled") setPlaylists(playlistRes.value);
      } catch (error) { console.error("Failed to fetch browse data:", error); }
      finally { setLoading(false); }
    }
    fetchData();
  }, []);

  return (
    <div className="min-h-screen">
      {/* Hero */}
      <section className="flex flex-col items-center justify-center px-6 pt-28 pb-16">
        <h1 className="text-4xl md:text-5xl font-extralight text-white mb-3 text-center tracking-wide">
          What are you in the mood for?
        </h1>
        <p className="text-[#555] text-sm mb-10 text-center max-w-lg font-light">
          Describe a feeling, a vibe, or what you want to watch
        </p>
        <SearchBar large />
        <div className="mt-6">
          <MoodPills />
        </div>
        <button onClick={openChat} className="mt-4 text-xs text-[#555] hover:text-[#888] transition-colors">
          or <span className="underline underline-offset-2">chat with AI matchmaker</span>
        </button>
      </section>

      {/* Content */}
      <section className="pb-12">
        {loading ? (
          <div className="py-4">
            {Array.from({ length: 3 }).map((_, s) => (
              <div key={s} className="mb-10">
                <div className="h-3 bg-[#161616] rounded w-32 mb-4 mx-6 animate-pulse" />
                <div className="flex gap-5 px-6 overflow-hidden">
                  {Array.from({ length: 15 }).map((_, i) => <SkeletonCard key={i} />)}
                </div>
              </div>
            ))}
          </div>
        ) : (
          <>
            {/* Mood Playlists */}
            {playlists.length > 0 && (
              <div className="mb-10">
                <h2 className="text-label mb-4 px-6">MOOD PLAYLISTS</h2>
                <div className="flex gap-4 overflow-x-auto scrollbar-hide px-6 pb-2" style={{ scrollbarWidth: "none" }}>
                  {playlists.map((pl) => (
                    <PlaylistCard key={pl.mood_key || pl.id} moodKey={pl.mood_key || pl.id} name={pl.name} description={pl.description} items={pl.items} />
                  ))}
                </div>
              </div>
            )}

            <Carousel title="TRENDING THIS WEEK" items={trending} />
            <Carousel title="TOP RATED MOVIES" items={topMovies} />
            <Carousel title="TOP RATED TV" items={topTV} />
          </>
        )}
      </section>
    </div>
  );
}
