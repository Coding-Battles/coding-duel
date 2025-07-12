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
      <div className="h-full w-full flex items-center justify-center bg-background border-l border-foreground/20">
        <div className="text-foreground/50">Loading question...</div>
      </div>
    );
  }

  if (error) {
    return (
      <div className="h-full w-full flex items-center justify-center bg-background border-l border-foreground/20">
        <div className="text-error">Error: {error}</div>
      </div>
    );
  }

  if (!questionData) {
    return (
      <div className="h-full w-full flex items-center justify-center bg-background border-l border-foreground/20">
        <div className="text-foreground/50">No question data available</div>
      </div>
    );
  }

  const getDifficultyColor = (difficulty: string) => {
    switch (difficulty.toLowerCase()) {
      case 'easy':
        return 'text-success bg-success/10';
      case 'medium':
        return 'text-accent bg-accent/10';
      case 'hard':
        return 'text-error bg-error/10';
      default:
        return 'text-foreground/60 bg-foreground/10';
    }
  };

  return (
    <div className="h-full w-full bg-background border-l border-foreground/20 overflow-y-auto">
      <div className="p-6 space-y-6">
        {/* Header */}
        <div className="space-y-3">
          <h1 className="text-2xl font-bold text-accent">{questionData.title}</h1>
          
          <div className="flex items-center gap-3">
            <span className={`px-3 py-1 rounded-full text-sm font-medium ${getDifficultyColor(questionData.difficulty)}`}>
              {questionData.difficulty}
            </span>
            
            <div className="flex flex-wrap gap-2">
              {questionData.tags.map((tag, index) => (
                <span 
                  key={index}
                  className="px-2 py-1 bg-accent/10 text-accent text-xs rounded-md"
                >
                  {tag}
                </span>
              ))}
            </div>
          </div>
        </div>

        {/* Description */}
        <div className="space-y-3">
          <h2 className="text-lg font-semibold text-foreground">Description</h2>
          <div 
            className="prose prose-sm max-w-none text-foreground/80"
            dangerouslySetInnerHTML={{ __html: questionData.description_html }}
          />
        </div>

        {/* Examples */}
        <div className="space-y-3">
          <h2 className="text-lg font-semibold text-foreground">Examples</h2>
          <div 
            className="prose prose-sm max-w-none"
            dangerouslySetInnerHTML={{ __html: questionData.examples_html }}
          />
        </div>

        {/* Constraints */}
        <div className="space-y-3">
          <h2 className="text-lg font-semibold text-foreground">Constraints</h2>
          <div 
            className="prose prose-sm max-w-none"
            dangerouslySetInnerHTML={{ __html: questionData.constraints_html }}
          />
        </div>

        {/* Follow-up */}
        {questionData.follow_up_html && (
          <div className="space-y-3">
            <h2 className="text-lg font-semibold text-foreground">Follow-up</h2>
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