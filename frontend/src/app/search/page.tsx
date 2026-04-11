"use client";
import { useEffect } from "react";
import { useSearchParams } from "next/navigation";
import SearchBar from "@/components/SearchBar";
import MovieCard from "@/components/MovieCard";
import AuthGate from "@/components/AuthGate";
import { useSearch } from "@/hooks/useSearch";

export default function SearchPage() {
  const searchParams = useSearchParams();
  const query = searchParams.get("q") || "";
  const { results, loading, error, performSearch } = useSearch();

  useEffect(() => { if (query) performSearch(query); }, [query]);

  return (
    <AuthGate>
      <div className="max-w-7xl mx-auto px-4 py-8">
        <div className="mb-8"><SearchBar initialQuery={query} /></div>
        {loading && <div className="flex flex-col items-center justify-center py-20"><div className="animate-pulse text-xl text-gray-400 mb-2">Searching for your vibe...</div><p className="text-gray-500 text-sm">Analyzing mood and finding matches</p></div>}
        {error && <div className="text-center py-20"><p className="text-red-400">{error}</p></div>}
        {!loading && !error && results.length > 0 && (
          <>
            <p className="text-gray-400 mb-6">Found {results.length} matches for &ldquo;{query}&rdquo;</p>
            <div className="grid grid-cols-2 sm:grid-cols-3 md:grid-cols-4 lg:grid-cols-5 gap-6">
              {results.map((r) => <MovieCard key={`${r.media_type}-${r.tmdb_id}`} tmdbId={r.tmdb_id} mediaType={r.media_type} title={r.title} posterPath={r.poster_path} voteAverage={r.vote_average} releaseYear={r.release_year} matchReason={r.match_reason} />)}
            </div>
          </>
        )}
        {!loading && !error && query && results.length === 0 && <div className="text-center py-20"><p className="text-gray-400 text-lg">No matches found. Try describing your mood differently.</p></div>}
      </div>
    </AuthGate>
  );
}
