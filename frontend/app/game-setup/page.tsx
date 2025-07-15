"use client";
import { useState, useEffect, useRef } from "react";
import { useRouter } from "next/navigation";
import { useSession, getAvatarUrl } from "@/lib/auth-client";
import { io, Socket } from "socket.io-client";
import DifficultySelector, {
  DifficultyState,
} from "@/components/DifficultySelector";
import { Button } from "@/components/ui/button";

interface CustomUser {
  username?: string;
  name?: string;
  image?: string;
  id?: string;
  selectedPfp?: number;
}

// Types for socket events (following existing patterns)
interface MatchFoundResponse {
  game_id: string;
  opponent_Name: string;
  opponentImageURL?: string;
  question_name: string;
}

interface QueueStatusResponse {
  status: string;
  queue_size: number;
}

export default function GameSetupPage() {
  const { data: session, isPending } = useSession();
  const router = useRouter();
  const socket = useRef<Socket>();
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

  // Socket connection setup (following queue layout pattern)
  useEffect(() => {
    if (!session?.user) return;

    // Initialize socket connection
    socket.current = io(
      process.env.NEXT_PUBLIC_API_BASE_URL || "http://localhost:8000",
      {
        transports: ["websocket"],
      }
    );

    // Event handlers
    const handleMatchFound = (data: MatchFoundResponse) => {
      console.log("Match found:", data);
      // Navigate to queue page with question name
      router.push(`/queue/${data.question_name}`);
    };

    const handleQueueStatus = (data: QueueStatusResponse) => {
      console.log("Queue status:", data);
    };

    // Setup event listeners
    socket.current.on("match_found", handleMatchFound);
    socket.current.on("queue_status", handleQueueStatus);

    // Cleanup function
    return () => {
      if (socket.current) {
        socket.current.off("match_found", handleMatchFound);
        socket.current.off("queue_status", handleQueueStatus);
        socket.current.disconnect();
      }
    };
  }, [session?.user, router]);

  // Show loading state while session is being fetched
  if (isPending) {
    return (
      <div className="min-h-screen bg-background text-foreground flex items-center justify-center">
        <div className="text-center">
          <div className="w-8 h-8 border-2 border-primary border-t-transparent rounded-full animate-spin mx-auto mb-4" />
          <p className="text-foreground/70">Loading...</p>
        </div>
      </div>
    );
  }

  // Don't render content if not authenticated (will redirect via useEffect)
  if (!session?.user) {
    return null;
  }

  const handleFindGame = () => {
    if (!socket.current || !session?.user) {
      console.error("Socket not connected or user not authenticated");
      return;
    }

    console.log("Finding game with difficulties:", selectedDifficulties);

    // Emit join_queue event with user data (following existing pattern)
    socket.current.emit("join_queue", {
      id: session.user.id,
      name: (session.user as CustomUser)?.username || session.user.name,
      imageURL: getAvatarUrl(session.user as CustomUser),
      anonymous: false,
      // Note: Backend may need to be updated to handle difficulty preferences
      // For now, following existing pattern that randomly selects questions
    });

    // Navigate to queue page to show waiting state
    router.push("/queue");
  };

  const hasSelectedDifficulty =
    Object.values(selectedDifficulties).some(Boolean);

  return (
    <div className="min-h-screen bg-background text-foreground flex items-center justify-center">
      <div className="container mx-auto px-6">
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
