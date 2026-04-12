"use client";
import { useState } from "react";
import { useRouter } from "next/navigation";
import { useAuth } from "@/hooks/useAuth";
import { signInWithGoogle } from "@/lib/firebase";

interface SearchBarProps { initialQuery?: string; large?: boolean; }

export default function SearchBar({ initialQuery = "", large = false }: SearchBarProps) {
  const [query, setQuery] = useState(initialQuery);
  const router = useRouter();
  const { user } = useAuth();

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!query.trim()) return;
    if (!user) { await signInWithGoogle(); return; }
    router.push(`/search?q=${encodeURIComponent(query.trim())}`);
  };

  return (
    <form onSubmit={handleSubmit} className="w-full max-w-2xl mx-auto">
      <div className="relative">
        <input type="text" value={query} onChange={(e) => setQuery(e.target.value)}
          placeholder="Describe a feeling, a scene, or what you want to watch..."
          className={`w-full bg-[#111] border border-[#222] text-white rounded-full focus:outline-none focus:border-[#444] placeholder-[#555] transition-colors ${large ? "px-8 py-5 text-lg font-light" : "px-6 py-3 text-sm"}`} />
        <button type="submit" className={`absolute right-2 top-1/2 -translate-y-1/2 bg-white text-black rounded-full font-medium transition-all hover:bg-gray-200 active:scale-95 ${large ? "px-6 py-2.5 text-sm" : "px-4 py-1.5 text-xs"}`}>Search</button>
      </div>
    </form>
  );
}
