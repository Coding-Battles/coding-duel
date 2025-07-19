import React, { useState, useCallback } from "react";
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

const CustomEmojiPicker: React.FC<CustomEmojiPickerProps> = ({
  onEmojiSelect,
  className = "",
}) => {
  // Top 20 curated competitive emojis
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

  const [carouselApi, setCarouselApi] = useState<any>(null);

  const handleEmojiClick = (emoji: string) => {
    onEmojiSelect({ native: emoji });
  };

  return (
    <div className={`gaming-command-center ${className}`}>
      <div className="px-4 py-2">
        <Carousel
          plugins={[
            WheelGesturesPlugin({
              forceWheelAxis: "x",
              threshold: 10,
            }),
          ]}
          opts={{
            align: "start",
            loop: false,
            skipSnaps: false,
            dragFree: true,
            containScroll: "trimSnaps",
          }}
          setApi={setCarouselApi}
          className="w-full"
        >
          <CarouselContent className="ml-0 py-2">
            {gamingEmojis.map((item, index) => (
              <CarouselItem key={index} className="pl-3 basis-auto">
                <button
                  onClick={() => handleEmojiClick(item.emoji)}
                  className="emoji-command-button group relative flex items-center justify-center w-12 h-12 text-2xl transition-all duration-300 rounded-lg border border-border/30 bg-background/80 backdrop-blur-sm hover:border-accent hover:bg-accent/10 hover:scale-110 hover:shadow-lg hover:shadow-accent/20 active:scale-95 active:shadow-inner"
                  title={item.name}
                  type="button"
                >
                  <span className="relative z-10 transition-all duration-300 group-hover:scale-110 group-hover:drop-shadow-lg">
                    {item.emoji}
                  </span>
                  {/* Gaming glow effect */}
                  <div className="absolute inset-0 rounded-lg bg-gradient-to-br from-accent/0 to-accent/0 group-hover:from-accent/20 group-hover:to-accent/5 transition-all duration-300" />
                </button>
              </CarouselItem>
            ))}
          </CarouselContent>
          <CarouselPrevious className="border-slate-500 hover:border-slate-400 text-slate-400 hover:text-slate-300 bg-background/80 -left-12" />
          <CarouselNext className="border-slate-500 hover:border-slate-400 text-slate-400 hover:text-slate-300 bg-background/80 -right-12" />
        </Carousel>
      </div>

      {/* Fade edges for scroll indication */}
      <div className="absolute left-0 top-0 bottom-0 w-8 bg-gradient-to-r from-background to-transparent pointer-events-none z-10" />
      <div className="absolute right-0 top-0 bottom-0 w-8 bg-gradient-to-l from-background to-transparent pointer-events-none z-10" />
    </div>
  );
};

export default CustomEmojiPicker;
