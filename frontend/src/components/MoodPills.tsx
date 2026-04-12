"use client";
import { useRouter } from "next/navigation";
import { useAuth } from "@/hooks/useAuth";
import { signInWithGoogle } from "@/lib/firebase";

const MOODS = [
  { label: "Thrilling", query: "thrilling intense suspenseful edge-of-seat" },
  { label: "Cozy", query: "cozy comforting warm heartwarming gentle" },
  { label: "Nostalgic", query: "nostalgic retro classic coming-of-age memorable" },
  { label: "Mind-bending", query: "mind-bending cerebral twist plot-twist thought-provoking" },
  { label: "Feel-good", query: "feel-good happy uplifting joyful lighthearted" },
  { label: "Dark", query: "dark gritty atmospheric noir intense psychological" },
  { label: "Romantic", query: "romantic love sweet tender passionate beautiful" },
  { label: "Epic", query: "epic grand sweeping adventure ambitious heroic" },
];

export default function MoodPills() {
  const router = useRouter();
  const { user } = useAuth();

  const handleClick = async (query: string) => {
    if (!user) { await signInWithGoogle(); return; }
    router.push(`/search?q=${encodeURIComponent(query)}`);
  };

  return (
    <div className="flex flex-wrap justify-center gap-2 max-w-xl mx-auto">
      {MOODS.map((mood) => (
        <button
          key={mood.label}
          onClick={() => handleClick(mood.query)}
          className="text-xs text-[#888] border border-[#222] px-4 py-2 rounded-full hover:border-[#444] hover:text-white transition-all active:scale-95"
        >
          {mood.label}
        </button>
      ))}
    </div>
  );
}
