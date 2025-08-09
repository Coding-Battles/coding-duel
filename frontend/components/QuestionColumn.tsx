import React from "react";
import { QuestionData } from "@/shared/types";
import { transformLeetCodeHtml } from "@/lib/leetcode-html-transformer";

interface QuestionColumnProps {
  questionData: QuestionData | null;
  loading?: boolean;
  width: number;
}

export default function QuestionColumn({
  questionData,
  loading = false,
  width,
}: QuestionColumnProps) {
  return (
    <div
      className="relative overflow-y-auto border-r"
      style={{ width: `${width}%` }}
    >
      <div className="p-4">
        {loading ? (
          <div>Loading question...</div>
        ) : questionData ? (
          <div className="space-y-4">
            {/* Terminal-style header */}
            <div className="flex items-center justify-between mb-4">
              <div className="font-mono text-2xl">
                <span className="text-secondary">
                  ~/{questionData.difficulty.toLowerCase()}/
                </span>
                <span className="text-accent">
                  {questionData.title.toLowerCase().replace(/\s+/g, "_")}
                </span>
                {/* <span className="text-secondary">$</span> */}
              </div>
            </div>
            {/* Semantic format with terminal styling */}
            <div className="font-mono text-sm space-y-6">
              {/* The Problem section */}
              <div>
                <div className="mb-3 text-lg">
                  <span className="text-secondary">$ </span>
                  <span className="text-accent">The Problem</span>
                </div>
                <div 
                  className="text-white leading-relaxed mb-4"
                  dangerouslySetInnerHTML={{
                    __html: questionData.problemDescription
                      .replace(/<=|>=|<|>/g, (match) => 
                        `<span class="text-secondary">${match}</span>`
                      )
                      .replace(
                        /(\d+)\s*\^\s*(\d+)/g,
                        (match, base, exp) => `${base}<sup>${exp}</sup>`
                      )
                  }}
                />
              </div>

              {/* Sample Runs section */}
              <div>
                <div className="mb-3 text-lg">
                  <span className="text-secondary">$ </span>
                  <span className="text-accent">Sample Runs</span>
                </div>
                <div className="space-y-2">
                  {questionData.examples.map((example, index) => (
                    <div key={index} className="text-white">
                      {example.input} <span className="text-secondary">→</span>{" "}
                      {example.output}
                    </div>
                  ))}
                </div>
              </div>

              {/* Bounds section - only show if constraints exist */}
              {questionData.constraints &&
                questionData.constraints.length > 0 && (
                  <div>
                    <div className="mb-3 text-lg">
                      <span className="text-secondary">$ </span>
                      <span className="text-accent">Bounds</span>
                    </div>
                    <div className="space-y-2 text-white leading-relaxed">
                      {questionData.constraints.map((constraint, index) => (
                        <div
                          key={index}
                          dangerouslySetInnerHTML={{
                            __html: constraint
                              .replace(
                                /<=|>=|<|>/g,
                                (match) =>
                                  `<span class="text-secondary">${match}</span>`
                              )
                              .replace(
                                /(\d+)\s*\^\s*(\d+)/g,
                                (match, base, exp) => `${base}<sup>${exp}</sup>`
                              ),
                          }}
                        />
                      ))}
                    </div>
                  </div>
                )}
            </div>
          </div>
        ) : (
          <div>Loading question...</div>
        )}
      </div>
    </div>
  );
}
