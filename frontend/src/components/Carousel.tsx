"use client";
import { useRef } from "react";
import MovieCard from "./MovieCard";

interface CarouselProps {
  title: string;
  items: Array<{
    id?: number; tmdb_id?: number; media_type?: string; title?: string; name?: string;
    poster_path?: string | null; vote_average?: number; release_date?: string; first_air_date?: string;
  }>;
}

export default function Carousel({ title, items }: CarouselProps) {
  const scrollRef = useRef<HTMLDivElement>(null);
  const scroll = (direction: "left" | "right") => {
    if (scrollRef.current) { scrollRef.current.scrollBy({ left: direction === "left" ? -600 : 600, behavior: "smooth" }); }
  };
  if (!items.length) return null;
  return (
    <div className="mb-8">
      <h2 className="text-xl font-bold text-white mb-4 px-4">{title}</h2>
      <div className="relative group">
        <button onClick={() => scroll("left")} className="absolute left-0 top-0 bottom-0 z-10 w-12 bg-black/50 text-white opacity-0 group-hover:opacity-100 transition-opacity flex items-center justify-center">&lt;</button>
        <div ref={scrollRef} className="flex gap-4 overflow-x-auto scrollbar-hide px-4 pb-2">
          {items.map((item) => {
            const id = item.tmdb_id || item.id || 0;
            const mediaType = item.media_type || (item.title ? "movie" : "tv");
            const name = item.title || item.name || "Unknown";
            const dateStr = item.release_date || item.first_air_date || "";
            const year = dateStr ? parseInt(dateStr.substring(0, 4)) : null;
            return <MovieCard key={`${mediaType}-${id}`} tmdbId={id} mediaType={mediaType} title={name} posterPath={item.poster_path || null} voteAverage={item.vote_average} releaseYear={year} />;
          })}
        </div>
        <button onClick={() => scroll("right")} className="absolute right-0 top-0 bottom-0 z-10 w-12 bg-black/50 text-white opacity-0 group-hover:opacity-100 transition-opacity flex items-center justify-center">&gt;</button>
      </div>
    </div>
  );
}
