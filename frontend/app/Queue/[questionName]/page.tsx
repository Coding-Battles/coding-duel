// This file was moved from in-game/page.tsx to [questionName]/page.tsx for dynamic routing.
"use client";
import { InGameSideBar } from "@/components/inGameSideBar";
import { Button } from "@/components/ui/button";
import {
  SidebarInset,
  SidebarProvider,
  SidebarTrigger,
} from "@/components/ui/sidebar";
import { QuestionData } from "@/types/question";
import EditorWithTerminal from "@/components/EditorWithTerminal";
import { Language, getLanguageConfig } from "@/types/languages";
import { TestResultsData } from "@/components/TestResults";
import { Check } from "lucide-react";
import { useParams, useRouter } from "next/navigation";
import React from "react";
import { useGameContext } from "../layout";

export default function InGamePage() {
  const [selectedLanguage, setSelectedLanguage] = React.useState<Language>('python');
  const [userCode, setUserCode] = React.useState<string>('');
  const [questionData, setQuestionData] = React.useState<QuestionData | null>(
    null
  );
  const [loading, setLoading] = React.useState(true);
  const [error, setError] = React.useState<string | null>(null);
  const [testResults, setTestResults] = React.useState<TestResultsData | undefined>(undefined);

  const context = useGameContext();
  const router = useRouter();
  const params = useParams();
  const questionName = params?.questionName;

  React.useEffect(() => {
    if (!context) {
      router.push("/queue");
    }
  }, [context, router]);

  React.useEffect(() => {
    const fetchQuestion = async () => {
      try {
        setLoading(true);
        if (!questionName) throw new Error("No question id in URL");
        const response = await fetch(
          `${process.env.NEXT_PUBLIC_API_BASE_URL}/get-question/${questionName}`
        );

        if (!response.ok) {
          throw new Error(`Failed to fetch question: ${response.statusText}`);
        }

        const data = await response.json();
        setQuestionData(data);
      } catch (err) {
        setError(
          err instanceof Error ? err.message : "Failed to load question"
        );
      } finally {
        setLoading(false);
      }
    };

    fetchQuestion();
  }, [questionName]);

  // Set initial starter code when question data loads
  React.useEffect(() => {
    if (questionData && questionData.starter_code) {
      const starterCode = questionData.starter_code[selectedLanguage];
      if (starterCode) {
        setUserCode(starterCode);
      }
    }
  }, [questionData, selectedLanguage]);

  if (!context) {
    return <div>Loading...</div>;
  }

  if (loading) {
    return (
      <div className="flex h-[100%] w-[100%] items-center justify-center">
        <div>Loading question...</div>
      </div>
    );
  }

  if (error) {
    return (
      <div className="flex h-[100%] w-[100%] items-center justify-center">
        <div className="text-red-500">Error: {error}</div>
      </div>
    );
  }

  const { socket } = context;

  const handleLanguageChange = (language: Language) => {
    setSelectedLanguage(language);
    if (questionData && questionData.starter_code) {
      const starterCode = questionData.starter_code[language];
      if (starterCode) {
        setUserCode(starterCode);
      }
    }
  };

  const runCode = async (code: string): Promise<TestResultsData> => {
    try {
      const response = await fetch(
        `${process.env.NEXT_PUBLIC_API_BASE_URL}/test_code`,
        {
          method: "POST",
          headers: {
            "Content-Type": "application/json",
          },
          body: JSON.stringify({
            code: code,
            question_name: questionName,
            language: selectedLanguage,
          }),
        }
      );

      const result = await response.json();
      console.log("Test execution result:", result);
      setTestResults(result);
      return result;
    } catch (error) {
      console.error("Error running tests:", error);
      const errorResult: TestResultsData = {
        success: false,
        test_results: [],
        total_passed: 0,
        total_failed: 0,
        error: error instanceof Error ? error.message : "Unknown error"
      };
      setTestResults(errorResult);
      return errorResult;
    }
  };
  return (
    <div className="flex h-screen w-screen">
      <SidebarProvider>
        <InGameSideBar questionData={questionData} />
        <SidebarInset>
          <header className="flex h-16 shrink-0 justify-between items-center gap-2 border-b px-4">
            <SidebarTrigger className="-ml-1" />
            <h1 className="text-lg font-semibold">BATTLE</h1>
            <div />
          </header>
          <div className="flex flex-1 flex-col gap-4 p-4">
            <div className="flex h-[100%] w-[100%]">
              <div className="flex-1 w-full h-full">
                <EditorWithTerminal
                  code={userCode}
                  onCodeChange={(value) => {
                    setUserCode(value || "");
                    console.log("User code:", value);
                  }}
                  language={getLanguageConfig(selectedLanguage).monacoLanguage}
                  theme="vs-dark"
                  onRunCode={runCode}
                  selectedLanguage={selectedLanguage}
                  onLanguageChange={handleLanguageChange}
                  onRun={() => runCode(userCode)}
                  onSubmit={() => runCode(userCode)}
                  testResults={testResults}
                />
              </div>
            </div>
          </div>
        </SidebarInset>
      </SidebarProvider>
    </div>
  );
}
