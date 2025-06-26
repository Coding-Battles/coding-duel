import React from 'react';
import { User, Calendar, Trophy, TrendingUp, Clock, CheckCircle, XCircle, Circle,ArrowLeft, ArrowLeftSquare } from 'lucide-react';
import { ProfileBar } from './components/ProfileBar';
import { UserStats } from '@/interfaces/UserStats';
import Link from "next/link";

interface Problem {
  id: number;
  title: string;
  difficulty: 'Easy' | 'Medium' | 'Hard';
  status: 'Solved' | 'Attempted' | 'Not Attempted';
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
    streak: 23
  };

  const recentSubmissions: Problem[] = [
    {
      id: 1,
      title: "Two Sum",
      difficulty: "Easy",
      status: "Solved",
      category: "Array",
      submittedAt: "2 hours ago"
    },
    {
      id: 42,
      title: "Trapping Rain Water",
      difficulty: "Hard",
      status: "Solved",
      category: "Dynamic Programming",
      submittedAt: "1 day ago"
    },
    {
      id: 15,
      title: "3Sum",
      difficulty: "Medium",
      status: "Attempted",
      category: "Array",
      submittedAt: "2 days ago"
    },
    {
      id: 739,
      title: "Daily Temperatures",
      difficulty: "Medium",
      status: "Solved",
      category: "Stack",
      submittedAt: "3 days ago"
    }
  ];

  const getDifficultyColor = (difficulty: string): string => {
    switch (difficulty) {
      case 'Easy': return 'text-green-600 bg-green-100';
      case 'Medium': return 'text-yellow-600 bg-yellow-100';
      case 'Hard': return 'text-red-600 bg-red-100';
      default: return 'text-gray-600 bg-gray-100';
    }
  };

  const getStatusIcon = (status: string) => {
    switch (status) {
      case 'Solved': return <CheckCircle className="w-4 h-4 text-green-600" />;
      case 'Attempted': return <XCircle className="w-4 h-4 text-red-600" />;
      default: return <Circle className="w-4 h-4 text-gray-400" />;
    }
  };

  const progressPercentage = (solved: number, total: number = 1000): number => {
    return Math.round((solved / total) * 100);
  };

  return (
    <div className="max-w-6xl mx-auto p-6 bg-gray-50 min-h-screen">
      <Link href="/" className="text-blue-600 absolute top-2 left-2 w-8 h-8 hover:text-blue-300 transition-colors cursor-pointer">
        <ArrowLeftSquare className="w-full h-full" />
      </Link>
      {/* Header */}
      <div className="bg-white rounded-lg shadow-md p-6 mb-6">
        <ProfileBar/>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        {/* Stats Panel */}
        <div className="lg:col-span-1">
          <div className="bg-white rounded-lg shadow-md p-6 mb-6">
            <h2 className="text-lg font-semibold text-gray-800 mb-4">Statistics</h2>
            
            {/* Total Solved */}
            <div className="mb-6">
              <div className="flex justify-between items-center mb-2">
                <span className="text-gray-600">Total Battles</span>
                <span className="font-bold text-2xl text-gray-800">{userStats.totalSolved}</span>
              </div>
              <div className="w-full bg-gray-200 rounded-full h-2">
                <div 
                  className="bg-green-600 h-2 rounded-full" 
                  style={{ width: `${progressPercentage(userStats.totalSolved)}%` }}
                ></div>
              </div>
            </div>

            {/* Difficulty Breakdown */}
            <div className="space-y-3 mb-6">
              <div className="flex justify-between items-center">
                <span className="text-green-600 font-medium">Easy</span>
                <span className="font-semibold">{userStats.easySolved}</span>
              </div>
              <div className="flex justify-between items-center">
                <span className="text-yellow-600 font-medium">Medium</span>
                <span className="font-semibold">{userStats.mediumSolved}</span>
              </div>
              <div className="flex justify-between items-center">
                <span className="text-red-600 font-medium">Hard</span>
                <span className="font-semibold">{userStats.hardSolved}</span>
              </div>
            </div>

            {/* Additional Stats */}
            <div className="border-t pt-4 space-y-3">
              <div className="flex justify-between items-center">
                <span className="text-gray-600">Win Rate</span>
                <span className="font-semibold text-green-600">{userStats.acceptanceRate}%</span>
              </div>
              <div className="flex justify-between items-center">
                <span className="text-gray-600">Total Submissions</span>
                <span className="font-semibold">{userStats.totalSubmissions.toLocaleString()}</span>
              </div>
            </div>
          </div>
        </div>

        {/* Recent Activity */}
        <div className="lg:col-span-2">
          <div className="bg-white rounded-lg shadow-md p-6">
            <h2 className="text-lg font-semibold text-gray-800 mb-4">Recent Submissions</h2>
            
            <div className="space-y-3">
              {recentSubmissions.map((problem) => (
                <div key={problem.id} className="border rounded-lg p-4 hover:bg-gray-50 transition-colors">
                  <div className="flex items-center justify-between">
                    <div className="flex items-center space-x-3">
                      {getStatusIcon(problem.status)}
                      <div>
                        <h3 className="font-medium text-gray-800">{problem.title}</h3>
                        <div className="flex items-center space-x-2 mt-1">
                          <span className={`px-2 py-1 rounded text-xs font-medium ${getDifficultyColor(problem.difficulty)}`}>
                            {problem.difficulty}
                          </span>
                          <span className="text-xs text-gray-500">{problem.category}</span>
                        </div>
                      </div>
                    </div>
                    <div className="text-right">
                      <div className="flex items-center space-x-1 text-sm text-gray-500">
                        <Clock className="w-4 h-4" />
                        <span>{problem.submittedAt}</span>
                      </div>
                    </div>
                  </div>
                </div>
              ))}
            </div>

            <div className="mt-6 text-center">
              <button className="bg-orange-500 hover:bg-orange-600 text-white px-6 py-2 rounded-lg font-medium transition-colors">
                View All Submissions
              </button>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};

export default LeetCodeProfile;