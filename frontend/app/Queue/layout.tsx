"use client";

import { createContext, useContext, useEffect, useRef, useState } from "react";
import {io, Socket} from "socket.io-client";

const GameContext = createContext<GameContextType | null>(null);

type GameContextType = {
  socket: Socket | null;
  loading: boolean;
};

export default function QueueLayout({
  children,
}: Readonly<{
  children: React.ReactNode;
}>) {
  const socketRef = useRef<Socket | null>(null);

  const [loadingState, setLoadingState] = useState<boolean>(true);

  useEffect(() => {
    socketRef.current = io("http://localhost:3001");

    socketRef.current.on("connect", () => {
      console.log("Connected to the server");
      setLoadingState(false)
    })
  }, [])
  return (
    <GameContext.Provider value={{ socket: socketRef.current, loading: loadingState }}>
      <div className="flex h-[100%] w-[100%] items-center justify-center">
          {children}
      </div>
    </GameContext.Provider>
  );
}

export function useGameContext() {
  return useContext(GameContext);
}