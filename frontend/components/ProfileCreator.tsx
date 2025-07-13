import React, {
  useState,
  useRef,
  ChangeEvent,
  useEffect,
  useCallback,
} from "react";
import Image from "next/image";
import { Input } from "./ui/input";
import { Button } from "./ui/button";
import { Shuffle, Upload, ChevronLeft, ChevronRight } from "lucide-react";

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
  const scrollContainerRef = useRef<HTMLDivElement>(null);
  const [focusedAvatarIndex, setFocusedAvatarIndex] = useState<number | null>(
    null
  );

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
      setFocusedAvatarIndex(index);
      // Clear custom avatar when selecting default avatar
      if (onCustomAvatarChange) {
        onCustomAvatarChange(null);
      }
    },
    [onAvatarChange, onCustomAvatarChange]
  );

  // Scroll avatar into view
  const scrollToAvatar = useCallback((index: number) => {
    if (!scrollContainerRef.current) return;

    const container = scrollContainerRef.current;
    const avatarWidth = 150 + 16; // avatar width + gap
    const containerWidth = container.clientWidth;
    const scrollLeft = container.scrollLeft;

    const avatarLeft = index * avatarWidth;
    const avatarRight = avatarLeft + avatarWidth;

    // Check if avatar is out of view and scroll to it
    if (avatarLeft < scrollLeft) {
      container.scrollTo({
        left: avatarLeft - 16, // Add some padding
        behavior: "smooth",
      });
    } else if (avatarRight > scrollLeft + containerWidth) {
      container.scrollTo({
        left: avatarRight - containerWidth + 16, // Add some padding
        behavior: "smooth",
      });
    }
  }, []);

  // Scroll by one avatar at a time
  const scrollByAvatar = useCallback((direction: "left" | "right") => {
    if (!scrollContainerRef.current) return;

    const container = scrollContainerRef.current;
    const avatarWidth = 150 + 16; // avatar width + gap
    const scrollAmount = direction === "left" ? -avatarWidth : avatarWidth;

    container.scrollBy({
      left: scrollAmount,
      behavior: "smooth",
    });
  }, []);

  // Keyboard navigation
  const handleKeyDown = useCallback(
    (e: KeyboardEvent) => {
      if (e.target !== document.body) return; // Only handle when not in input

      const avatarCount = 6; // Update this if you change the number of avatars
      let newIndex = focusedAvatarIndex;

      switch (e.key) {
        case "ArrowLeft":
          e.preventDefault();
          newIndex =
            focusedAvatarIndex === null
              ? 0
              : Math.max(0, focusedAvatarIndex - 1);
          break;
        case "ArrowRight":
          e.preventDefault();
          newIndex =
            focusedAvatarIndex === null
              ? 0
              : Math.min(avatarCount - 1, focusedAvatarIndex + 1);
          break;
        case "Enter":
        case " ":
          if (focusedAvatarIndex !== null) {
            e.preventDefault();
            handleAvatarSelect(focusedAvatarIndex);
          }
          break;
        default:
          return;
      }

      if (newIndex !== null && newIndex !== focusedAvatarIndex) {
        setFocusedAvatarIndex(newIndex);
        scrollToAvatar(newIndex);
      }
    },
    [focusedAvatarIndex, handleAvatarSelect, scrollToAvatar]
  );

  // Add keyboard event listeners
  useEffect(() => {
    document.addEventListener("keydown", handleKeyDown);
    return () => document.removeEventListener("keydown", handleKeyDown);
  }, [handleKeyDown]);

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

        {/* Avatar Section: Preview + Selection */}
        <div className="mb-12 overflow-hidden">
          <div className="flex flex-col lg:flex-row items-center gap-8 mb-8">
            {/* Avatar Preview */}
            <div className="flex-shrink-0">
              <div className="w-32 h-32 sm:w-48 sm:h-48 relative">
                {selectedAvatar !== null ? (
                  selectedAvatar === 999 && customAvatar ? (
                    <div
                      className="w-full h-full rounded-2xl overflow-hidden selected-gradient p-2 cursor-pointer hover:opacity-90 transition-opacity"
                      onClick={handleAvatarPreviewClick}
                    >
                      <Image
                        src={customAvatar}
                        alt="Selected custom avatar"
                        width={176}
                        height={176}
                        className="w-full h-full rounded-xl object-cover"
                      />
                    </div>
                  ) : (
                    <div
                      className="w-full h-full rounded-2xl overflow-hidden selected-gradient p-2 cursor-pointer hover:opacity-90 transition-opacity"
                      onClick={handleAvatarPreviewClick}
                    >
                      <Image
                        src={`/avatars/${selectedAvatar}.png`}
                        alt={`Selected Avatar ${selectedAvatar}`}
                        width={176}
                        height={176}
                        className="w-full h-full rounded-xl object-cover"
                      />
                    </div>
                  )
                ) : (
                  <div
                    className="w-full h-full rounded-2xl border border-border cursor-pointer transition-all duration-200 hover:scale-105 flex flex-col items-center justify-center text-muted-foreground hover:text-primary"
                    onClick={handleAvatarPreviewClick}
                  >
                    <Upload className="w-8 h-8 mb-3" />
                    <span className="text-sm font-medium mb-1">
                      Upload Custom
                    </span>
                    <span className="text-xs opacity-70">Click to browse</span>
                  </div>
                )}
              </div>

              {/* Hidden file input */}
              <input
                ref={fileInputRef}
                type="file"
                accept="image/*"
                onChange={handleFileSelect}
                className="hidden"
              />
            </div>

            {/* Avatar Selection Carousel */}
            <div className="flex-1 relative overflow-hidden">
              {/* Navigation Arrows */}
              <ChevronLeft
                onClick={() => scrollByAvatar("left")}
                role="button"
                tabIndex={0}
                onKeyDown={(e) =>
                  (e.key === "Enter" || e.key === " ") && scrollByAvatar("left")
                }
                className="absolute left-2 top-1/2 -translate-y-1/2 z-20 h-16 w-10 text-primary cursor-pointer hover:scale-110 transition-transform duration-200"
                aria-label="Scroll left"
              />

              <ChevronRight
                onClick={() => scrollByAvatar("right")}
                role="button"
                tabIndex={0}
                onKeyDown={(e) =>
                  (e.key === "Enter" || e.key === " ") &&
                  scrollByAvatar("right")
                }
                className="absolute right-2 top-1/2 -translate-y-1/2 z-20 h-16 w-10 text-primary cursor-pointer hover:scale-110 transition-transform duration-200"
                aria-label="Scroll right"
              />

              {/* Fade edges for scroll indication */}
              <div className="absolute left-0 top-0 bottom-0 w-12 bg-gradient-to-r from-background to-transparent z-10 pointer-events-none" />
              <div className="absolute right-0 top-0 bottom-0 w-12 bg-gradient-to-l from-background to-transparent z-10 pointer-events-none" />

              {/* Horizontal scrollable container */}
              <div
                ref={scrollContainerRef}
                className="flex gap-4 overflow-x-auto scrollbar-hide py-4 px-12"
                style={{
                  scrollbarWidth: "none",
                  msOverflowStyle: "none",
                  WebkitOverflowScrolling: "touch",
                }}
                onWheel={(e) => {
                  // Enable horizontal scrolling with mouse wheel
                  if (scrollContainerRef.current) {
                    e.preventDefault();
                    scrollContainerRef.current.scrollLeft += e.deltaY;
                  }
                }}
              >
                {/* Avatars */}
                {Array.from({ length: 6 }, (_, index) => (
                  <button
                    key={index}
                    onClick={() => handleAvatarSelect(index)}
                    onFocus={() => setFocusedAvatarIndex(index)}
                    className="relative flex-shrink-0 cursor-pointer focus:outline-none rounded-xl"
                    aria-label={`Select Avatar ${index + 1}`}
                  >
                    <div
                      className={`w-32 h-32 sm:w-36 sm:h-36 lg:w-40 lg:h-40 rounded-xl p-2 overflow-hidden transition-all duration-300 hover:transform hover:-translate-y-2 ${
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
                        priority={index < 4} // Prioritize first 4 visible avatars
                      />
                    </div>
                  </button>
                ))}
              </div>
            </div>
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
