"use client";
import { Suspense, useEffect, useCallback, useState, useRef } from "react";
import { useSearchParams } from "next/navigation";
import SearchBar from "@/components/SearchBar";
import SmartFilter from "@/components/SmartFilter";
import MovieCard from "@/components/MovieCard";
import AuthGate from "@/components/AuthGate";
import { useSearch } from "@/hooks/useSearch";

function SearchContent() {
  const searchParams = useSearchParams();
  const query = searchParams.get("q") || "";
  const { results, loading, error, performSearch } = useSearch();
  const [filterText, setFilterText] = useState("");

  const queryRef = useRef(query);
  queryRef.current = query;

  useEffect(() => { if (query) performSearch(query); }, [query]); // eslint-disable-line react-hooks/exhaustive-deps

  const handleFilter = useCallback((text: string) => {
    setFilterText(text);
    if (queryRef.current) performSearch(queryRef.current, text);
  }, [performSearch]);

  return (
    <AuthGate>
      <div className="max-w-7xl mx-auto px-6 py-10">
        <div className="mb-6"><SearchBar initialQuery={query} /></div>
        <SmartFilter onFilter={handleFilter} />
        {loading && (
          <div className="flex flex-col items-center justify-center py-20">
            <div className="animate-pulse text-[#555] mb-2">Searching for your vibe...</div>
            <p className="text-[#444] text-xs">Analyzing mood and finding matches</p>
          </div>
        )}
        {error && <div className="text-center py-20"><p className="text-[#666]">{error}</p></div>}
        {!loading && !error && results.length > 0 && (
          <>
            <p className="text-label mb-6">FOUND {results.length} MATCHES FOR &ldquo;{query}&rdquo;</p>
            <div className="grid grid-cols-2 sm:grid-cols-3 md:grid-cols-4 lg:grid-cols-5 gap-6">
              {results.map((r) => (
                <MovieCard key={`${r.media_type}-${r.tmdb_id}`} tmdbId={r.tmdb_id} mediaType={r.media_type} title={r.title}
                  posterPath={r.poster_path} voteAverage={r.vote_average} releaseYear={r.release_year}
                  matchReason={r.match_reason} moodTags={r.mood_tags} />
              ))}
            </div>
          </>
        )}
        {!loading && !error && query && results.length === 0 && (
          <div className="text-center py-20"><p className="text-[#555] font-light">No matches found. Try describing your mood differently.</p></div>
        )}
      </div>
    </AuthGate>
  );
}

export default function SearchPage() {
  return (
    <Suspense fallback={<div className="flex items-center justify-center min-h-[50vh]"><div className="animate-pulse text-[#444]">Loading...</div></div>}>
      <SearchContent />
    </Suspense>
  );
}
