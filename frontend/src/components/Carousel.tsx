"use client";
import { useRef } from "react";
import MovieCard from "./MovieCard";

interface CarouselProps {
  title: string;
  items: Array<{
    id?: number; tmdb_id?: number; media_type?: string; title?: string; name?: string;
    poster_path?: string | null; vote_average?: number; release_date?: string; first_air_date?: string;
    mood_tags?: string[];
  }>;
}

export default function Carousel({ title, items }: CarouselProps) {
  const scrollRef = useRef<HTMLDivElement>(null);
  const scroll = (direction: "left" | "right") => {
    if (scrollRef.current) { scrollRef.current.scrollBy({ left: direction === "left" ? -600 : 600, behavior: "smooth" }); }
  };
  if (!items.length) return null;
  return (
    <div className="mb-6">
      <h2 className="text-label mb-4 px-6">{title}</h2>
      <div className="relative group">
        <button onClick={() => scroll("left")} className="absolute left-0 top-0 bottom-12 z-30 w-10 text-[#444] hover:text-white opacity-0 group-hover:opacity-100 transition-all flex items-center justify-center text-lg">&#8249;</button>
        <div ref={scrollRef} className="flex gap-5 overflow-x-auto scrollbar-hide px-6 pt-4 pb-6" style={{ scrollbarWidth: "none", clipPath: "inset(-20px -0px -20px -0px)" }}>
          {items.map((item) => {
            const id = item.tmdb_id || item.id || 0;
            const mediaType = item.media_type || (item.title ? "movie" : "tv");
            const name = item.title || item.name || "Unknown";
            const dateStr = item.release_date || item.first_air_date || "";
            const year = dateStr ? parseInt(dateStr.substring(0, 4)) : null;
            return <MovieCard key={`${mediaType}-${id}`} tmdbId={id} mediaType={mediaType} title={name} posterPath={item.poster_path || null} voteAverage={item.vote_average} releaseYear={year} moodTags={item.mood_tags} zoomOnHover />;
          })}
        </div>
        <button onClick={() => scroll("right")} className="absolute right-0 top-0 bottom-12 z-30 w-10 text-[#444] hover:text-white opacity-0 group-hover:opacity-100 transition-all flex items-center justify-center text-lg">&#8250;</button>
      </div>
    </div>
  );
}
