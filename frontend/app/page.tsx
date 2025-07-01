"use client";
import Link from "next/link";
import { useState } from "react";
import { useSession, signOut } from "@/lib/auth-client";
import GameSetup from "@/components/ProfileCreatorCard";

export default function HomePage() {
  const { data: session } = useSession();

  console.log("Session data:", session);

  return (
    <>
      {session && (
        <div className="fixed top-16 right-4 flex gap-2 z-50">
          {/* <Link
            href="/profile"
            className="p-2 bg-gray-800 text-white rounded-lg hover:bg-gray-700 transition"
          >
            <img
              src={session.user.image || "/default-avatar.png"}
              alt="User Avatar"
              className="w-8 h-8 rounded-full"
            />
          </Link> */}
          <button
            onClick={() => signOut()}
            className="px-3 py-2 bg-red-600 text-white rounded-lg hover:bg-red-700 transition text-sm"
          >
            Logout
          </button>
        </div>
      )}
      <div className="min-h-screen bg-gray-950 text-white">
        {/* Profile Creator Section */}
        <section className="min-h-screen flex items-center justify-center relative px-6 pt-20">
          <div className="absolute inset-0 bg-gradient-to-br from-blue-500/20 via-transparent to-purple-600/20" />
          <div className="container mx-auto max-w-6xl relative">
            <div className="text-center mb-12">
              <h1 className="text-4xl md:text-6xl font-bold leading-tight mb-2">
                Head-to-head algorithm fights
              </h1>
              <div className="text-lg md:text-2xl text-gray-300 font-medium">
                Touch grass later
              </div>
            </div>

            <div className="max-w-4xl mx-auto">
              <GameSetup />
            </div>
          </div>
        </section>

        {/* Footer */}
        <footer className="py-12 px-6 border-t border-gray-800">
          <div className="container mx-auto max-w-6xl">
            <div className="flex flex-col md:flex-row justify-between items-center gap-4">
              <Link href="/" className="flex items-center space-x-2">
                <div className="w-8 h-8 bg-gradient-to-br from-blue-500 to-purple-600 rounded-lg flex items-center justify-center">
                  <span className="text-white font-bold text-lg">CD</span>
                </div>
                <span className="text-xl font-bold">CodeDuel</span>
              </Link>

              <div className="flex gap-6 text-sm text-gray-400">
                {/* <Link href="/privacy" className="hover:text-white transition">
                Privacy
              </Link>
              <Link href="/terms" className="hover:text-white transition">
                Terms
              </Link>
              <Link href="/contact" className="hover:text-white transition">
                Contact
              </Link> */}
                <a
                  href="https://github.com/Andriy3333/coding-duel"
                  target="_blank"
                  rel="noopener noreferrer"
                  className="hover:text-white transition"
                >
                  GitHub
                </a>
              </div>
            </div>
          </div>
        </footer>
      </div>
    </>
  );
}
