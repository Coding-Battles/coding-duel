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
        className={`${className} text-white border-white-600 hover:bg-gray-700 focus:ring-blue-500 focus:border-blue-500 data-[state=open]:text-white focus:text-white [&_svg]:text-white [&_svg]:opacity-100`}
        size="sm"
        className="bg-primary"
      >
        <SelectValue />
      </SelectTrigger>
      <SelectContent
        className="text-white border-white-600"
        className="bg-primary"
      >
        {languages.map((language) => (
          <SelectItem
            key={language}
            value={language}
            className="text-white [&_svg]:text-white"
          >
            {SUPPORTED_LANGUAGES[language].displayName}
          </SelectItem>
        ))}
      </SelectContent>
    </Select>
  );
}

export { LanguageSelector };
