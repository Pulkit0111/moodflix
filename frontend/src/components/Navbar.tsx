"use client";
import Link from "next/link";
import { useAuth } from "@/hooks/useAuth";
import { signInWithGoogle, signOut } from "@/lib/firebase";
import { useChat } from "@/contexts/ChatContext";

export default function Navbar() {
  const { user, loading } = useAuth();
  const { openChat } = useChat();
  return (
    <nav className="fixed top-0 left-0 right-0 z-50 bg-[#0a0a0a]/95 backdrop-blur-md border-b border-[#1a1a1a]">
      <div className="max-w-7xl mx-auto px-6 flex items-center justify-between h-16">
        <Link href="/" className="text-lg font-light tracking-[0.25em] text-white">MOODFLIX</Link>
        <div className="flex items-center gap-6">
          {!loading && (
            <>
              {user ? (
                <>
                  <Link href="/" className="text-sm text-[#a0a0a0] hover:text-white transition-colors">Discover</Link>
                  <Link href="/profile" className="text-sm text-[#a0a0a0] hover:text-white transition-colors">My List</Link>
                  <button onClick={openChat} className="text-sm text-white bg-gradient-to-r from-[#333] to-[#222] px-4 py-1.5 rounded-full hover:from-[#444] hover:to-[#333] transition-all border border-[#444]">&#10022; AI Chat</button>
                  <button onClick={() => signOut()} className="text-xs text-[#666] hover:text-white transition-colors">Sign Out</button>
                  {user.photoURL && <img src={user.photoURL} alt={user.displayName || "User"} className="w-7 h-7 rounded-full opacity-80 hover:opacity-100 transition-opacity" />}
                </>
              ) : (
                <button onClick={() => signInWithGoogle()} className="text-sm text-white border border-[#333] px-4 py-2 rounded-full hover:bg-white/5 transition-all active:scale-95">Sign In</button>
              )}
            </>
          )}
        </div>
      </div>
    </nav>
  );
}
