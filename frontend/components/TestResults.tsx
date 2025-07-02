"use client";

import React, { useState } from "react";

interface TestCase {
  input: Record<string, any>;
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
  height?: string;
  className?: string;
}

export default function TestResults({
  testResults,
  height = "300px",
  className = "",
}: TestResultsProps) {
  const [selectedTest, setSelectedTest] = useState<number | null>(null);

  if (!testResults) {
    return (
      <div
        className={`bg-[#1e1e1e] border border-gray-600 ${className}`}
        style={{ height }}
      >
        <div className="flex items-center justify-between bg-gray-800 px-3 py-1 border-b border-gray-600">
          <span className="text-white text-sm font-medium">Test Results</span>
        </div>
        <div className="p-4 text-gray-400 text-sm">
          Run your code to see test results
        </div>
      </div>
    );
  }

  const { success, test_results, total_passed, total_failed, error } = testResults;

  return (
    <div
      className={`bg-[#1e1e1e] border border-gray-600 ${className}`}
      style={{ height }}
    >
      <div className="flex items-center justify-between bg-gray-800 px-3 py-1 border-b border-gray-600">
        <span className="text-white text-sm font-medium">Test Results</span>
      </div>
      
      <div className="p-4 space-y-4 h-[calc(100%-2rem)] overflow-y-auto">
        {error && (
          <div className="text-red-400 text-sm bg-red-900/20 p-3 rounded border border-red-800">
            {error}
          </div>
        )}
        
        {/* Summary */}
        <div className="flex items-center gap-4">
          <span className={success ? "text-green-400" : "text-red-400"}>
            {success ? "✓ Accepted" : "✗ Wrong Answer"}
          </span>
          <span className="text-gray-400">
            {total_passed}/{total_passed + total_failed} test cases passed
          </span>
        </div>

        {/* Test Cases (first 3) */}
        {test_results.slice(0, 3).map((test, i) => (
          <div
            key={i}
            className="border border-gray-600 rounded p-3 cursor-pointer hover:bg-gray-800/50 transition-colors"
            onClick={() => setSelectedTest(selectedTest === i ? null : i)}
          >
            <div className="flex justify-between items-center">
              <span className={test.passed ? "text-green-400" : "text-red-400"}>
                {test.passed ? "✓" : "✗"} Test Case {i + 1}
              </span>
              <span className="text-xs text-gray-500">
                {test.execution_time}ms
              </span>
            </div>
            {!test.passed && (
              <div className="text-red-400 text-sm mt-1">
                Expected: {test.expected_output}
              </div>
            )}
            {selectedTest === i && (
              <div className="mt-3 space-y-2 text-sm border-t border-gray-600 pt-3">
                <div>
                  <span className="text-gray-400">Input: </span>
                  <span className="text-white">
                    {JSON.stringify(test.input, null, 2)}
                  </span>
                </div>
                <div>
                  <span className="text-gray-400">Expected: </span>
                  <span className="text-green-400">{test.expected_output}</span>
                </div>
                <div>
                  <span className="text-gray-400">Actual: </span>
                  <span className={test.passed ? "text-green-400" : "text-red-400"}>
                    {test.actual_output}
                  </span>
                </div>
                {test.error && (
                  <div>
                    <span className="text-gray-400">Error: </span>
                    <span className="text-red-400">{test.error}</span>
                  </div>
                )}
              </div>
            )}
          </div>
        ))}

        {test_results.length > 3 && (
          <div className="text-gray-400 text-sm text-center">
            ... and {test_results.length - 3} more test cases
          </div>
        )}
      </div>
    </div>
  );
}

export { TestResults };
export type { TestResultsData, TestCase };