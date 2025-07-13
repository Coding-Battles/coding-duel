"use client";

import { useSession, getAvatarUrl } from "@/lib/auth-client";
import { useRouter } from "next/navigation";
import { createContext, useContext, useEffect, useRef, useState } from "react";
import { io, Socket } from "socket.io-client";
import { User } from "better-auth";
import { DifficultyState } from "@/components/DifficultySelector";

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

const GameContext = createContext<GameContextType | null>(null);

type OpponentData = {
  image_url: string;
  name: string;
};

type GameContextType = {
  socket: Socket | null;
  loading: boolean;
  opponent: OpponentData;
  user: CustomUser | null;
  gameId: string;
  isAnonymous?: boolean;
  anonymousId?: string;
  selectedDifficulties?: DifficultyState;
  setSelectedDifficulties?: React.Dispatch<React.SetStateAction<DifficultyState>>;
  handleFindGame?: () => void;

};

type MatchFoundData = {
  //data returned from backend
  game_id: string;
  opponentName: string;
  opponentImageURL: string | null;
  question_name: string;
};

export default function QueueLayout({
  children,
}: Readonly<{
  children: React.ReactNode;
}>) {
  const socketRef = useRef<Socket | null>(null);

  const [loadingState, setLoadingState] = useState<boolean>(true);

  const { data: session } = useSession();
  const router = useRouter();
  const [opponentData, setOpponentData] = useState<OpponentData>({
    image_url: "",
    name: "",
  });
  const [gameId, setGameId] = useState<string>("");
  const [anonymousId, setAnonymousId] = useState<string>("");
  const [isAnonymous, setIsAnonymous] = useState<boolean>(true); // Default to anonymous until session is loaded
  
  const [selectedDifficulties, setSelectedDifficulties] =
    useState<DifficultyState>({
      easy: true,
      medium: false,
      hard: false,
    });


  // Initialize socket connection once
  useEffect(() => {
    if (socketRef.current) {
      console.log("Socket already initialized");
      return;
    }

    console.log("=== INITIALIZING SOCKET CONNECTION ===");
    
    const socket = io(process.env.NEXT_PUBLIC_API_BASE_URL, {
      transports: ["websocket", "polling"], // Add polling fallback
      timeout: 10000, // 10 second connection timeout
      reconnection: true, // Enable auto-reconnection
      reconnectionDelay: 1000, // Wait 1s before reconnecting
      reconnectionDelayMax: 5000, // Max 5s between reconnection attempts
      reconnectionAttempts: 3, // Try 3 times then give up
      forceNew: false, // Don't force new connection
    });

    socketRef.current = socket;

    socket.on("connect", () => {
      console.log("Connected to server with SID:", socket.id);
      setLoadingState(false);
      
      // Join queue immediately when socket connects
      const currentlyAnonymous = !session?.user?.id;
      const newAnonymousId = currentlyAnonymous 
        ? "Guest-" + Math.random().toString(36).substring(2, 15) + "-" + Date.now()
        : "";
      
      if (currentlyAnonymous) {
        console.log("🔴 Setting anonymous ID on connect:", newAnonymousId);
        setAnonymousId(newAnonymousId);
        setIsAnonymous(true);
      } else {
        console.log("✅ Using session data on connect:", session);
        setIsAnonymous(false);
      }

      const username = (session?.user as CustomUser)?.username || session?.user?.name || "Guest";
      const avatarUrl = getAvatarUrl(session?.user as CustomUser);
      
      // console.log("Joining queue on connect with data:", {
      //   name: username,
      //   imageURL: avatarUrl,
      //   id: session?.user?.id || newAnonymousId,
      //   anonymous: currentlyAnonymous,
      // });

      // socket.emit("join_queue", {
      //   name: username,
      //   imageURL: avatarUrl,
      //   id: session?.user?.id || newAnonymousId,
      //   anonymous: currentlyAnonymous,
      // });
    });

    socket.on("disconnect", (reason) => {
      console.log("Disconnected from server, reason:", reason);
      setLoadingState(true);
      
      // If disconnected due to timeout, try to reconnect
      if (reason === "io client disconnect") {
        console.log("Manual disconnect, not attempting to reconnect");
      } else {
        console.log("Unexpected disconnect, will attempt to reconnect");
      }
    });

    socket.on("connect_error", (error) => {
      console.error("Connection error:", error);
      setLoadingState(true);
    });

    socket.on("queue_status", (data) => {
      console.log("Queue status:", data);
    });

    socket.on("match_found", (data: MatchFoundData) => {
      console.log("Match found!", data);
      setTimeout(() => {
        setOpponentData({
          name: data.opponentName,
          image_url: data.opponentImageURL || "",
        });
        setGameId(data.game_id);
        router.push("/game-setup/queue/" + data.question_name);
      }, 5000);
    });

    socket.on("error", (err) => {
      console.error("Socket error:", err);
    });

    // Cleanup only on component unmount
    return () => {
      console.log("Cleaning up socket connection");
      socket.disconnect();
      socketRef.current = null;
    };
  }, [router, session]); // Add router and session as dependencies

  // Handle session changes separately without reconnecting
  useEffect(() => {
    if (!socketRef.current) return;

    console.log("=== HANDLING SESSION CHANGE ===");
    console.log("Session:", session);
    
    const currentlyAnonymous = !session?.user?.id;
    setIsAnonymous(currentlyAnonymous);
    
    // Only update queue data if socket is connected and session has actually changed
    if (socketRef.current.connected) {
      const newAnonymousId = currentlyAnonymous 
        ? "Guest-" + Math.random().toString(36).substring(2, 15) + "-" + Date.now()
        : "";
      
      if (currentlyAnonymous) {
        console.log("🔴 Updating anonymous ID:", newAnonymousId);
        setAnonymousId(newAnonymousId);
      } else {
        console.log("✅ Updating session data:", session);
      }

      const username = (session?.user as CustomUser)?.username || session?.user?.name || "Guest";
      const avatarUrl = getAvatarUrl(session?.user as CustomUser);
      
      console.log("Updating queue with new session data:", {
        name: username,
        imageURL: avatarUrl,
        id: session?.user?.id || newAnonymousId,
        anonymous: currentlyAnonymous,
      });

      // // Re-join queue with updated session data
      // socketRef.current.emit("join_queue", {
      //   name: username,
      //   imageURL: avatarUrl,
      //   id: session?.user?.id || newAnonymousId,
      //   easy: 
      //   anonymous: currentlyAnonymous,
      // });
    }
  }, [session]); // Only depend on session 
  
  const handleFindGame = () => {
    if (!socketRef.current || !session?.user) {
      console.error("Socket not connected or user not authenticated");
      return;
    }

    console.log("Finding game with difficulties:", selectedDifficulties);

    // Emit join_queue event with user data (following existing pattern)
    socketRef.current.emit("join_queue", {
      id: session.user.id,
      name: (session.user as CustomUser)?.username || session.user.name,
      easy: selectedDifficulties.easy,
      medium: selectedDifficulties.medium,
      hard: selectedDifficulties.hard,
      imageURL: getAvatarUrl(session.user as CustomUser),
      anonymous: false,
      // Note: Backend may need to be updated to handle difficulty preferences
      // For now, following existing pattern that randomly selects questions
    });

    // Navigate to queue page to show waiting state
    router.push("/game-setup/queue");
  };

  return (
    <GameContext.Provider
      value={{
        socket: socketRef.current,
        user: session?.user as CustomUser || null,
        loading: loadingState,
        opponent: opponentData,
        gameId: gameId,
        isAnonymous: isAnonymous,
        anonymousId: anonymousId,
        selectedDifficulties: selectedDifficulties,
        setSelectedDifficulties: setSelectedDifficulties,
        handleFindGame: handleFindGame,
      }}
    >
      <div className="flex h-[100%] w-[100%] items-center justify-center">
        {children}
      </div>
    </GameContext.Provider>
  );
}

export function useGameContext() {
  return useContext(GameContext);
}

export type { OpponentData, CustomUser };
