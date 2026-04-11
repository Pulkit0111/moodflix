"use client";
import { useState, useEffect } from "react";
import SearchBar from "@/components/SearchBar";
import Carousel from "@/components/Carousel";
import { getTrending, getTopRated } from "@/lib/api";

export default function Home() {
  const [trending, setTrending] = useState<any[]>([]);
  const [topMovies, setTopMovies] = useState<any[]>([]);
  const [topTV, setTopTV] = useState<any[]>([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    async function fetchData() {
      try {
        const [trendingRes, moviesRes, tvRes] = await Promise.allSettled([getTrending(), getTopRated("movie"), getTopRated("tv")]);
        if (trendingRes.status === "fulfilled") setTrending(trendingRes.value);
        if (moviesRes.status === "fulfilled") setTopMovies(moviesRes.value);
        if (tvRes.status === "fulfilled") setTopTV(tvRes.value);
      } catch (error) { console.error("Failed to fetch browse data:", error); }
      finally { setLoading(false); }
    }
    fetchData();
  }, []);

  return (
    <div className="min-h-screen">
      <section className="flex flex-col items-center justify-center px-4 py-24 bg-gradient-to-b from-gray-900 to-gray-950">
        <h1 className="text-5xl font-bold text-white mb-4 text-center">What are you in the <span className="text-red-500">mood</span> for?</h1>
        <p className="text-gray-400 text-lg mb-8 text-center max-w-xl">Describe how you feel or what you want to watch, and we will find the perfect movie or show for you.</p>
        <SearchBar large />
      </section>
      <section className="py-8">
        {loading ? (
          <div className="flex items-center justify-center py-20"><div className="animate-pulse text-gray-400 text-lg">Loading content...</div></div>
        ) : (
          <>
            <Carousel title="Trending This Week" items={trending} />
            <Carousel title="Top Rated Movies" items={topMovies} />
            <Carousel title="Top Rated TV Shows" items={topTV} />
          </>
        )}
      </section>
    </div>
  );
}
