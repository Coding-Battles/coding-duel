export type Language = 'python' | 'java' | 'cpp' | 'javascript';

export interface LanguageConfig {
  displayName: string;
  monacoLanguage: string;
}

export const SUPPORTED_LANGUAGES: Record<Language, LanguageConfig> = {
  python: {
    displayName: 'Python',
    monacoLanguage: 'python'
  },
  java: {
    displayName: 'Java',
    monacoLanguage: 'java'
  },
  cpp: {
    displayName: 'C++',
    monacoLanguage: 'cpp'
  },
  javascript: {
    displayName: 'JavaScript',
    monacoLanguage: 'javascript'
  }
};

export const getLanguageConfig = (language: Language): LanguageConfig => {
  return SUPPORTED_LANGUAGES[language];
};