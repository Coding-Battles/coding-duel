"use client";
import TypeIt from "typeit-react";
import { useGameContext } from "@/app/game-setup/layout";
import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";
import { useEffect, useState } from "react";
import { useSession, getAvatarUrl } from "@/lib/auth-client";
import AvatarCard from "./AvatarCard";
import OpponentPlaceholder from "./OpponentPlaceholder";

interface CustomUser {
  username?: string;
  name?: string;
  image?: string;
  id?: string;
  selectedPfp?: number;
}

interface QueueWaitingRoomProps {
  onCancel?: () => void;
}

export default function QueueWaitingRoom({ onCancel }: QueueWaitingRoomProps) {
  const context = useGameContext();
  const { data: session } = useSession();
  const [key, setKey] = useState(0); // used to loop the type animation
  const [timer, setTimer] = useState(0);
  const [playerFound] = useState(false);

  // Funny roasting messages for queue waiting
  const queueMessages = [
    "Lowering standards...",
    "Finding someone easier...",
    "Looking for noobs...",
    "Difficulty: Potato mode...",
    "Still no takers...",
    "Crickets chirping...",
    "Even bots are avoiding you...",
    "Maybe try easier mode?",
    "Your reputation precedes you...",
    "Loading disappointment...",
    "Charging up the L...",
    "Buffering your loss...",
    "Questioning life choices...",
    "Reconsidering career paths...",
  ];

  // Function to get random roasting message
  const getRandomMessage = () => {
    const randomIndex = Math.floor(Math.random() * queueMessages.length);
    return queueMessages[randomIndex];
  };

  // Helper function to get user avatar with proper fallbacks
  const getUserAvatar = () => {
    // Try context user first, then session user
    const user = context?.user || (session?.user as CustomUser);
    return getAvatarUrl(user);
  };

  // Timer effect - must be before conditional returns
  useEffect(() => {
    if (!context?.socket) return;

    const interval = setInterval(() => {
      setTimer((prev) => prev + 1);
    }, 1000);

    return () => {
      clearInterval(interval);
    };
  }, [context?.socket]);

  if (!context) {
    return (
      <div className="flex h-[100%] w-[100%] items-center justify-center">
        <p className="text-error">Game context is not available.</p>
      </div>
    );
  }

  const { opponent } = context;

  return (
    <div className="flex h-[100%] w-[100%] flex-col">
      {/* Header with Status and Cancel */}
      <div className="flex flex-col sm:flex-row items-start sm:items-center justify-between p-4 border-b border-foreground/10 gap-3 sm:gap-4">
        <div className="flex flex-col sm:flex-row items-start sm:items-center gap-3 sm:gap-4">
          <div className="flex items-center gap-2">
            <div className="w-3 h-3 rounded-full bg-error" />
            <div className="w-3 h-3 rounded-full bg-accent" />
            <div className="w-3 h-3 rounded-full bg-success" />
          </div>
          <div className="flex flex-col sm:flex-row items-start sm:items-center gap-2 sm:gap-4 text-sm">
            <span className="text-foreground/60">
              Time:{" "}
              <span className="font-mono text-foreground">
                {Math.floor(timer / 60)}:{timer % 60 < 10 && 0}
                {timer % 60}
              </span>
            </span>
            {!playerFound ? (
              <Badge variant="outline" className="border-accent text-accent">
                Finding Opponent...
              </Badge>
            ) : (
              <Badge variant="outline" className="border-success text-success">
                Opponent Found
              </Badge>
            )}
          </div>
        </div>

        {/* Cancel Button in Header */}
        {onCancel && (
          <Button onClick={onCancel} variant="ghost" size="sm">
            Cancel
          </Button>
        )}
      </div>

      {/* Status Display */}
      <div className="flex justify-center p-4">
        <div className="text-center font-mono text-sm bg-foreground/5 px-4 py-2 rounded-lg whitespace-nowrap">
          <div className="text-accent">
            {!playerFound ? (
              <TypeIt
                key={key} // use key to reset TypeIt instance
                options={{
                  speed: 50,
                  deleteSpeed: 30,
                }}
                getBeforeInit={(instance) => {
                  const message1 = getRandomMessage();
                  const message2 = getRandomMessage();
                  instance
                    .type(`<span style="color: orange;">${message1}</span>`)
                    .pause(400)
                    .delete(message1.length)
                    .type(`<span style="color: orange;">${message2}</span>`)
                    .pause(600)
                    .delete(message2.length)
                    .exec(() => {
                      setKey((prevKey) => prevKey + 1); // trigger re-render to reset TypeIt
                    });
                  return instance;
                }}
              />
            ) : (
              <TypeIt
                getBeforeInit={(instance) => {
                  instance
                    .type('<span style="color: orange;">Player Found!</span>')
                    .pause(2000)
                    .exec(() => {
                      // Navigate to game with question name from match_found event
                      // This will be handled by the layout's match_found listener
                    });
                  return instance;
                }}
              />
            )}
          </div>
        </div>
      </div>

      {/* Main Battle Area */}
      <div className="flex-1 flex items-center justify-center p-4">
        <div className="flex flex-col md:flex-row items-center gap-12 md:gap-20 lg:gap-32 w-full max-w-6xl">
          {/* User Avatar */}
          <div className="flex-shrink-0">
            <AvatarCard
              src={getUserAvatar()}
              alt={`${
                (context?.user as CustomUser)?.username ||
                context?.user?.name ||
                (session?.user as CustomUser)?.username ||
                session?.user?.name ||
                "User"
              } Avatar`}
              name={
                (context?.user as CustomUser)?.username ||
                context?.user?.name ||
                (session?.user as CustomUser)?.username ||
                session?.user?.name ||
                "Guest"
              }
              size="lg"
              player="player1"
            />
          </div>

          {/* VS Section */}
          <div className="flex flex-col items-center gap-4 flex-shrink-0">
            <div className="text-2xl md:text-4xl font-bold text-foreground/60">
              VS
            </div>
          </div>

          {/* Opponent Avatar */}
          <div className="flex-shrink-0">
            {opponent.image_url && opponent.name && playerFound ? (
              <AvatarCard
                src={opponent.image_url}
                alt={`${opponent.name} Avatar`}
                name={opponent.name}
                size="lg"
                player="player2"
              />
            ) : (
              <OpponentPlaceholder size="lg" />
            )}
          </div>
        </div>
      </div>
    </div>
  );
}
