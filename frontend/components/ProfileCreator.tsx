import React, { useState, useRef, useCallback, ChangeEvent } from "react";
import Image from "next/image";
import { Input } from "./ui/input";
import { Button } from "./ui/button";
import { Dices, Upload } from "lucide-react";
import {
  Carousel,
  CarouselContent,
  CarouselItem,
  CarouselNext,
  CarouselPrevious,
} from "./ui/carousel";
import { WheelGesturesPlugin } from "embla-carousel-wheel-gestures";

interface ProfileCreatorProps {
  username: string;
  onUsernameChange: (username: string) => void;
  selectedAvatar: number | null;
  onAvatarChange: (avatar: number) => void;
  customAvatar?: string | null;
  onCustomAvatarChange?: (avatarUrl: string | null) => void;
  userId?: string;
  onComplete?: () => void;
  className?: string;
  isGuestMode?: boolean;
}

const ProfileCreator: React.FC<ProfileCreatorProps> = ({
  username,
  onUsernameChange,
  selectedAvatar,
  onAvatarChange,
  customAvatar,
  onCustomAvatarChange,
  userId,
  onComplete,
  className = "",
  isGuestMode = false,
}) => {
  const [usernameAvailable, setUsernameAvailable] = useState<boolean | null>(
    null
  );
  const [suggestedUsername, setSuggestedUsername] = useState<string>("");
  const [isGeneratingUsername, setIsGeneratingUsername] = useState(false);
  const [isPoweringUp, setIsPoweringUp] = useState(false);
  const [justValidated, setJustValidated] = useState(false);
  const [lastValidatedUsername, setLastValidatedUsername] =
    useState<string>("");
  const [currentCheckingUsername, setCurrentCheckingUsername] =
    useState<string>("");
  const fileInputRef = useRef<HTMLInputElement>(null);
  const currentUsernameRef = useRef<string>("");
  const [carouselApi, setCarouselApi] = useState<any>(null);

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

    console.log("Checking username:", username);
    setCurrentCheckingUsername(username);

    // Skip API call in guest mode - always mark as available
    if (isGuestMode) {
      console.log("Guest mode: Marking username as available");
      if (username === currentUsernameRef.current) {
        setUsernameAvailable(true);
        if (username !== lastValidatedUsername) {
          setLastValidatedUsername(username);
          setJustValidated(true);
          setTimeout(() => setJustValidated(false), 600);
        }
      }
      setSuggestedUsername("");
      return;
    }

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
      console.log("API response:", data.available);
      console.log("Setting usernameAvailable to:", data.available);

      // Only update state if this response is for the current username in the input
      if (username === currentUsernameRef.current) {
        setUsernameAvailable(data.available);
      } else {
        console.log("Ignoring stale response for:", username);
      }

      // Only trigger success animation if username is available AND it's different from last validated
      if (data.available && username !== lastValidatedUsername) {
        setLastValidatedUsername(username);
        setJustValidated(true);
        setTimeout(() => setJustValidated(false), 600);
      }

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
      console.log("Setting usernameAvailable to null - error");
      setUsernameAvailable(null);
    }
  };

  const generateAiUsername = async () => {
    setIsGeneratingUsername(true);
    setIsPoweringUp(true);
    try {
      // Use API for both guest and authenticated mode
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
      console.log("🎲 [USERNAME DEBUG] API Response:", data);
      
      // Check for error response
      if (data.error) {
        console.error("🎲 [USERNAME DEBUG] API returned error:", data.error);
        throw new Error(data.error);
      }
      
      // Directly fill the input with the generated username
      if (data.usernames && data.usernames[0]) {
        console.log("🎲 [USERNAME DEBUG] Using username:", data.usernames[0]);
        handleUsernameChange(data.usernames[0], "generated");
      } else {
        console.warn("🎲 [USERNAME DEBUG] No usernames in response:", data);
        throw new Error("No usernames generated by AI service");
      }
    } catch (error) {
      console.error("Error generating username:", error);
    } finally {
      setIsGeneratingUsername(false);
      setTimeout(() => setIsPoweringUp(false), 300);
    }
  };

  // Debounced username checking
  const debouncedUsernameCheck = useCallback(
    debounce((username: string) => {
      checkUsernameAvailability(username);
    }, 1000),
    []
  );

  const handleUsernameChange = (
    value: string,
    source: "manual" | "generated" = "manual"
  ) => {
    onUsernameChange(value);
    currentUsernameRef.current = value;

    // Reset states
    console.log("Setting usernameAvailable to null - user typing");
    setUsernameAvailable(null);
    setSuggestedUsername("");

    // Only reset justValidated if the username actually changed
    if (value !== lastValidatedUsername) {
      setJustValidated(false);
    }

    if (source === "generated") {
      // Generated usernames are guaranteed to be available
      setUsernameAvailable(true);
      // Only trigger animation if it's a new username
      if (value !== lastValidatedUsername) {
        setLastValidatedUsername(value);
        setJustValidated(true);
        setTimeout(() => setJustValidated(false), 600);
      }
    } else {
      // Clear last validated username when manually typing
      if (value !== lastValidatedUsername) {
        setLastValidatedUsername("");
      }
      // Debounced availability check for manually typed usernames
      if (value.trim()) {
        debouncedUsernameCheck(value.trim());
      }
    }
  };

  const handleAvatarSelect = useCallback(
    (index: number) => {
      onAvatarChange(index);
      // Clear custom avatar when selecting default avatar
      if (onCustomAvatarChange) {
        onCustomAvatarChange(null);
      }
    },
    [onAvatarChange, onCustomAvatarChange]
  );

  const handleAvatarPreviewClick = () => {
    fileInputRef.current?.click();
  };

  const handleFileSelect = async (event: ChangeEvent<HTMLInputElement>) => {
    const file = event.target.files?.[0];
    if (!file) return;

    // Skip file upload in guest mode
    if (isGuestMode) {
      console.log("Guest mode: File upload disabled");
      event.target.value = "";
      return;
    }

    // Validate file
    if (file.size > 5 * 1024 * 1024) {
      console.error("File size must be less than 5MB");
      return;
    }

    const validTypes = ["image/jpeg", "image/png", "image/gif", "image/webp"];
    if (!validTypes.includes(file.type)) {
      console.error(
        "Please select a valid image file (JPEG, PNG, GIF, or WebP)"
      );
      return;
    }

    // Upload file
    try {
      const formData = new FormData();
      formData.append("image", file);

      const endpoint = `${process.env.NEXT_PUBLIC_API_BASE_URL}/api/image/${userId}`;
      const response = await fetch(endpoint, {
        method: "POST",
        body: formData,
      });

      const data = await response.json();

      if (response.ok) {
        if (onCustomAvatarChange) {
          onCustomAvatarChange(data.path);
        }
        // Set custom avatar as selected
        onAvatarChange(999); // Use 999 to indicate custom avatar
      } else {
        console.error("Upload failed:", data);
      }
    } catch (error) {
      console.error("Upload error:", error);
    }

    // Clear file input
    event.target.value = "";
  };

  return (
    <div className={`relative ${className}`}>
      {/* Content container */}
      <div className="relative">
        {/* Main vertical spacing container - now includes the title */}
        <div className="">
          {/* Main Title */}
          <div className="text-center pu-12">
            <h1
              className="text-4xl sm:text-6xl lg:text-6xl uppercase text-gradient font-bold tracking-wide gaming-title"
              data-text="Choose your fighter"
            >
              Choose your fighter
            </h1>
          </div>

          {/* Avatar Selection Carousel */}
          <div className="overflow-visible">
            <div className="px-16 overflow-visible">
              <Carousel
                plugins={[
                  WheelGesturesPlugin({
                    forceWheelAxis: "x",
                    threshold: 20,
                  }),
                ]}
                opts={{
                  align: "start",
                  loop: false,
                  skipSnaps: true,
                  dragFree: true,
                  containScroll: "trimSnaps",
                }}
                setApi={setCarouselApi}
                className="w-full max-w-4xl mx-auto"
              >
                <CarouselContent className="ml-0 md:ml-0 px-3 py-18 overflow-visible">
                  {/* Upload Custom Avatar Item - Hide in guest mode */}
                  {!isGuestMode && (
                    <CarouselItem className="pl-2 md:pl-4 basis-1/3 px-2">
                      <button
                        onClick={handleAvatarPreviewClick}
                        className="relative w-full cursor-pointer focus:outline-none rounded-xl"
                        aria-label="Upload Custom Avatar"
                      >
                        <div className="w-full aspect-square rounded-xl p-2 border-gradient hover:shadow-xl hover:shadow-slate-500/30 transition-all duration-300 hover:transform hover:-translate-y-2 hover:scale-105">
                          <div className="w-full h-full flex flex-col items-center justify-center text-muted-foreground hover:text-accent">
                            <Upload className="w-8 h-8 mb-2" />
                            <span className="text-sm font-medium mb-1">
                              Upload
                            </span>
                          </div>
                        </div>
                      </button>
                    </CarouselItem>
                  )}

                  {/* Default Avatar Items */}
                  {Array.from({ length: 6 }, (_, index) => (
                    <CarouselItem
                      key={index}
                      className="pl-2 md:pl-4 basis-1/3 px-2"
                    >
                      <button
                        onClick={() => handleAvatarSelect(index)}
                        className="relative w-full cursor-pointer focus:outline-none rounded-xl"
                        aria-label={`Select Avatar ${index + 1}`}
                      >
                        <div
                          className={`w-full aspect-square rounded-xl p-2 transition-all duration-300 hover:transform hover:-translate-y-2 ${
                            selectedAvatar === index
                              ? "selected-gradient shadow-2xl shadow-accent/50 -translate-y-2 scale-105"
                              : "border-gradient hover:shadow-xl hover:shadow-slate-500/30 hover:scale-105"
                          }`}
                        >
                          <Image
                            src={`/avatars/${index}.png`}
                            alt={`Avatar ${index + 1}`}
                            width={160}
                            height={160}
                            className="w-full h-full rounded-lg object-cover bg-muted"
                            priority={index < 4}
                          />
                        </div>
                      </button>
                    </CarouselItem>
                  ))}

                  {/* Custom Avatar Item (if uploaded) */}
                  {selectedAvatar === 999 && customAvatar && (
                    <CarouselItem className="pl-2 md:pl-4 basis-1/3 px-2">
                      <button
                        onClick={() => handleAvatarSelect(999)}
                        className="relative w-full cursor-pointer focus:outline-none rounded-xl"
                        aria-label="Select Custom Avatar"
                      >
                        <div className="w-full aspect-square rounded-xl p-2 overflow-hidden transition-all duration-300 hover:transform hover:-translate-y-2 selected-gradient shadow-2xl shadow-accent/50 -translate-y-2 scale-105">
                          <Image
                            src={customAvatar}
                            alt="Custom Avatar"
                            width={160}
                            height={160}
                            className="w-full h-full rounded-lg object-cover bg-muted"
                          />
                        </div>
                      </button>
                    </CarouselItem>
                  )}
                </CarouselContent>
                <CarouselPrevious className="border-slate-500 hover:border-slate-400 text-slate-400 hover:text-slate-300 bg-background/80" />
                <CarouselNext className="border-slate-500 hover:border-slate-400 text-slate-400 hover:text-slate-300 bg-background/80" />
              </Carousel>

              {/* Hidden file input */}
              <input
                ref={fileInputRef}
                type="file"
                accept="image/*"
                onChange={handleFileSelect}
                className="hidden"
              />
            </div>
          </div>

          {/* Username Section */}
          <div>
            <div className="max-w-md mx-auto pb-15">
              <div className="relative">
                <Input
                  type="text"
                  placeholder="Enter your username"
                  value={username}
                  onChange={(e) => handleUsernameChange(e.target.value)}
                  className={`w-full h-10 sm:h-12 bg-input rounded-lg px-3 pr-20 text-foreground text-base
                       focus:outline-none focus-visible:ring-0 transition-all duration-200 ${
                         username && usernameAvailable === true
                           ? "border-slate-300 shadow-2xl shadow-accent/50"
                           : username && usernameAvailable === false
                           ? "border-error"
                           : username && usernameAvailable === null
                           ? "border-border"
                           : "border-border"
                       }`}
                  maxLength={20}
                />

                {/* Right side container for indicator and button */}
                <div className="absolute right-3 top-1/2 transform -translate-y-1/2 flex items-center gap-2">
                  {/* Loading indicator */}
                  {username && usernameAvailable === null && (
                    <div className="w-4 h-4 border-2 border-ring border-t-transparent rounded-full animate-spin" />
                  )}

                  {/* Generate button */}
                  <button
                    type="button"
                    onClick={generateAiUsername}
                    disabled={isGeneratingUsername}
                    className="p-1 text-primary hover:text-primary transition-all duration-200 hover:scale-105 active:scale-95 cursor-pointer disabled:cursor-not-allowed disabled:opacity-50"
                    title="Generate username"
                  >
                    {isGeneratingUsername ? (
                      <div className="w-4 h-4 border-2 border-current border-t-transparent rounded-full animate-spin" />
                    ) : (
                      <Dices className="w-4 h-4" />
                    )}
                  </button>
                </div>
              </div>

              {/* Username suggestions */}
              <div className="mt-4 h-6">
                {usernameAvailable === false && suggestedUsername ? (
                  <div className="text-sm text-muted-foreground">
                    <span>&ldquo;{username}&rdquo; is taken. Try </span>
                    <Button
                      variant="link"
                      onClick={() =>
                        handleUsernameChange(suggestedUsername, "generated")
                      }
                      className="p-0 h-auto font-medium"
                    >
                      &ldquo;{suggestedUsername}&rdquo;
                    </Button>
                    <span>?</span>
                  </div>
                ) : null}
              </div>
            </div>
          </div>

          {/* Next Button (if present) */}
          {onComplete && (
            <div className="text-center">
              <button
                onClick={onComplete}
                disabled={!username.trim() || selectedAvatar === null}
                className={`relative cursor-pointer h-16 w-64 font-bold uppercase tracking-wider transition-all duration-300 transform hover:scale-105 focus:outline-none disabled:cursor-not-allowed overflow-hidden rounded-lg ${
                  !username.trim() || selectedAvatar === null
                    ? ""
                    : "shadow-2xl shadow-accent/50"
                }`}
              >
                {/* Gradient border effect - always present */}
                <div
                  className={`absolute inset-0 rounded-lg p-[2px] transition-all duration-300 ${
                    !username.trim() || selectedAvatar === null
                      ? "bg-gradient-to-r from-slate-800 via-slate-700 to-slate-800"
                      : "bg-gradient-to-r from-slate-500 via-slate-300 to-slate-500 hover:from-slate-400 hover:via-slate-200 hover:to-slate-400"
                  }`}
                >
                  <div className="w-full h-full rounded-md bg-background flex items-center justify-center">
                    <span
                      className={`relative z-10 transition-colors duration-300 ${
                        !username.trim() || selectedAvatar === null
                          ? "text-slate-500"
                          : "text-slate-200 hover:text-slate-100"
                      }`}
                    >
                      Next
                    </span>
                  </div>
                </div>

                {/* Shine effect when ready */}
                {username.trim() && selectedAvatar !== null && (
                  <div className="absolute inset-0 -top-2 -left-2 bg-gradient-to-r from-transparent via-white/20 to-transparent rotate-45 w-8 h-20 animate-pulse opacity-50"></div>
                )}
              </button>
            </div>
          )}
        </div>
      </div>
    </div>
  );
};

export default ProfileCreator;
