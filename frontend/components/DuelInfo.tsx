import React, { useEffect, useState } from "react";
import Image from "next/image";
import GameTimer from "./GameTimer";
import { CustomUser, OpponentData } from "@/app/game-setup/layout";
import { UserStats } from "@/interfaces/UserStats";
import Picker from '@emoji-mart/react'
import data from '@emoji-mart/data'
import { useTheme } from "next-themes";
import { set } from "better-auth";
import { Socket } from "socket.io-client";


interface DuelInfoProps {
  timeRef?: React.RefObject<number>;
  opponentData?: OpponentData;
  user? : CustomUser;
  socket?: Socket;
  gameId?: string;
}

const DuelInfo = ({ timeRef, opponentData, user, socket, gameId }: DuelInfoProps) => {
  // // Mock data - replace with real props/state
  // const opponentData = {
  //   username: "CodeNinja42",
  //   avatar:
  //     "data:image/svg+xml;base64,PHN2ZyB3aWR0aD0iNjQiIGhlaWdodD0iNjQiIHZpZXdCb3g9IjAgMCA2NCA2NCIgZmlsbD0ibm9uZSIgeG1sbnM9Imh0dHA6Ly93d3cudzMub3JnLzIwMDAvc3ZnIj4KPHJlY3Qgd2lkdGg9IjY0IiBoZWlnaHQ9IjY0IiByeD0iMzIiIGZpbGw9IiNGM0Y0RjYiLz4KPHRleHQgeD0iNTAlIiB5PSI1MCUiIGZvbnQtZmFtaWx5PSJBcmlhbCwgc2Fucy1zZXJpZiIgZm9udC1zaXplPSIyNCIgZmlsbD0iIzM3NDE1MSIgdGV4dC1hbmNob3I9Im1pZGRsZSIgZG9taW5hbnQtYmFzZWxpbmU9ImNlbnRyYWwiPvCfpJY8L3RleHQ+Cjwvc3ZnPgo=", // Robot emoji as avatar
  //   status: "typing", // typing, running, idle, submitted
  //   timesRan: 3,
  //   timeElapsed: "04:23",
  //   wins: 127,
  // };

  console.log("opponentData " + opponentData?.image_url)
  console.log ("user " + user?.image)
  const { theme} = useTheme();

  const [userEmoji, setUserEmoji] = React.useState<string | null>(null);
  const [opponentEmoji, setOpponentEmoji] = React.useState<string | null>(null);
  const [opponentKey, setOpponentKey] = useState(0);
  const [userKey, setUserKey] = useState(0);
  const [showPicker, setShowPicker] = useState(false);

  const getStatusColor = (status: string) => {
    switch (status) {
      case "typing":
        return "bg-success";
      case "running":
        return "bg-accent";
      case "submitted":
        return "bg-accent";
      case "idle":
        return "bg-foreground/40";
      default:
        return "bg-foreground/40";
    }
  };

  const getStatusText = (status: string) => {
    switch (status) {
      case "typing":
        return "Typing...";
      case "running":
        return "Running code";
      case "submitted":
        return "Submitted!";
      case "idle":
        return "Thinking";
      default:
        return "Offline";
    }
  };

  useEffect(() => {
    if(socket == null) return;

    socket.on("emoji_received", async (data: {emoji: string }) => {
      console.log("Received emoji update:", data);
      setOpponentEmoji(data.emoji);
      setOpponentKey(prev => prev + 1); // Force re-render to trigger animation
    });
    
  }, [socket])

  const onUserEmojiSelect = async (emoji: any) => {
    console.log("Selected emoji:", emoji);
    setUserEmoji(emoji);
    setUserKey(prev => prev + 1); // Force re-render to trigger animation

    console.log("player1: " + user?.id)

    const response = await fetch(
    `${process.env.NEXT_PUBLIC_API_BASE_URL}/${gameId}/send-emoji`,
    {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
      },
      body: JSON.stringify({
        emoji: emoji,
        player1: user?.id
      }),
    })
    // Optionally, you can also set opponent emoji here if needed
    // setOpponentEmoji(emoji.native);
  }
  

  return (
    <div className="w-full ">
      {/* Timer */}
      {timeRef && (
        <div className="mb-4 text-center">
          <GameTimer timeRef={timeRef} />
        </div>
      )}
      
      {/* Opponent Avatar */}
      <div className="flex items-start justify-center gap-8 mb-4">
        <div className="flex flex-col gap-2">
          <div className="flex justify-center mb-3">
            <div className="relative w-[120px] h-30">
              <Image
                src={opponentData?.image_url || "/images/default-avatar.png"}
                alt={`${opponentData?.name} avatar`}
                fill
                className="object-cover w-full border-2 border-gray-100 rounded-full"
              />
              {/* Status indicator dot
              <div
                className={`absolute -bottom-1 -right-1 w-4 h-4 rounded-full border-2 border-white ${getStatusColor(
                  opponentData.status
                )}`}
              >
                {opponentData.status === "typing" && (
                  <div className="w-full h-full rounded-full animate-pulse bg-success"></div>
                )}
              </div> */}
              {/* Speech bubble positioned absolutely */}
              <div className="absolute top-0 w-auto h-auto ml-3 right-full">
                <div key={opponentKey} className="relative flex items-center justify-center w-[50px] h-[50px] text-3xl rounded-lg bg-foreground/10  animate-bounce-scale">
                  {opponentEmoji}
                  {/* Speech bubble tail pointing left */}
                  <div className="absolute transform -translate-y-1/2 right-full top-1/2">
                    <div className="w-0 h-0 border-t-4 border-b-4 border-l-8 border-transparent border-l-gray-100"></div>
                  </div>
                </div>
              </div>
            </div>
          </div>

          {/* Username */}
          <div className="mb-4 text-center">
            <p className="font-semibold text-foreground">{opponentData?.name}</p>
          </div>
        </div>
        
        {/*user avatar */}
        <div className="flex flex-col gap-2">
          <div className="flex justify-center mb-3">
            <div className="relative w-[120px] h-30">
              <Image
                src={user?.image || "/images/default-avatar.png"}
                alt={`${user?.name} avatar`}
                fill
                className="object-cover w-full border-2 border-gray-100 rounded-full cursor-pointer"
                onClick={() => setShowPicker(!showPicker)}
              /> 
              {/* Status indicator dot
              <div
                className={`absolute -bottom-1 -right-1 w-4 h-4 rounded-full border-2 border-white ${getStatusColor(
                  opponentData.status
                )}`}
              >
                {opponentData.status === "typing" && (
                  <div className="w-full h-full rounded-full animate-pulse bg-success"></div>
                )}
              </div> */}
              {/* Speech bubble positioned absolutely */}
              <div className="absolute top-0 w-auto h-auto ml-3 left-full">
                <div 
                  key={userKey} 
                  className="relative flex items-center justify-center w-[50px] h-[50px] text-3xl rounded-lg bg-foreground/10 animate-bounce-scale cursor-pointer"
                  onClick={() => setShowPicker(!showPicker)}
                >
                  {userEmoji}
                  {/* Speech bubble tail pointing left */}
                  {!showPicker ? (
                    <div className="absolute transform -translate-y-1/2 right-full top-1/2">
                      <div className="w-0 h-0 border-t-4 border-b-4 border-l-8 border-transparent border-l-gray-100"></div>
                    </div>
                  ) : 
                    <div className="absolute transform -translate-y-1/2 right-full top-1/2">
                      <div className="w-0 h-0 border-t-4 border-b-4 border-r-8 border-transparent border-r-gray-100"></div>
                    </div>
                  }
                </div>
              </div>
              {showPicker &&
                <span className="absolute right-0 w-auto h-auto ml-3">
                  <Picker 
                    data={data} 
                    onEmojiSelect={(emoji : any) => {onUserEmojiSelect(emoji.native)}} 
                    theme={theme}
                  />
                </span>
              }
            </div>
          </div>

          {/* Username */}
          <div className="mb-4 text-center">
            <p className="font-semibold text-foreground">{user?.name}</p>
          </div>
        </div>

      </div>

      {/* Stats */}
      {/* <div className="space-y-3"> */}
        {/* Status */}
        {/* <div className="flex items-center justify-center">
          <span className="text-sm text-foreground/60">Status: </span>
          <div className="flex items-center gap-2">
            <span className="text-sm font-medium">
              {getStatusText(opponentData.status)}
            </span>
          </div>
        </div> */}

        {/* Time */}
        {/* <div className="flex items-center justify-center">
          <span className="text-sm text-foreground/60">Time: </span>
          <span className="font-mono text-sm font-medium">
            {opponentData.timeElapsed}
          </span>
        </div> */}

        {/* Runs */}
        {/* <div className="flex items-center justify-center">
          <span className="text-sm text-foreground/60">Code Runs: </span>
          <span className="text-sm font-medium">{opponentData.timesRan}</span>
        </div> */}

        {/* User Info */}
        {/* <div className="flex items-center justify-center">
          <span className="text-sm text-foreground/60">W&apos;s: </span>
          <span className="text-sm font-medium">{opponentData.wins}</span>
        </div>
      </div> */}

      {/* Opponent Code Preview */}
      <div className="pt-4 mt-4 border-t">
        <h4 className="mb-2 text-sm font-semibold text-foreground/70">
          Opponent&apos;s Code (30s delay)
        </h4>
        <div className="p-3 overflow-y-auto font-mono text-xs rounded-md bg-foreground/5 text-success h-80">
          <div className="text-foreground/50"># Python starter code</div>
          <div className="text-accent">def</div>{" "}
          <div className="inline text-accent">two_sum</div>
          <div className="inline text-foreground">(nums, target):</div>
          <div className="ml-4 text-foreground/50"># Your solution here</div>
          <div className="ml-4 text-accent">pass</div>
        </div>
      </div>

    </div>
  );
};

export default DuelInfo;
