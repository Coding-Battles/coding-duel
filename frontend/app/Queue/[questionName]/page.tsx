// This file was moved from in-game/page.tsx to [questionName]/page.tsx for dynamic routing.
"use client";
import { QuestionData } from "@/types/question";
import EditorWithTerminal from "@/components/EditorWithTerminal";
import { Language, getLanguageConfig } from "@/types/languages";
import { TestResultsData } from "@/components/TestResults";
import { useParams, useRouter } from "next/navigation";
import React from "react";
import { useGameContext } from "../layout";
import DuelInfo from "@/components/DuelInfo";
import { Button } from "@/components/ui/button";

export default function InGamePage() {
  const [selectedLanguage, setSelectedLanguage] =
    React.useState<Language>("python");
  const [userCode, setUserCode] = React.useState<string>("");
  const [questionData, setQuestionData] = React.useState<QuestionData | null>(
    null
  );
  const [loading, setLoading] = React.useState(true);
  const [error, setError] = React.useState<string | null>(null);
  const [testResults, setTestResults] = React.useState<
    TestResultsData | undefined
  >(undefined);
  const [isRunning, setIsRunning] = React.useState(false);
  const [hasResults, setHasResults] = React.useState(false);

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

  const runSampleTests = async (code: string): Promise<TestResultsData> => {
    setIsRunning(true);
    setTestResults(undefined); // Clear previous results for immediate feedback

    try {
      const response = await fetch(
        `${process.env.NEXT_PUBLIC_API_BASE_URL}/run-sample-tests`,
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
      setHasResults(true);
      return result;
    } catch (error) {
      console.error("Error running tests:", error);
      const errorResult: TestResultsData = {
        success: false,
        test_results: [],
        total_passed: 0,
        total_failed: 0,
        error: error instanceof Error ? error.message : "Unknown error",
      };
      setTestResults(errorResult);
      setHasResults(true);
      return errorResult;
    } finally {
      setIsRunning(false);
    }
  };

  const runAllTests = async (code: string): Promise<TestResultsData> => {
    setIsRunning(true);
    setTestResults(undefined); // Clear previous results for immediate feedback

    try {
      const response = await fetch(
        `${process.env.NEXT_PUBLIC_API_BASE_URL}/run-all-tests`,
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
      console.log("Full test execution result:", result);
      setTestResults(result);
      setHasResults(true);
      return result;
    } catch (error) {
      console.error("Error running all tests:", error);
      const errorResult: TestResultsData = {
        success: false,
        test_results: [],
        total_passed: 0,
        total_failed: 0,
        error: error instanceof Error ? error.message : "Unknown error",
      };
      setTestResults(errorResult);
      setHasResults(true);
      return errorResult;
    } finally {
      setIsRunning(false);
    }
  };

  const handleCloseResults = () => {
    setTestResults(undefined);
    setHasResults(false);
  };

  return (
    <div className="flex h-screen w-screen">
      <div className="flex flex-1 flex-row h-screen h-full gap-4 p-4 items-start justify-start">
        {/* Left panel - Question Description */}
        <div className="w-80 min-w-[400px] h-[calc(100vh-2rem)] bg-white border border-gray-200 rounded-lg p-4 overflow-y-auto">
          <h2 className="text-lg font-semibold text-gray-900 mb-4">
            {questionData?.title || "Loading..."}
          </h2>
          {questionData?.description_html ? (
            <div
              className="text-sm leading-relaxed"
              dangerouslySetInnerHTML={{
                __html: questionData.description_html,
              }}
            />
          ) : (
            <div className="text-gray-500">Loading question description...</div>
          )}
        </div>

        {/* Middle - Editor */}
        <div className="flex-1 min-w-[400px] w-full h-[calc(100vh-2rem)]">
          <EditorWithTerminal
            code={userCode}
            onCodeChange={(value) => {
              setUserCode(value || "");
              console.log("User code:", value);
            }}
            language={getLanguageConfig(selectedLanguage).monacoLanguage}
            theme="vs-dark"
            onRunCode={runSampleTests}
            selectedLanguage={selectedLanguage}
            onLanguageChange={handleLanguageChange}
            onRun={() => runSampleTests(userCode)}
            onSubmit={() => runAllTests(userCode)}
            testResults={testResults}
            isRunning={isRunning}
            hasResults={hasResults}
            onCloseResults={handleCloseResults}
            disableCopyPaste={true}
          />
        </div>

        {/* Right panel */}
        <div className="w-64 min-w-[300px] h-[calc(100vh-2rem)] justify-center items-center bg-white rounded-lg border border-gray-200 p-4 shadow-sm">
          <DuelInfo />
          <Button
            variant="destructive"
            className="mt-4"
            onClick={() => {
              // TODO: Replace with actual surrender logic
              alert("You have surrendered!");
            }}
          >
            Surrender
          </Button>
        </div>
      </div>
    </div>
  );
}
