'use client';

import { Moon, Sun } from 'lucide-react';
import { useTheme } from 'next-themes';
import { useEffect, useState } from 'react';

export function NightModeButton() {
  const { theme, setTheme } = useTheme();
  const [mounted, setMounted] = useState(false);

  // Avoid hydration mismatch
  useEffect(() => {
    setMounted(true);
  }, []);

  if (!mounted) {
    return (
      <div className="w-10 h-10 rounded-lg fixed top-4 right-4 z-50" />
    );
  }

  const toggleTheme = () => {
    setTheme(theme === 'dark' ? 'light' : 'dark');
  };

  return (
    <button
      onClick={toggleTheme}
      className="w-10 h-10 rounded-lg fixed top-4 right-4 z-50 cursor-pointer bg-background/80 border border-border hover:bg-background hover:scale-105 transition-all duration-200 flex items-center justify-center backdrop-blur-sm"
    >
      {theme === 'dark' ? (
        <Moon className="text-foreground w-5 h-5" />
      ) : (
        <Sun className="text-foreground w-5 h-5" />
      )}
    </button>
  );
}
