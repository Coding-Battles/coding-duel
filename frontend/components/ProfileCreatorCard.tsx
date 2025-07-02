import React, { useState, useEffect } from "react";
import Image from "next/image";
import { Input } from "./ui/input";
import { Button } from "./ui/button";
import {
  updateUserProfile,
  useSession,
  signOut,
  getUserProfile,
} from "@/lib/auth-client";
import GoogleSignInButton from "./GoogleSignInButton";

interface GameSetupProps {
  onProfileChange?: (username: string) => void;
}

const GameSetup: React.FC<GameSetupProps> = ({ onProfileChange }) => {
  const { data: session } = useSession();
  const [username, setUsername] = useState("");
  const [selectedAvatar, setSelectedAvatar] = useState<number | null>(null);
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

  // Type-safe debounce utility function
  const debounce = <T extends (...args: never[]) => void>(
    func: T,
    delay: number
  ): T => {
    let timeoutId: NodeJS.Timeout;
    return ((...args: Parameters<T>) => {
      clearTimeout(timeoutId);
      timeoutId = setTimeout(() => func(...args), delay);
    }) as T;
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
  const debouncedUsernameCheck = debounce((username: string) => {
    checkUsernameAvailability(username);
  }, 500);


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



  // Load form state on component mount
  useEffect(() => {
    loadFormState();
  }, []);

  // Load existing profile data when user logs in
  useEffect(() => {
    const loadUserProfile = async () => {
      if (session?.user) {
        try {
          console.log("Loading profile for logged in user. Current state:", {
            username,
            selectedAvatar,
          });
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
            if (
              profileData.selectedPfp !== undefined &&
              selectedAvatar === null
            ) {
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
