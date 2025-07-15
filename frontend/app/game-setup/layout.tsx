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
  clearGameData?: () => void;

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
  const [opponentData, setOpponentData] = useState<OpponentData>(() => {
    // Restore opponent data from sessionStorage
    if (typeof window !== "undefined") {
      const saved = sessionStorage.getItem("game_opponent_data");
      return saved ? JSON.parse(saved) : { image_url: "", name: "" };
    }
    return { image_url: "", name: "" };
  });
  const [gameId, setGameId] = useState<string>(() => {
    // Restore game ID from sessionStorage
    if (typeof window !== "undefined") {
      return sessionStorage.getItem("game_id") || "";
    }
    return "";
  });
  const [anonymousId, setAnonymousId] = useState<string>("");
  const [isAnonymous, setIsAnonymous] = useState<boolean>(true); // Default to anonymous until session is loaded
  
  const [selectedDifficulties, setSelectedDifficulties] =
    useState<DifficultyState>({
      easy: true,
      medium: false,
      hard: false,
    });

  // Custom setters that persist to sessionStorage
  const setOpponentDataPersistent = (data: OpponentData) => {
    setOpponentData(data);
    if (typeof window !== "undefined") {
      sessionStorage.setItem("game_opponent_data", JSON.stringify(data));
    }
  };

  const setGameIdPersistent = (id: string) => {
    setGameId(id);
    if (typeof window !== "undefined") {
      sessionStorage.setItem("game_id", id);
    }
  };

  // Clear game data (useful for cleanup)
  const clearGameData = () => {
    setOpponentData({ image_url: "", name: "" });
    setGameId("");
    if (typeof window !== "undefined") {
      sessionStorage.removeItem("game_opponent_data");
      sessionStorage.removeItem("game_id");
    }
  };


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
        setOpponentDataPersistent({
          name: data.opponentName,
          image_url: data.opponentImageURL || "",
        });
        setGameIdPersistent(data.game_id);
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
  }, [router]); // Only depend on router

  // Handle session changes and set authentication state
  useEffect(() => {
    console.log("=== HANDLING SESSION CHANGE ===");
    console.log("Session:", session);
    
    const currentlyAnonymous = !session?.user?.id;
    setIsAnonymous(currentlyAnonymous);
    
    if (currentlyAnonymous) {
      // Generate anonymous ID only once per session
      const newAnonymousId = "Guest-" + Math.random().toString(36).substring(2, 15) + "-" + Date.now();
      console.log("🔴 Setting anonymous ID:", newAnonymousId);
      setAnonymousId(newAnonymousId);
    } else {
      console.log("✅ User authenticated:", session?.user?.name);
      setAnonymousId(""); // Clear anonymous ID when user is authenticated
    }
  }, [session]); // Only depend on session 
  
  const handleFindGame = () => {
    // Check if socket is connected
    if (!socketRef.current) {
      console.error("Socket not connected");
      // TODO: Show user-friendly error message
      return;
    }

    if (!socketRef.current.connected) {
      console.error("Socket not connected to server");
      // TODO: Show user-friendly error message
      return;
    }

    // Check if user is authenticated
    if (!session?.user) {
      console.error("User not authenticated");
      // TODO: Redirect to login or show auth error
      router.push("/");
      return;
    }

    // Check if at least one difficulty is selected
    const hasSelectedDifficulty = Object.values(selectedDifficulties).some(Boolean);
    if (!hasSelectedDifficulty) {
      console.error("No difficulty selected");
      // TODO: Show user-friendly error message
      return;
    }

    console.log("Finding game with difficulties:", selectedDifficulties);

    try {
      // Emit join_queue event with user data
      socketRef.current.emit("join_queue", {
        id: session.user.id,
        name: (session.user as CustomUser)?.username || session.user.name,
        easy: selectedDifficulties.easy,
        medium: selectedDifficulties.medium,
        hard: selectedDifficulties.hard,
        imageURL: getAvatarUrl(session.user as CustomUser),
        anonymous: false,
      });

      // Navigate to queue page to show waiting state
      router.push("/game-setup/queue");
    } catch (error) {
      console.error("Error joining queue:", error);
      // TODO: Show user-friendly error message
    }
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
        clearGameData: clearGameData,
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
