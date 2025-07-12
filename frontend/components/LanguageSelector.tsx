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
        className={`${className} text-foreground border-foreground/20 hover:bg-foreground/10 bg-background [&_svg]:text-foreground cursor-pointer`}
        size="sm"
      >
        <SelectValue />
      </SelectTrigger>
      <SelectContent
        className="text-foreground border-foreground/20 bg-background"
      >
        {languages.map((language) => (
          <SelectItem
            key={language}
            value={language}
            className="text-foreground hover:bg-foreground/5 focus:bg-foreground/5 focus:text-foreground cursor-pointer [&_svg]:text-foreground"
          >
            {SUPPORTED_LANGUAGES[language].displayName}
          </SelectItem>
        ))}
      </SelectContent>
    </Select>
  );
}

export { LanguageSelector };
