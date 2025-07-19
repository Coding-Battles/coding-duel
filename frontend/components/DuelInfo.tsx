import React, { useEffect, useState } from "react";
import GameTimer from "./GameTimer";
import { CustomUser, OpponentData } from "@/app/game-setup/layout";
import { UserStats } from "@/interfaces/UserStats";
import CustomEmojiPicker from "./CustomEmojiPicker";
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
  const [opponentEmojiQueue, setOpponentEmojiQueue] = React.useState<
    Array<{ emoji: string; timestamp: number }>
  >([]);

  useEffect(() => {
    if (socket == null || !gameId || !user?.id) {
      console.log("🚀 [CODE DEBUG] Socket effect skipped - missing:", { socket: !!socket, gameId, userId: user?.id });
      return;
    }

    console.log("🚀 [CODE DEBUG] Setting up socket listeners for gameId:", gameId);

    socket.on("emoji_received", async (data: { emoji: string }) => {
      console.log("Received emoji update:", data);
      setOpponentEmoji(data.emoji);
      setOpponentKey((prev) => prev + 1); // Force re-render to trigger animation

      // Add to emoji queue
      const newEmojiItem = { emoji: data.emoji, timestamp: Date.now() };
      setOpponentEmojiQueue((prev) => [...prev, newEmojiItem].slice(-10)); // Keep last 10

      // Auto-hide after 4 seconds
      setTimeout(() => {
        setOpponentEmoji(null);
      }, 4000);
    });

    socket.on(
      "opponent_code",
      (data: { code: string | null; available: boolean }) => {
        console.log("🚀 [CODE DEBUG] Received opponent code event:", data);
        setOpponentCode(data.code);
        setCodeAvailable(data.available);
      }
    );

    // Function to fetch opponent code
    const fetchOpponentCode = () => {
      if (socket && gameId && user?.id) {
        console.log("🚀 [CODE DEBUG] Emitting get_opponent_code:", { game_id: gameId, player_id: user.id });
        socket.emit("get_opponent_code", {
          game_id: gameId,
          player_id: user.id,
        });
      } else {
        console.log("🚀 [CODE DEBUG] Cannot fetch opponent code - missing:", { socket: !!socket, gameId, userId: user?.id });
      }
    };

    // Fetch opponent code immediately and then every 5 seconds
    console.log("🚀 [CODE DEBUG] Starting opponent code fetching...");
    fetchOpponentCode();
    const interval = setInterval(fetchOpponentCode, 5000);
    console.log("🚀 [CODE DEBUG] Set up 5-second interval for opponent code");

    // Cleanup
    return () => {
      console.log("🚀 [CODE DEBUG] Cleaning up socket listeners and interval");
      socket.off("emoji_received");
      socket.off("opponent_code");
      clearInterval(interval);
    };
  }, [socket, gameId, user?.id]);

  const onUserEmojiSelect = async (emoji: { native: string }) => {
    console.log("🚀 [EMOJI DEBUG] Selected emoji:", emoji);
    console.log("🚀 [EMOJI DEBUG] GameId:", gameId);
    console.log("🚀 [EMOJI DEBUG] User ID:", user?.id);
    console.log("🚀 [EMOJI DEBUG] Socket connected:", socket?.connected);

    setUserEmoji(emoji.native);
    setUserKey((prev) => prev + 1); // Force re-render to trigger animation

    // Auto-hide user emoji after 4 seconds
    setTimeout(() => {
      setUserEmoji(null);
    }, 4000);

    const apiUrl = `${process.env.NEXT_PUBLIC_API_BASE_URL}/api/${gameId}/send-emoji`;
    console.log("🚀 [EMOJI DEBUG] API URL:", apiUrl);
    console.log("🚀 [EMOJI DEBUG] Request body:", {
      emoji: emoji.native,
      player1: user?.id,
    });

    try {
      const response = await fetch(apiUrl, {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify({
          emoji: emoji.native,
          player1: user?.id,
        }),
      });

      console.log("🚀 [EMOJI DEBUG] Response status:", response.status);

      if (!response.ok) {
        console.error(
          "🚀 [EMOJI DEBUG] Failed to send emoji:",
          response.status,
          response.statusText
        );
        const errorText = await response.text();
        console.error("🚀 [EMOJI DEBUG] Error details:", errorText);
      } else {
        console.log("🚀 [EMOJI DEBUG] Emoji sent successfully!");
        const responseData = await response.json();
        console.log("🚀 [EMOJI DEBUG] Response data:", responseData);
      }
    } catch (error) {
      console.error("🚀 [EMOJI DEBUG] Network error:", error);
    }
  };

  return (
    <div className="w-full px-6 py-4">
      {/* Timer */}
      {timeRef && (
        <div className="text-center py-4">
          <GameTimer timeRef={timeRef} />
        </div>
      )}

      {/* Avatars: User left, Opponent right */}
      <div className="flex items-start justify-center gap-16">
        {/* User avatar (left) */}
        <div className="flex flex-col gap-2">
          <div className="flex justify-center mb-3 relative">
            <AvatarCard
              src={getAvatarUrl(user)}
              alt={`${user?.username || user?.name || "User"} avatar`}
              name={user?.username || user?.name || "User"}
              size="md"
              player="player1"
            />
            {/* Floating emoji positioned absolutely */}
            {userEmoji && (
              <div className="absolute -top-4 -left-4 z-10">
                <div
                  key={userKey}
                  className="text-5xl animate-in slide-in-from-left-2 fade-in duration-300"
                  style={{
                    animation:
                      "slideInBounce 0.3s ease-out, fadeOut 0.5s ease-in 3.5s forwards",
                  }}
                >
                  {userEmoji}
                </div>
              </div>
            )}
          </div>
        </div>

        {/* Opponent avatar (right) */}
        <div className="flex flex-col gap-2">
          <div className="flex justify-center mb-3 relative">
            <AvatarCard
              src={opponentData?.image_url || "/images/default-avatar.png"}
              alt={`${opponentData?.name || "Opponent"} avatar`}
              name={opponentData?.name || "Opponent"}
              size="md"
              player="player2"
            />
            {/* Floating emoji positioned absolutely */}
            {opponentEmoji && (
              <div className="absolute -top-4 -right-4 z-10">
                <div
                  key={opponentKey}
                  className="text-5xl animate-in slide-in-from-right-2 fade-in duration-300"
                  style={{
                    animation:
                      "slideInBounce 0.3s ease-out, fadeOut 0.5s ease-in 3.5s forwards",
                  }}
                >
                  {opponentEmoji}
                </div>
              </div>
            )}
          </div>
        </div>
      </div>

      {/* Emoji Queue */}
      {/* {opponentEmojiQueue.length > 0 && (
        <div className="flex justify-start mb-4">
          <div className="flex items-center gap-2 overflow-hidden">
            <span className="text-xs text-foreground/60 flex-shrink-0">
              Recent:
            </span>
            <div className="flex gap-1 overflow-hidden whitespace-nowrap">
              {opponentEmojiQueue.map((item, index) => (
                <div
                  key={`${item.timestamp}-${index}`}
                  className="flex-shrink-0 text-lg opacity-80"
                  title={`Sent ${Math.round(
                    (Date.now() - item.timestamp) / 1000
                  )}s ago`}
                >
                  {item.emoji}
                </div>
              ))}
            </div>
          </div>
        </div>
      )} */}

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

      {/* Always Visible Emoji Picker */}
      <div className="">
        <h4 className="mb-2 text-sm font-semibold text-foreground/70">
          Send Emoji
        </h4>
        <div className="flex justify-center mb-4">
          <CustomEmojiPicker
            onEmojiSelect={(emoji: { native: string }) => {
              onUserEmojiSelect(emoji);
            }}
          />
        </div>
      </div>

      {/* Opponent Code Preview */}
      <div className="">
        <h4 className="mb-2 text-sm font-semibold text-foreground/70">
          Opponent&apos;s Code
          <span className="text-xs text-foreground/40 ml-2">
            🚀 [DEBUG] Available: {codeAvailable ? 'Yes' : 'No'} | Has Code: {opponentCode ? 'Yes' : 'No'}
          </span>
        </h4>
        <div className="overflow-y-auto rounded-md bg-foreground/5 h-80">
          {opponentCode ? (
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
            <div className="flex items-center justify-center h-full text-foreground/60">
              <p>Loading opponent code...</p>
            </div>
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
