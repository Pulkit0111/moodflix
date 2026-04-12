"use client";
import Link from "next/link";

interface MovieCardProps {
  tmdbId: number; mediaType: string; title: string; posterPath: string | null;
  voteAverage?: number; releaseYear?: number | null; matchReason?: string;
}

const IMAGE_BASE = process.env.NEXT_PUBLIC_TMDB_IMAGE_BASE || "https://image.tmdb.org/t/p";

export default function MovieCard({ tmdbId, mediaType, title, posterPath, voteAverage, releaseYear, matchReason }: MovieCardProps) {
  const imageUrl = posterPath ? `${IMAGE_BASE}/w300${posterPath}` : null;
  return (
    <Link href={`/title/${mediaType}/${tmdbId}`} className="group flex-shrink-0 w-44 cursor-pointer">
      <div className="relative overflow-hidden rounded-lg aspect-[2/3] bg-gray-800">
        {imageUrl ? <img src={imageUrl} alt={title} className="w-full h-full object-cover group-hover:scale-105 transition-transform duration-300" /> : <div className="w-full h-full flex items-center justify-center text-gray-600 text-xs p-2 text-center">{title}</div>}
        <div className="absolute top-2 right-2 bg-black/70 text-yellow-400 text-xs font-bold px-2 py-1 rounded">{voteAverage?.toFixed(1) || "N/A"}</div>
        <div className="absolute top-2 left-2 bg-red-600 text-white text-xs font-bold px-2 py-1 rounded uppercase">{mediaType}</div>
      </div>
      <div className="mt-2">
        <h3 className="text-white text-sm font-medium truncate group-hover:text-red-400 transition-colors">{title}</h3>
        {releaseYear && <p className="text-gray-500 text-xs">{releaseYear}</p>}
        {matchReason && <p className="text-gray-400 text-sm mt-1 line-clamp-3">{matchReason}</p>}
      </div>
    </Link>
  );
}
