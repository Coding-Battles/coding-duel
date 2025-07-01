"use client";
import Link from "next/link";
import GameSetup from "@/components/ProfileCreatorCard";

export default function HomePage() {

  return (
    <>
      <div className="min-h-screen bg-gray-950 text-white">
        {/* Profile Creator Section */}
        {/* Hello Claude */}
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
