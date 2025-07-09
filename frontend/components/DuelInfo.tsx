import React from "react";
import Image from "next/image";
import GameTimer from "./GameTimer";

interface DuelInfoProps {
  timeRef?: React.RefObject<number>;
}

const DuelInfo = ({ timeRef }: DuelInfoProps) => {
  // Mock data - replace with real props/state
  const opponentData = {
    username: "CodeNinja42",
    avatar:
      "data:image/svg+xml;base64,PHN2ZyB3aWR0aD0iNjQiIGhlaWdodD0iNjQiIHZpZXdCb3g9IjAgMCA2NCA2NCIgZmlsbD0ibm9uZSIgeG1sbnM9Imh0dHA6Ly93d3cudzMub3JnLzIwMDAvc3ZnIj4KPHJlY3Qgd2lkdGg9IjY0IiBoZWlnaHQ9IjY0IiByeD0iMzIiIGZpbGw9IiNGM0Y0RjYiLz4KPHRleHQgeD0iNTAlIiB5PSI1MCUiIGZvbnQtZmFtaWx5PSJBcmlhbCwgc2Fucy1zZXJpZiIgZm9udC1zaXplPSIyNCIgZmlsbD0iIzM3NDE1MSIgdGV4dC1hbmNob3I9Im1pZGRsZSIgZG9taW5hbnQtYmFzZWxpbmU9ImNlbnRyYWwiPvCfpJY8L3RleHQ+Cjwvc3ZnPgo=", // Robot emoji as avatar
    status: "typing", // typing, running, idle, submitted
    timesRan: 3,
    timeElapsed: "04:23",
    wins: 127,
  };

  const getStatusColor = (status: string) => {
    switch (status) {
      case "typing":
        return "bg-green-500";
      case "running":
        return "bg-yellow-500";
      case "submitted":
        return "bg-blue-500";
      case "idle":
        return "bg-gray-400";
      default:
        return "bg-gray-400";
    }
  };

  const getStatusText = (status: string) => {
    switch (status) {
      case "typing":
        return "Typing...";
      case "running":
        return "Running code";
      case "submitted":
        return "Submitted!";
      case "idle":
        return "Thinking";
      default:
        return "Offline";
    }
  };

  return (
    <div className="w-full ">
      {/* Timer */}
      {timeRef && (
        <div className="mb-4 text-center">
          <GameTimer timeRef={timeRef} />
        </div>
      )}
      
      {/* Avatar */}
      <div className="flex justify-center mb-3">
        <div className="relative w-30 h-30">
          <Image
            src={opponentData.avatar}
            alt={`${opponentData.username} avatar`}
            fill
            className="rounded-full border-2 border-gray-100 object-cover"
          />
          {/* Status indicator dot */}
          <div
            className={`absolute -bottom-1 -right-1 w-4 h-4 rounded-full border-2 border-white ${getStatusColor(
              opponentData.status
            )}`}
          >
            {opponentData.status === "typing" && (
              <div className="w-full h-full rounded-full animate-pulse bg-green-400"></div>
            )}
          </div>
          {/* Speech bubble positioned absolutely */}
          <div className="absolute right-full top-0 ml-3">
            <div className="relative bg-gray-100 rounded-lg px-4 py-2 text-3xl">
              😂
              {/* Speech bubble tail pointing left */}
              <div className="absolute right-full top-1/2 transform -translate-y-1/2">
                <div className="w-0 h-0 border-t-4 border-b-4 border-l-8 border-transparent border-l-gray-100"></div>
              </div>
            </div>
          </div>
        </div>
      </div>

      {/* Username */}
      <div className="text-center mb-4">
        <p className="font-semibold text-gray-900">{opponentData.username}</p>
      </div>

      {/* Stats */}
      <div className="space-y-3">
        {/* Status */}
        <div className="flex items-center justify-center">
          <span className="text-sm text-gray-600">Status: </span>
          <div className="flex items-center gap-2">
            <span className="text-sm font-medium">
              {getStatusText(opponentData.status)}
            </span>
          </div>
        </div>

        {/* Time */}
        <div className="flex items-center justify-center">
          <span className="text-sm text-gray-600">Time: </span>
          <span className="text-sm font-mono font-medium">
            {opponentData.timeElapsed}
          </span>
        </div>

        {/* Runs */}
        <div className="flex items-center justify-center">
          <span className="text-sm text-gray-600">Code Runs: </span>
          <span className="text-sm font-medium">{opponentData.timesRan}</span>
        </div>

        {/* User Info */}
        <div className="flex items-center justify-center">
          <span className="text-sm text-gray-600">W&apos;s: </span>
          <span className="text-sm font-medium">{opponentData.wins}</span>
        </div>
      </div>

      {/* Opponent Code Preview */}
      <div className="mt-4 border-t pt-4">
        <h4 className="text-sm font-semibold text-gray-700 mb-2">
          Opponent&apos;s Code (30s delay)
        </h4>
        <div className="bg-gray-900 rounded-md p-3 text-xs font-mono text-green-400 h-80 overflow-y-auto">
          <div className="text-gray-500"># Python starter code</div>
          <div className="text-blue-400">def</div>{" "}
          <div className="text-yellow-300 inline">two_sum</div>
          <div className="text-white inline">(nums, target):</div>
          <div className="ml-4 text-gray-500"># Your solution here</div>
          <div className="ml-4 text-purple-400">pass</div>
        </div>
      </div>
    </div>
  );
};

export default DuelInfo;
