"use client";
import { useAuth } from "@/hooks/useAuth";
import { signInWithGoogle } from "@/lib/firebase";

interface AuthGateProps { children: React.ReactNode; fallback?: React.ReactNode; }

export default function AuthGate({ children, fallback }: AuthGateProps) {
  const { user, loading } = useAuth();
  if (loading) return <div className="flex items-center justify-center min-h-[50vh]"><div className="animate-pulse text-gray-400">Loading...</div></div>;
  if (!user) return fallback || (
    <div className="flex flex-col items-center justify-center min-h-[50vh] gap-6">
      <div className="text-center">
        <h2 className="text-2xl font-bold text-white mb-2">Sign in to search</h2>
        <p className="text-gray-400">Describe your mood and discover your next favorite movie or show</p>
      </div>
      <button onClick={() => signInWithGoogle()} className="bg-red-600 hover:bg-red-700 text-white px-6 py-3 rounded-lg text-lg font-medium transition-colors">Sign in with Google</button>
    </div>
  );
  return <>{children}</>;
}
