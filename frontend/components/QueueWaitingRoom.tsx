"use client";
import TypeIt from "typeit-react";
import { Card, CardContent } from "@/components/ui/card";
import { useGameContext } from "@/app/game-setup/layout";
import { Badge } from "@/components/ui/badge";
import { useEffect, useState } from "react";
import { useSession, getAvatarUrl } from "@/lib/auth-client";
import AvatarCard from "./AvatarCard";

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
    <div className="flex h-[100%] w-[100%] items-center justify-center flex-col">
      <Card className="mt-16 shadow-2xl bg-background border-foreground/20 animate-float">
        <div className="flex items-center justify-between px-4 py-3 rounded-t-lg bg-foreground/10">
          <div className="flex items-center gap-2">
            <div className="w-3 h-3 rounded-full bg-error" />
            <div className="w-3 h-3 rounded-full bg-accent" />
            <div className="w-3 h-3 rounded-full bg-success" />
          </div>
          <div className="flex items-center gap-4 text-sm">
            <span className="text-foreground/60">
              Time:{" "}
              <span className="font-mono text-foreground">
                {Math.floor(timer / 60)}:{timer % 60 < 10 && 0}
                {timer % 60}
              </span>
            </span>
            {!playerFound ? (
              <Badge
                variant="outline"
                className="border-accent text-accent"
              >
                Finding Opponent...
              </Badge>
            ) : (
              <Badge
                variant="outline"
                className="border-success text-success"
              >
                Opponent Found
              </Badge>
            )}
          </div>
        </div>
        <CardContent className="p-6 font-mono text-sm">
          <div className="ml-4 text-accent">
            const <span className="text-foreground">Status</span> ={" "}
            <span className="text-accent">&quot;</span>
            {!playerFound ? (
              <TypeIt
                key={key} // use key to reset TypeIt instance
                getBeforeInit={(instance) => {
                  instance
                    .type('<span style="color: orange;">loading...</span>')
                    .pause(750)
                    .delete(10)
                    .type('<span style="color: orange;">loading!</span>')
                    .pause(1000)
                    .delete(8)
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
            <span className="text-accent">&quot;</span>
          </div>
        </CardContent>
      </Card>

      <div className="flex gap-8 mt-16">
        <AvatarCard
          src={getUserAvatar()}
          alt={`${(context?.user as CustomUser)?.username || context?.user?.name || (session?.user as CustomUser)?.username || session?.user?.name || "User"} Avatar`}
          name={(context?.user as CustomUser)?.username || context?.user?.name || (session?.user as CustomUser)?.username || session?.user?.name || "Guest"}
          size="lg"
        />

        <AvatarCard
          src={opponent.image_url || "/avatars/0.png"}
          alt={`${opponent.name || "Opponent"} Avatar`}
          name={opponent.name || "Finding"}
          size="lg"
        />
      </div>

      {/* Cancel Button */}
      {onCancel && (
        <div className="text-center mt-8">
          <button
            onClick={onCancel}
            className="relative cursor-pointer h-12 w-48 font-bold uppercase tracking-wider transition-all duration-300 transform hover:scale-105 focus:outline-none overflow-hidden rounded-lg shadow-lg shadow-slate-500/30"
          >
            {/* Gradient border effect */}
            <div className="absolute inset-0 rounded-lg p-[2px] bg-gradient-to-r from-slate-500 via-slate-300 to-slate-500 hover:from-slate-400 hover:via-slate-200 hover:to-slate-400 transition-all duration-300">
              <div className="w-full h-full rounded-md bg-background flex items-center justify-center">
                <span className="relative z-10 text-slate-200 hover:text-slate-100 transition-colors duration-300">
                  Cancel
                </span>
              </div>
            </div>

            {/* Shine effect */}
            <div className="absolute inset-0 -top-2 -left-2 bg-gradient-to-r from-transparent via-white/20 to-transparent rotate-45 w-8 h-20 animate-pulse opacity-50"></div>
          </button>
        </div>
      )}
    </div>
  );
}