"use client";
import Link from "next/link";
import { useAuth } from "@/hooks/useAuth";
import { signInWithGoogle, signOut } from "@/lib/firebase";

export default function Navbar() {
  const { user, loading } = useAuth();
  return (
    <nav className="fixed top-0 left-0 right-0 z-50 bg-black/90 backdrop-blur-sm border-b border-gray-800">
      <div className="max-w-7xl mx-auto px-4 flex items-center justify-between h-16">
        <Link href="/" className="text-2xl font-bold text-red-500">MoodFlix</Link>
        <div className="flex items-center gap-4">
          {!loading && (
            <>
              {user ? (
                <>
                  <Link href="/profile" className="text-gray-300 hover:text-white transition-colors">My Profile</Link>
                  <button onClick={() => signOut()} className="text-gray-400 hover:text-white text-sm transition-colors">Sign Out</button>
                  {user.photoURL && <img src={user.photoURL} alt={user.displayName || "User"} className="w-8 h-8 rounded-full" />}
                </>
              ) : (
                <button onClick={() => signInWithGoogle()} className="bg-red-600 hover:bg-red-700 text-white px-4 py-2 rounded-md text-sm font-medium transition-colors">Sign In with Google</button>
              )}
            </>
          )}
        </div>
      </div>
    </nav>
  );
}
