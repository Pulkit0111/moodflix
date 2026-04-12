"use client";
import { useState, useRef, useEffect } from "react";

interface SmartFilterProps {
  onFilter: (filterText: string) => void;
}

const SUGGESTIONS = [
  "under 2 hours",
  "feel-good ending",
  "good for a first date",
  "something my parents would enjoy",
  "won't make me cry",
];

export default function SmartFilter({ onFilter }: SmartFilterProps) {
  const [text, setText] = useState("");
  const onFilterRef = useRef(onFilter);
  onFilterRef.current = onFilter;
  const isFirstRender = useRef(true);

  useEffect(() => {
    // Skip firing on mount with empty text
    if (isFirstRender.current) {
      isFirstRender.current = false;
      return;
    }
    const timeout = setTimeout(() => {
      onFilterRef.current(text);
    }, 600);
    return () => clearTimeout(timeout);
  }, [text]);

  return (
    <div className="mb-6">
      <input
        type="text"
        value={text}
        onChange={(e) => setText(e.target.value)}
        placeholder="Refine: under 2 hours, feel-good ending, good for a date..."
        className="w-full bg-transparent border-b border-[#1a1a1a] focus:border-[#333] text-sm text-white placeholder-[#444] py-2 outline-none transition-colors font-light"
      />
      {!text && (
        <div className="flex gap-2 mt-2 flex-wrap">
          {SUGGESTIONS.map((s) => (
            <button key={s} onClick={() => setText(s)} className="text-[10px] text-[#555] border border-[#1a1a1a] px-2.5 py-1 rounded-full hover:border-[#333] hover:text-[#888] transition-all">
              {s}
            </button>
          ))}
        </div>
      )}
    </div>
  );
}
