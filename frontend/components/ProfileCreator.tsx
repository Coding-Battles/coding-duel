import React, { useState, useEffect } from "react";
import Image from "next/image";
import { Input } from "./ui/input";
import { Button } from "./ui/button";

interface ProfileCreatorProps {
  username: string;
  onUsernameChange: (username: string) => void;
  selectedAvatar: number | null;
  onAvatarChange: (avatar: number) => void;
  onComplete?: () => void;
  className?: string;
}

const ProfileCreator: React.FC<ProfileCreatorProps> = ({
  username,
  onUsernameChange,
  selectedAvatar,
  onAvatarChange,
  onComplete,
  className = ""
}) => {
  const [usernameAvailable, setUsernameAvailable] = useState<boolean | null>(null);
  const [isCheckingUsername, setIsCheckingUsername] = useState(false);
  const [suggestedUsername, setSuggestedUsername] = useState<string>("");
  const [isGeneratingUsername, setIsGeneratingUsername] = useState(false);

  // Type-safe debounce utility function
  function debounce<Args extends readonly unknown[]>(
    func: (...args: Args) => void,
    delay: number
  ): (...args: Args) => void {
    let timeoutId: NodeJS.Timeout;
    return (...args: Args) => {
      clearTimeout(timeoutId);
      timeoutId = setTimeout(() => func(...args), delay);
    };
  }

  // API utility functions
  const checkUsernameAvailability = async (username: string) => {
    if (!username.trim()) return;

    setIsCheckingUsername(true);
    try {
      const response = await fetch(
        "http://localhost:8000/api/users/check-username",
        {
          method: "POST",
          headers: { "Content-Type": "application/json" },
          body: JSON.stringify({ username }),
        }
      );

      if (!response.ok) {
        const text = await response.text();
        console.error("API Error:", response.status, text);
        throw new Error(`HTTP ${response.status}: ${text}`);
      }

      const data = await response.json();
      setUsernameAvailable(data.available);

      // If not available, get suggestion
      if (!data.available) {
        const suggestionResponse = await fetch(
          "http://localhost:8000/api/users/available-username",
          {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({ username }),
          }
        );

        if (!suggestionResponse.ok) {
          const text = await suggestionResponse.text();
          console.error(
            "Suggestion API Error:",
            suggestionResponse.status,
            text
          );
          return;
        }

        const suggestionData = await suggestionResponse.json();
        setSuggestedUsername(suggestionData.available);
      } else {
        setSuggestedUsername("");
      }
    } catch (error) {
      console.error("Error checking username:", error);
      setUsernameAvailable(null);
    } finally {
      setIsCheckingUsername(false);
    }
  };

  const generateAiUsername = async () => {
    setIsGeneratingUsername(true);
    try {
      const response = await fetch(
        "http://localhost:8000/api/users/generate-username",
        {
          method: "POST",
          headers: { "Content-Type": "application/json" },
          body: JSON.stringify({ count: 1 }),
        }
      );

      if (!response.ok) {
        const text = await response.text();
        console.error("AI Generation API Error:", response.status, text);
        throw new Error(`HTTP ${response.status}: ${text}`);
      }

      const data = await response.json();
      // Directly fill the input with the generated username
      if (data.usernames && data.usernames[0]) {
        handleUsernameChange(data.usernames[0], "generated");
      }
    } catch (error) {
      console.error("Error generating username:", error);
    } finally {
      setIsGeneratingUsername(false);
    }
  };

  // Debounced username checking
  const debouncedUsernameCheck = debounce((username: string) => {
    checkUsernameAvailability(username);
  }, 500);

  const handleUsernameChange = (
    value: string,
    source: "manual" | "generated" = "manual"
  ) => {
    onUsernameChange(value);

    // Reset states
    setUsernameAvailable(null);
    setSuggestedUsername("");

    if (source === "generated") {
      // Generated usernames are guaranteed to be available
      setUsernameAvailable(true);
    } else {
      // Debounced availability check for manually typed usernames
      if (value.trim()) {
        debouncedUsernameCheck(value.trim());
      }
    }
  };

  const handleAvatarSelect = (index: number) => {
    onAvatarChange(index);
  };

  return (
    <div className={`bg-card rounded-3xl p-8 border border-border shadow-2xl ${className}`}>
      {/* Step 1: Warrior Name */}
      <div className="mb-8">
        <div className="text-center mb-4">
          <h2 className="text-primary font-bold text-xl uppercase tracking-wide">
            FORGE YOUR IDENTITY
          </h2>
        </div>
        <div className="flex gap-2 items-center justify-center">
          <div className="relative w-64">
            <Input
              type="text"
              placeholder="Enter your username"
              value={username}
              onChange={(e) => handleUsernameChange(e.target.value)}
              className="w-full h-12 bg-input border-2 border-border rounded-lg px-3 pr-10 text-foreground text-base
                         focus:border-ring focus:ring-2 focus:ring-ring/20 focus:outline-none
                         transition-all duration-200"
              maxLength={20}
            />

            {/* Availability indicator */}
            {username && (
              <div className="absolute right-3 top-1/2 transform -translate-y-1/2">
                {isCheckingUsername ? (
                  <div className="w-4 h-4 border-2 border-ring border-t-transparent rounded-full animate-spin" />
                ) : usernameAvailable === true ? (
                  <span className="text-green-500 text-xl">✓</span>
                ) : usernameAvailable === false ? (
                  <span className="text-red-500 text-xl">✗</span>
                ) : null}
              </div>
            )}
          </div>

          {/* Generate button */}
          <Button
            type="button"
            variant="ghost"
            size="icon"
            onClick={generateAiUsername}
            disabled={isGeneratingUsername}
            className="shrink-0 h-12 w-12 bg-muted/50 hover:bg-muted
                       border border-border hover:border-ring
                       transition-all duration-200 hover:scale-105 active:scale-95
                       cursor-pointer disabled:cursor-not-allowed disabled:opacity-50"
            title="Generate AI username"
          >
            {isGeneratingUsername ? (
              <div className="w-4 h-4 border-2 border-muted-foreground border-t-transparent rounded-full animate-spin" />
            ) : (
              <span className="text-lg">🎲</span>
            )}
          </Button>
        </div>

        {/* Username suggestions */}
        {usernameAvailable === false && suggestedUsername && (
          <p className="text-sm text-muted-foreground mt-2">
            &ldquo;{username}&rdquo; is taken. Try{" "}
            <button
              onClick={() =>
                handleUsernameChange(suggestedUsername, "generated")
              }
              className="text-primary hover:underline font-medium"
            >
              &ldquo;{suggestedUsername}&rdquo;
            </button>
            ?
          </p>
        )}
      </div>

      {/* Step 2: Pick Your Fighter */}
      <div className="mb-8">
        <div className="text-center mb-4">
          <h2 className="text-primary font-bold text-xl uppercase tracking-wide">
            CHOOSE YOUR FIGHTER
          </h2>
        </div>
        <div className="grid grid-cols-6 gap-3">
          {Array.from({ length: 6 }, (_, index) => (
            <button
              key={index}
              onClick={() => handleAvatarSelect(index)}
              className={`relative rounded-lg p-1 text-center cursor-pointer overflow-hidden
                         transition-all duration-200 hover:transform hover:-translate-y-1
                         ${
                           selectedAvatar === index
                             ? "bg-gradient-to-r from-yellow-400 via-orange-400 to-red-400 shadow-xl shadow-orange-500/70 -translate-y-1 ring-4 ring-yellow-300 scale-105"
                             : "bg-gradient-to-r from-slate-400 via-slate-500 to-slate-600 hover:shadow-lg hover:shadow-slate-500/30"
                         }`}
            >
              {selectedAvatar === index && (
                <div
                  className="absolute -top-1 -right-1 w-6 h-6 bg-gradient-to-br from-yellow-400 to-orange-500 rounded-full 
                            flex items-center justify-center text-white text-sm font-bold
                            shadow-lg shadow-orange-500/50 ring-2 ring-yellow-300/50"
                >
                  ⚔️
                </div>
              )}
              <Image
                src={`/avatars/${index}.png`}
                alt={`Avatar ${index}`}
                width={100}
                height={100}
                className={`w-full h-auto rounded object-cover bg-muted transition-all duration-200 ${
                  selectedAvatar === index ? "scale-115 drop-shadow-lg" : ""
                }`}
              />
            </button>
          ))}
        </div>
      </div>

      {/* Next Button */}
      {onComplete && (
        <div className="mt-8 text-center">
          <Button
            onClick={onComplete}
            disabled={!username.trim() || selectedAvatar === null}
            className={`px-8 py-3 text-lg font-medium rounded-xl transition-all duration-300 uppercase tracking-wide
                       ${
                         username.trim() && selectedAvatar !== null
                           ? "bg-primary text-primary-foreground hover:bg-primary/90 hover:-translate-y-1 shadow-lg shadow-primary/50"
                           : "bg-muted text-muted-foreground cursor-not-allowed"
                       }`}
          >
            {!username.trim() ? "Enter Username" : selectedAvatar === null ? "Select Avatar" : "Next"}
          </Button>
        </div>
      )}
    </div>
  );
};

export default ProfileCreator;