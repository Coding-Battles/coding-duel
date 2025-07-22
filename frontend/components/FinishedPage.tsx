'use client'
import { User } from "better-auth";
import React, { useEffect, useState } from "react";
import { TestResultsData } from "./TestResults";
import { CustomUser, OpponentData } from "@/app/game-setup/layout";
import { useRouter } from "next/navigation";
import { getAvatarUrl } from "@/lib/auth-client";
import { Trophy, Clock, Zap, Target, Home, ArrowRight } from "lucide-react";

interface FinishedPageProps {
  opponent: OpponentData,
  user: CustomUser | null,
  gameEndData: any, // Complete game end info from backend
  userStats?: TestResultsData, // May be undefined if user didn't complete
  opponentStats?: TestResultsData; // May be undefined if opponent didn't complete
}

const FinishedPage = ({opponent, user, gameEndData, opponentStats, userStats} : FinishedPageProps) => {
  const [mounted, setMounted] = useState(false);
  const router = useRouter();
  
  // Determine winner based on gameEndData (first to solve wins)
  const userWon = gameEndData?.winner_id === user?.id;
  
  // Create winner and loser data from available information
  const winnerData = {
    id: gameEndData?.winner_id,
    name: gameEndData?.winner_name || (userWon ? user?.name : opponent?.name),
    image: userWon ? getAvatarUrl(user) : opponent.image_url,
    stats: userWon ? userStats : (gameEndData?.winner_stats || opponentStats)
  };
  
  const loserData = {
    id: gameEndData?.loser_id,
    name: gameEndData?.loser_name || (userWon ? opponent?.name : user?.name),
    image: userWon ? opponent.image_url : getAvatarUrl(user),
    stats: userWon ? opponentStats : userStats
  };

  useEffect(() => {
    setMounted(true);
    console.log("🏆 [FINISHED PAGE] User won:", userWon);
    console.log("🏆 [FINISHED PAGE] Game end data:", gameEndData);
    console.log("🏆 [FINISHED PAGE] Winner data:", winnerData);
    console.log("🏆 [FINISHED PAGE] Loser data:", loserData);
  }, [userWon, gameEndData, winnerData, loserData])
  
  return (
    <div className="relative flex flex-col items-center justify-center min-h-screen p-8 overflow-hidden ">
      {/* Decorative background elements */}
      <div className="absolute top-0 left-0 w-full h-full pointer-events-none">
        <div className="absolute w-32 h-32 rounded-full top-20 left-20 bg-accent/5 blur-3xl"></div>
        <div className="absolute w-40 h-40 rounded-full bottom-20 right-20 bg-success/5 blur-3xl"></div>
        <div className="absolute w-24 h-24 rounded-full top-1/2 left-1/4 bg-primary/5 blur-2xl"></div>
      </div>

      {/* Main content */}
      <div className={`relative z-10 w-full max-w-4xl transition-all duration-1000 ${mounted ? 'opacity-100 translate-y-0' : 'opacity-0 translate-y-8'}`}>
        
        {/* Header */}
        <div className="mb-12 text-center">
          <div className="inline-flex items-center gap-3 mb-4">
            <Trophy className="w-8 h-8 text-accent" />
            <h1 className="text-4xl font-bold text-transparent bg-gradient-to-r from-accent to-success bg-clip-text">
              Game Complete
            </h1>
            <Trophy className="w-8 h-8 text-accent" />
          </div>
          <p className="text-lg text-foreground/70">
            {userWon ? "Congratulations! You won!" : "Great effort! Better luck next time!"}
          </p>
        </div>

        {/* Winner/Loser Cards */}
        <div className="grid gap-8 mb-12 md:grid-cols-2">
          {/* Winner Card */}
          <div className={`relative overflow-hidden rounded-2xl bg-gradient-to-br from-success/20 to-success/5 border-2 border-success/30 p-8 shadow-2xl transition-all duration-700 hover:scale-105 ${mounted ? 'animate-pulse' : ''}`}>
            <div className="absolute top-0 right-0 w-24 h-24 rounded-full bg-success/10 blur-2xl"></div>
            <div className="relative z-10">
              <div className="flex items-center gap-4 mb-6">
                <div className="relative">
                  <img
                    src={winnerData.image}
                    alt="Winner"
                    className="w-20 h-20 border-4 rounded-full shadow-lg border-success"
                  />
                  <div className="absolute flex items-center justify-center w-8 h-8 rounded-full -top-2 -right-2 bg-success">
                    <Trophy className="w-4 h-4 text-white" />
                  </div>
                </div>
                <div>
                  <h2 className="text-2xl font-bold text-success">Winner</h2>
                  <p className="font-semibold text-foreground/80">{winnerData.name}</p>
                </div>
              </div>
              
              <div className="space-y-3">
                <div className="flex items-center justify-between p-3 rounded-lg bg-background/50">
                  <div className="flex items-center gap-2">
                    <Clock className="w-4 h-4 text-success" />
                    <span className="text-sm font-medium">Implementation</span>
                  </div>
                  <span className="font-bold text-success">
                    {winnerData.stats?.implement_time || "N/A"}
                  </span>
                </div>
                
                <div className="flex items-center justify-between p-3 rounded-lg bg-background/50">
                  <div className="flex items-center gap-2">
                    <Zap className="w-4 h-4 text-success" />
                    <span className="text-sm font-medium">Complexity</span>
                  </div>
                  <span className="font-bold text-success">
                    {winnerData.stats?.complexity || "N/A"}
                  </span>
                </div>
                
                <div className="flex items-center justify-between p-3 rounded-lg bg-background/50">
                  <div className="flex items-center gap-2">
                    <Target className="w-4 h-4 text-success" />
                    <span className="text-sm font-medium">Total Score</span>
                  </div>
                  <span className="font-bold text-success">
                    {winnerData.stats?.final_time || "N/A"}
                  </span>
                </div>
              </div>
            </div>
          </div>

          {/* Loser Card */}
          <div className="relative p-8 overflow-hidden transition-all duration-700 border-2 shadow-2xl rounded-2xl bg-gradient-to-br from-error/20 to-error/5 border-error/30 hover:scale-105">
            <div className="absolute top-0 right-0 w-24 h-24 rounded-full bg-error/10 blur-2xl"></div>
            <div className="relative z-10">
              <div className="flex items-center gap-4 mb-6">
                <div className="relative">
                  <img
                    src={loserData.image}
                    alt="Runner-up"
                    className="w-20 h-20 border-4 rounded-full shadow-lg border-error"
                  />
                  <div className="absolute flex items-center justify-center w-8 h-8 rounded-full -top-2 -right-2 bg-error">
                    <span className="text-sm font-bold text-white">2</span>
                  </div>
                </div>
                <div>
                  <h2 className="text-2xl font-bold text-error">Loser</h2>
                  <p className="font-semibold text-foreground/80">{loserData.name}</p>
                  {!loserData.stats && (
                    <p className="text-xs text-foreground/50">Didn't complete</p>
                  )}
                </div>
              </div>
              
              <div className="space-y-3">
                {loserData.stats ? (
                  <>
                    <div className="flex items-center justify-between p-3 rounded-lg bg-background/50">
                      <div className="flex items-center gap-2">
                        <Clock className="w-4 h-4 text-error" />
                        <span className="text-sm font-medium">Implementation</span>
                      </div>
                      <span className="font-bold text-error">{loserData.stats.implement_time}</span>
                    </div>
                    
                    <div className="flex items-center justify-between p-3 rounded-lg bg-background/50">
                      <div className="flex items-center gap-2">
                        <Zap className="w-4 h-4 text-error" />
                        <span className="text-sm font-medium">Complexity</span>
                      </div>
                      <span className="font-bold text-error">{loserData.stats.complexity}</span>
                    </div>
                    
                    <div className="flex items-center justify-between p-3 rounded-lg bg-background/50">
                      <div className="flex items-center gap-2">
                        <Target className="w-4 h-4 text-error" />
                        <span className="text-sm font-medium">Total Score</span>
                      </div>
                      <span className="font-bold text-error">{loserData.stats.final_time}</span>
                    </div>
                  </>
                ) : (
                  <div className="p-4 text-center rounded-lg bg-background/30">
                    <p className="text-sm text-foreground/60">Player didn't complete the challenge</p>
                  </div>
                )}
              </div>
            </div>
          </div>
        </div>

        {/* Stats Comparison */}
        <div className="p-8 mb-8 border shadow-xl bg-background/80 backdrop-blur-sm rounded-2xl border-foreground/10">
          <h3 className="flex items-center justify-center gap-2 mb-6 text-xl font-bold text-center">
            <div className="w-2 h-2 rounded-full bg-accent"></div>
            Match Statistics
            <div className="w-2 h-2 rounded-full bg-accent"></div>
          </h3>
          
          <div className="grid gap-6 md:grid-cols-3">
            <div className="p-4 text-center border bg-accent/5 rounded-xl border-accent/20">
              <Trophy className="w-8 h-8 mx-auto mb-2 text-accent" />
              <p className="mb-1 text-sm text-foreground/70">Game Result</p>
              <p className="text-lg font-bold text-accent">
                {gameEndData?.game_end_reason === "first_win" ? "First to Solve" : "Game Complete"}
              </p>
            </div>
            
            <div className="p-4 text-center border bg-primary/5 rounded-xl border-primary/20">
              <Zap className="w-8 h-8 mx-auto mb-2 text-primary" />
              <p className="mb-1 text-sm text-foreground/70">Winner's Complexity</p>
              <p className="text-2xl font-bold text-primary">
                {winnerData.stats?.complexity || "N/A"}
              </p>
            </div>
            
            <div className="p-4 text-center border bg-success/5 rounded-xl border-success/20">
              <Target className="w-8 h-8 mx-auto mb-2 text-success" />
              <p className="mb-1 text-sm text-foreground/70">Winner's Time</p>
              <p className="text-2xl font-bold text-success">
                {winnerData.stats?.final_time ? `${winnerData.stats.final_time}s` : "N/A"}
              </p>
            </div>
          </div>
        </div>

        {/* Action Buttons */}
        <div className="flex flex-col items-center justify-center gap-4 sm:flex-row">
          <button 
            onClick={() => router.push("/")}
            className="flex items-center gap-3 px-8 py-4 font-semibold transition-all duration-300 shadow-lg cursor-pointer group bg-gradient-to-r from-accent to-accent/80 text-background rounded-xl hover:shadow-xl hover:scale-105"
          >
            <Home className="w-5 h-5" />
            Back to Main Menu
            <ArrowRight className="w-4 h-4 transition-transform group-hover:translate-x-1" />
          </button>
          
          <button 
            onClick={() => window.location.reload()}
            className="flex items-center gap-3 px-8 py-4 font-semibold transition-all duration-300 shadow-lg cursor-pointer group bg-gradient-to-r from-primary to-primary/80 text-background rounded-xl hover:shadow-xl hover:scale-105"
          >
            <Trophy className="w-5 h-5" />
            Play Again
            <ArrowRight className="w-4 h-4 transition-transform group-hover:translate-x-1" />
          </button>
        </div>
      </div>
    </div>
  );
};

export default FinishedPage;