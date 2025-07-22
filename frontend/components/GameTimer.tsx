import {useState } from "react";
import React, { useEffect } from "react";

export default function GameTimer({
  timeRef,
  gameStartTime,
  isGameStarted = false
}: {
  timeRef: React.RefObject<number>;
  gameStartTime?: number | null;
  isGameStarted?: boolean;
}) {
  const [time, setTime] = useState(0);
  const [milliseconds, setMilliseconds] = useState(0);
  
  useEffect(() => {
    console.log("🚀 [TIMER DEBUG] GameTimer useEffect - isGameStarted:", isGameStarted, "gameStartTime:", gameStartTime);
    if (!isGameStarted || !gameStartTime) {
      // Don't start timer until game has officially started
      console.log("🚀 [TIMER DEBUG] Timer not starting - conditions not met");
      setTime(0);
      setMilliseconds(0);
      timeRef.current = 0;
      return;
    }

    console.log("🚀 [TIMER DEBUG] Starting timer with gameStartTime:", gameStartTime);

    const interval = setInterval(() => {
      // Calculate time based on server start timestamp for synchronization
      const now = Date.now() / 1000; // Convert to seconds
      const elapsed = Math.floor(now - gameStartTime);
      timeRef.current = elapsed;
      setTime(elapsed);
    }, 1000);

    return () => clearInterval(interval);
  }, [isGameStarted, gameStartTime, timeRef]);

  // Sub-second timer for smooth updates
  useEffect(() => {
    if (!isGameStarted || !gameStartTime) {
      setMilliseconds(0);
      return;
    }

    const msInterval = setInterval(() => {
      const now = Date.now() / 1000;
      const elapsed = now - gameStartTime;
      const ms = Math.floor((elapsed % 1) * 10); // Get decimal part as 0-9
      setMilliseconds(ms);
    }, 100);

    return () => clearInterval(msInterval);
  }, [isGameStarted, gameStartTime]);

  const formatTime = (seconds: number, ms: number) => {
    const mins = Math.floor(seconds / 60);
    const secs = seconds % 60;
    return `${mins}:${secs.toString().padStart(2, '0')}.${ms}`;
  };

  return (
    <div className="text-2xl text-left text-foreground font-mono w-24 mx-auto">
      {formatTime(time, milliseconds)}
    </div>
  );
}