import React, { useEffect, useState } from "react";
import GameTimer from "./GameTimer";
import { CustomUser, OpponentData } from "@/app/game-setup/layout";
import { UserStats } from "@/interfaces/UserStats";
import Picker from "@emoji-mart/react";
import data from "@emoji-mart/data";
import { useTheme } from "next-themes";
import { Socket } from "socket.io-client";
import { Prism as SyntaxHighlighter } from "react-syntax-highlighter";
import vsDark from "react-syntax-highlighter/dist/esm/styles/prism/vs-dark";
import { Language } from "@/types/languages";
import AvatarCard from "./AvatarCard";
import { getAvatarUrl } from "@/lib/auth-client";

interface DuelInfoProps {
  timeRef?: React.RefObject<number>;
  opponentData?: OpponentData;
  user?: CustomUser;
  socket?: Socket;
  gameId?: string;
  starterCode?: string;
  selectedLanguage?: Language;
}

const DuelInfo = ({
  timeRef,
  opponentData,
  user,
  socket,
  gameId,
  starterCode,
  selectedLanguage = "python",
}: DuelInfoProps) => {
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

  console.log("opponentData " + opponentData?.image_url);
  console.log("user " + user?.image);
  const { theme } = useTheme();

  // Map our language types to Prism language names for syntax highlighting
  const getPrismLanguage = (language: Language): string => {
    switch (language) {
      case "python":
        return "python";
      case "java":
        return "java";
      case "cpp":
        return "cpp";
      case "javascript":
        return "javascript";
      default:
        return "python";
    }
  };

  // Use Monaco Editor vs-dark theme with class name overrides
  const syntaxTheme = {
    ...vsDark,
    // Override class names to match Monaco (light gray, no decoration)
    "class-name": {
      color: "#d4d4d4",
      textDecoration: "none",
    },
    entity: {
      color: "#d4d4d4",
      textDecoration: "none",
    },
  };

  const [userEmoji, setUserEmoji] = React.useState<string | null>(null);
  const [opponentEmoji, setOpponentEmoji] = React.useState<string | null>(null);
  const [opponentKey, setOpponentKey] = useState(0);
  const [userKey, setUserKey] = useState(0);
  const [opponentCode, setOpponentCode] = React.useState<string | null>(null);
  const [codeAvailable, setCodeAvailable] = React.useState(false);
  const [showPicker, setShowPicker] = React.useState(false);

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
    if (socket == null || !gameId || !user?.id) return;

    socket.on("emoji_received", async (data: { emoji: string }) => {
      console.log("Received emoji update:", data);
      setOpponentEmoji(data.emoji);
      setOpponentKey((prev) => prev + 1); // Force re-render to trigger animation
    });

    socket.on(
      "opponent_code",
      (data: { code: string | null; available: boolean }) => {
        console.log("Received opponent code:", data);
        setOpponentCode(data.code);
        setCodeAvailable(data.available);
      }
    );

    // Function to fetch opponent code
    const fetchOpponentCode = () => {
      if (socket && gameId && user?.id) {
        socket.emit("get_opponent_code", {
          game_id: gameId,
          player_id: user.id,
        });
      }
    };

    // Fetch opponent code immediately and then every 5 seconds
    fetchOpponentCode();
    const interval = setInterval(fetchOpponentCode, 5000);

    // Cleanup
    return () => {
      socket.off("emoji_received");
      socket.off("opponent_code");
      clearInterval(interval);
    };
  }, [socket, gameId, user?.id]);

  const onUserEmojiSelect = async (emoji: { native: string }) => {
    console.log("Selected emoji:", emoji);
    setUserEmoji(emoji.native);
    setUserKey((prev) => prev + 1); // Force re-render to trigger animation

    console.log("player1: " + user?.id);

    await fetch(
      `${process.env.NEXT_PUBLIC_API_BASE_URL}/${gameId}/send-emoji`,
      {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify({
          emoji: emoji.native,
          player1: user?.id,
        }),
      }
    );
    // Optionally, you can also set opponent emoji here if needed
    // setOpponentEmoji(emoji.native);
  };

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
          <div className="relative flex justify-center mb-3">
            <AvatarCard
              src={opponentData?.image_url || "/images/default-avatar.png"}
              alt={`${opponentData?.name || "Opponent"} avatar`}
              name={opponentData?.name || "Opponent"}
              size="md"
              player="player2"
            />
            {/* Speech bubble positioned absolutely */}
            <div className="absolute top-0 w-auto h-auto ml-3 right-full">
              <div
                key={opponentKey}
                className="relative flex items-center justify-center w-[50px] h-[50px] text-3xl rounded-lg bg-foreground/10  animate-bounce-scale"
              >
                {opponentEmoji}
                {/* Speech bubble tail pointing left */}
                <div className="absolute transform -translate-y-1/2 right-full top-1/2">
                  <div className="w-0 h-0 border-t-4 border-b-4 border-l-8 border-transparent border-l-gray-100"></div>
                </div>
              </div>
            </div>
          </div>
        </div>

        {/*user avatar */}
        <div className="flex flex-col gap-2">
          <div className="relative flex justify-center mb-3">
            <AvatarCard
              src={getAvatarUrl(user)}
              alt={`${user?.name || "User"} avatar`}
              name={user?.name || "User"}
              size="md"
              player="player1"
              clickable={true}
              onClick={() => setShowPicker(!showPicker)}
            />
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
                ) : (
                  <div className="absolute transform -translate-y-1/2 right-full top-1/2">
                    <div className="w-0 h-0 border-t-4 border-b-4 border-r-8 border-transparent border-r-gray-100"></div>
                  </div>
                )}
              </div>
            </div>
            {showPicker && (
              <span className="absolute right-0 z-50 w-auto h-auto ml-3">
                <Picker
                  data={data}
                  onEmojiSelect={(emoji: { native: string }) => {
                    onUserEmojiSelect(emoji);
                  }}
                  theme={theme}
                />
              </span>
            )}
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
          Opponent&apos;s Code
        </h4>
        <div className="overflow-y-auto rounded-md bg-foreground/5 h-80">
          {codeAvailable && opponentCode ? (
            <SyntaxHighlighter
              language={getPrismLanguage(selectedLanguage)}
              style={syntaxTheme}
              className="!m-0 !bg-transparent"
              customStyle={{
                fontSize: "12px",
                margin: 0,
                padding: "12px",
                background: "transparent",
              }}
            >
              {opponentCode}
            </SyntaxHighlighter>
          ) : (
            <SyntaxHighlighter
              language={getPrismLanguage(selectedLanguage)}
              style={syntaxTheme}
              className="!m-0 !bg-transparent"
              customStyle={{
                fontSize: "12px",
                margin: 0,
                padding: "12px",
                background: "transparent",
                opacity: 0.7,
              }}
            >
              {starterCode || "# No code available yet"}
            </SyntaxHighlighter>
          )}
        </div>
        <div className="mt-1 text-xs text-foreground/40">
          * Code updates are delayed by 30 seconds
        </div>
      </div>
    </div>
  );
};

export default DuelInfo;
