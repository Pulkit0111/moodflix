"use client";
import { useState, useEffect } from "react";
import { useParams } from "next/navigation";
import { getDetails, getSimilar, addToWatchlist, addToHistory, getPitch } from "@/lib/api";
import Carousel from "@/components/Carousel";
import { useAuth } from "@/hooks/useAuth";
import { useToast } from "@/contexts/ToastContext";

const IMAGE_BASE = process.env.NEXT_PUBLIC_TMDB_IMAGE_BASE || "https://image.tmdb.org/t/p";

export default function DetailPage() {
  const params = useParams();
  const mediaType = params.type as string;
  const tmdbId = parseInt(params.id as string);
  const { user } = useAuth();
  const { showToast } = useToast();
  const [detail, setDetail] = useState<any>(null);
  const [similar, setSimilar] = useState<any[]>([]);
  const [pitch, setPitch] = useState("");
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    async function fetchData() {
      try {
        const [detailRes, similarRes] = await Promise.allSettled([getDetails(mediaType, tmdbId), getSimilar(mediaType, tmdbId)]);
        if (detailRes.status === "fulfilled") setDetail(detailRes.value);
        if (similarRes.status === "fulfilled") setSimilar(similarRes.value);
      } catch (error) { console.error("Failed to fetch details:", error); }
      finally { setLoading(false); }
    }
    fetchData();
  }, [mediaType, tmdbId]);

  // Fetch pitch after detail loads (async, non-blocking)
  useEffect(() => {
    if (!user || !detail) return;
    getPitch(mediaType, tmdbId).then((res) => setPitch(res.pitch)).catch(() => {});
  }, [user, detail, mediaType, tmdbId]);

  if (loading) return (
    <div>
      <div className="h-[60vh] bg-[#0f0f0f] animate-pulse" />
      <div className="max-w-7xl mx-auto px-6 py-10 space-y-4">
        <div className="h-5 bg-[#161616] rounded w-64 animate-pulse" />
        <div className="h-3 bg-[#161616] rounded w-full max-w-xl animate-pulse" />
        <div className="h-3 bg-[#161616] rounded w-full max-w-lg animate-pulse" />
      </div>
    </div>
  );
  if (!detail) return <div className="flex items-center justify-center min-h-screen"><p className="text-[#555]">Title not found</p></div>;

  const title = detail.title || detail.name;
  const year = (detail.release_date || detail.first_air_date || "").substring(0, 4);
  const backdropUrl = detail.backdrop_path ? `${IMAGE_BASE}/original${detail.backdrop_path}` : null;
  const posterUrl = detail.poster_path ? `${IMAGE_BASE}/w500${detail.poster_path}` : null;
  const genres = (detail.genres || []).map((g: any) => g.name);
  const moodTags = detail.mood_tags || [];
  const cast = (detail.credits?.cast || []).slice(0, 10);
  const trailers = (detail.videos?.results || []).filter((v: any) => v.site === "YouTube" && v.type === "Trailer");
  const providers = detail["watch/providers"]?.results?.US?.flatrate || [];

  return (
    <div>
      {/* Hero */}
      <div className="relative h-[60vh] overflow-hidden">
        {backdropUrl && <img src={backdropUrl} alt={title} className="w-full h-full object-cover" />}
        <div className="absolute inset-0 bg-gradient-to-t from-[#0a0a0a] via-[#0a0a0a]/70 to-transparent" />
        <div className="absolute bottom-0 left-0 right-0 p-8 max-w-7xl mx-auto">
          <div className="flex gap-8 items-end">
            {posterUrl && <img src={posterUrl} alt={title} className="w-44 rounded-lg shadow-2xl hidden md:block" />}
            <div>
              <h1 className="text-3xl md:text-4xl font-light text-white mb-3 tracking-wide">{title}</h1>
              <div className="flex items-center gap-4 text-[#999] text-sm mb-3">
                {year && <span>{year}</span>}
                {detail.runtime && <span>{detail.runtime} min</span>}
                <span className="text-white font-medium">{detail.vote_average?.toFixed(1)}</span>
              </div>
              <div className="flex gap-2 flex-wrap mb-3">
                {genres.map((genre: string) => <span key={genre} className="text-[11px] text-[#888] border border-[#2a2a2a] px-3 py-1 rounded-full">{genre}</span>)}
                {moodTags.map((tag: string) => <span key={tag} className="text-[11px] text-[#666] border border-[#222] px-3 py-1 rounded-full italic">{tag}</span>)}
              </div>
              {pitch && (
                <p className="text-sm text-[#a0a0a0] font-light italic mb-4 max-w-lg">&ldquo;{pitch}&rdquo;</p>
              )}
              {user && (
                <div className="flex gap-3">
                  <button onClick={async () => { try { await addToWatchlist(tmdbId, mediaType, title, detail.poster_path); showToast("Added to watchlist"); } catch { showToast("Failed to add to watchlist"); } }} className="text-sm text-white border border-[#333] px-5 py-2 rounded-full hover:bg-white/5 transition-all active:scale-95">+ Watchlist</button>
                  <button onClick={async () => { try { await addToHistory(tmdbId, mediaType, title, detail.poster_path); showToast("Marked as watched"); } catch { showToast("Failed to mark as watched"); } }} className="text-sm text-[#888] border border-[#222] px-5 py-2 rounded-full hover:bg-white/5 transition-all active:scale-95">Watched</button>
                </div>
              )}
            </div>
          </div>
        </div>
      </div>

      {/* Content */}
      <div className="max-w-7xl mx-auto px-6 py-10">
        <section className="mb-10">
          <h2 className="text-label mb-3">OVERVIEW</h2>
          <p className="text-[#a0a0a0] text-sm leading-relaxed max-w-3xl font-light">{detail.overview}</p>
        </section>

        {providers.length > 0 && (
          <section className="mb-10">
            <h2 className="text-label mb-3">WHERE TO WATCH</h2>
            <div className="flex gap-3">{providers.map((p: any) => <span key={p.provider_name} className="text-xs text-[#888] border border-[#222] px-4 py-2 rounded-full">{p.provider_name}</span>)}</div>
          </section>
        )}

        {trailers.length > 0 && (
          <section className="mb-10">
            <h2 className="text-label mb-3">TRAILER</h2>
            <div className="aspect-video max-w-2xl"><iframe src={`https://www.youtube.com/embed/${trailers[0].key}`} title="Trailer" className="w-full h-full rounded-lg" allowFullScreen /></div>
          </section>
        )}

        {cast.length > 0 && (
          <section className="mb-10">
            <h2 className="text-label mb-3">CAST</h2>
            <div className="flex gap-5 overflow-x-auto pb-2" style={{ scrollbarWidth: "none" }}>
              {cast.map((person: any) => (
                <div key={person.name} className="flex-shrink-0 w-24 text-center">
                  {person.profile_path ? <img src={`${IMAGE_BASE}/w185${person.profile_path}`} alt={person.name} className="w-16 h-16 rounded-full mx-auto object-cover mb-2 opacity-80" /> : <div className="w-16 h-16 rounded-full mx-auto bg-[#111] mb-2" />}
                  <p className="text-white text-[11px]">{person.name}</p>
                  <p className="text-[#555] text-[10px]">{person.character}</p>
                </div>
              ))}
            </div>
          </section>
        )}

        {similar.length > 0 && <Carousel title="SIMILAR VIBES" items={similar} />}
      </div>
    </div>
  );
}
