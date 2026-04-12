"use client";
import { useState, useEffect } from "react";
import { useParams } from "next/navigation";
import MovieCard from "@/components/MovieCard";
import SkeletonCard from "@/components/SkeletonCard";
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

  if (loading) return (
    <div className="max-w-7xl mx-auto px-6 py-10">
      <div className="h-6 bg-[#161616] rounded w-48 mb-3 animate-pulse" />
      <div className="h-3 bg-[#161616] rounded w-72 mb-8 animate-pulse" />
      <div className="grid grid-cols-2 sm:grid-cols-3 md:grid-cols-4 lg:grid-cols-5 xl:grid-cols-6 gap-6">
        {Array.from({ length: 12 }).map((_, i) => <SkeletonCard key={i} />)}
      </div>
    </div>
  );

  if (!playlist) return <div className="flex items-center justify-center min-h-[50vh]"><p className="text-[#555]">Playlist not found</p></div>;

  return (
    <div className="max-w-7xl mx-auto px-6 py-10">
      <h1 className="text-2xl font-light text-white mb-2 tracking-wide">{playlist.name}</h1>
      <p className="text-sm text-[#666] font-light mb-8">{playlist.description}</p>
      {playlist.items.length > 0 ? (
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
      ) : (
        <div className="text-center py-20">
          <p className="text-[#555] text-sm font-light mb-2">No movies available for this mood yet</p>
          <p className="text-[#444] text-xs">Check back later -- new titles are added regularly</p>
        </div>
      )}
    </div>
  );
}
