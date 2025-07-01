import React, { useState, useEffect, useCallback } from "react";
import { useRouter } from "next/navigation";
import { Input } from "./ui/input";
import { Button } from "./ui/button";
import { updateUserProfile, useSession, signOut, getUserProfile } from "@/lib/auth-client";
import GoogleSignInButton from "./GoogleSignInButton";

interface GameSetupProps {
  onProfileChange?: (username: string) => void;
}

const GameSetup: React.FC<GameSetupProps> = ({ onProfileChange }) => {
  const router = useRouter();
  const { data: session } = useSession();
  const [username, setUsername] = useState("");
  const [selectedAvatar, setSelectedAvatar] = useState<number | null>(null);
  const [selectedDifficulties, setSelectedDifficulties] = useState({
    easy: true,
    medium: false,
    hard: false,
  });
  const [isUpdatingProfile, setIsUpdatingProfile] = useState(false);
  const [usernameAvailable, setUsernameAvailable] = useState<boolean | null>(
    null
  );
  const [isCheckingUsername, setIsCheckingUsername] = useState(false);
  const [suggestedUsername, setSuggestedUsername] = useState<string>("");
  const [isGeneratingUsername, setIsGeneratingUsername] = useState(false);

  // localStorage key for form state
  const FORM_STATE_KEY = "profile-form-state";

  // Save form state to localStorage
  const saveFormState = () => {
    const state = {
      username,
      selectedAvatar,
      selectedDifficulties,
      timestamp: Date.now(),
    };
    localStorage.setItem(FORM_STATE_KEY, JSON.stringify(state));
  };

  // Load form state from localStorage
  const loadFormState = () => {
    try {
      const savedState = localStorage.getItem(FORM_STATE_KEY);
      if (savedState) {
        const state = JSON.parse(savedState);
        // Only load if saved within last 24 hours
        if (Date.now() - state.timestamp < 24 * 60 * 60 * 1000) {
          if (state.username) setUsername(state.username);
          if (
            state.selectedAvatar !== null &&
            state.selectedAvatar !== undefined
          ) {
            setSelectedAvatar(state.selectedAvatar);
          }
          if (state.selectedDifficulties) {
            setSelectedDifficulties(state.selectedDifficulties);
          }
        }
      }
    } catch (error) {
      console.error("Error loading form state:", error);
    }
  };

  // Clear form state from localStorage
  const clearFormState = () => {
    localStorage.removeItem(FORM_STATE_KEY);
  };

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

    if (source === "generated") {
      // Generated usernames are guaranteed to be available
      setUsernameAvailable(true);
    } else {
      // Debounced availability check for manually typed usernames
      if (value.trim()) {
        debouncedUsernameCheck(value.trim());
      }
    }

    // Save to localStorage
    setTimeout(saveFormState, 100); // Small delay to ensure state is updated
  };

  const handleAvatarSelect = (index: number) => {
    setSelectedAvatar(index);
    // Save to localStorage
    setTimeout(saveFormState, 100);
  };

  const handleDifficultySelect = (
    difficulty: keyof typeof selectedDifficulties
  ) => {
    setSelectedDifficulties((prev) => ({
      ...prev,
      [difficulty]: !prev[difficulty],
    }));
    // Save to localStorage
    setTimeout(saveFormState, 100);
  };

  const handleStartBattle = () => {
    if (isReady) {
      router.push("/queue");
    }
  };

  // Load form state on component mount
  useEffect(() => {
    loadFormState();
  }, []);

  // Load existing profile data when user logs in
  useEffect(() => {
    const loadUserProfile = async () => {
      if (session?.user) {
        try {
          console.log("Loading profile for logged in user. Current state:", { username, selectedAvatar });
          const profileData = await getUserProfile();
          console.log("Retrieved profile data:", profileData);
          
          if (profileData) {
            // Load username if current username is empty
            if (profileData.username && !username.trim()) {
              console.log("Loading username:", profileData.username);
              setUsername(profileData.username);
              onProfileChange?.(profileData.username);
            }
            
            // Load avatar if current avatar is null
            if (profileData.selectedPfp !== undefined && selectedAvatar === null) {
              console.log("Loading avatar:", profileData.selectedPfp);
              setSelectedAvatar(profileData.selectedPfp);
            }
          }
        } catch (error) {
          console.error("Failed to load user profile:", error);
        }
      }
    };

    loadUserProfile();
  }, [session?.user, username, selectedAvatar, onProfileChange]);

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
            // Clear form state after successful profile update
            clearFormState();
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

  const getButtonText = () => {
    if (!username.trim()) {
      return "ENTER USERNAME";
    }
    if (selectedAvatar === null) {
      return "SELECT FIGHTER";
    }
    if (!Object.values(selectedDifficulties).some(Boolean)) {
      return "SELECT DIFFICULTY";
    }
    return "START BATTLE";
  };

  const isReady =
    username.trim().length > 0 &&
    selectedAvatar !== null &&
    Object.values(selectedDifficulties).some(Boolean);

  return (
    <div className="w-full max-w-4xl mx-auto">
      {/* Main Panel */}
      <div className="bg-card rounded-3xl p-8 border border-border shadow-2xl">
        {/* Step 1: Warrior Name */}
        {/* Hello Claude */}
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
                                  shadow-lg shadow-orange-500/50 ring-2 ring-yellow-300/50
"
                  >
                    ⚔️
                  </div>
                )}
                <img
                  src={`/avatars/${index}.png`}
                  alt={`Avatar ${index}`}
                  className={`w-full h-auto rounded object-cover bg-muted transition-all duration-200 ${
                    selectedAvatar === index ? "scale-115 drop-shadow-lg" : ""
                  }`}
                />
              </button>
            ))}
          </div>
        </div>

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

        {/* Start Battle Button */}
        <div>
          <Button
            onClick={handleStartBattle}
            disabled={!isReady}
            className={`w-full h-16 text-xl font-bold rounded-xl transition-all duration-300 uppercase tracking-wide
                       ${
                         isReady
                           ? "bg-primary text-primary-foreground hover:bg-primary/90 hover:-translate-y-1 shadow-lg shadow-primary/50"
                           : "bg-muted text-muted-foreground cursor-not-allowed"
                       }`}
          >
            {getButtonText()}
          </Button>
        </div>

        {/* Auth Section */}
        <div className="mt-8 pt-6 border-t border-border/50">
          <div className="text-center">
            <p className="text-sm text-muted-foreground mb-4">
              Save profile info by logging in
            </p>
            <div className="flex justify-center">
              {session ? (
                <button
                  onClick={() => signOut()}
                  className="px-4 py-2 bg-red-600 text-white rounded-lg hover:bg-red-700 transition-all duration-200 text-sm font-medium"
                >
                  Logout
                </button>
              ) : (
                <GoogleSignInButton 
                  className="px-4 py-2 text-sm font-medium"
                  username={username}
                  selectedAvatar={selectedAvatar ?? undefined}
                >
                  Sign In
                </GoogleSignInButton>
              )}
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};

export default GameSetup;
