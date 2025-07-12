import React from "react";
import { Button } from "./ui/button";

export interface DifficultyState {
  easy: boolean;
  medium: boolean;
  hard: boolean;
}

interface DifficultySelectorProps {
  selectedDifficulties: DifficultyState;
  onDifficultyChange: (difficulties: DifficultyState) => void;
  onEditProfile?: () => void;
  className?: string;
}

const DifficultySelector: React.FC<DifficultySelectorProps> = ({
  selectedDifficulties,
  onDifficultyChange,
  onEditProfile,
  className = "",
}) => {
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

  return (
    <div
      className={`bg-card rounded-3xl p-8 border border-border shadow-2xl relative ${className}`}
    >
      {/* Edit Profile Button */}
      {onEditProfile && (
        <Button variant="outline" size="sm" className="absolute top-4 right-4" onClick={onEditProfile}>
          <svg
            className="w-4 h-4 mr-2"
            fill="none"
            stroke="currentColor"
            viewBox="0 0 24 24"
          >
            <path
              strokeLinecap="round"
              strokeLinejoin="round"
              strokeWidth={2}
              d="M16 7a4 4 0 11-8 0 4 4 0 018 0zM12 14a7 7 0 00-7 7h14a7 7 0 00-7-7z"
            />
          </svg>
          Edit Profile
        </Button>
      )}

      {/* Step 3: Pick Your Poison */}
      <div className="mb-8">
        <div className="text-center mb-4">
          <h2 className="text-primary font-bold text-xl uppercase tracking-wide">
            PICK YOUR POISON
          </h2>
        </div>
        <div className="flex flex-col gap-4">
          {/* Selection Count */}
          <div className="text-center text-sm text-muted-foreground">
            {Object.values(selectedDifficulties).filter(Boolean).length} of 3
            difficulties selected
          </div>

          <div className="grid grid-cols-3 gap-4">
            {difficulties.map((diff) => (
              <button
                key={diff.key}
                onClick={() => handleDifficultySelect(diff.key)}
                className={`relative rounded-lg p-4 text-center cursor-pointer
                           transition-all duration-200 hover:transform hover:-translate-y-0.5 min-h-[120px]
                           ${
                             selectedDifficulties[diff.key]
                               ? "border-2 border-selected bg-selected/10 shadow-xl ring-2 ring-selected/30"
                               : "bg-background border-2 border-foreground/20 shadow-lg hover:shadow-xl hover:border-foreground/40"
                           }`}
              >
                {/* Checkbox indicator */}
                <div className="absolute top-3 left-3">
                  <div
                    className={`w-5 h-5 rounded border-2 flex items-center justify-center transition-all duration-200
                              ${
                                selectedDifficulties[diff.key]
                                  ? "bg-selected border-selected text-background"
                                  : "border-muted-foreground bg-transparent"
                              }`}
                  >
                    {selectedDifficulties[diff.key] && (
                      <span className="text-xs font-bold">✓</span>
                    )}
                  </div>
                </div>

                <div className="flex flex-col items-center justify-center h-full">
                  <div className="text-3xl mb-2">{diff.emoji}</div>
                  <div className="font-bold text-sm text-foreground">
                    {diff.label}
                  </div>
                </div>
              </button>
            ))}
          </div>
        </div>
      </div>
    </div>
  );
};

export default DifficultySelector;
