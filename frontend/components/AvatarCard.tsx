import React from "react";
import Image from "next/image";
import { cn } from "@/lib/utils";

interface AvatarCardProps {
  src: string;
  alt: string;
  name: string;
  size?: 'sm' | 'md' | 'lg';
  showName?: boolean;
  className?: string;
  player?: 'player1' | 'player2';
  onClick?: () => void;
  clickable?: boolean;
}

const sizeVariants = {
  sm: {
    container: "w-20 h-20",
    image: "w-16 h-16",
    text: "text-sm"
  },
  md: {
    container: "w-32 h-32", 
    image: "w-28 h-28",
    text: "text-base"
  },
  lg: {
    container: "w-40 h-40",
    image: "w-36 h-36", 
    text: "text-lg"
  }
};

export default function AvatarCard({ 
  src, 
  alt, 
  name, 
  size = 'md',
  showName = true,
  className = "",
  player = 'player2',
  onClick,
  clickable = false
}: AvatarCardProps) {
  const sizeClasses = sizeVariants[size];
  const borderClass = player === 'player1' ? 'border-gradient-player1' : 'border-gradient';

  const handleClick = () => {
    if (onClick && (clickable || onClick)) {
      onClick();
    }
  };

  return (
    <div className={cn("flex flex-col items-center", className)}>
      <div 
        className={cn(
          "relative rounded-xl",
          sizeClasses.container,
          (clickable || onClick) && "cursor-pointer"
        )}
        onClick={handleClick}
      >
        <div className={cn("w-full h-full rounded-xl p-2", borderClass)}>
          <Image
            src={src}
            alt={alt}
            width={160}
            height={160}
            className="w-full h-full rounded-lg object-cover bg-muted"
          />
        </div>
      </div>
      
      {showName && (
        <h3 className={cn(
          "mt-3 font-bold text-center text-foreground",
          sizeClasses.text
        )}>
          {name}
        </h3>
      )}
    </div>
  );
}