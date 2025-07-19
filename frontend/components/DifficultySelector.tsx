import React from "react";
import { Button } from "./ui/button";
import AvatarCard from "./AvatarCard";
import { useRouter } from "next/navigation";

export interface DifficultyState {
  easy: boolean;
  medium: boolean;
  hard: boolean;
}

interface DifficultySelectorProps {
  selectedDifficulties: DifficultyState;
  onDifficultyChange: (difficulties: DifficultyState) => void;
  onEditProfile?: () => void;
  onFindGame?: () => void;
  userAvatar?: string;
  userName?: string;
  className?: string;
}

const DifficultySelector: React.FC<DifficultySelectorProps> = ({
  selectedDifficulties,
  onDifficultyChange,
  onEditProfile,
  onFindGame,
  userAvatar,
  userName,
  className = "",
}) => {
  const router = useRouter();
  const difficulties = [
    {
      key: "easy" as const,
      label: "EASY",
      emoji: "😴",
    },
    {
      key: "medium" as const,
      label: "MEDIUM",
      emoji: "🔥",
    },
    {
      key: "hard" as const,
      label: "HARD",
      emoji: "💀",
    },
  ];

  const handleDifficultySelect = (difficulty: keyof DifficultyState) => {
    const newDifficulties = {
      ...selectedDifficulties,
      [difficulty]: !selectedDifficulties[difficulty],
    };
    onDifficultyChange(newDifficulties);
  };

  // Check if any difficulty is selected
  const hasSelectedDifficulty =
    Object.values(selectedDifficulties).some(Boolean);

  const handleProfileClick = () => {
    router.push("/profile");
  };

  return (
    <div className={`bg-card rounded-3xl p-8 shadow-2xl relative ${className}`}>
      {/* Step 3: Pick Your Poison */}
      <div className="mb-8">
        {/* Header: Title + Avatar */}
        <div className="flex flex-col lg:flex-row lg:items-center lg:justify-between pb-12 gap-8">
          {/* Title */}
          <div className="text-center lg:text-left flex-1">
            <h1
              className="text-4xl sm:text-6xl lg:text-7xl xl:text-8xl uppercase text-gradient font-bold tracking-wide gaming-title"
              data-text="Pick your poison"
            >
              Pick your poison
            </h1>
          </div>

          {/* User Avatar */}
          {userAvatar && userName && (
            <div className="flex justify-center lg:justify-end">
              <AvatarCard
                src={userAvatar}
                alt={`${userName} Avatar`}
                name={userName}
                size="md"
                onClick={handleProfileClick}
                clickable={true}
                player="player1"
              />
            </div>
          )}
        </div>
        <div className="flex flex-col gap-4">
          <div className="grid grid-cols-3 gap-4">
            {difficulties.map((diff) => (
              <div className="flex justify-center" key={diff.key}>
                {" "}
                {/* Add this wrapper */}
                <button
                  onClick={() => handleDifficultySelect(diff.key)}
                  className={`relative cursor-pointer focus:outline-none rounded-xl transition-all duration-300 hover:transform hover:-translate-y-2 hover:scale-105 ${
                    selectedDifficulties[diff.key]
                      ? "shadow-2xl shadow-accent/50 -translate-y-2 scale-105"
                      : ""
                  }`}
                  aria-label={`Select ${diff.label} difficulty`}
                >
                  <div
                    className={`w-50 h-50 rounded-xl p-2 transition-all duration-300 ${
                      selectedDifficulties[diff.key]
                        ? "bg-gradient-to-r from-slate-500 via-slate-300 to-slate-500 hover:from-slate-400 hover:via-slate-200 hover:to-slate-400"
                        : "border-gradient hover:shadow-xl hover:shadow-slate-500/30"
                    }`}
                  >
                    <div className="w-full h-full rounded-lg bg-background flex items-center justify-center relative overflow-hidden">
                      <span
                        className={`font-bold text-xl uppercase tracking-wider transition-colors duration-300 relative z-10 ${
                          selectedDifficulties[diff.key]
                            ? "text-slate-200 hover:text-slate-100"
                            : "text-foreground"
                        }`}
                      >
                        {diff.label}
                      </span>
                      {/* Shine effect for selected cards */}
                      {selectedDifficulties[diff.key] && (
                        <div className="absolute inset-0 -top-2 -left-2 bg-gradient-to-r from-transparent via-white/20 to-transparent rotate-45 w-8 h-20 animate-pulse opacity-50"></div>
                      )}
                    </div>
                  </div>
                </button>
              </div>
            ))}
          </div>
        </div>

        {/* Find Game Button */}
        {true && (
          <div className="text-center mt-20">
            <button
              onClick={onFindGame}
              disabled={!hasSelectedDifficulty}
              className={`relative cursor-pointer h-16 w-64 font-bold uppercase tracking-wider transition-all duration-300 transform hover:scale-105 focus:outline-none disabled:cursor-not-allowed overflow-hidden rounded-lg ${
                !hasSelectedDifficulty ? "" : "shadow-2xl shadow-accent/50"
              }`}
            >
              {/* Gradient border effect - always present */}
              <div
                className={`absolute inset-0 rounded-lg p-[2px] transition-all duration-300 ${
                  !hasSelectedDifficulty
                    ? "bg-gradient-to-r from-slate-800 via-slate-700 to-slate-800"
                    : "bg-gradient-to-r from-slate-500 via-slate-300 to-slate-500 hover:from-slate-400 hover:via-slate-200 hover:to-slate-400"
                }`}
              >
                <div className="w-full h-full rounded-md bg-background flex items-center justify-center">
                  <span
                    className={`relative z-10 transition-colors duration-300 ${
                      !hasSelectedDifficulty
                        ? "text-slate-500"
                        : "text-slate-200 hover:text-slate-100"
                    }`}
                  >
                    Find Game
                  </span>
                </div>
              </div>

              {/* Shine effect when ready */}
              {hasSelectedDifficulty && (
                <div className="absolute inset-0 -top-2 -left-2 bg-gradient-to-r from-transparent via-white/20 to-transparent rotate-45 w-8 h-20 animate-pulse opacity-50"></div>
              )}
            </button>
          </div>
        )}
      </div>
    </div>
  );
};

export default DifficultySelector;
