import type { Metadata } from "next";
import { Inter } from "next/font/google";
import "./globals.css";
import Navbar from "@/components/Navbar";

const inter = Inter({ subsets: ["latin"] });

export const metadata: Metadata = {
  title: "MoodFlix - Find Movies by Mood",
  description: "Describe your mood and discover movies and TV shows that match",
};

export default function RootLayout({ children }: { children: React.ReactNode }) {
  return (
    <html lang="en" className="dark">
      <body className={`${inter.className} bg-gray-950 text-white min-h-screen`}>
        <Navbar />
        <main className="pt-16">{children}</main>
      </body>
    </html>
  );
}
