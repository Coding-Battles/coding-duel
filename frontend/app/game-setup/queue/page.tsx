"use client";
import TypeIt from "typeit-react";
import { Card, CardContent } from "@/components/ui/card";
import { useGameContext } from "../layout";
import { Badge } from "@/components/ui/badge";
import { useEffect, useState } from "react";
import { FileQuestion, User } from "lucide-react";
import { useRouter } from "next/navigation";
import { useSession, getAvatarUrl } from "@/lib/auth-client";
import Image from "next/image";

interface CustomUser {
  username?: string;
  name?: string;
  image?: string;
  id?: string;
  selectedPfp?: number;
}

export default function QueueLayout() {
  const context = useGameContext();
  const { data: session } = useSession();
  const [key, setKey] = useState(0); //used to loop the type animation
  const [timer, setTimer] = useState(0);

  const [playerFound, setPlayerFound] = useState(false);

  const router = useRouter();

  // Helper function to get user avatar with proper fallbacks
  const getUserAvatar = () => {
    // Try context user first, then session user
    const user = context?.user || (session?.user as CustomUser);
    return getAvatarUrl(user);
  };

  if (!context) {
    return (
      <div className="flex h-[100%] w-[100%] items-center justify-center">
        <p className="text-red-500">Game context is not available.</p>
      </div>
    );
  }

  useEffect(() => {
    const interval = setInterval(() => {
      setTimer((prev) => prev + 1);
    }, 1000);

    return () => {
      clearInterval(interval);
    };
  }, [context.socket]);

  const { socket, loading, opponent } = context;
  return (
    <div className="flex h-[100%] w-[100%] items-center justify-center flex-col">
      <Card className="mt-16 bg-gray-900 border-gray-800 shadow-2xl animate-float">
        <div className="flex items-center justify-between px-4 py-3 bg-gray-800 rounded-t-lg">
          <div className="flex items-center gap-2">
            <div className="w-3 h-3 bg-red-500 rounded-full" />
            <div className="w-3 h-3 bg-yellow-500 rounded-full" />
            <div className="w-3 h-3 bg-green-500 rounded-full" />
          </div>
          <div className="flex items-center gap-4 text-sm">
            <span className="text-gray-400">
              Time:{" "}
              <span className="font-mono text-white">
                {Math.floor(timer / 60)}:{timer % 60 < 10 && 0}
                {timer % 60}
              </span>
            </span>
            {!playerFound ? (
              <Badge
                variant="outline"
                className="text-yellow-400 border-yellow-500"
              >
                Finding Opponent...
              </Badge>
            ) : (
              <Badge
                variant="outline"
                className="text-green-400 border-green-500"
              >
                Opponent Found
              </Badge>
            )}
          </div>
        </div>
        <CardContent className="p-6 font-mono text-sm">
          <div className="ml-4 text-purple-400">
            const <span className="text-white">Status</span> ={" "}
            <span className="text-orange-400">"</span>
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
                      router.push("/game-setup/queue/in-game");
                    });
                  return instance;
                }}
              />
            )}
            <span className="text-orange-400">"</span>
          </div>
        </CardContent>
      </Card>

      <div className="flex gap-8 mt-[100px]">
        <div className="flex flex-col items-center justify-center p-6 border-2 w-[170px] rounded-lg">
          <Image
            src={getUserAvatar()}
            alt={`${(context?.user as CustomUser)?.username || context?.user?.name || (session?.user as CustomUser)?.username || session?.user?.name || "User"} Image`}
            width={96}
            height={96}
            className="object-cover w-24 h-24 mb-4 border-2 border-gray-300 rounded-full"
          />
          <h1 className="text-2xl font-bold">
            {(() => {
              console.log('=== QUEUE PAGE DISPLAY DEBUG ===');
              console.log('context?.user?.username:', (context?.user as CustomUser)?.username);
              console.log('context?.user?.name:', context?.user?.name);
              console.log('session?.user?.username:', (session?.user as CustomUser)?.username);
              console.log('session?.user?.name:', session?.user?.name);
              const displayName = (context?.user as CustomUser)?.username || context?.user?.name || (session?.user as CustomUser)?.username || session?.user?.name || "Guest";
              console.log('Final display name:', displayName);
              return displayName;
            })()}
          </h1>
        </div>

        <div className="flex flex-col items-center justify-center p-6 border-2 rounded-lg w-[170px]">
          {opponent.image_url ? (
            <Image
              src={opponent.image_url}
              alt={`${opponent.name || "Opponent"} Image`}
              width={96}
              height={96}
              className="object-cover w-24 h-24 mb-4 border-2 border-gray-300 rounded-full"
            />
          ) : (
            <div className="flex items-center justify-center w-24 h-24 mb-4 bg-gray-100 border-2 border-gray-300 rounded-full">
              <FileQuestion className="w-8 h-8 text-gray-500" />
            </div>
          )}
          <h1 className="text-2xl font-bold">
            {opponent.name ? opponent.name : "Finding"}
          </h1>
        </div>
      </div>
    </div>
  );
}
