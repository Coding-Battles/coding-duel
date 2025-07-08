"use client";

import { useSession, getAvatarUrl } from "@/lib/auth-client";
import { useRouter } from "next/navigation";
import { createContext, useContext, useEffect, useRef, useState } from "react";
import { io, Socket } from "socket.io-client";
import { User } from "better-auth";

interface CustomUser extends User {
  username?: string;
  selectedPfp?: number;
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

  useEffect(() => {
    //HAANDLING ALL THE SOCKET LOGIC HERE

    console.log("=== DEBUGGING SESSION DATA ===");
    console.log("useEffect triggered, session:", session);
    console.log("session?.user.id:", session?.user.id);
    console.log("session?.user.name:", session?.user.name);
    
    // Calculate isAnonymous based on current session state
    const currentlyAnonymous = !session?.user?.id;
    setIsAnonymous(currentlyAnonymous);
    console.log("isAnonymous (calculated):", currentlyAnonymous);
    console.log("socketRef.current:", socketRef.current);

    // Only return early for invalid session states
    if (session && !session?.user?.id) {
      console.log("Early return - invalid session state");
      return;
    }

    // Handle socket reconnection - socket is already connected, no need to update user data
    if (socketRef.current && socketRef.current.connected) {
      console.log("Socket already connected");
      return;
    }

    // Disconnect existing socket if it exists but isn't connected
    if (socketRef.current && !socketRef.current.connected) {
      console.log("Cleaning up disconnected socket");
      socketRef.current.disconnect();
      socketRef.current = null;
    }

    const socket = io(process.env.NEXT_PUBLIC_API_BASE_URL, {
      transports: ["websocket"],
    });

    socketRef.current = socket;
    console.log("Connecting to server...: ", session?.user?.id);

    const newAnonymousId =
      "Guest-" + Math.random().toString(36).substring(2, 15) + "-" + Date.now();

    if (currentlyAnonymous) {
      console.log("🔴 SETTING ANONYMOUS ID because currentlyAnonymous =", currentlyAnonymous);
      console.log("🔴 Anonymous ID being set:", newAnonymousId);
      setAnonymousId(newAnonymousId);
    } else {
      console.log(
        "✅ USING SESSION DATA because currentlyAnonymous =",
        currentlyAnonymous
      );
      console.log("✅ Session data being used:", session);
    }

    socket.on("connect", () => {
      console.log("Connected to server with SID:", socket.id);
      const username = (session?.user as CustomUser)?.username || session?.user?.name || "Guest";
      const avatarUrl = getAvatarUrl(session?.user as CustomUser);
      socket.emit("join_queue", {
        name: username,
        imageURL: avatarUrl,
        id: session?.user?.id || newAnonymousId,
        anonymous: currentlyAnonymous,
      });
    });

    const username = (session?.user as CustomUser)?.username || session?.user?.name || "Guest";
    const avatarUrl = getAvatarUrl(session?.user as CustomUser);
    console.log("socket joined queue with data:", {
      name: username,
      imageURL: avatarUrl,
      id: session?.user?.id || newAnonymousId,
      anonymous: currentlyAnonymous,
    });

    socket.on("disconnect", () => {
      console.log("Disconnected from server");
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
        router.push("/queue/" + data.question_name);
      }, 5000);
    });

    socket.on("error", (err) => {
      console.error("Socket error:", err);
    });

    socket.on("connect_error", (error) => {
      console.error("Connection error:", error);
      setLoadingState(true);
    });

    return () => {
      socket.disconnect();
    };
  }, [session]);

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

export type { OpponentData };
