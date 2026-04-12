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
          placeholder="What are you in the mood for?"
          className={`w-full bg-gray-800 border border-gray-700 text-white rounded-full focus:outline-none focus:ring-2 focus:ring-red-500 focus:border-transparent placeholder-gray-500 ${large ? "px-8 py-5 text-xl" : "px-6 py-3 text-base"}`} />
        <button type="submit" className={`absolute right-2 top-1/2 -translate-y-1/2 bg-red-600 hover:bg-red-700 active:bg-red-800 active:scale-95 text-white rounded-full font-medium transition-all ${large ? "px-6 py-3 text-lg" : "px-4 py-2 text-sm"}`}>Search</button>
      </div>
    </form>
  );
}
