'use client';

import { useEffect, useState, useTransition } from 'react';
import { toggleTheme } from '@/app/actions/toggleTheme';
import { useRouter } from 'next/navigation';
import { Moon, Sun } from 'lucide-react';
import { useTheme } from 'next-themes';
import { set } from 'better-auth';

export function NightModeButton() {
  const [isPending, startTransition] = useTransition();
  const router = useRouter();

  const [theme, setLocalTheme] = useState<'light' | 'dark'>('light');

  useEffect(() => {
    const cookieTheme =
      document.cookie
        .split('; ')
        .find((row) => row.startsWith('theme='))?.split('=')[1] ?? 'light';

    setLocalTheme(cookieTheme === 'dark' ? 'dark' : 'light');
  }, []);

  const handleClick = () => {
    startTransition(async () => {
      await toggleTheme();         // Server sets cookie
      setLocalTheme((prev) => (prev === 'dark' ? 'light' : 'dark')); // Update local state
      router.refresh();            // SSR re-renders with new cookie
    });
  };

  return (
    <button
      onClick={handleClick}
      disabled={isPending}
      className="w-6 h-6 rounded-full fixed bottom-2 right-2 z-40 cursor-pointer"
    >
      {theme === 'dark' ? (
        <Moon className="text-gray-400" />
      ) : (
        <Sun className="text-yellow-400" />
      )}
    </button>
  );
}
