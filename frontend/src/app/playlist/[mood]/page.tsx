"use client";
import { useState, useEffect } from "react";
import { useParams } from "next/navigation";
import MovieCard from "@/components/MovieCard";
import { getPlaylist } from "@/lib/api";
import type { MoodPlaylist } from "@/types";

export default function PlaylistPage() {
  const params = useParams();
  const moodKey = params.mood as string;
  const [playlist, setPlaylist] = useState<MoodPlaylist | null>(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    async function fetchData() {
      try {
        const data = await getPlaylist(moodKey);
        setPlaylist(data);
      } catch (e) { console.error("Failed to load playlist:", e); }
      finally { setLoading(false); }
    }
    fetchData();
  }, [moodKey]);

  if (loading) return <div className="flex items-center justify-center min-h-[50vh]"><div className="animate-pulse text-[#444]">Curating playlist...</div></div>;
  if (!playlist) return <div className="flex items-center justify-center min-h-[50vh]"><p className="text-[#555]">Playlist not found</p></div>;

  return (
    <div className="max-w-7xl mx-auto px-6 py-10">
      <h1 className="text-2xl font-light text-white mb-2 tracking-wide">{playlist.name}</h1>
      <p className="text-sm text-[#666] font-light mb-8">{playlist.description}</p>
      <div className="grid grid-cols-2 sm:grid-cols-3 md:grid-cols-4 lg:grid-cols-5 xl:grid-cols-6 gap-6">
        {playlist.items.map((item) => (
          <MovieCard
            key={`${item.media_type}-${item.tmdb_id}`}
            tmdbId={item.tmdb_id}
            mediaType={item.media_type}
            title={item.title}
            posterPath={item.poster_path}
            voteAverage={item.vote_average}
            releaseYear={item.release_year}
            moodTags={item.mood_tags}
          />
        ))}
      </div>
    </div>
  );
}
