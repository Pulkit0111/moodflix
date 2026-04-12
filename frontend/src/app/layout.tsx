import type { Metadata } from "next";
import { Inter } from "next/font/google";
import "./globals.css";
import Navbar from "@/components/Navbar";
import { ChatProvider } from "@/contexts/ChatContext";
import ChatPanel from "@/components/ChatPanel";

const inter = Inter({ subsets: ["latin"], weight: ["300", "400", "500", "600"] });

export const metadata: Metadata = {
  title: "MoodFlix - Find Movies by Mood",
  description: "Describe your mood and discover movies and TV shows that match",
};

export default function RootLayout({ children }: { children: React.ReactNode }) {
  return (
    <html lang="en" className="dark">
      <body className={`${inter.className} bg-[#0a0a0a] text-white min-h-screen antialiased`}>
        <ChatProvider>
          <Navbar />
          <main className="pt-16">{children}</main>
          <ChatPanel />
        </ChatProvider>
      </body>
    </html>
  );
}
