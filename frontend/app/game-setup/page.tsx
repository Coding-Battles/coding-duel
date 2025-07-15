"use client";
import { useState, useEffect } from "react";
import { useRouter } from "next/navigation";
import { useSession } from "@/lib/auth-client";
import DifficultySelector from "@/components/DifficultySelector";
import { useGameContext } from "./layout";
import QueueWaitingRoom from "@/components/QueueWaitingRoom";



type QueueStatus = 'idle' | 'searching' | 'found';

export default function GameSetupPage() {
  const { data: session, isPending } = useSession();
  const router = useRouter();
  const [queueStatus, setQueueStatus] = useState<QueueStatus>('idle');

  const context = useGameContext();

  // Handle authentication redirect in useEffect to avoid render-time navigation
  useEffect(() => {
    if (!isPending && !session?.user) {
      router.push("/");
    }
  }, [session, isPending, router]);

  // Listen for queue_left confirmation from backend
  useEffect(() => {
    if (!context?.socket) return;

    const handleQueueLeft = (data: { status: string }) => {
      console.log('Queue left:', data);
      // Additional cleanup or user feedback could go here
    };

    context.socket.on('queue_left', handleQueueLeft);

    return () => {
      context.socket?.off('queue_left', handleQueueLeft);
    };
  }, [context?.socket]);



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
  
  const { selectedDifficulties, setSelectedDifficulties, handleFindGame: contextHandleFindGame } = context;

  if (!setSelectedDifficulties || !selectedDifficulties || !contextHandleFindGame) {
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

  // Local handleFindGame that updates queue status instead of navigating
  const handleFindGame = () => {
    setQueueStatus('searching');
    // Call the context handleFindGame but don't navigate
    if (contextHandleFindGame) {
      contextHandleFindGame();
    }
  };

  // Handle canceling queue and returning to difficulty selector
  const handleCancelQueue = () => {
    // Emit leave_queue to backend to properly remove user from queue
    if (context?.socket) {
      context.socket.emit('leave_queue');
    }
    setQueueStatus('idle');
  };


  return (
    <div className="flex items-center justify-center min-h-screen bg-background text-foreground">
      <div className="container px-6 mx-auto">
        <div className="max-w-4xl mx-auto">
          {queueStatus === 'idle' && (
            <DifficultySelector
              selectedDifficulties={selectedDifficulties}
              onDifficultyChange={setSelectedDifficulties}
              onEditProfile={() => router.push("/profile")}
              onFindGame={handleFindGame}
            />
          )}
          {queueStatus === 'searching' && (
            <QueueWaitingRoom onCancel={handleCancelQueue} />
          )}
        </div>
      </div>
    </div>
  );
}
