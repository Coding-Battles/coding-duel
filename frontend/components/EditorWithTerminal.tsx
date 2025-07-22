"use client";

import React, { useState, useRef } from "react";
import CodeEditor from "./CodeEditor";
import TestResults, { TestResultsData } from "./TestResults";
import LanguageSelector from "./LanguageSelector";
import { Button } from "@/components/ui/button";
import { Language } from "@/types/languages";
import { Check, Play, Loader2 } from "lucide-react";

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
  isRunning?: boolean;
  hasResults?: boolean;
  onCloseResults?: () => void;
  disableCopyPaste?: boolean;
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
  isRunning = false,
  hasResults = false,
  onCloseResults,
  disableCopyPaste = false,
}: EditorWithTerminalProps) {
  return (
    <div
      className={`flex flex-col h-full w-full ${className} rounded-lg overflow-hidden shadow-lg`}
    >
      {/* Editor Header Bar */}
      <div className="flex items-center justify-between border-b border-foreground/20 px-4 py-3 min-h-[48px] bg-foreground/5">
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
              className="text-foreground border-foreground/20 bg-background hover:bg-foreground/5"
              disabled={isRunning}
            >
              {isRunning ? (
                <Loader2 size={14} className="mr-1 animate-spin" />
              ) : (
                <Play size={14} className="mr-1" />
              )}
              Run
            </Button>
          )}
          {onSubmit && (
            <Button
              onClick={onSubmit}
              size="sm"
              variant="default"
              className="border-0 bg-success hover:bg-success/80 text-background"
              disabled={isRunning}
            >
              {isRunning ? (
                <Loader2 size={14} className="mr-1 animate-spin" />
              ) : (
                <Check size={14} className="mr-1" />
              )}
              Submit
            </Button>
          )}
        </div>
      </div>

      {/* Editor and Test Results */}
      <div className="flex flex-col flex-1 h-full min-h-0">
        <div className={hasResults ? "flex-1 min-h-0" : "flex-1"}>
          <CodeEditor
            value={code}
            onChange={onCodeChange}
            language={language}
            theme={theme}
            height="100%"
            disableCopyPaste={disableCopyPaste}
          />
        </div>
        {hasResults && (
          <div className="flex-shrink-0 border-t border-slate-600/30 max-h-[40%]">
            <TestResults
              testResults={testResults}
              isRunning={isRunning}
              onCloseResults={onCloseResults}
            />
          </div>
        )}
      </div>
    </div>
  );
}

export { EditorWithTerminal };
