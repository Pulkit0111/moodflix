"use client";
import type { TasteDNA as TasteDNAType } from "@/types";

interface TasteDNAProps {
  data: TasteDNAType;
}

export default function TasteDNA({ data }: TasteDNAProps) {
  const maxMoodPct = Math.max(...data.top_moods.map((m) => m.percentage), 1);

  return (
    <div className="border border-[#1a1a1a] rounded-xl p-6 mb-8">
      <h2 className="text-label mb-6">YOUR TASTE DNA</h2>

      {/* Summary */}
      <p className="text-sm text-[#a0a0a0] font-light leading-relaxed mb-6 italic">{data.summary}</p>

      <div className="grid grid-cols-1 md:grid-cols-2 gap-8">
        {/* Top Moods */}
        <div>
          <h3 className="text-[11px] uppercase tracking-wider text-[#555] mb-3">Top Moods</h3>
          <div className="space-y-2.5">
            {data.top_moods.map((mood) => (
              <div key={mood.mood} className="flex items-center gap-3">
                <span className="text-xs text-[#888] w-24 text-right">{mood.mood}</span>
                <div className="flex-1 h-1.5 bg-[#111] rounded-full overflow-hidden">
                  <div className="h-full bg-white/20 rounded-full transition-all" style={{ width: `${(mood.percentage / maxMoodPct) * 100}%` }} />
                </div>
                <span className="text-[10px] text-[#555] w-8">{mood.percentage}%</span>
              </div>
            ))}
          </div>
        </div>

        {/* Genre Breakdown */}
        <div>
          <h3 className="text-[11px] uppercase tracking-wider text-[#555] mb-3">Genres</h3>
          <div className="flex flex-wrap gap-2">
            {data.genre_breakdown.map((g) => (
              <span key={g.genre} className="text-xs text-[#888] border border-[#222] px-3 py-1.5 rounded-full">
                {g.genre} <span className="text-[#555]">{g.count}</span>
              </span>
            ))}
          </div>
        </div>

        {/* Preferred Eras */}
        <div>
          <h3 className="text-[11px] uppercase tracking-wider text-[#555] mb-3">Preferred Eras</h3>
          <div className="flex gap-2 flex-wrap">
            {data.preferred_eras.map((era) => (
              <span key={era.era} className="text-xs text-[#888] border border-[#222] px-3 py-1.5 rounded-full">
                {era.era} <span className="text-[#555]">{era.count}</span>
              </span>
            ))}
          </div>
        </div>

        {/* Director Affinities */}
        {data.director_affinities.length > 0 && (
          <div>
            <h3 className="text-[11px] uppercase tracking-wider text-[#555] mb-3">Directors You Love</h3>
            <div className="flex gap-2 flex-wrap">
              {data.director_affinities.map((name) => (
                <span key={name} className="text-xs text-[#a0a0a0]">{name}</span>
              ))}
            </div>
          </div>
        )}
      </div>
    </div>
  );
}
