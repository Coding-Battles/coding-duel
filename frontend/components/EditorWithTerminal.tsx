"use client";

import React, { useState, useRef } from "react";
import CodeEditor from "./CodeEditor";
import TestResults, { TestResultsData } from "./TestResults";
import LanguageSelector from "./LanguageSelector";
import { Button } from "@/components/ui/button";
import { Language } from "@/types/languages";
import { Check, Play } from "lucide-react";

interface EditorWithTerminalProps {
  code?: string;
  onCodeChange?: (value: string | undefined) => void;
  language?: string;
  theme?: string;
  className?: string;
  onRunCode?: (code: string) => Promise<TestResultsData>;
  selectedLanguage?: Language;
  onLanguageChange?: (language: Language) => void;
  onRun?: () => void;
  onSubmit?: () => void;
  testResults?: TestResultsData;
}

export default function EditorWithTerminal({
  code = "# Start typing...",
  onCodeChange,
  language = "python",
  theme = "vs-dark",
  className = "",
  onRunCode,
  selectedLanguage = "python",
  onLanguageChange,
  onRun,
  onSubmit,
  testResults,
}: EditorWithTerminalProps) {
  return (
    <div className={`flex flex-col h-full w-full ${className}`}>
      {/* Editor Header Bar */}
      <div className="flex items-center justify-between bg-gray-900 border-b border-gray-700 px-4 py-2 min-h-[48px]">
        <div className="flex items-center gap-3">
          {onLanguageChange && (
            <LanguageSelector
              selectedLanguage={selectedLanguage}
              onLanguageChange={onLanguageChange}
              className="text-sm"
            />
          )}
        </div>
        <div className="flex items-center gap-2">
          {onRun && (
            <Button
              onClick={onRun}
              size="sm"
              variant="outline"
              className="text-gray-300 border-gray-600 hover:bg-gray-800 hover:text-white"
            >
              <Play size={14} className="mr-1" />
              Run
            </Button>
          )}
          {onSubmit && (
            <Button
              onClick={onSubmit}
              size="sm"
              className="bg-green-600 hover:bg-green-700 text-white"
            >
              <Check size={14} className="mr-1" />
              Submit
            </Button>
          )}
        </div>
      </div>

      {/* Editor and Test Results */}
      <div className="flex flex-col flex-1 min-h-0">
        <div className="h-[calc(100%-300px)] min-h-0">
          <CodeEditor
            value={code}
            onChange={onCodeChange}
            language={language}
            theme={theme}
            height="100%"
          />
        </div>
        <div className="h-[300px] border-t border-gray-700 bg-black">
          <TestResults testResults={testResults} height="100%" />
        </div>
      </div>
    </div>
  );
}

export { EditorWithTerminal };
