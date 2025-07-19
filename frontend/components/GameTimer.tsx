import {useState } from "react";
import React, { useEffect } from "react";

export default function GameTimer({
  timeRef
}: {
  timeRef: React.RefObject<number>;
}) {
  const [time, setTime] = useState(0);
  const [milliseconds, setMilliseconds] = useState(0);
  
  useEffect(() => {
    const interval = setInterval(() => {
      timeRef.current += 1; // Increment the timer by 1 second
      setTime(timeRef.current); // Update the state to trigger a re-render
    }, 1000);

    return () => clearInterval(interval); // cleanup on unmount
  }, []);

  // Sub-second timer for smooth updates
  useEffect(() => {
    const msInterval = setInterval(() => {
      setMilliseconds(prev => (prev + 1) % 10);
    }, 100); // Update every 100ms (0.1 seconds)

    return () => clearInterval(msInterval);
  }, []);

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