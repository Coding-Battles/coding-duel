import React, { useState, useEffect, useCallback } from "react";
import { useRouter } from "next/navigation";
import { Input } from "./ui/input";
import { Button } from "./ui/button";
import {
  signInWithGoogle,
  updateUserProfile,
  useSession,
} from "@/lib/auth-client";

interface GameSetupProps {
  onProfileChange?: (username: string) => void;
}

const GameSetup: React.FC<GameSetupProps> = ({ onProfileChange }) => {
  const router = useRouter();
  const { data: session } = useSession();
  const [username, setUsername] = useState("");
  const [selectedAvatar, setSelectedAvatar] = useState<number | null>(null);
  const [selectedDifficulties, setSelectedDifficulties] = useState({
    easy: false,
    medium: true,
    hard: false,
  });
  const [isUpdatingProfile, setIsUpdatingProfile] = useState(false);
  const [usernameAvailable, setUsernameAvailable] = useState<boolean | null>(
    null
  );
  const [isCheckingUsername, setIsCheckingUsername] = useState(false);
  const [suggestedUsername, setSuggestedUsername] = useState<string>("");
  const [isGeneratedUsername, setIsGeneratedUsername] = useState(false);
  const [isGeneratingUsername, setIsGeneratingUsername] = useState(false);

  // Utility function for debouncing
  const debounce = (func: (...args: any[]) => void, delay: number) => {
    let timeoutId: NodeJS.Timeout;
    return (...args: any[]) => {
      clearTimeout(timeoutId);
      timeoutId = setTimeout(() => func(...args), delay);
    };
  };

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
  const debouncedUsernameCheck = useCallback(
    debounce((username: string) => {
      checkUsernameAvailability(username);
    }, 500),
    []
  );

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

  const handleUsernameChange = (
    value: string,
    source: "manual" | "generated" = "manual"
  ) => {
    setUsername(value);
    onProfileChange?.(value);

    // Reset states
    setUsernameAvailable(null);
    setSuggestedUsername("");
    setIsGeneratedUsername(source === "generated");

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
    setSelectedAvatar(index);
  };

  const handleDifficultySelect = (
    difficulty: keyof typeof selectedDifficulties
  ) => {
    setSelectedDifficulties((prev) => ({
      ...prev,
      [difficulty]: !prev[difficulty],
    }));
  };

  const handleStartBattle = () => {
    if (isReady) {
      router.push("/queue");
    }
  };

  // Effect to handle profile update after successful sign-in
  useEffect(() => {
    const handlePostAuthProfileUpdate = async () => {
      if (session?.user && !isUpdatingProfile) {
        const storedData = localStorage.getItem("pendingProfileData");
        if (storedData) {
          setIsUpdatingProfile(true);
          try {
            const profileData = JSON.parse(storedData);
            console.log("Updating profile with:", profileData);

            await updateUserProfile(profileData);
            localStorage.removeItem("pendingProfileData");
            console.log("Profile updated successfully");
          } catch (error) {
            console.error("Failed to update profile after sign-in:", error);
          } finally {
            setIsUpdatingProfile(false);
          }
        }
      }
    };

    handlePostAuthProfileUpdate();
  }, [session?.user, isUpdatingProfile]);

  const handleGoogleSignIn = async () => {
    try {
      // Store profile data before sign-in
      const profileData = {
        username: username.trim() || undefined,
        selectedPfp: selectedAvatar !== null ? selectedAvatar : undefined,
      };

      // Only store non-undefined values
      const filteredData = Object.fromEntries(
        Object.entries(profileData).filter(([, value]) => value !== undefined)
      );

      if (Object.keys(filteredData).length > 0) {
        localStorage.setItem(
          "pendingProfileData",
          JSON.stringify(filteredData)
        );
      }

      // Sign in with Google - useEffect will handle profile update after success
      await signInWithGoogle();
    } catch (error) {
      console.error("Google sign-in failed:", error);
      // Clean up stored data on error
      localStorage.removeItem("pendingProfileData");
    }
  };

  const getButtonText = () => {
    if (selectedAvatar === null) {
      return "SELECT FIGHTER";
    }
    return "START BATTLE";
  };

  const isReady =
    selectedAvatar !== null &&
    Object.values(selectedDifficulties).some(Boolean);

  return (
    <div className="w-full max-w-2xl mx-auto">
      {/* Main Panel */}
      <div className="bg-card rounded-3xl p-8 border border-border shadow-2xl">
        {/* Step 1: Warrior Name */}
        <div className="mb-6">
          <div className="text-primary font-semibold text-lg mb-3">
            1. Warrior Name
          </div>
          <div className="flex gap-2 items-center">
            <div className="relative w-64">
              <Input
                type="text"
                placeholder="Enter your warrior name (optional)"
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
                <span className="text-base text-muted-foreground">✨</span>
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
        <div className="mb-6">
          <div className="text-primary font-semibold text-lg mb-3">
            2. Pick Your Fighter
          </div>
          <div className="grid grid-cols-3 md:grid-cols-6 gap-2">
            {Array.from({ length: 6 }, (_, index) => (
              <button
                key={index}
                onClick={() => handleAvatarSelect(index)}
                className={`relative bg-muted rounded-lg p-2 text-center cursor-pointer
                           transition-all duration-200 border-2 hover:transform hover:-translate-y-1
                           ${
                             selectedAvatar === index
                               ? "border-ring bg-ring/10 shadow-lg shadow-ring/30 -translate-y-1"
                               : "border-transparent hover:border-ring hover:shadow-lg hover:shadow-ring/30"
                           }`}
              >
                {selectedAvatar === index && (
                  <div
                    className="absolute top-0 right-0 w-5 h-5 bg-primary rounded-full 
                                  flex items-center justify-center text-primary-foreground text-xs font-bold
                                  transform translate-x-1 -translate-y-1 border-2 border-background
                                  shadow-lg"
                  >
                    ✓
                  </div>
                )}
                <img
                  src={`/avatars/${index}.png`}
                  alt={`Avatar ${index}`}
                  className="w-full h-auto rounded-lg object-cover"
                />
              </button>
            ))}
          </div>
        </div>

        {/* Google Sign In Option */}
        <div className="mb-6">
          <Button
            variant="outline"
            className="w-full bg-background text-foreground border-border hover:bg-accent gap-2 h-11"
            onClick={handleGoogleSignIn}
          >
            <svg className="w-4 h-4" viewBox="0 0 24 24">
              <path
                fill="#4285F4"
                d="M22.56 12.25c0-.78-.07-1.53-.2-2.25H12v4.26h5.92c-.26 1.37-1.04 2.53-2.21 3.31v2.77h3.57c2.08-1.92 3.28-4.74 3.28-8.09z"
              />
              <path
                fill="#34A853"
                d="M12 23c2.97 0 5.46-.98 7.28-2.66l-3.57-2.77c-.98.66-2.23 1.06-3.71 1.06-2.86 0-5.29-1.93-6.16-4.53H2.18v2.84C3.99 20.53 7.7 23 12 23z"
              />
              <path
                fill="#FBBC05"
                d="M5.84 14.09c-.22-.66-.35-1.36-.35-2.09s.13-1.43.35-2.09V7.07H2.18C1.43 8.55 1 10.22 1 12s.43 3.45 1.18 4.93l2.85-2.22.81-.62z"
              />
              <path
                fill="#EA4335"
                d="M12 5.38c1.62 0 3.06.56 4.21 1.64l3.15-3.15C17.45 2.09 14.97 1 12 1 7.7 1 3.99 3.47 2.18 7.07l3.66 2.84c.87-2.6 3.3-4.53 6.16-4.53z"
              />
            </svg>
            Sign in with Google to save your profile and history
          </Button>
        </div>

        {/* Step 3: Pick Your Poison */}
        <div className="mb-6">
          <div className="text-primary font-semibold text-lg mb-3">
            3. Pick Your Poison
          </div>
          <div className="grid grid-cols-3 gap-3">
            {difficulties.map((diff) => (
              <button
                key={diff.key}
                onClick={() => handleDifficultySelect(diff.key)}
                className={`relative bg-muted rounded-lg p-3 text-center cursor-pointer
                           transition-all duration-200 border-2 hover:-translate-y-0.5
                           ${
                             selectedDifficulties[diff.key]
                               ? "border-ring bg-ring/10 shadow-lg shadow-ring/30"
                               : "border-transparent hover:border-ring hover:shadow-lg hover:shadow-ring/30"
                           }`}
              >
                {selectedDifficulties[diff.key] && (
                  <div
                    className="absolute top-0 right-0 w-5 h-5 bg-primary rounded-full 
                                  flex items-center justify-center text-primary-foreground text-xs font-bold
                                  transform translate-x-1 -translate-y-1 border-2 border-background
                                  shadow-lg"
                  >
                    ✓
                  </div>
                )}
                <div className="text-2xl mb-1">{diff.emoji}</div>
                <div className="font-bold text-sm text-foreground">
                  {diff.label}
                </div>
              </button>
            ))}
          </div>
        </div>

        {/* Start Battle Button */}
        <div>
          <Button
            onClick={handleStartBattle}
            disabled={!isReady}
            className={`w-full h-16 text-xl font-bold rounded-xl transition-all duration-300 uppercase tracking-wide
                       ${
                         isReady
                           ? "bg-primary text-primary-foreground hover:bg-primary/90 hover:-translate-y-1 shadow-lg shadow-primary/50 animate-pulse"
                           : "bg-muted text-muted-foreground cursor-not-allowed"
                       }`}
          >
            {getButtonText()}
          </Button>
        </div>
      </div>
    </div>
  );
};

export default GameSetup;
