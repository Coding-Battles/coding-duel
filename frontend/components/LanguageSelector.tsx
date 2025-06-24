'use client';

import { Language, SUPPORTED_LANGUAGES } from '@/types/languages';
import { ChevronDown } from 'lucide-react';

interface LanguageSelectorProps {
  selectedLanguage: Language;
  onLanguageChange: (language: Language) => void;
  className?: string;
}

export default function LanguageSelector({
  selectedLanguage,
  onLanguageChange,
  className = ''
}: LanguageSelectorProps) {
  const languages = Object.keys(SUPPORTED_LANGUAGES) as Language[];

  return (
    <div className={`relative ${className}`}>
      <select
        value={selectedLanguage}
        onChange={(e) => onLanguageChange(e.target.value as Language)}
        className="appearance-none bg-transparent border-2 border-gray-400 text-gray-700 hover:border-gray-600 hover:bg-gray-100 px-4 py-2 pr-8 rounded cursor-pointer focus:outline-none focus:border-blue-500 min-w-[120px]"
      >
        {languages.map((language) => (
          <option key={language} value={language}>
            {SUPPORTED_LANGUAGES[language].displayName}
          </option>
        ))}
      </select>
      <div className="absolute inset-y-0 right-0 flex items-center px-2 pointer-events-none">
        <ChevronDown size={16} className="text-gray-500" />
      </div>
    </div>
  );
}

export { LanguageSelector };