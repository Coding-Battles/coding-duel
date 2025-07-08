"use client";

import React, { useState } from "react";
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
  const [selectedTest, setSelectedTest] = useState<number | null>(null);

  const formatExpectedOutput = (expected: unknown): string => {
    if (Array.isArray(expected)) {
      if (expected.length === 1) {
        // Single expected answer: [[0,1]] → [0,1] (compact to match actual output)
        return JSON.stringify(expected[0]);
      } else if (expected.length > 1) {
        // Multiple expected answers: [[1,2], [0,3]] → [1,2] or [0,3]
        return expected.map((item) => JSON.stringify(item)).join(" or ");
      }
    }
    // Fallback for non-array values (objects still pretty-printed)
    return JSON.stringify(expected, null, 2);
  };

  // Show loading state when tests are running
  if (isRunning) {
    return (
      <div
        className={`bg-gradient-to-br from-slate-900 via-slate-800 to-slate-900 ${className}`}
      >
        <div className="flex items-center justify-between bg-gradient-to-r from-slate-800/80 to-slate-700/80 backdrop-blur-sm px-4 py-3 border-b border-slate-600/30">
          <span className="text-white text-sm font-semibold flex items-center gap-2">
            <div
              className="w-2 h-2 rounded-full animate-pulse"
              className="bg-primary"
            ></div>
            Test Results
          </span>
        </div>
        <div className="p-6 flex items-center justify-center h-[calc(100%-3rem)]">
          <div className="flex items-center gap-4 text-slate-300 bg-slate-800/50 px-6 py-4 rounded-lg backdrop-blur-sm border border-slate-600/20">
            <Loader2
              size={24}
              className="animate-spin"
              className="text-primary"
            />
            <span className="text-lg font-medium">Running tests...</span>
          </div>
        </div>
      </div>
    );
  }

  if (!testResults) {
    return (
      <div
        className={`bg-gradient-to-br from-slate-900 via-slate-800 to-slate-900 ${className}`}
      >
        <div className="flex items-center justify-between bg-gradient-to-r from-slate-800/80 to-slate-700/80 backdrop-blur-sm px-4 py-3 border-b border-slate-600/30">
          <span className="text-white text-sm font-semibold flex items-center gap-2">
            <div className="w-2 h-2 bg-slate-500 rounded-full"></div>
            Test Results
          </span>
        </div>
        <div className="p-6 flex items-center justify-center h-[calc(100%-3rem)]">
          <div className="text-slate-400 text-center">
            <div className="mb-2 text-slate-500">
              <svg
                className="w-12 h-12 mx-auto mb-3 opacity-50"
                fill="none"
                stroke="currentColor"
                viewBox="0 0 24 24"
              >
                <path
                  strokeLinecap="round"
                  strokeLinejoin="round"
                  strokeWidth={1}
                  d="M9 5H7a2 2 0 00-2 2v12a2 2 0 002 2h10a2 2 0 002-2V7a2 2 0 00-2-2h-2M9 5a2 2 0 002 2h2a2 2 0 002-2M9 5a2 2 0 012-2h2a2 2 0 012 2"
                />
              </svg>
            </div>
            <p className="text-lg font-medium mb-1">Ready to test</p>
            <p className="text-sm text-slate-500">
              Run your code to see test results
            </p>
          </div>
        </div>
      </div>
    );
  }

  const { success, test_results, total_passed, total_failed, error } =
    testResults;

  return (
    <div className={` ${className}`}>
      <div
        className="flex items-center justify-between px-4 py-3 border-b border-slate-600/30"
        className="bg-primary"
      >
        <span className="text-white text-sm font-semibold flex items-center gap-2">
          <div
            className={`w-2 h-2 rounded-full ${
              success ? "bg-emerald-400" : "bg-red-400"
            } animate-pulse`}
          ></div>
          Test Results
        </span>
        {onCloseResults && (
          <button
            onClick={onCloseResults}
            className="text-slate-400 hover:text-white hover:bg-slate-700/50 p-1.5 rounded-md transition-colors"
            title="Close test results"
          >
            <X size={16} />
          </button>
        )}
      </div>

      <div
        className="p-4 space-y-4"
        className="bg-primary"
      >
        {error && (
          <div className="text-red-400 text-sm bg-red-900/20 p-3 rounded border border-red-800">
            {error}
          </div>
        )}

        {/* Expandable Detail Strip */}
        {selectedTest !== null && (
          <div className="bg-slate-800/40 border border-slate-600/20 rounded-lg p-3 mb-4">
            <div className="flex items-center justify-between mb-2">
              <span className="text-slate-300 font-medium">
                Test Case {selectedTest + 1} Details
              </span>
              <button
                onClick={() => setSelectedTest(null)}
                className="text-slate-400 hover:text-white text-sm"
              >
                ✕
              </button>
            </div>
            <div className="space-y-2 text-sm">
              <div>
                <span className="text-slate-400">Input: </span>
                <span 
                  className="font-mono bg-slate-900/50 px-2 py-1 rounded"
                  className="text-primary/80"
                >
                  {JSON.stringify(test_results[selectedTest].input)}
                </span>
              </div>
              {!test_results[selectedTest].passed && (
                <div>
                  <span className="text-slate-400">Expected: </span>
                  <span className="text-emerald-200 font-mono bg-emerald-900/30 px-2 py-1 rounded">
                    {formatExpectedOutput(test_results[selectedTest].expected_output)}
                  </span>
                </div>
              )}
              <div>
                <span className="text-slate-400">Actual: </span>
                <span 
                  className={`font-mono px-2 py-1 rounded ${
                    test_results[selectedTest].passed
                      ? "text-emerald-200 bg-emerald-900/30"
                      : "text-red-200 bg-red-900/30"
                  }`}
                >
                  {test_results[selectedTest].actual_output}
                </span>
              </div>
              {test_results[selectedTest].error && (
                <div>
                  <span className="text-slate-400">Error: </span>
                  <span className="text-red-200 font-mono bg-red-900/30 px-2 py-1 rounded">
                    {test_results[selectedTest].error}
                  </span>
                </div>
              )}
            </div>
          </div>
        )}

        {/* Horizontal Test Pills */}
        <div className="flex gap-4 flex-wrap">
          {test_results.slice(0, 3).map((test, i) => (
            <button
              key={i}
              onClick={() => setSelectedTest(selectedTest === i ? null : i)}
              className={`flex flex-col items-start gap-2 px-6 py-4 rounded-xl font-medium text-base transition-all min-w-[200px] border ${
                selectedTest === i
                  ? "ring-2 ring-slate-400"
                  : ""
              } ${
                test.passed
                  ? "bg-emerald-500/20 text-emerald-300 hover:bg-emerald-500/30 border-emerald-500/30"
                  : "bg-red-500/20 text-red-300 hover:bg-red-500/30 border-red-500/30"
              }`}
            >
              <div className="flex items-center gap-3 w-full">
                <span className={`text-xl font-bold ${
                  test.passed ? "text-emerald-400" : "text-red-400"
                }`}>
                  {test.passed ? "✓" : "✗"}
                </span>
                <span className="text-lg font-semibold">Test {i + 1}</span>
              </div>
              {!test.passed && (
                <div className="text-sm text-left w-full mt-1 opacity-90">
                  <div className="text-slate-400">Expected: <span className="text-emerald-300 font-mono">{formatExpectedOutput(test.expected_output)}</span></div>
                  <div className="text-slate-400">Got: <span className="text-red-300 font-mono">{test.actual_output}</span></div>
                </div>
              )}
              {test.passed && (
                <div className="text-sm text-slate-400 w-full mt-1">
                  Output: <span className="text-emerald-300 font-mono">{test.actual_output}</span>
                </div>
              )}
            </button>
          ))}
        </div>

        {test_results.length > 3 && (
          <div className="text-slate-400 text-sm text-center mt-4">
            <span className="text-slate-300">... and </span>
            <span
              className="font-semibold"
              className="text-primary/80"
            >
              {test_results.length - 3}
            </span>
            <span className="text-slate-300"> more test cases</span>
          </div>
        )}
      </div>
    </div>
  );
}

export { TestResults };
export type { TestResultsData, TestCase };
