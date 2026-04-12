"use client";
import { useAuth } from "@/hooks/useAuth";
import { signInWithGoogle } from "@/lib/firebase";

interface AuthGateProps { children: React.ReactNode; fallback?: React.ReactNode; }

export default function AuthGate({ children, fallback }: AuthGateProps) {
  const { user, loading } = useAuth();
  if (loading) return <div className="flex items-center justify-center min-h-[50vh]"><div className="animate-pulse text-[#444]">Loading...</div></div>;
  if (!user) return fallback || (
    <div className="flex flex-col items-center justify-center min-h-[50vh] gap-8">
      <div className="text-center">
        <h2 className="text-2xl font-light text-white mb-3 tracking-wide">Sign in to discover</h2>
        <p className="text-[#666] text-sm font-light">Describe your mood and find your next favorite watch</p>
      </div>
      <button onClick={() => signInWithGoogle()} className="text-sm text-white border border-[#333] px-6 py-3 rounded-full hover:bg-white/5 transition-all active:scale-95">Sign in with Google</button>
    </div>
  );
  return <>{children}</>;
}
