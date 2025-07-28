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
              <div className="font-mono text-xl">
                <span className="text-secondary">
                  ~/{questionData.difficulty.toLowerCase()}/
                </span>
                <span className="text-accent">
                  {questionData.title.toLowerCase().replace(/\s+/g, "_")}
                </span>
                {/* <span className="text-secondary">$</span> */}
              </div>
            </div>
            <div
              className="text-sm prose-sm prose max-w-none"
              dangerouslySetInnerHTML={{
                __html: transformLeetCodeHtml(
                  questionData.description_html || questionData.description
                ),
              }}
            />
          </div>
        ) : (
          <div>Loading question...</div>
        )}
      </div>
    </div>
  );
}
