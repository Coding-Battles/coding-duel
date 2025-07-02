"use client";
import TypeIt from "typeit-react";
import { Card, CardContent } from "@/components/ui/card";
import { useGameContext } from "./layout";
import { Badge } from "@/components/ui/badge";
import { useEffect, useState } from "react";
import { FileQuestion } from "lucide-react";
import { useRouter } from "next/navigation";

export default function QueueLayout() {
  const context = useGameContext();
  const [key, setKey] = useState(0); //used to loop the type animation
  const [timer, setTimer] = useState(0);

  const [playerFound, setPlayerFound] = useState(false);

  const router = useRouter();

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
        <div className="bg-gray-800 px-4 py-3 flex items-center justify-between rounded-t-lg">
          <div className="flex items-center gap-2">
            <div className="w-3 h-3 bg-red-500 rounded-full" />
            <div className="w-3 h-3 bg-yellow-500 rounded-full" />
            <div className="w-3 h-3 bg-green-500 rounded-full" />
          </div>
          <div className="flex items-center gap-4 text-sm">
            <span className="text-gray-400">
              Time:{" "}
              <span className="text-white font-mono">
                {Math.floor(timer / 60)}:{timer % 60 < 10 && 0}
                {timer % 60}
              </span>
            </span>
            {!playerFound ? (
              <Badge
                variant="outline"
                className="border-yellow-500 text-yellow-400"
              >
                Finding Opponent...
              </Badge>
            ) : (
              <Badge
                variant="outline"
                className="border-green-500 text-green-400"
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
                      router.push("/queue/in-game");
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
          <img
            src=""
            alt="Player Image"
            className="w-24 h-24 mb-4 border-2 border-gray-300"
          />
          <h1 className="text-2xl font-bold">Username1</h1>
        </div>

        <div className="flex flex-col items-center justify-center p-6 border-2 rounded-lg w-[170px]">
          {opponent.image_url ? 
            <img src={opponent.image_url} alt="Opponent Image" className="w-24 h-24 mb-4 border-2 border-gray-300"/> 
            : 
            <FileQuestion className="w-8 h-8 text-gray-500" />
          }
          <h1 className="text-2xl font-bold">{opponent.name? opponent.name : "Finding"}</h1>
        </div>
      </div>
    </div>
  );
}
