// This file was moved from in-game/finished/page.tsx to [questionId]/finished/page.tsx for dynamic routing.
// You may want to update this file to use the questionId param if needed.
'use client'
import { User } from "better-auth";
import React, { useEffect } from "react";
import { TestResultsData } from "./TestResults";
import { OpponentData } from "@/app/queue/layout";
import { useRouter } from "next/navigation";
import { getAvatarUrl } from "@/lib/auth-client";


interface CustomUser extends User {
  username?: string;
  selectedPfp?: number;
}

interface FinishedPageProps {
  opponent: OpponentData,
  user: CustomUser | null,
  opponentStats: TestResultsData,
  userStats: TestResultsData;
}

const FinishedPage = ({opponent, user, opponentStats, userStats} : FinishedPageProps) => {
  const userWon = userStats.final_time && opponentStats.final_time ? 
    userStats.final_time < opponentStats.final_time : true;
  
  const winnerStats = userWon ? userStats : opponentStats;
  const loserStats = userWon ? opponentStats : userStats;
  const winnerImage = userWon ? getAvatarUrl(user) : opponent.image_url;
  const loserImage = userWon ? opponent.image_url : getAvatarUrl(user);
  const router = useRouter();

  useEffect(() => {
    console.log("User won:", userWon);
    console.log("Winner Stats:", winnerStats);
    console.log("Loser Stats:", loserStats);
  }, [userWon, winnerStats, loserStats])
  
  return (
    <div className="flex flex-col items-center justify-center h-[100%] w-[100%]">
      <div className="border-2 borde-gray-300 shadow-xl px-4 pt-2 pb-8 text-xs w-auto h-[300px] rounded-xl">
        <div className="grid grid-cols-3 gap-4 w-full mt-2 font-bold">
          <span className="text-xs justify-self-start">{winnerStats.player_name}</span>
          <span className="text-lg justify-self-center">Stats</span>
          <span className="text-xs justify-self-end">{loserStats.player_name}</span>
        </div>
        
        <div className="grid grid-cols-3 gap-4 items-center w-full mt-8">
          <span className="justify-self-start">{winnerStats.implement_time}</span>
          <b className="justify-self-center">Time Finished</b>
          <span className="justify-self-end">{loserStats.implement_time}</span>
        </div>
        
        <div className="grid grid-cols-3 gap-4 items-center w-full mt-8">
          <span className="justify-self-start">{winnerStats.complexity}</span>
          <b className="justify-self-center">Time Complexity</b>
          <span className="justify-self-end">{loserStats.complexity}</span>
        </div>
        
        <div className="grid grid-cols-3 gap-4 items-center w-full mt-8">
          <span className="justify-self-start">{winnerStats.final_time}</span>
          <b className="justify-self-center">Total score</b>
          <span className="justify-self-end">{loserStats.final_time}</span>
        </div>
      </div>
      <div className="flex gap-4 mt-[100px]">
        <div className="flex flex-col items-center justify-center p-6 border-2 border-green-300 rounded-lg">
          <img
            src={winnerImage}
            alt="winnerImage"
            className="w-24 h-24 mb-4 border-2 border-gray-300"
          />
          <span className="text-xs font-bold">{winnerStats.player_name}</span>
          <h1 className="text-2xl font-bold">Winner</h1>
        </div>

        <div className="flex flex-col items-center justify-center p-6 border-2 border-red-300 rounded-lg">
          <img
            src={loserImage}
            alt="loserImage"
            className="w-24 h-24 mb-4 border-2 border-gray-300"
          />
          <span className="text-xs font-bold">{loserStats.player_name}</span>
          <h1 className="text-2xl font-bold">Loser</h1>
        </div>
      </div>
      <div className="mt-12">
        <button className="px-4 py-2 bg-blue-500 text-white rounded hover:bg-blue-600" onClick={() => {router.push("/")}}>
          Go back to main menu
        </button>
      </div>
    </div>
  );
};

export default FinishedPage;
