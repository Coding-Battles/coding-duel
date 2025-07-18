"use client";

import React from "react";
import { Loader2, X } from "lucide-react";

interface TestCase {
  input: Record<string, unknown>;
  expected_output: string;
  actual_output: string;
  passed: boolean;
  error?: string;
  execution_time: number;
}

interface TestResultsData {
  message: string;
  code: string;
  opponent_id: string;
  player_name: string;
  success: boolean;
  test_results: TestCase[];
  total_passed: number;
  total_failed: number;
  error?: string;
  complexity?: string;
  implement_time?: number;
  final_time?: number;
}

interface TestResultsProps {
  testResults?: TestResultsData;
  className?: string;
  isRunning?: boolean;
  onCloseResults?: () => void;
}

export default function TestResults({
  testResults,
  className = "",
  isRunning = false,
  onCloseResults,
}: TestResultsProps) {
  // Show loading state when tests are running
  if (isRunning) {
    return (
      <div className={`bg-background border-t border-foreground/20 ${className}`}>
        <div className="flex items-center gap-3 px-4 py-3">
          <Loader2 size={16} className="animate-spin text-foreground/60" />
          <span className="text-foreground/60">Running tests...</span>
        </div>
      </div>
    );
  }

  if (!testResults) {
    return (
      <div className={`bg-background border-t border-foreground/20 ${className}`}>
        <div className="px-4 py-3">
          <span className="text-foreground/50">
            Run your code to see results
          </span>
        </div>
      </div>
    );
  }

  const { test_results = [], total_passed, total_failed, error } = testResults;

  return (
    <div className={`bg-background border-t border-foreground/20 ${className}`}>
      {/* Header */}
      <div className="flex items-center justify-between px-4 py-3 border-b border-foreground/20">
        <span className="text-foreground">
          {total_passed}/{test_results?.length || 0} tests passed
        </span>
        {onCloseResults && (
          <button
            onClick={onCloseResults}
            className="text-foreground/40 hover:text-foreground/60"
            title="Close"
          >
            <X size={16} />
          </button>
        )}
      </div>

      {/* Content */}
      <div className="p-4 space-y-3 overflow-y-scroll">
        {/* Error Message */}
        {error && (
          <div className="p-3 text-sm rounded text-error bg-error/10">
            {error}
          </div>
        )}

        {/* Test Results - Minimal Layout */}
        {test_results && test_results.length > 0 ? (
          test_results.map((test, i) => (
            <div key={i} className="py-2 border-b border-foreground/10 last:border-b-0">
              <div className="flex items-center gap-4">
                {/* Pass/Fail Indicator */}
                <span className={`w-5 h-5 rounded-full flex items-center justify-center text-xs font-medium ${
                  test.passed 
                    ? "bg-success/10 text-success" 
                    : "bg-error/10 text-error"
                }`}>
                  {test.passed ? "✓" : "✗"}
                </span>

                {/* Test Info */}
                <div className="flex-1 min-w-0">
                  <div className="flex items-center gap-3 text-sm">
                    <span className="font-medium text-foreground">
                      Test {i + 1}
                    </span>
                    <code className="font-mono text-xs text-foreground/60">
                      {JSON.stringify(test.input)}
                    </code>
                    <span className="text-foreground/40">→</span>
                    <code className="font-mono text-xs text-foreground">
                      {test.actual_output}
                    </code>
                    {!test.passed && (
                      <>
                        <span className="text-xs text-foreground/40">expected</span>
                        <code className="font-mono text-xs text-foreground/60">
                          {Array.isArray(test.expected_output) 
                            ? JSON.stringify(test.expected_output[0] || test.expected_output)
                            : JSON.stringify(test.expected_output)
                          }
                        </code>
                      </>
                    )}
                  </div>
                  
                  {/* Error (if any) */}
                  {test.error && (
                    <div className="mt-1 text-xs text-error">
                      {test.error}
                    </div>
                  )}
                </div>
              </div>
            </div>
          ))
        ) : (
          <div className="p-4 text-center text-foreground/50">
            No test results available
          </div>
        )}
      </div>
    </div>
  );
}

export { TestResults };
export type { TestResultsData, TestCase };