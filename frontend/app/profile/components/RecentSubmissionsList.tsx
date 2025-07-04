"use client";
import { useSession } from '@/lib/auth-client';
import { Session } from 'better-auth';
import { CheckCircle, Circle, Clock, Loader, XCircle } from 'lucide-react';
import React, { useEffect } from 'react'

type GameParticipant = {
  game_id: number;
  player_name: string;
  player_code: string;
  implement_time: string;
  time_complexity: string;
  final_time: string;
  user_id: string;
}

type GameHistoryItem = {
  game_id: number;
  participants: GameParticipant[];
  user_won: boolean;
  result: "won" | "lost" | "tie";
  user_time: number;
  opponent_best_time: number;
}

const getDifficultyColor = (difficulty: string): string => {
  switch (difficulty) {
    case 'Easy': return 'text-green-600 bg-green-100';
    case 'Medium': return 'text-yellow-600 bg-yellow-100';
    case 'Hard': return 'text-red-600 bg-red-100';
    default: return 'text-gray-600 bg-gray-100';
  }
};

const getStatusIcon = (result: string) => {
  switch (result) {
    case 'won': return <CheckCircle className="w-4 h-4 text-green-600" />;
    case 'lost': return <XCircle className="w-4 h-4 text-red-600" />;
    case 'tie': return <Circle className="w-4 h-4 text-yellow-600" />;
    default: return <Circle className="w-4 h-4 text-gray-400" />;
  }
};

export const RecentSubmissionsList = () => {
  const {data: session} = useSession();

  const [loaded, setLoad] = React.useState<boolean>(false);
  const [userGameHistory, setUserGameHistory] = React.useState<GameHistoryItem[]>([]);
  const [totalBattles, setTotalBattles] = React.useState<number>(0);
  const [totalWins, setTotalWins] = React.useState<number>(0);

  const getUserGameHistory = async () => {
    fetch(`${process.env.NEXT_PUBLIC_API_BASE_URL}/user/${session?.user.id}/game-history`)
    .then(response => response.json())
    .then(data => {
      console.log("User Game History:", data);
      setLoad(true);
      var battles = 0;
      var wins = 0;

      // Type the accumulator properly
      const groupedHistory = data.reduce((acc: Record<number, GameParticipant[]>, curr: GameParticipant) => {
        const {game_id} = curr;
        if (!acc[game_id]) {
          battles++;
          acc[game_id] = [];
        }
        acc[game_id].push(curr);
        return acc;
      }, {} as Record<number, GameParticipant[]>);

      // Convert grouped history to proper format
      const processedHistory: GameHistoryItem[] = [];

      Object.entries(groupedHistory).forEach(([gameId, participants]) => {
        var userTime = 40000;
        var lowestTimeFromOther = 30000;
        var result: "won" | "lost" | "tie" = "lost";

        const gameParticipants = participants as GameParticipant[];
        gameParticipants.forEach((participant) => {
          if(participant.user_id == session?.user.id) {
            userTime = parseInt(participant.final_time);
          } else {
            if(parseInt(participant.final_time) < lowestTimeFromOther) {
              lowestTimeFromOther = parseInt(participant.final_time);
            }
          }
        });

        if(userTime < lowestTimeFromOther) {
          wins++;
          result = "won";
        } else if(userTime > lowestTimeFromOther) {
          result = "lost";
        } else {
          result = "tie";
        }

        processedHistory.push({
          game_id: parseInt(gameId),
          participants: gameParticipants,
          user_won: result === "won",
          result: result,
          user_time: userTime,
          opponent_best_time: lowestTimeFromOther
        });
      });

      console.log("Processed Game History:", processedHistory);
      setUserGameHistory(processedHistory);
      setTotalBattles(battles);
      setTotalWins(wins);
    })
    .catch(error => {
      console.error("Error fetching game history:", error);
      setLoad(true);
    });
  }

  useEffect(() => {
    if (session) {
      getUserGameHistory()
    }
  }, [session])

  return (
    <div className="space-y-3">
      {userGameHistory.length > 0 && (
        <>
          <div className="mb-4 p-4 bg-blue-50 rounded-lg">
            <h3 className="font-semibold text-blue-900">Battle Statistics</h3>
            <p className="text-blue-700">Total Battles: {totalBattles} | Wins: {totalWins} | Win Rate: {totalBattles > 0 ? Math.round((totalWins / totalBattles) * 100) : 0}%</p>
          </div>
          
          {userGameHistory.map((game) => (
            <div key={game.game_id} className="border rounded-lg p-4 hover:bg-gray-50 transition-colors">
              <div className="flex items-center justify-between">
                <div className="flex items-center space-x-3">
                  {getStatusIcon(game.result)}
                  <div>
                    <h3 className="font-medium text-gray-800">Game #{game.game_id}</h3>
                    <div className="flex items-center space-x-2 mt-1">
                      <span className={`px-2 py-1 rounded text-xs font-medium ${
                        game.result === 'won' ? 'text-green-600 bg-green-100' :
                        game.result === 'lost' ? 'text-red-600 bg-red-100' :
                        'text-yellow-600 bg-yellow-100'
                      }`}>
                        {game.result.toUpperCase()}
                      </span>
                      <span className="text-xs text-gray-500">{game.participants.length} players</span>
                    </div>
                    <div className="mt-2 text-sm text-gray-600">
                      <p>Your time: {game.user_time}ms</p>
                      <p>Best opponent: {game.opponent_best_time}ms</p>
                    </div>
                  </div>
                </div>
                <div className="text-right">
                  <div className="flex items-center space-x-1 text-sm text-gray-500">
                    <Clock className="w-4 h-4" />
                    <span>Recently played</span>
                  </div>
                </div>
              </div>
            </div>
          ))}
        </>
      )}
      {!loaded && <Loader className="w-6 h-6 animate-spin text-gray-500 mx-auto" />}
      {loaded && userGameHistory.length === 0 && (
        <div className="text-center py-8 text-gray-500">
          <p>No game history found</p>
        </div>
      )}
    </div>
  )
}