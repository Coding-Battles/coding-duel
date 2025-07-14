import React, { useState, useRef, useCallback, ChangeEvent } from "react";
import Image from "next/image";
import { Input } from "./ui/input";
import { Button } from "./ui/button";
import { Shuffle, Upload } from "lucide-react";
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
}) => {
  const [usernameAvailable, setUsernameAvailable] = useState<boolean | null>(
    null
  );
  const [suggestedUsername, setSuggestedUsername] = useState<string>("");
  const [isGeneratingUsername, setIsGeneratingUsername] = useState(false);
  const fileInputRef = useRef<HTMLInputElement>(null);
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

      const endpoint = `${process.env.NEXT_PUBLIC_API_BASE_URL}/image/${userId}`;
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
      <div className="relative p-8">
        {/* Main Title */}
        <div className="text-center mb-12">
          <h1
            className="text-4xl sm:text-6xl lg:text-8xl uppercase text-gradient font-bold tracking-wide gaming-title"
            data-text="Choose your fighter"
          >
            Choose your fighter
          </h1>
        </div>

        {/* Avatar Selection Carousel */}
        <div className="mb-12">
          <div className="px-16">
            <Carousel
              plugins={[WheelGesturesPlugin()]}
              opts={{
                align: "start",
                loop: false,
                skipSnaps: false,
              }}
              setApi={setCarouselApi}
              className="w-full max-w-4xl mx-auto"
            >
              <CarouselContent className="ml-0 md:ml-0 py-16 pl-3">
                {/* Upload Custom Avatar Item */}
                <CarouselItem className="pl-2 md:pl-4 basis-1/3 px-2">
                  <button
                    onClick={handleAvatarPreviewClick}
                    className="relative w-full cursor-pointer focus:outline-none rounded-xl"
                    aria-label="Upload Custom Avatar"
                  >
                    <div className="w-full aspect-square rounded-xl p-2 border-gradient hover:shadow-xl hover:shadow-slate-500/30 transition-all duration-300 hover:transform hover:-translate-y-2 hover:scale-105">
                      <div className="w-full h-full flex flex-col items-center justify-center text-muted-foreground hover:text-accent">
                        <Upload className="w-8 h-8 mb-2" />
                        <span className="text-sm font-medium mb-1">Upload</span>
                        <span className="text-xs opacity-70">Custom</span>
                      </div>
                    </div>
                  </button>
                </CarouselItem>

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
                        className={`w-full aspect-square rounded-xl p-2 overflow-hidden transition-all duration-300 hover:transform hover:-translate-y-2 ${
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
        <div className="mb-12">
          <div className="max-w-md mx-auto">
            <div className="relative">
              <Input
                type="text"
                placeholder="Enter your username"
                value={username}
                onChange={(e) => handleUsernameChange(e.target.value)}
                className={`w-full h-10 sm:h-12 bg-input border-2 rounded-lg px-3 pr-20 text-foreground text-base
                       focus:outline-none transition-all duration-200 ${
                         username && usernameAvailable === true
                           ? "border-success focus-visible:border-success focus-visible:ring-success/20 shadow-lg shadow-success/20"
                           : username && usernameAvailable === false
                           ? "border-error focus-visible:border-error focus-visible:ring-error/20 shadow-lg shadow-error/20"
                           : "border-border focus-visible:border-ring focus-visible:ring-ring/20"
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
                  title="Generate AI username"
                >
                  {isGeneratingUsername ? (
                    <div className="w-4 h-4 border-2 border-current border-t-transparent rounded-full animate-spin" />
                  ) : (
                    <Shuffle className="w-4 h-4" />
                  )}
                </button>
              </div>
            </div>

            {/* Username suggestions */}
            {usernameAvailable === false && suggestedUsername && (
              <div className="mt-4">
                <p className="text-sm text-muted-foreground">
                  &ldquo;{username}&rdquo; is taken. Try{" "}
                  <span
                    onClick={() =>
                      handleUsernameChange(suggestedUsername, "generated")
                    }
                    className="text-primary hover:underline font-medium cursor-pointer"
                  >
                    &ldquo;{suggestedUsername}&rdquo;
                  </span>
                  ?
                </p>
              </div>
            )}
          </div>
        </div>

        {/* Next Button */}
        {onComplete && (
          <div className="mt-8 text-center">
            <Button
              onClick={onComplete}
              disabled={!username.trim() || selectedAvatar === null}
              variant="default"
              size="lg"
            >
              {!username.trim()
                ? "Enter Username"
                : selectedAvatar === null
                ? "Select Avatar"
                : "Next"}
            </Button>
          </div>
        )}
      </div>
    </div>
  );
};

export default ProfileCreator;
