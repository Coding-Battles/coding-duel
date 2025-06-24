"use client";

import React, { useEffect, useState } from "react";

interface QuestionData {
  id: string;
  title: string;
  difficulty: string;
  tags: string[];
  description_html: string;
  examples_html: string;
  constraints_html: string;
  follow_up_html?: string;
}

interface QuestionSidebarProps {
  questionName: string;
}

export function QuestionSidebar({ questionName }: QuestionSidebarProps) {
  const [questionData, setQuestionData] = useState<QuestionData | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    const fetchQuestion = async () => {
      try {
        setLoading(true);
        const response = await fetch(`${process.env.NEXT_PUBLIC_API_BASE_URL}/get-question/${questionName}`);
        
        if (!response.ok) {
          throw new Error(`Failed to fetch question: ${response.statusText}`);
        }
        
        const data = await response.json();
        setQuestionData(data);
      } catch (err) {
        setError(err instanceof Error ? err.message : 'Failed to load question');
      } finally {
        setLoading(false);
      }
    };

    fetchQuestion();
  }, [questionName]);

  if (loading) {
    return (
      <div className="h-full w-full flex items-center justify-center bg-white border-l border-gray-200">
        <div className="text-gray-500">Loading question...</div>
      </div>
    );
  }

  if (error) {
    return (
      <div className="h-full w-full flex items-center justify-center bg-white border-l border-gray-200">
        <div className="text-red-500">Error: {error}</div>
      </div>
    );
  }

  if (!questionData) {
    return (
      <div className="h-full w-full flex items-center justify-center bg-white border-l border-gray-200">
        <div className="text-gray-500">No question data available</div>
      </div>
    );
  }

  const getDifficultyColor = (difficulty: string) => {
    switch (difficulty.toLowerCase()) {
      case 'easy':
        return 'text-green-600 bg-green-100';
      case 'medium':
        return 'text-yellow-600 bg-yellow-100';
      case 'hard':
        return 'text-red-600 bg-red-100';
      default:
        return 'text-gray-600 bg-gray-100';
    }
  };

  return (
    <div className="h-full w-full bg-white border-l border-gray-200 overflow-y-auto">
      <div className="p-6 space-y-6">
        {/* Header */}
        <div className="space-y-3">
          <h1 className="text-2xl font-bold text-gray-900">{questionData.title}</h1>
          
          <div className="flex items-center gap-3">
            <span className={`px-3 py-1 rounded-full text-sm font-medium ${getDifficultyColor(questionData.difficulty)}`}>
              {questionData.difficulty}
            </span>
            
            <div className="flex flex-wrap gap-2">
              {questionData.tags.map((tag, index) => (
                <span 
                  key={index}
                  className="px-2 py-1 bg-blue-100 text-blue-700 text-xs rounded-md"
                >
                  {tag}
                </span>
              ))}
            </div>
          </div>
        </div>

        {/* Description */}
        <div className="space-y-3">
          <h2 className="text-lg font-semibold text-gray-800">Description</h2>
          <div 
            className="prose prose-sm max-w-none text-gray-700"
            dangerouslySetInnerHTML={{ __html: questionData.description_html }}
          />
        </div>

        {/* Examples */}
        <div className="space-y-3">
          <h2 className="text-lg font-semibold text-gray-800">Examples</h2>
          <div 
            className="prose prose-sm max-w-none"
            dangerouslySetInnerHTML={{ __html: questionData.examples_html }}
          />
        </div>

        {/* Constraints */}
        <div className="space-y-3">
          <h2 className="text-lg font-semibold text-gray-800">Constraints</h2>
          <div 
            className="prose prose-sm max-w-none"
            dangerouslySetInnerHTML={{ __html: questionData.constraints_html }}
          />
        </div>

        {/* Follow-up */}
        {questionData.follow_up_html && (
          <div className="space-y-3">
            <h2 className="text-lg font-semibold text-gray-800">Follow-up</h2>
            <div 
              className="prose prose-sm max-w-none"
              dangerouslySetInnerHTML={{ __html: questionData.follow_up_html }}
            />
          </div>
        )}
      </div>
    </div>
  );
}