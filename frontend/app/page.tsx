"use client";

import React from "react";
import Link from "next/link";
import { Button } from "@/components/ui/button";
import { Card, CardContent } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { CheckCircle2 } from "lucide-react";
import { LoginDialog } from "@/components/LoginDialog";
import { useRouter } from "next/navigation";
import { signIn, useSession } from "@/lib/auth-client";

export default function HomePage() {
  const { data: session } = useSession();
  const router = useRouter();  

  // Log session data for testing
  if (session) {
    console.log("User session data:", session);
  }

  const handleSignIn = async () => {
    try {
      await signIn();
    } catch (error) {
      console.error("Sign-in error:", error);
    }
  };

  return (
    <div className="min-h-screen bg-gray-950 text-white">
      {/* Hero Section */}
      <section className="min-h-screen flex items-center justify-center relative px-6 pt-20">
        <div className="absolute inset-0 bg-gradient-to-br from-blue-500/20 via-transparent to-purple-600/20" />
        <div className="container mx-auto max-w-6xl relative">
          <div className="text-center space-y-8">
            <div className="space-y-4">
              <h1 className="text-5xl md:text-7xl font-bold leading-tight">
                Code Fast.
                <br />
                <span className="bg-gradient-to-r from-blue-500 to-purple-600 bg-clip-text text-transparent">
                  Win Faster.
                </span>
              </h1>
              <p className="text-xl md:text-2xl text-gray-400 max-w-3xl mx-auto">
                Real-time competitive coding battles. Race against opponents to
                solve algorithm challenges and climb the leaderboard.
              </p>
            </div>

            <div className="flex flex-col sm:flex-row gap-4 justify-center pt-8">
              <Button
                size="lg"
                className="bg-white text-black text-lg px-8 py-6 hover:bg-gray-400"
                onClick={() => router.push("/Queue")}
              >
                Start Playing Free
              </Button>

              {!session && (
                <Button
                  onClick={handleSignIn}
                  size="lg"
                  className="bg-white text-black text-lg px-8 py-6 hover:bg-gray-400"
                >
                  Sign In with Google
                </Button>
              )}
            </div>

            <div className="flex justify-center gap-8 pt-8 text-sm text-gray-400">
              <div className="flex items-center gap-2">
                <CheckCircle2 className="w-5 h-5 text-green-500" />
                <span>No Installation</span>
              </div>
              <div className="flex items-center gap-2">
                <CheckCircle2 className="w-5 h-5 text-green-500" />
                <span>Real-time Battles</span>
              </div>
              <div className="flex items-center gap-2">
                <CheckCircle2 className="w-5 h-5 text-green-500" />
                <span>ELO Rating System</span>
              </div>
            </div>
          </div>

          {/* Animated Code Editor Preview */}
          <Card className="mt-16 bg-gray-900 border-gray-800 shadow-2xl animate-float">
            <div className="bg-gray-800 px-4 py-3 flex items-center justify-between rounded-t-lg">
              <div className="flex items-center gap-2">
                <div className="w-3 h-3 bg-red-500 rounded-full" />
                <div className="w-3 h-3 bg-yellow-500 rounded-full" />
                <div className="w-3 h-3 bg-green-500 rounded-full" />
              </div>
              <div className="flex items-center gap-4 text-sm">
                <span className="text-gray-400">
                  Time: <span className="text-white font-mono">4:32</span>
                </span>
                <Badge
                  variant="outline"
                  className="border-yellow-500 text-yellow-400"
                >
                  Opponent: Solving...
                </Badge>
              </div>
            </div>
            <CardContent className="p-6 font-mono text-sm">
              <div className="text-gray-400 mb-2">{/* Two Sum Problem */}</div>
              <div className="text-blue-400">
                function <span className="text-yellow-300">twoSum</span>(
                <span className="text-orange-300">nums</span>,{" "}
                <span className="text-orange-300">target</span>) {`{`}
              </div>
              <div className="ml-4 text-purple-400">
                const <span className="text-white">map</span> ={" "}
                <span className="text-blue-400">new</span>{" "}
                <span className="text-yellow-300">Map</span>();
              </div>
              <div className="ml-4 text-purple-400">
                for (<span className="text-blue-400">let</span> i ={" "}
                <span className="text-green-400">0</span>; i {"<"} nums.length;
                i++) {`{`}
              </div>
              <div className="ml-8 text-white">...</div>
              <div className="text-blue-400">{`}`}</div>
            </CardContent>
          </Card>
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
  );
}
