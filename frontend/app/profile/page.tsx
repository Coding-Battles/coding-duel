"use client";
import React, { useEffect } from "react";
import {
  User,
  Calendar,
  Trophy,
  TrendingUp,
  Clock,
  CheckCircle,
  XCircle,
  Circle,
  ArrowLeft,
  ArrowLeftSquare,
} from "lucide-react";
import { ProfileBar } from "./components/ProfileBar";
import { UserStats } from "@/interfaces/UserStats";
import Link from "next/link";

import { useSession } from "@/lib/auth-client";
import { UserStatsAndHistory } from "./components/UserStatsAndHistory";

type GameParticipant = {
  game_id: number;
  player_name: string;
  player_code: string;
  implement_time: string;
  time_complexity: string;
  final_time: string;
  user_id: string;
};

type GameHistoryItem = {
  game_id: number;
  participants: GameParticipant[];
  user_won: boolean;
  result: "won" | "lost" | "tie";
  user_time: number;
  opponent_best_time: number;
};

interface Problem {
  id: number;
  title: string;
  difficulty: "Easy" | "Medium" | "Hard";
  status: "Solved" | "Attempted" | "Not Attempted";
  category: string;
  submittedAt?: string;
}

const LeetCodeProfile: React.FC = () => {
  const userStats: UserStats = {
    totalSolved: 342,
    easySolved: 156,
    mediumSolved: 142,
    hardSolved: 44,
    totalSubmissions: 1247,
    acceptanceRate: 67.2,
    ranking: 12543,
    streak: 23,
  };

  const { data: session } = useSession();

  const [loaded, setLoad] = React.useState<boolean>(false);
  const [userGameHistory, setUserGameHistory] = React.useState<GameHistoryItem[][]>([]);
  const [totalBattles, setTotalBattles] = React.useState<number>(0);
  const [totalWins, setTotalWins] = React.useState<number>(0);

  const itemsPerPage = 5;

  const getUserGameHistory = async () => {
    fetch(
      `${process.env.NEXT_PUBLIC_API_BASE_URL}/user/${session?.user.id}/game-history`
    )
      .then((response) => response.json())
      .then((data) => {
        console.log("User Game History:", data);
        setLoad(true);
        var battles = 0;
        var wins = 0;

        // Check if data exists and is a non-empty array
        const groupedHistory = (data && Array.isArray(data) && data.length > 0)
          ? data.reduce(
              (acc: Record<number, GameParticipant[]>, curr: GameParticipant) => {
                const { game_id } = curr;
                if (!acc[game_id]) {
                  battles++;
                  acc[game_id] = [];
                }
                acc[game_id].push(curr);
                return acc;
              },
              {} as Record<number, GameParticipant[]>
            )
          : {} as Record<number, GameParticipant[]>;

        // Convert grouped history to proper format
        const processedHistory: GameHistoryItem[] = [];

        Object.entries(groupedHistory).forEach(([gameId, participants]) => {
          var userTime = 40000;
          var lowestTimeFromOther = 30000;
          var result: "won" | "lost" | "tie" = "lost";

          const gameParticipants = participants as GameParticipant[];
          gameParticipants.forEach((participant) => {
            if (participant.user_id == session?.user.id) {
              userTime = parseInt(participant.final_time);
            } else {
              if (parseInt(participant.final_time) < lowestTimeFromOther) {
                lowestTimeFromOther = parseInt(participant.final_time);
              }
            }
          });

          if (userTime < lowestTimeFromOther) {
            wins++;
            result = "won";
          } else if (userTime > lowestTimeFromOther) {
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

      processedHistory.reverse();

      console.log("Processed Game History:", processedHistory);

      const compressedList: GameHistoryItem[][] = [];
      for (let i = 0; i < processedHistory.length; i += itemsPerPage) {
        compressedList.push(processedHistory.slice(i, i + itemsPerPage));
      }
    
      setUserGameHistory(compressedList);
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
      getUserGameHistory();
    }
  }, [session]);

  const recentSubmissions: Problem[] = [
    {
      id: 1,
      title: "Two Sum",
      difficulty: "Easy",
      status: "Solved",
      category: "Array",
      submittedAt: "2 hours ago",
    },
    {
      id: 42,
      title: "Trapping Rain Water",
      difficulty: "Hard",
      status: "Solved",
      category: "Dynamic Programming",
      submittedAt: "1 day ago",
    },
    {
      id: 15,
      title: "3Sum",
      difficulty: "Medium",
      status: "Attempted",
      category: "Array",
      submittedAt: "2 days ago",
    },
    {
      id: 739,
      title: "Daily Temperatures",
      difficulty: "Medium",
      status: "Solved",
      category: "Stack",
      submittedAt: "3 days ago",
    },
  ];

  return (
    <div className="max-w-6xl mx-auto p-6 bg-gray-50 min-h-screen">
      <Link
        href="/"
        className="text-blue-600 absolute top-2 left-2 w-8 h-8 hover:text-blue-300 transition-colors cursor-pointer"
      >
        <ArrowLeftSquare className="w-full h-full" />
      </Link>
      {/* Header */}
      <div className="bg-white rounded-lg shadow-md p-6 mb-6">
        <ProfileBar />
      </div>

      <UserStatsAndHistory
        userStats={userStats}
        userGameHistory={userGameHistory}
        totalBattles={totalBattles}
        totalWins={totalWins}
      />
    </div>
  );
};

export type {Problem, GameHistoryItem}

export default LeetCodeProfile;
