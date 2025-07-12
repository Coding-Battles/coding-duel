import {useState } from "react";

import React, { useEffect } from "react";

export default function GameTimer({
  timeRef
}: {
  timeRef: React.RefObject<number>;
}) {
  const [time, setTime] = useState(0);
  useEffect(() => {
    const interval = setInterval(() => {
      timeRef.current += 1; // Increment the timer by 1 second

      setTime(timeRef.current); // Update the state to trigger a re-render
    }, 1000);

    return () => clearInterval(interval); // cleanup on unmount
  }, []);
  return (
    <div className="text-xs font-bold border-2 border-foreground/30 rounded-md p-2 bg-foreground/10 text-foreground">
      Timer: {time} second{time !== 1 && "s"}
    </div>
  );
}