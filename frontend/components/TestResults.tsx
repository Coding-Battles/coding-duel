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
      <div className={`bg-white dark:bg-gray-800 border-t border-gray-200 dark:border-gray-600 ${className}`}>
        <div className="flex items-center gap-3 px-4 py-3">
          <Loader2 size={16} className="animate-spin text-gray-600 dark:text-gray-400" />
          <span className="text-gray-600 dark:text-gray-400">Running tests...</span>
        </div>
      </div>
    );
  }

  if (!testResults) {
    return (
      <div className={`bg-white dark:bg-gray-800 border-t border-gray-200 dark:border-gray-600 ${className}`}>
        <div className="px-4 py-3">
          <span className="text-gray-500 dark:text-gray-400">
            Run your code to see results
          </span>
        </div>
      </div>
    );
  }

  const { test_results = [], total_passed, total_failed, error } = testResults;

  return (
    <div className={`bg-white dark:bg-gray-800 border-t border-gray-200 dark:border-gray-600 ${className}`}>
      {/* Header */}
      <div className="flex items-center justify-between px-4 py-3 border-b border-gray-200 dark:border-gray-600">
        <span className="text-gray-900 dark:text-gray-100">
          {total_passed}/{test_results?.length || 0} tests passed
        </span>
        {onCloseResults && (
          <button
            onClick={onCloseResults}
            className="text-gray-400 hover:text-gray-600 dark:hover:text-gray-300"
            title="Close"
          >
            <X size={16} />
          </button>
        )}
      </div>

      {/* Content */}
      <div className="p-4 space-y-3">
        {/* Error Message */}
        {error && (
          <div className="text-red-700 dark:text-red-300 bg-red-50 dark:bg-red-900/20 p-3 rounded text-sm">
            {error}
          </div>
        )}

        {/* Test Results - Minimal Layout */}
        {test_results && test_results.length > 0 ? (
          test_results.map((test, i) => (
            <div key={i} className="py-2 border-b border-gray-200 dark:border-gray-700 last:border-b-0">
              <div className="flex items-center gap-4">
                {/* Pass/Fail Indicator */}
                <span className={`w-5 h-5 rounded-full flex items-center justify-center text-xs font-medium ${
                  test.passed 
                    ? "bg-green-100 dark:bg-green-900/30 text-green-700 dark:text-green-300" 
                    : "bg-red-100 dark:bg-red-900/30 text-red-700 dark:text-red-300"
                }`}>
                  {test.passed ? "✓" : "✗"}
                </span>

                {/* Test Info */}
                <div className="flex-1 min-w-0">
                  <div className="flex items-center gap-3 text-sm">
                    <span className="text-gray-900 dark:text-gray-100 font-medium">
                      Test {i + 1}
                    </span>
                    <code className="text-gray-600 dark:text-gray-400 font-mono text-xs">
                      {JSON.stringify(test.input)}
                    </code>
                    <span className="text-gray-400">→</span>
                    <code className="text-gray-900 dark:text-gray-100 font-mono text-xs">
                      {test.actual_output}
                    </code>
                    {!test.passed && (
                      <>
                        <span className="text-gray-400 text-xs">expected</span>
                        <code className="text-gray-600 dark:text-gray-400 font-mono text-xs">
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
                    <div className="mt-1 text-xs text-red-600 dark:text-red-400">
                      {test.error}
                    </div>
                  )}
                </div>
              </div>
            </div>
          ))
        ) : (
          <div className="p-4 text-center text-gray-500 dark:text-gray-400">
            No test results available
          </div>
        )}
      </div>
    </div>
  );
}

export { TestResults };
export type { TestResultsData, TestCase };