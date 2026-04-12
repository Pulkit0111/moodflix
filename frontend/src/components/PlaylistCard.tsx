"use client";
import Link from "next/link";

const IMAGE_BASE = process.env.NEXT_PUBLIC_TMDB_IMAGE_BASE || "https://image.tmdb.org/t/p";

const MOOD_COLORS: Record<string, string> = {
  "cozy-rainy-day": "from-[#1a1a2e] to-[#16213e]",
  "adrenaline-rush": "from-[#2e1a1a] to-[#3e1621]",
  "post-breakup-comfort": "from-[#2e1a2e] to-[#211640]",
  "mind-benders": "from-[#1a2e2e] to-[#163e3e]",
  "feel-good-friday": "from-[#1a2e1a] to-[#163e21]",
  "late-night-dark": "from-[#1a1a1a] to-[#0a0a0a]",
  "nostalgic-rewind": "from-[#2e2a1a] to-[#3e3016]",
  "epic-adventures": "from-[#1a1a2e] to-[#21163e]",
  "romantic-escape": "from-[#2e1a24] to-[#3e1630]",
  "quirky-gems": "from-[#1a2e24] to-[#163e30]",
};

interface PlaylistCardProps {
  moodKey: string;
  name: string;
  description: string;
  items?: Array<{ poster_path?: string | null }>;
}

export default function PlaylistCard({ moodKey, name, description, items = [] }: PlaylistCardProps) {
  const posters = items.filter((i) => i.poster_path).slice(0, 4);
  const gradientClass = MOOD_COLORS[moodKey] || "from-[#111] to-[#1a1a1a]";
  return (
    <Link href={`/playlist/${moodKey}`} className="group flex-shrink-0 w-64 block">
      <div className={`relative h-36 rounded-lg overflow-hidden bg-gradient-to-br ${gradientClass} border border-[#1a1a1a] group-hover:border-[#2a2a2a] transition-colors`}>
        {/* Stacked poster thumbnails */}
        <div className="absolute inset-0 flex items-center justify-center gap-1 px-4 opacity-30 group-hover:opacity-50 transition-opacity">
          {posters.map((item, i) => (
            <div key={i} className="w-16 h-24 rounded overflow-hidden flex-shrink-0">
              <img src={`${IMAGE_BASE}/w92${item.poster_path}`} alt="" className="w-full h-full object-cover" />
            </div>
          ))}
        </div>
        {/* Overlay text */}
        <div className="absolute inset-0 flex flex-col justify-end p-4 bg-gradient-to-t from-[#0a0a0a] via-[#0a0a0a]/60 to-transparent">
          <h3 className="text-white text-sm font-medium mb-1">{name}</h3>
          <p className="text-[#666] text-xs font-light line-clamp-2">{description}</p>
        </div>
      </div>
    </Link>
  );
}
