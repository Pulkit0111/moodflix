"use client";
import { useState } from "react";
import { search as apiSearch } from "@/lib/api";
import type { SearchResult } from "@/types";

export function useSearch() {
  const [results, setResults] = useState<SearchResult[]>([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  async function performSearch(query: string, filterText?: string) {
    if (!query.trim()) return;
    setLoading(true); setError(null);
    try { const data = await apiSearch(query, filterText); setResults(data.results); }
    catch (err) { setError(err instanceof Error ? err.message : "Search failed"); setResults([]); }
    finally { setLoading(false); }
  }
  return { results, loading, error, performSearch };
}
