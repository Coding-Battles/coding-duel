"use client";

import { useSession, getAvatarUrl } from "@/lib/auth-client";
import { useRouter, usePathname } from "next/navigation";
import { createContext, useContext, useEffect, useRef, useState } from "react";
import { io, Socket } from "socket.io-client";
import { User } from "better-auth";
import { DifficultyState } from "@/components/DifficultySelector";
import { CustomUser, OpponentData, GameContextType, MatchFoundResponse, QueueStatusResponse } from "@/shared/types";

const GameContext = createContext<GameContextType | null>(null);

const debugPage = true;

export default function QueueLayout({
  children,
}: Readonly<{
  children: React.ReactNode;
}>) {
  const socketRef = useRef<Socket | null>(null);


  const [loadingState, setLoadingState] = useState<boolean>(true);

  const { data: session } = useSession();
  const sessionRef = useRef(session);
  const router = useRouter();
  const pathname = usePathname();
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
  const [gameDifficulty, setGameDifficulty] = useState<string>("easy"); // match found difficulty'
  const [playerLp, setPlayerLp] = useState<number>(0); // Player LP for the current game
  
  const [selectedDifficulties, setSelectedDifficulties] =
    useState<DifficultyState>({
      easy: true,
      medium: false,
      hard: false,
    });

  // Custom setters that persist to sessionStorage
  const setOpponentDataPersistent = (data: OpponentData) => {
    setOpponentData(data);
    console.log("Setting opponent data:", data);
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

    socket.on("connection_displaced", (data) => {
      console.log("Connection displaced:", data);
      alert("Your connection has been replaced by a new tab/window. Please refresh this page to reconnect.");
      setLoadingState(true);
    });

    socket.on("connect_error", (error) => {
      console.error("Connection error:", error);
      setLoadingState(true);
    });

    socket.on("remove_duplicate", (data) => {
      console.log("Duplicate player removed:", data);
      alert("You have been removed from the queue due to a duplicate connection. Please refresh the page.");
      clearGameData();
      setLoadingState(true);
    });

    socket.on("queue_status", (data) => {
      console.log("Queue status:", data);
    });

    socket.on("match_found", (data: MatchFoundResponse) => {
      console.log("Match found!", data);
      
      // Set opponent data immediately so users can see the opponent avatar
      setOpponentDataPersistent({
        name: (data as any).opponent_Name || data.opponent_name,
        image_url: (data as any).opponentImageURL || data.opponent_image_url || "",
        playerLp: (data as any).opponent_lp || 0,
      });

      setGameIdPersistent(data.game_id);

      setGameDifficulty(data.difficulty || "easy"); // Set match difficulty

      console.log("match found session: ", session);

      console.log("session.user: ", session?.user);

      switch (data.difficulty) {
        case "easy":
          setPlayerLp((sessionRef.current?.user as CustomUser).easylp || 0);
          console.log("Setting player LP for easy difficulty:", (sessionRef.current?.user as CustomUser).easylp || 0);
          break;
        case "medium":
          setPlayerLp((sessionRef.current?.user as CustomUser).mediumlp || 0);
          console.log("Setting player LP for medium difficulty:", (sessionRef.current?.user as CustomUser).mediumlp || 0);
          break;
        case "hard":
          setPlayerLp((sessionRef.current?.user as CustomUser).hardlp || 0);
          console.log("Setting player LP for hard difficulty:", (sessionRef.current?.user as CustomUser).hardlp || 0);
          break;
        default:
          setPlayerLp(0);
      }

      
      // Keep original 5-second delay for synchronized navigation
      setTimeout(() => {
        if(!debugPage) {
          router.push("/game-setup/queue/" + data.question_name);
        }
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
    console.log("user: ", session?.user, "isAnonymous:", currentlyAnonymous);
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

    sessionRef.current = session;
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

    // Check if user is authenticated OR is anonymous with guest profile
    const guestProfile = typeof window !== 'undefined' ? JSON.parse(localStorage.getItem('guestProfile') || 'null') : null;
    
    if (!session?.user && !isAnonymous) {
      console.error("User not authenticated and not in anonymous mode");
      router.push("/");
      return;
    }

    if (isAnonymous && !guestProfile) {
      console.error("Anonymous user but no guest profile found");
      router.push("/guestlogin");
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
    console.log("Anonymous mode:", isAnonymous, "Guest profile:", guestProfile);

    try {
      if (isAnonymous && guestProfile) {
        // Anonymous user - emit with guest data
        socketRef.current.emit("join_queue", {
          id: anonymousId,
          name: guestProfile.username,
          easy: selectedDifficulties.easy,
          medium: selectedDifficulties.medium,
          hard: selectedDifficulties.hard,
          imageURL: `/avatars/${guestProfile.selectedAvatar}.png`,
          anonymous: true,
          easyLp: 0,
          mediumLp: 0,
          hardLp: 0,
        });
      } else if (session?.user) {
        // Authenticated user - emit with session data
        socketRef.current.emit("join_queue", {
          id: session.user.id,
          name: (session.user as CustomUser)?.username || session.user.name,
          easy: selectedDifficulties.easy,
          medium: selectedDifficulties.medium,
          hard: selectedDifficulties.hard,
          imageURL: getAvatarUrl(session.user as CustomUser),
          anonymous: false,
          easyLp: (session.user as CustomUser).easylp || 0,
          mediumLp: (session.user as CustomUser).mediumlp || 0,
          hardLp: (session.user as CustomUser).hardlp || 0,
        });
      }

      // Only navigate to queue page if we're not already on the main game-setup page
      if (pathname !== "/game-setup") {
        router.push("/game-setup/queue");
      }
    } catch (error) {
      console.error("Error joining queue:", error);
      // TODO: Show user-friendly error message
    }
  };

  // Get guest user data for context
  const getContextUser = () => {
    if (session?.user) {
      return session.user as CustomUser;
    }
    
    if (isAnonymous && typeof window !== 'undefined') {
      const guestProfile = JSON.parse(localStorage.getItem('guestProfile') || 'null');
      if (guestProfile) {
        return {
          id: anonymousId,
          name: guestProfile.username,
          username: guestProfile.username,
          email: null,
          image: `/avatars/${guestProfile.selectedAvatar}.png`,
        } as CustomUser;
      }
    }
    
    return null;
  };

  return (
    <GameContext.Provider
      value={{
        socket: socketRef.current,
        user: getContextUser(),
        loading: loadingState,
        opponent: opponentData,
        gameId: gameId,
        isAnonymous: isAnonymous,
        anonymousId: anonymousId,
        selectedDifficulties: selectedDifficulties,
        setSelectedDifficulties: setSelectedDifficulties,
        handleFindGame: handleFindGame,
        clearGameData: clearGameData,
        playerLp: playerLp,
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

