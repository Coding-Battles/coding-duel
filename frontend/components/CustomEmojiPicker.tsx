import React, { useState, useCallback, useEffect, useMemo } from "react";
import {
  Carousel,
  CarouselContent,
  CarouselItem,
  CarouselNext,
  CarouselPrevious,
} from "./ui/carousel";
import { WheelGesturesPlugin } from "embla-carousel-wheel-gestures";

interface CustomEmojiPickerProps {
  onEmojiSelect: (emoji: { native: string }) => void;
  className?: string;
}

interface RecentEmoji {
  emoji: string;
  count: number;
  lastUsed: number;
}

// Top 20 curated competitive emojis (moved outside component to prevent recreating on each render)
const gamingEmojis = [
  { emoji: "😤", name: "Huffing" },
  { emoji: "💀", name: "Dead" },
  { emoji: "🤡", name: "Clown" },
  { emoji: "😡", name: "Angry" },
  { emoji: "👑", name: "King" },
  { emoji: "😈", name: "Devil" },
  { emoji: "🤓", name: "Nerd" },
  { emoji: "💩", name: "Poop" },
  { emoji: "🗿", name: "Moai" },
  { emoji: "😬", name: "Grimace" },
  { emoji: "😎", name: "Cool" },
  { emoji: "👏", name: "Clap" },
  { emoji: "💪", name: "Strong" },
  { emoji: "🤷‍♂️", name: "Shrug" },
  { emoji: "🙄", name: "Eye Roll" },
  { emoji: "🤬", name: "Swearing" },
  { emoji: "🫠", name: "Melting" },
  { emoji: "🤨", name: "Raised Eyebrow" },
  { emoji: "🫡", name: "Salute" },
  { emoji: "🧠", name: "Brain" },
];

const CustomEmojiPicker: React.FC<CustomEmojiPickerProps> = ({
  onEmojiSelect,
  className = "",
}) => {
  const [recentEmojis, setRecentEmojis] = useState<RecentEmoji[]>([]);

  // LocalStorage key for persisting recent emojis
  const RECENT_EMOJIS_KEY = "coding-duel-recent-emojis";
  const MAX_RECENT_EMOJIS = 8;
  const RECENT_EMOJI_EXPIRY_DAYS = 30;

  // Load recent emojis from localStorage on mount
  useEffect(() => {
    try {
      const stored = localStorage.getItem(RECENT_EMOJIS_KEY);
      if (stored) {
        const parsed = JSON.parse(stored) as RecentEmoji[];
        const now = Date.now();
        const cutoffTime = now - RECENT_EMOJI_EXPIRY_DAYS * 24 * 60 * 60 * 1000;

        // Filter out expired entries
        const validRecent = parsed.filter((item) => item.lastUsed > cutoffTime);
        setRecentEmojis(validRecent);

        // Clean up localStorage if we removed any expired items
        if (validRecent.length !== parsed.length) {
          localStorage.setItem(RECENT_EMOJIS_KEY, JSON.stringify(validRecent));
        }
      }
    } catch (error) {
      console.warn("Failed to load recent emojis from localStorage:", error);
    }
  }, []);

  // Save recent emojis to localStorage
  const saveRecentEmojis = useCallback((emojis: RecentEmoji[]) => {
    try {
      localStorage.setItem(RECENT_EMOJIS_KEY, JSON.stringify(emojis));
    } catch (error) {
      console.warn("Failed to save recent emojis to localStorage:", error);
    }
  }, []);

  // Update recent emojis when an emoji is selected (save for next game)
  const updateRecentEmojis = useCallback(
    (selectedEmoji: string) => {
      // Get current data from localStorage
      let storedData: RecentEmoji[] = [];
      try {
        const stored = localStorage.getItem(RECENT_EMOJIS_KEY);
        if (stored) {
          storedData = JSON.parse(stored) as RecentEmoji[];
        }
      } catch (error) {
        console.warn("Failed to read recent emojis from localStorage:", error);
      }

      const now = Date.now();
      const existingIndex = storedData.findIndex(
        (item) => item.emoji === selectedEmoji
      );

      let newRecent: RecentEmoji[];

      if (existingIndex >= 0) {
        // Update existing emoji
        newRecent = [...storedData];
        newRecent[existingIndex] = {
          ...newRecent[existingIndex],
          count: newRecent[existingIndex].count + 1,
          lastUsed: now,
        };
      } else {
        // Add new emoji
        const newEntry: RecentEmoji = {
          emoji: selectedEmoji,
          count: 1,
          lastUsed: now,
        };
        newRecent = [newEntry, ...storedData];
      }

      // Sort by score (frequency + recency) and limit to MAX_RECENT_EMOJIS
      newRecent.sort((a, b) => {
        const scoreA = a.count * 2 + a.lastUsed / 1000000; // Normalize timestamp
        const scoreB = b.count * 2 + b.lastUsed / 1000000;
        return scoreB - scoreA;
      });

      const limitedRecent = newRecent.slice(0, MAX_RECENT_EMOJIS);
      saveRecentEmojis(limitedRecent);

      // Don't update state - keep current layout unchanged
    },
    [saveRecentEmojis]
  );

  const handleEmojiClick = useCallback(
    (emoji: string) => {
      console.log("🚀 [PICKER DEBUG] Emoji clicked in picker:", emoji);
      console.log(
        "🚀 [PICKER DEBUG] onEmojiSelect function exists:",
        !!onEmojiSelect
      );
      updateRecentEmojis(emoji);
      onEmojiSelect({ native: emoji });
    },
    [updateRecentEmojis, onEmojiSelect]
  );

  // Create combined emoji list: recent first, then gaming emojis (excluding duplicates)
  const combinedEmojis = useMemo(() => {
    const items: Array<{
      emoji: string;
      name: string;
      isRecent: boolean;
      count?: number;
    }> = [];

    // Add recent emojis first
    recentEmojis.forEach((recent) => {
      const gamingEmoji = gamingEmojis.find((g) => g.emoji === recent.emoji);
      items.push({
        emoji: recent.emoji,
        name: gamingEmoji?.name || "Recent",
        isRecent: true,
        count: recent.count,
      });
    });

    // Add gaming emojis (excluding those already in recent)
    const recentEmojiSet = new Set(recentEmojis.map((r) => r.emoji));
    gamingEmojis.forEach((gaming) => {
      if (!recentEmojiSet.has(gaming.emoji)) {
        items.push({
          emoji: gaming.emoji,
          name: gaming.name,
          isRecent: false,
        });
      }
    });

    return items;
  }, [recentEmojis]);

  return (
    <div
      className={`relative rounded backdrop-blur-md bg-gradient-to-br from-black/[0.02] to-black/[0.05] w-80 ${className}`}
    >
      <div className="px-4 py-2">
        <Carousel
          plugins={[
            WheelGesturesPlugin({
              forceWheelAxis: "x",
              threshold: 25,
              wheelFactor: 0.3,
            }),
          ]}
          opts={{
            align: "start",
            loop: false,
            skipSnaps: false,
            dragFree: false,
            containScroll: "trimSnaps",
            duration: 25,
            inViewThreshold: 0.7,
          }}
          className="w-full"
        >
          <CarouselContent className="ml-0 py-2">
            {combinedEmojis.map((item) => {
              // Render emoji button
              return (
                <CarouselItem
                  key={`emoji-${item.emoji}`}
                  className="pl-3 basis-auto"
                >
                  <button
                    onClick={() => handleEmojiClick(item.emoji)}
                    className="group relative flex items-center justify-center w-15 h-20 text-3xl transition-all duration-300 rounded cursor-pointer bg-background/80 hover:bg-background active:scale-95 active:translate-y-px font-[system-ui,'Apple_Color_Emoji','Segoe_UI_Emoji','Noto_Color_Emoji',sans-serif]"
                    title={item.name}
                    type="button"
                  >
                    <span className="relative">{item.emoji}</span>
                  </button>
                </CarouselItem>
              );
            })}
          </CarouselContent>
          <CarouselPrevious className="border-slate-500 hover:border-slate-400 text-slate-400 hover:text-slate-300 bg-background/80 z-10 -left-3 !w-4 !h-6" />
          <CarouselNext className="border-slate-500 hover:border-slate-400 text-slate-400 hover:text-slate-300 bg-background/80 z-10 -right-3 !w-4 !h-6" />
        </Carousel>
      </div>

      {/* Fade edges for scroll indication */}
      <div className="absolute left-0 top-0 bottom-0 w-8 bg-gradient-to-r from-background to-transparent pointer-events-none z-0" />
      <div className="absolute right-0 top-0 bottom-0 w-8 bg-gradient-to-l from-background to-transparent pointer-events-none z-0" />
    </div>
  );
};

export default CustomEmojiPicker;
