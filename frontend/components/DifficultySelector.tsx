import React from "react";

export interface DifficultyState {
  easy: boolean;
  medium: boolean;
  hard: boolean;
}

interface DifficultySelectorProps {
  selectedDifficulties: DifficultyState;
  onDifficultyChange: (difficulties: DifficultyState) => void;
  className?: string;
}

const DifficultySelector: React.FC<DifficultySelectorProps> = ({
  selectedDifficulties,
  onDifficultyChange,
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
      <button className="absolute top-4 right-4 flex items-center gap-2 px-3 py-2 rounded-lg bg-gradient-to-r from-orange-500/20 to-amber-500/20 border border-orange-500/30 text-orange-500 hover:from-orange-500/30 hover:to-amber-500/30 hover:border-orange-400 transition-all duration-200 text-sm font-medium group">
        <svg className="w-4 h-4 group-hover:scale-110 transition-transform duration-200" fill="none" stroke="currentColor" viewBox="0 0 24 24">
          <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M16 7a4 4 0 11-8 0 4 4 0 018 0zM12 14a7 7 0 00-7 7h14a7 7 0 00-7-7z" />
        </svg>
        <span>Edit Profile</span>
      </button>

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
                               ? "border-2 border-transparent bg-gradient-to-br from-muted via-background to-muted shadow-xl shadow-primary/20 ring-2 ring-primary/30"
                               : "bg-gradient-to-br from-muted via-muted/80 to-muted border-2 border-border/50 shadow-lg hover:shadow-xl hover:from-muted/90 hover:to-muted/90 hover:border-border"
                           }`}
                style={
                  selectedDifficulties[diff.key]
                    ? {
                        background:
                          "linear-gradient(135deg, hsl(var(--muted)), hsl(var(--background)), hsl(var(--muted))) padding-box, linear-gradient(to right, rgb(251 191 36), rgb(251 146 60), rgb(248 113 113)) border-box",
                      }
                    : {}
                }
              >
                {/* Checkbox indicator */}
                <div className="absolute top-3 left-3">
                  <div
                    className={`w-5 h-5 rounded border-2 flex items-center justify-center transition-all duration-200
                              ${
                                selectedDifficulties[diff.key]
                                  ? "bg-orange-500 border-orange-500 text-white"
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
