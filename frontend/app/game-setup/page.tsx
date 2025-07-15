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
      <div className="flex items-center justify-center min-h-screen bg-background text-foreground">
        <div className="text-center">
          <div className="w-8 h-8 mx-auto mb-4 border-2 rounded-full border-primary border-t-transparent animate-spin" />
          <p className="text-foreground/70">Loading...</p>
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
    <div className="flex items-center justify-center min-h-screen bg-background text-foreground">
      <div className="container px-6 mx-auto">
        <div className="max-w-4xl mx-auto">
          <DifficultySelector
            selectedDifficulties={selectedDifficulties}
            onDifficultyChange={setSelectedDifficulties}
            onEditProfile={() => router.push("/profile")}
          />
        </div>
      </div>
    </div>
  );
}
