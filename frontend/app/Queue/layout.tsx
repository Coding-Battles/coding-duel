"use client";

import { useSessionContext } from "@/components/SessionProvider";
import { useRouter } from "next/navigation";
import { createContext, useContext, useEffect, useRef, useState } from "react";
import { io, Socket } from "socket.io-client";

const GameContext = createContext<GameContextType | null>(null);

type UserData = {
    image_url: string;
    name: string;
}

type GameContextType = {
  socket: Socket | null;
  loading: boolean;
  opponent: UserData;
  user: UserData
  gameId: string;
  isAnonymous?: boolean;
  anonymousId?: string;
};

type MatchFoundData = { //data returned from backend
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
  const [opponentData, setOpponentData] = useState<UserData>({image_url: "",name: ""})
  const [gameId, setGameId] = useState<string>("");
  const userDataRef = useRef<UserData>({
    name: "",
    image_url: "https://www.gravatar.com/avatar/00000000000000000000000000000000?d=mp&f=y"
  });
  const [anonymousId, setAnonymousId] = useState<string>("");
  const isAnonymous = !session?.id; // Check if session ID is not present

  useEffect(() => { //HAANDLING ALL THE SOCKET LOGIC HERE

    console.log('useEffect triggered, session:', session);
    console.log('session?.id:', session?.id);
    console.log('socketRef.current:', socketRef.current);

    
    
    if((session && !session?.id) || (socketRef.current && socketRef.current.connected)) {
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

    const newAnonymousId = "Guest-" + Math.random().toString(36).substring(2, 15) + "-" + Date.now();

    if(isAnonymous)
    {
      console.log('Setting anonymous ID:', newAnonymousId);
      setAnonymousId(newAnonymousId);
      userDataRef.current.name = newAnonymousId
    }
    else
    {
      console.log('Setting user data from session:', session);
      userDataRef.current.name = session?.name || "Guest";
      userDataRef.current.image_url = session?.image || "https://www.gravatar.com/avatar/"
    }

    socket.on('connect', () => {
      console.log('Connected to server with SID:', socket.id);
        socket.emit("join_queue", {
          name: session?.name || "Guest",
          imageURL: session?.image || "https://www.gravatar.com/avatar/00000000000000000000000000000000?d=mp&f=y",
          id: session?.id || newAnonymousId,
        });
    });

    console.log('socket joined queue with data:', {
          name: session?.name || "Guest",
          imageURL: session?.image || "https://www.gravatar.com/avatar/00000000000000000000000000000000?d=mp&f=y",
          id: session?.id || newAnonymousId,
        })

    socket.on('disconnect', () => {
      console.log('Disconnected from server');
    });

    socket.on('queue_status', (data) => {
      console.log('Queue status:', data);
    });

    socket.on('match_found', (data : MatchFoundData) => {
      console.log('Match found!', data);
      setTimeout(() => {
        setOpponentData({
          name: data.opponentName,
          image_url: data.opponentImageURL || "https://www.gravatar.com/avatar/"
        })
        setGameId(data.game_id);
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
      value={{ socket: socketRef.current, user: userDataRef.current, loading: loadingState, opponent: opponentData, gameId: gameId, isAnonymous: isAnonymous, anonymousId: anonymousId }}
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

export type {UserData}
