"use client";
import { useState, useRef, useCallback } from "react";
import Link from "next/link";

interface MovieCardProps {
  tmdbId: number; mediaType: string; title: string; posterPath: string | null;
  voteAverage?: number; releaseYear?: number | null; matchReason?: string;
  moodTags?: string[]; pitch?: string; zoomOnHover?: boolean;
}

const IMAGE_BASE = process.env.NEXT_PUBLIC_TMDB_IMAGE_BASE || "https://image.tmdb.org/t/p";

function ratingColor(rating: number): string {
  if (rating >= 7.5) return "text-green-400";
  if (rating >= 6) return "text-yellow-400";
  return "text-[#999]";
}

export default function MovieCard({ tmdbId, mediaType, title, posterPath, voteAverage, releaseYear, matchReason, moodTags, pitch, zoomOnHover = false }: MovieCardProps) {
  const imageUrl = posterPath ? `${IMAGE_BASE}/w300${posterPath}` : null;
  const [zoomed, setZoomed] = useState(false);
  const timerRef = useRef<ReturnType<typeof setTimeout> | null>(null);

  const handleMouseEnter = useCallback(() => {
    if (!zoomOnHover) return;
    timerRef.current = setTimeout(() => setZoomed(true), 400);
  }, [zoomOnHover]);

  const handleMouseLeave = useCallback(() => {
    if (!zoomOnHover) return;
    if (timerRef.current) clearTimeout(timerRef.current);
    setZoomed(false);
  }, [zoomOnHover]);

  return (
    <Link
      href={`/title/${mediaType}/${tmdbId}`}
      className={`group flex-shrink-0 w-44 relative ${zoomed ? "z-20" : "z-0"}`}
      onMouseEnter={handleMouseEnter}
      onMouseLeave={handleMouseLeave}
    >
      <div className={`transition-transform duration-300 ease-out origin-center ${zoomed ? "scale-[1.15] -translate-y-3" : ""}`}>
        <div className={`relative overflow-hidden rounded-lg aspect-[2/3] bg-[#111] transition-shadow duration-300 ${zoomed ? "shadow-2xl shadow-black/80" : ""}`}>
          {imageUrl ? (
            <img src={imageUrl} alt={title} className="w-full h-full object-cover" />
          ) : (
            <div className="w-full h-full flex items-center justify-center text-[#444] text-xs p-3 text-center font-light">{title}</div>
          )}
          {/* Rating badge */}
          {voteAverage != null && voteAverage > 0 && (
            <div className="absolute top-2 right-2 bg-black/80 backdrop-blur-sm rounded-md px-1.5 py-0.5 flex items-center gap-1">
              <span className="text-yellow-400 text-[10px]">&#9733;</span>
              <span className={`text-[11px] font-semibold ${ratingColor(voteAverage)}`}>{voteAverage.toFixed(1)}</span>
            </div>
          )}
        </div>
        <div className="mt-2.5">
          <h3 className="text-white text-sm font-normal truncate group-hover:text-[#ccc] transition-colors">{title}</h3>
          <div className="flex items-center gap-2 mt-0.5">
            {releaseYear && <span className="text-[#555] text-xs">{releaseYear}</span>}
            {mediaType && <span className="text-[#444] text-[10px] uppercase">{mediaType}</span>}
          </div>
          {moodTags && moodTags.length > 0 && (
            <div className="flex gap-1 mt-1.5 flex-wrap">
              {moodTags.slice(0, 3).map((tag) => (
                <span key={tag} className="text-[10px] text-[#666] border border-[#222] px-2 py-0.5 rounded-full">{tag}</span>
              ))}
            </div>
          )}
          {(pitch || matchReason) && (
            <p className="text-[#555] text-xs mt-1.5 line-clamp-2 italic font-light">{pitch || matchReason}</p>
          )}
        </div>
      </div>
    </Link>
  );
}
