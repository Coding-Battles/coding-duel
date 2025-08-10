import React from "react";
import Image from "next/image";
import { cn } from "@/lib/utils";

interface AvatarCardProps {
  src: string;
  alt: string;
  name: string;
  size?: "sm" | "md" | "lg";
  showName?: boolean;
  className?: string;
  player?: "player1" | "player2";
  onClick?: () => void;
  clickable?: boolean;
  opponentLp?: number; // Used for displaying opponent's LP
  isOpponent?: boolean; // Flag to indicate if this is the opponent's avatar
}

const sizeVariants = {
  sm: {
    container: "w-20 h-20",
    image: "w-16 h-16",
    text: "text-sm",
  },
  md: {
    container: "w-32 h-32",
    image: "w-28 h-28",
    text: "text-base",
  },
  lg: {
    container: "w-40 h-40",
    image: "w-36 h-36",
    text: "text-lg",
  },
};

export default function AvatarCard({
  src,
  alt,
  name,
  size = "md",
  showName = true,
  className = "",
  player = "player2",
  opponentLp = 0,
  isOpponent = false,
  onClick,
  clickable = false,
}: AvatarCardProps) {
  const sizeClasses = sizeVariants[size];
  const borderClass =
    player === "player1"
      ? "border-gradient-player1"
      : "border-gradient-player2";

  const handleClick = () => {
    if (onClick && (clickable || onClick)) {
      onClick();
    }
  };

  return (
    <div className={cn("flex flex-col items-center pb-8", className)}>
      <div
        className={cn(
          "relative rounded-xl transition-all duration-300 flex flex-col items-center",
          sizeClasses.container,
          (clickable || onClick) &&
            "cursor-pointer hover:transform hover:-translate-y-2 hover:scale-105"
        )}
        onClick={handleClick}
      >
        <div className={cn("w-full h-full rounded-xl p-2", borderClass)}>
          <Image
            src={src}
            alt={alt}
            width={160}
            height={160}
            className="object-cover w-full h-full rounded-lg bg-muted"
          />
        </div>

        {showName && (
          <h3
            className={cn(
              "mt-3 font-bold text-center text-foreground",
              sizeClasses.text
            )}
          >
            {name}
          </h3>
        )}

        {isOpponent && (
          <p className="mt-1 text-sm text-foreground/70">
            LP: {opponentLp > 0 ? opponentLp : "?"}
          </p>
        )}
      </div>
    </div>
  );
}
