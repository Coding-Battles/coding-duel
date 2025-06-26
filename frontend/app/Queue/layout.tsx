"use client";

import { useSessionContext } from "@/components/SessionProvider";
import { useRouter } from "next/navigation";
import { createContext, useContext, useEffect, useRef, useState } from "react";
import { io, Socket } from "socket.io-client";

const GameContext = createContext<GameContextType | null>(null);

type GameContextType = {
  socket: Socket | null;
  loading: boolean;
  opponentName: string;
  opponentImageURL: string;
};

type MatchFoundData = {
    game_id: string
    opponentName: string
    opponentImageURL: string | null
    question_name: string
}

export default function QueueLayout({
  children,
}: Readonly<{
  children: React.ReactNode;
}>) {
  const socketRef = useRef<Socket | null>(null);

  const [loadingState, setLoadingState] = useState<boolean>(true);

  const session = useSessionContext();
  const router = useRouter();
  const [opponentName, setOpponentName] = useState<string>("");
  const [opponentImageURL, setOpponentImageURL] = useState<string | null>("");

  useEffect(() => {

    console.log('useEffect triggered, session:', session);
    console.log('session?.id:', session?.id);
    console.log('socketRef.current:', socketRef.current);
    
    if(!session?.id || (socketRef.current && socketRef.current.connected)) {
    console.log('Early return - conditions:', {
      hasSessionId: !!session?.id,
      hasSocket: !!socketRef.current,
      isConnected: socketRef.current?.connected
    });
      return;
    }

    // Disconnect existing socket if it exists but isn't connected
    if (socketRef.current && !socketRef.current.connected) {
      console.log('Cleaning up disconnected socket');
      socketRef.current.disconnect();
      socketRef.current = null;
    }

    const socket = io(process.env.NEXT_PUBLIC_API_BASE_URL, {
      transports: ['websocket'],
    });

    socketRef.current = socket;
    console.log('Connecting to server...: ', session?.id);

    socket.on('connect', () => {
      console.log('Connected to server with SID:', socket.id);
        socket.emit("join_queue", {
          name: session?.name || "Guest",
          imageURL: session?.image || "https://www.gravatar.com/avatar/00000000000000000000000000000000?d=mp&f=y",
          id: session?.id || "guest_" + Date.now(),
        });
    });

    socket.on('disconnect', () => {
      console.log('Disconnected from server');
    });

    socket.on('queue_status', (data) => {
      console.log('Queue status:', data);
    });

    socket.on('match_found', (data : MatchFoundData) => {
      console.log('Match found!', data);
      setTimeout(() => {
        setOpponentName(data.opponentName)
        setOpponentImageURL(data.opponentImageURL);
        router.push('/queue/' + data.question_name)
      }, 5000)

    });

    socket.on('error', (err) => {
      console.error('Socket error:', err);
    });

    socket.on('connect_error', (error) => {
      console.error('Connection error:', error);
      setLoadingState(true);
    });

    return () => {
      socket.disconnect();
    };
  }, [session]);

  return (
    <GameContext.Provider
      value={{ socket: socketRef.current, loading: loadingState, opponentName: opponentName, opponentImageURL: opponentImageURL ?? "" }}
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
