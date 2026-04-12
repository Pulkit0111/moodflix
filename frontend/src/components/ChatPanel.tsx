"use client";
import { useState, useRef, useEffect } from "react";
import Link from "next/link";
import { useChat } from "@/contexts/ChatContext";
import { useAuth } from "@/hooks/useAuth";
import { streamChat } from "@/lib/api";
import type { ChatMessage } from "@/types";

const IMAGE_BASE = process.env.NEXT_PUBLIC_TMDB_IMAGE_BASE || "https://image.tmdb.org/t/p";

interface ParsedRec { tmdb_id: number; title: string; media_type: string; pitch: string; poster_path?: string }

function parseRecommendations(content: string): { text: string; recs: ParsedRec[] } {
  const jsonMatch = content.match(/```json\s*([\s\S]*?)```/);
  if (!jsonMatch) return { text: content, recs: [] };
  try {
    const recs = JSON.parse(jsonMatch[1]);
    const text = content.replace(/```json[\s\S]*?```/, "").trim();
    return { text, recs: Array.isArray(recs) ? recs : [] };
  } catch {
    return { text: content, recs: [] };
  }
}

export default function ChatPanel() {
  const { isOpen, closeChat } = useChat();
  const { user } = useAuth();
  const [messages, setMessages] = useState<ChatMessage[]>([]);
  const [input, setInput] = useState("");
  const [streaming, setStreaming] = useState(false);
  const scrollRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    if (scrollRef.current) scrollRef.current.scrollTop = scrollRef.current.scrollHeight;
  }, [messages, streaming]);

  const sendMessage = async () => {
    if (!input.trim() || streaming) return;
    const userMsg: ChatMessage = { role: "user", content: input.trim() };
    const newMessages = [...messages, userMsg];
    setMessages(newMessages);
    setInput("");
    setStreaming(true);

    try {
      const reader = await streamChat(newMessages);
      let assistantContent = "";
      setMessages([...newMessages, { role: "assistant", content: "" }]);

      while (true) {
        const { done, value } = await reader.read();
        if (done) break;
        const text = new TextDecoder().decode(value);
        const lines = text.split("\n");
        for (const line of lines) {
          if (line.startsWith("data: ")) {
            const data = line.slice(6);
            if (data === "[DONE]") break;
            assistantContent += data;
            setMessages([...newMessages, { role: "assistant", content: assistantContent }]);
          }
        }
      }
    } catch (e) {
      console.error("Chat error:", e);
      setMessages([...newMessages, { role: "assistant", content: "Sorry, something went wrong. Please try again." }]);
    }
    setStreaming(false);
  };

  if (!isOpen || !user) return null;

  return (
    <>
      {/* Backdrop */}
      <div className="fixed inset-0 bg-black/40 z-40" onClick={closeChat} />

      {/* Panel */}
      <div className="fixed right-0 top-0 bottom-0 w-full sm:w-[420px] bg-[#0a0a0a] border-l border-[#1a1a1a] z-50 flex flex-col animate-slide-in">
        {/* Header */}
        <div className="flex items-center justify-between px-5 py-4 border-b border-[#1a1a1a]">
          <span className="text-label">AI MATCHMAKER</span>
          <button onClick={closeChat} className="text-[#555] hover:text-white transition-colors text-lg">&times;</button>
        </div>

        {/* Messages */}
        <div ref={scrollRef} className="flex-1 overflow-y-auto px-5 py-4 space-y-4">
          {messages.length === 0 && (
            <div className="text-center py-8">
              <div className="text-2xl mb-3">✦</div>
              <p className="text-sm text-[#888] font-light">Tell me what you&apos;re in the mood for and I&apos;ll find the perfect watch.</p>
            </div>
          )}
          {messages.map((msg, i) => {
            const isAssistant = msg.role === "assistant";
            const { text, recs } = isAssistant ? parseRecommendations(msg.content) : { text: msg.content, recs: [] };
            return (
              <div key={i} className={`flex ${isAssistant ? "" : "justify-end"}`}>
                <div className={`max-w-[85%] rounded-2xl px-4 py-3 text-sm font-light leading-relaxed ${isAssistant ? "bg-[#111] text-[#ccc]" : "bg-[#1a1a2a] text-[#ddd]"}`}>
                  <p className="whitespace-pre-wrap">{text}</p>
                  {recs.length > 0 && (
                    <div className="mt-3 space-y-2">
                      {recs.map((rec) => (
                        <Link key={rec.tmdb_id} href={`/title/${rec.media_type}/${rec.tmdb_id}`} onClick={closeChat}
                          className="flex gap-3 p-2 rounded-lg bg-[#0a0a0a] hover:bg-[#161616] transition-colors">
                          {rec.poster_path && <img src={`${IMAGE_BASE}/w92${rec.poster_path}`} alt="" className="w-10 h-14 rounded object-cover flex-shrink-0" />}
                          <div className="min-w-0">
                            <p className="text-white text-xs font-medium truncate">{rec.title}</p>
                            <p className="text-[#666] text-[10px] mt-0.5 line-clamp-2">{rec.pitch}</p>
                          </div>
                        </Link>
                      ))}
                    </div>
                  )}
                </div>
              </div>
            );
          })}
          {streaming && messages[messages.length - 1]?.role !== "assistant" && (
            <div className="flex"><div className="bg-[#111] rounded-2xl px-4 py-3 text-sm text-[#555]">Thinking...</div></div>
          )}
        </div>

        {/* Input */}
        <div className="px-5 py-4 border-t border-[#1a1a1a]">
          <form onSubmit={(e) => { e.preventDefault(); sendMessage(); }} className="flex gap-2">
            <input
              value={input}
              onChange={(e) => setInput(e.target.value)}
              placeholder="Tell me what you're in the mood for..."
              className="flex-1 bg-[#111] border border-[#1a1a1a] rounded-full px-4 py-2.5 text-sm text-white placeholder-[#444] outline-none focus:border-[#333] transition-colors font-light"
              disabled={streaming}
            />
            <button type="submit" disabled={streaming || !input.trim()}
              className="bg-white text-black rounded-full px-4 py-2.5 text-xs font-medium disabled:opacity-30 hover:bg-gray-200 transition-all active:scale-95">
              Send
            </button>
          </form>
        </div>
      </div>

      <style jsx>{`
        @keyframes slideIn { from { transform: translateX(100%); } to { transform: translateX(0); } }
        .animate-slide-in { animation: slideIn 0.2s ease-out; }
      `}</style>
    </>
  );
}
