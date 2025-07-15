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
  className = "" 
}: AvatarCardProps) {
  const sizeClasses = sizeVariants[size];

  return (
    <div className={cn("flex flex-col items-center", className)}>
      <div className={cn(
        "relative cursor-pointer focus:outline-none rounded-xl transition-all duration-300 hover:transform hover:-translate-y-2 hover:scale-105",
        sizeClasses.container
      )}>
        <div className="w-full h-full rounded-xl p-2 border-gradient hover:shadow-xl hover:shadow-slate-500/30">
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