"use client";
import { useState, useEffect } from "react";
import { useParams } from "next/navigation";
import { getDetails, getSimilar, addToWatchlist, addToHistory } from "@/lib/api";
import Carousel from "@/components/Carousel";
import { useAuth } from "@/hooks/useAuth";

const IMAGE_BASE = process.env.NEXT_PUBLIC_TMDB_IMAGE_BASE || "https://image.tmdb.org/t/p";

export default function DetailPage() {
  const params = useParams();
  const mediaType = params.type as string;
  const tmdbId = parseInt(params.id as string);
  const { user } = useAuth();
  const [detail, setDetail] = useState<any>(null);
  const [similar, setSimilar] = useState<any[]>([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    async function fetchData() {
      try {
        const [detailData, similarData] = await Promise.all([getDetails(mediaType, tmdbId), getSimilar(mediaType, tmdbId).catch(() => [])]);
        setDetail(detailData);
        setSimilar(similarData);
      } catch (error) { console.error("Failed to fetch details:", error); }
      finally { setLoading(false); }
    }
    fetchData();
  }, [mediaType, tmdbId]);

  if (loading) return <div className="flex items-center justify-center min-h-screen"><div className="animate-pulse text-gray-400">Loading...</div></div>;
  if (!detail) return <div className="flex items-center justify-center min-h-screen"><p className="text-gray-400">Title not found</p></div>;

  const title = detail.title || detail.name;
  const year = (detail.release_date || detail.first_air_date || "").substring(0, 4);
  const backdropUrl = detail.backdrop_path ? `${IMAGE_BASE}/original${detail.backdrop_path}` : null;
  const posterUrl = detail.poster_path ? `${IMAGE_BASE}/w500${detail.poster_path}` : null;
  const genres = (detail.genres || []).map((g: any) => g.name);
  const cast = (detail.credits?.cast || []).slice(0, 10);
  const trailers = (detail.videos?.results || []).filter((v: any) => v.site === "YouTube" && v.type === "Trailer");
  const providers = detail["watch/providers"]?.results?.US?.flatrate || [];

  return (
    <div>
      <div className="relative h-[60vh] overflow-hidden">
        {backdropUrl && <img src={backdropUrl} alt={title} className="w-full h-full object-cover" />}
        <div className="absolute inset-0 bg-gradient-to-t from-gray-950 via-gray-950/60 to-transparent" />
        <div className="absolute bottom-0 left-0 right-0 p-8 max-w-7xl mx-auto">
          <div className="flex gap-8 items-end">
            {posterUrl && <img src={posterUrl} alt={title} className="w-48 rounded-lg shadow-2xl hidden md:block" />}
            <div>
              <h1 className="text-4xl font-bold text-white mb-2">{title}</h1>
              <div className="flex items-center gap-4 text-gray-300 mb-4">
                {year && <span>{year}</span>}
                {detail.runtime && <span>{detail.runtime} min</span>}
                <span className="text-yellow-400 font-bold">{detail.vote_average?.toFixed(1)}</span>
              </div>
              <div className="flex gap-2 flex-wrap mb-4">
                {genres.map((genre: string) => <span key={genre} className="bg-gray-800 text-gray-300 px-3 py-1 rounded-full text-sm">{genre}</span>)}
              </div>
              {user && (
                <div className="flex gap-3">
                  <button onClick={() => addToWatchlist(tmdbId, mediaType, title, detail.poster_path)} className="bg-red-600 hover:bg-red-700 text-white px-5 py-2 rounded-lg font-medium transition-colors">+ Watchlist</button>
                  <button onClick={() => addToHistory(tmdbId, mediaType, title)} className="bg-gray-700 hover:bg-gray-600 text-white px-5 py-2 rounded-lg font-medium transition-colors">Watched</button>
                </div>
              )}
            </div>
          </div>
        </div>
      </div>
      <div className="max-w-7xl mx-auto px-4 py-8">
        <section className="mb-8"><h2 className="text-xl font-bold text-white mb-3">Overview</h2><p className="text-gray-300 leading-relaxed max-w-3xl">{detail.overview}</p></section>
        {providers.length > 0 && <section className="mb-8"><h2 className="text-xl font-bold text-white mb-3">Where to Watch</h2><div className="flex gap-3">{providers.map((p: any) => <span key={p.provider_name} className="bg-gray-800 text-gray-300 px-4 py-2 rounded-lg text-sm">{p.provider_name}</span>)}</div></section>}
        {trailers.length > 0 && <section className="mb-8"><h2 className="text-xl font-bold text-white mb-3">Trailer</h2><div className="aspect-video max-w-2xl"><iframe src={`https://www.youtube.com/embed/${trailers[0].key}`} title="Trailer" className="w-full h-full rounded-lg" allowFullScreen /></div></section>}
        {cast.length > 0 && (
          <section className="mb-8"><h2 className="text-xl font-bold text-white mb-3">Cast</h2>
            <div className="flex gap-4 overflow-x-auto pb-2">
              {cast.map((person: any) => (
                <div key={person.name} className="flex-shrink-0 w-28 text-center">
                  {person.profile_path ? <img src={`${IMAGE_BASE}/w185${person.profile_path}`} alt={person.name} className="w-20 h-20 rounded-full mx-auto object-cover mb-2" /> : <div className="w-20 h-20 rounded-full mx-auto bg-gray-800 mb-2" />}
                  <p className="text-white text-xs font-medium">{person.name}</p>
                  <p className="text-gray-500 text-xs">{person.character}</p>
                </div>
              ))}
            </div>
          </section>
        )}
        {similar.length > 0 && <Carousel title="Similar Vibes" items={similar} />}
      </div>
    </div>
  );
}
