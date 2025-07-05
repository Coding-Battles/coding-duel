"use client";
import { useState, useEffect } from "react";
import { useRouter } from "next/navigation";
import { useSession } from "@/lib/auth-client";
import DifficultySelector, {
  DifficultyState,
} from "@/components/DifficultySelector";
import { Button } from "@/components/ui/button";

export default function GameSetupPage() {
  const { data: session, isPending } = useSession();
  const router = useRouter();
  const [selectedDifficulties, setSelectedDifficulties] =
    useState<DifficultyState>({
      easy: true,
      medium: false,
      hard: false,
    });

  // Handle authentication redirect in useEffect to avoid render-time navigation
  useEffect(() => {
    if (!isPending && !session?.user) {
      router.push("/");
    }
  }, [session, isPending, router]);

  // Show loading state while session is being fetched
  if (isPending) {
    return (
      <div className="min-h-screen bg-gray-950 text-white flex items-center justify-center">
        <div className="text-center">
          <div className="w-8 h-8 border-2 border-primary border-t-transparent rounded-full animate-spin mx-auto mb-4" />
          <p className="text-gray-300">Loading...</p>
        </div>
      </div>
    );
  }

  // Don't render content if not authenticated (will redirect via useEffect)
  if (!session?.user) {
    return null;
  }

  const handleFindGame = () => {
    // TODO: Implement game finding logic
    console.log("Finding game with difficulties:", selectedDifficulties);
    // For now, just show an alert
    alert("Game finding functionality coming soon!");
  };

  const hasSelectedDifficulty =
    Object.values(selectedDifficulties).some(Boolean);

  return (
    <div className="min-h-screen bg-gray-950 text-white">
      <div className="container mx-auto px-6 py-20">
        <div className="text-center mb-8">
          <h1 className="text-3xl md:text-4xl font-bold mb-4">Game Setup</h1>
          <p className="text-gray-300 text-lg">
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
