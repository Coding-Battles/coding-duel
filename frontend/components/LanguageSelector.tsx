"use client";

import { Language, SUPPORTED_LANGUAGES } from "@/types/languages";
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from "@/components/ui/select";

interface LanguageSelectorProps {
  selectedLanguage: Language;
  onLanguageChange: (language: Language) => void;
  className?: string;
}

export default function LanguageSelector({
  selectedLanguage,
  onLanguageChange,
  className = "",
}: LanguageSelectorProps) {
  const languages = Object.keys(SUPPORTED_LANGUAGES) as Language[];

  return (
    <Select value={selectedLanguage} onValueChange={onLanguageChange}>
      <SelectTrigger
        className={`${className} text-black dark:text-white border-slate-300 dark:border-slate-600 hover:bg-gray-300 dark:hover:bg-gray-700 bg-white dark:bg-gray-700 [&_svg]:text-black [&_svg]:dark:text-white cursor-pointer`}
        size="sm"
      >
        <SelectValue />
      </SelectTrigger>
      <SelectContent
        className="text-black dark:text-white border-slate-300 dark:border-slate-600 bg-white dark:bg-gray-700"
      >
        {languages.map((language) => (
          <SelectItem
            key={language}
            value={language}
            className="text-black dark:text-white hover:bg-gray-100 dark:hover:bg-gray-600 focus:bg-gray-100 dark:focus:bg-gray-600 focus:text-black dark:focus:text-white cursor-pointer [&_svg]:text-black [&_svg]:dark:text-white"
          >
            {SUPPORTED_LANGUAGES[language].displayName}
          </SelectItem>
        ))}
      </SelectContent>
    </Select>
  );
}

export { LanguageSelector };
