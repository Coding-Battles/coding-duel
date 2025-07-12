"use client";
import { useSession } from '@/lib/auth-client';
import { Session } from 'better-auth';
import { CheckCircle, Circle, Clock, Loader, XCircle } from 'lucide-react';
import React, { useEffect, useState } from 'react'
import ExpandedGameResults from './ExpandedGameResults';
import { GameHistoryItem } from '../page';

interface UserStatsAndHistoryProps {
  userStats: {
    totalSolved: number;
    easySolved: number;
    mediumSolved: number;
    hardSolved: number;
    totalSubmissions: number;
    acceptanceRate: number;
  };
  userGameHistory: GameHistoryItem[][];
  totalBattles: number;
  totalWins: number;
}

const getDifficultyColor = (difficulty: string): string => {
  switch (difficulty) {
    case 'Easy': return 'text-success bg-success/10';
    case 'Medium': return 'text-accent bg-accent/10';
    case 'Hard': return 'text-error bg-error/10';
    default: return 'text-foreground/60 bg-foreground/10';
  }
};

const getStatusIcon = (result: string) => {
  switch (result) {
    case 'won': return <CheckCircle className="w-4 h-4 text-success" />;
    case 'lost': return <XCircle className="w-4 h-4 text-error" />;
    case 'tie': return <Circle className="w-4 h-4 text-accent" />;
    default: return <Circle className="w-4 h-4 text-foreground/40" />;
  }
};

const WinRatePercentage = (solved: number, total: number = 1000): number => {
  return Math.round((solved / total) * 100);
};

export const UserStatsAndHistory = ({userGameHistory, totalBattles, totalWins} : UserStatsAndHistoryProps) => {

  const [expandedGames, setExpandedGame] = useState<boolean[]>(Array(userGameHistory.length).fill(false));
  const [selectedIndex, setSelectedIndex] = useState<number>(1);
  const onClickExpand = (index: number) => {
    setExpandedGame((prev) => {
      const newState = [...prev]; // Create a copy of the previous state
      newState[index] = !newState[index]; // Update the specific index
      return newState; // Return the updated state
    });
  }

  return (
<div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
  {/* Stats Panel */}
  <div className="lg:col-span-1">
    <div className="bg-background rounded-lg shadow-md p-6 mb-6">
      <h2 className="text-lg font-semibold text-foreground mb-4">Statistics</h2>
      
      {/* Total Solved */}
      <div className="mb-6">
        <div className="flex justify-between items-center mb-2">
          <span className="text-foreground/60">Total Battles</span>
          <span className="font-bold text-2xl text-foreground">{totalBattles}</span>
        </div>
        <div className="w-full bg-foreground/20 rounded-full h-2">
          <div 
            className="bg-success h-2 rounded-full" 
            style={{ width: `${totalBattles > 0 ? Math.round((totalWins / totalBattles) * 100) : 0}%` }}
          ></div>
        </div>
      </div>

      {/* Difficulty Breakdown */}
      <div className="space-y-3 mb-6">
        <div className="flex justify-between items-center">
          <span className="text-success font-medium">Easy</span>
          <span className="font-semibold">?</span>
        </div>
        <div className="flex justify-between items-center">
          <span className="text-accent font-medium">Medium</span>
          <span className="font-semibold">?</span>
        </div>
        <div className="flex justify-between items-center">
          <span className="text-error font-medium">Hard</span>
          <span className="font-semibold">?</span>
        </div>
      </div>

      {/* Additional Stats */}
      <div className="border-t pt-4 space-y-3">
        <div className="flex justify-between items-center">
          <span className="text-foreground/60">Win Rate</span>
          <span className="font-semibold text-success">{totalBattles > 0 ? Math.round((totalWins / totalBattles) * 100) : 0}%</span>
        </div>

        <div className="flex justify-between items-center">
          <span className="text-foreground/60">Wins</span>
          <span className="font-semibold text-success">{totalWins}</span>
        </div>
      </div>
    </div>
  </div>
  <div className="lg:col-span-2">
    <div className="bg-background rounded-lg shadow-md p-6">
      <h2 className="text-lg font-semibold text-foreground mb-4">Recent Submissions</h2>
      <div className="space-y-3">
        {userGameHistory.length > 0 && (
          <>
            {userGameHistory[selectedIndex].map((game, index) => (
              <div key={game.game_id} className="border rounded-lg p-4 hover:bg-foreground/5 transition-colors h-auto">
                <div className='w-full absolute h-[70px] bg-transparent cursor-pointer' onClick={() => onClickExpand(index)} />
                <div className="flex items-center justify-between">
                  <div className="flex items-center space-x-3">
                    {getStatusIcon(game.result)}
                    <div>
                      <h3 className="font-medium text-foreground">Game #{game.game_id}</h3>
                      <div className="flex items-center space-x-2 mt-1">
                        <span className={`px-2 py-1 rounded text-xs font-medium ${
                          game.result === 'won' ? 'text-success bg-success/10' :
                          game.result === 'lost' ? 'text-error bg-error/10' :
                          'text-accent bg-accent/10'
                        }`}>
                          {game.result.toUpperCase()}
                        </span>
                        <span className="text-xs text-foreground/50">{game.participants.length} players</span>
                      </div>
                      <div className="mt-2 text-sm text-foreground/60">
                        <p>Your time: {game.user_time}ms</p>
                        <p>Best opponent: {game.opponent_best_time}ms</p>
                      </div>
                    </div>
                  </div>
                  <div className="text-right">
                    <div className="flex items-center space-x-1 text-sm text-foreground/50">
                      <Clock className="w-4 h-4" />
                      <span>Recently played</span>
                    </div>
                  </div>
                </div>

                {expandedGames[index] && <ExpandedGameResults game={game} />}
              </div>
            ))}
          </>
        )}
      </div>
      </div>

      <div className='flex justify-center gap-4 mt-4'>
        {userGameHistory.map((_, index) => (
          <button
            key={index}
            className={`px-3 py-1 text-sm font-medium transition-colors cursor-pointer ${
              selectedIndex === index
                ? 'bg-accent text-background'
                : 'bg-foreground/10 text-foreground/70 hover:bg-foreground/20'
            }`}
            onClick={() => {
              setSelectedIndex(index);
              setExpandedGame(Array(userGameHistory[index].length).fill(false));
            }}
          >
            {index + 1}
          </button>
        ))}
      </div>
    </div>
  </div>
  )
}