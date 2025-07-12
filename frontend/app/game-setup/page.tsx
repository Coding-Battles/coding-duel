"use client";
import { useState, useEffect, useRef } from "react";
import { useRouter } from "next/navigation";
import { useSession, getAvatarUrl } from "@/lib/auth-client";
import { io, Socket } from "socket.io-client";
import DifficultySelector, {
  DifficultyState,
} from "@/components/DifficultySelector";
import { Button } from "@/components/ui/button";
import { useGameContext } from "./layout";



export default function GameSetupPage() {
  const { data: session, isPending } = useSession();
  const router = useRouter();

  const context = useGameContext();

  // Handle authentication redirect in useEffect to avoid render-time navigation
  useEffect(() => {
    if (!isPending && !session?.user) {
      router.push("/");
    }
  }, [session, isPending, router]);



  // Show loading state while session is being fetched
  if (isPending || !context) {
    return (
      <div className="flex items-center justify-center min-h-screen text-white bg-gray-950">
        <div className="text-center">
          <div className="w-8 h-8 mx-auto mb-4 border-2 rounded-full border-primary border-t-transparent animate-spin" />
          <p className="text-gray-300">Loading...</p>
        </div>
      </div>
    );
  }
  
  const { socket, user, selectedDifficulties, setSelectedDifficulties, handleFindGame } = context;

  if (!setSelectedDifficulties || !selectedDifficulties || !handleFindGame) {
    return (
      <div className="flex items-center justify-center min-h-screen text-white bg-gray-950">
        <div className="text-center">
          <div className="w-8 h-8 mx-auto mb-4 border-2 rounded-full border-primary border-t-transparent animate-spin" />
          <p className="text-gray-300">Loading...</p>
        </div>
      </div>
    );
  }
  

  // Don't render content if not authenticated (will redirect via useEffect)
  if (!session?.user) {
    return null;
  }


  const hasSelectedDifficulty =
    Object.values(selectedDifficulties).some(Boolean);

  return (
    <div className="min-h-screen text-white bg-gray-950">
      <div className="container px-6 py-20 mx-auto">
        <div className="mb-8 text-center">
          <h1 className="mb-4 text-3xl font-bold md:text-4xl">Game Setup</h1>
          <p className="text-lg text-gray-300">
            Choose your preferred difficulty levels
          </p>
        </div>

        <div className="max-w-4xl mx-auto">
          <DifficultySelector
            selectedDifficulties={selectedDifficulties}
            onDifficultyChange={setSelectedDifficulties}
            onEditProfile={() => router.push("/profile")}
          />

          {/* Find Game Button */}
          <div className="mt-8 text-center">
            <Button
              onClick={handleFindGame}
              disabled={!hasSelectedDifficulty}
              variant="default"
              className={`px-8 py-4 text-xl font-bold rounded-xl transition-all duration-300 uppercase tracking-wide
                         ${
                           hasSelectedDifficulty
                             ? "bg-primary text-primary-foreground hover:bg-primary/90 hover:-translate-y-1 shadow-lg shadow-primary/50"
                             : "bg-muted text-muted-foreground cursor-not-allowed"
                         }`}
            >
              {hasSelectedDifficulty ? "Find Game" : "Select Difficulty"}
            </Button>
          </div>
        </div>
      </div>
    </div>
  );
}
