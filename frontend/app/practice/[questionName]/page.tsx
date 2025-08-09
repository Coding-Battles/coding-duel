"use client";
import { QuestionData, TestResultsData } from "@/shared/types";
import EditorWithTerminal from "@/components/EditorWithTerminal";
import QuestionColumn from "@/components/QuestionColumn";
import { Language, getLanguageConfig } from "@/types/languages";
import { useParams, useRouter } from "next/navigation";
import React, { useCallback, useEffect, useRef, useState } from "react";
import { useSession } from "@/lib/auth-client";
import { StackableAlerts } from "@/components/ui/alert";

type AlertType = { id: string; message: string; variant?: string };

export default function PracticePage() {
  // Always use dark theme for Monaco editor
  const monacoTheme = "vs-dark";

  // All useState hooks
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
  const [alerts, setAlerts] = React.useState<AlertType[]>([]);
  const [leftWidth, setLeftWidth] = useState(33.33);
  // Removed right column, so no rightWidth
  const [isRunning, setIsRunning] = React.useState(false);
  const [hasResults, setHasResults] = React.useState(false);

  // All useRef hooks
  const timeRef = useRef<number>(0);
  const isDraggingLeft = useRef(false);
  // Removed right column, so no isDraggingRight
  const containerRef = useRef<HTMLDivElement>(null);

  const router = useRouter();
  const params = useParams();
  const { data: userSession } = useSession();

  // All useCallback hooks
  const handleLeftMouseDown = useCallback(
    (e: React.MouseEvent<HTMLDivElement>) => {
      isDraggingLeft.current = true;
      e.preventDefault();
    },
    []
  );

  // Removed right column, so no handleRightMouseDown

  const handleMouseMove = useCallback((e: MouseEvent) => {
    if (!containerRef.current) return;

    const containerRect = containerRef.current.getBoundingClientRect();
    const containerWidth = containerRect.width;
    const mouseX = e.clientX - containerRect.left;
    const percentage = (mouseX / containerWidth) * 100;

    if (isDraggingLeft.current) {
      const newLeftWidth = Math.min(Math.max(percentage, 20), 60);
      setLeftWidth(newLeftWidth);
    }
    // No right column logic
  }, []);

  const handleMouseUp = useCallback(() => {
    isDraggingLeft.current = false;
    // No right column
  }, []);

  // All useEffect hooks
  React.useEffect(() => {
    document.addEventListener("mousemove", handleMouseMove);
    document.addEventListener("mouseup", handleMouseUp);

    return () => {
      document.removeEventListener("mousemove", handleMouseMove);
      document.removeEventListener("mouseup", handleMouseUp);
    };
  }, [handleMouseMove, handleMouseUp]);

  useEffect(() => {
    timeRef.current = 0;
  }, []);

  useEffect(() => {
    const questionName = params?.questionName;
    const fetchQuestion = async () => {
      try {
        console.log(
          "🚀 [PRACTICE DEBUG] Starting to fetch question:",
          questionName
        );
        setLoading(true);
        if (!questionName)
          throw new Error(
            "No question name found in URL. Please check the URL and try again."
          );
        const response = await fetch(
          `${process.env.NEXT_PUBLIC_API_BASE_URL}/api/get-question/${questionName}`
        );

        if (!response.ok) {
          throw new Error(`Failed to fetch question: ${response.statusText}`);
        }

        const data = await response.json();
        console.log(
          "🚀 [PRACTICE DEBUG] Question data loaded successfully:",
          !!data
        );
        setQuestionData(data);
      } catch (err) {
        console.error("🚀 [PRACTICE DEBUG] Failed to fetch question:", err);
        setError(
          err instanceof Error ? err.message : "Failed to load question"
        );
      } finally {
        setLoading(false);
      }
    };

    if (questionName) {
      fetchQuestion();
    } else {
      console.warn("🚀 [PRACTICE DEBUG] No question name in params:", params);
    }
  }, [params?.questionName]);

  useEffect(() => {
    console.log(
      "🚀 [PRACTICE DEBUG] useEffect triggered - questionData:",
      !!questionData,
      "selectedLanguage:",
      selectedLanguage
    );
    if (questionData && questionData.starter_code) {
      const starterCode = questionData.starter_code[selectedLanguage];
      console.log(
        "🚀 [PRACTICE DEBUG] Found starter code for",
        selectedLanguage,
        ":",
        !!starterCode,
        "length:",
        starterCode?.length
      );
      if (starterCode) {
        setUserCode(starterCode);
        console.log("🚀 [PRACTICE DEBUG] Set userCode to starter code");
      }
    } else {
      console.warn(
        "🚀 [PRACTICE DEBUG] Missing questionData or starter_code:",
        {
          questionData: !!questionData,
          starter_code: !!questionData?.starter_code,
          selectedLanguage,
        }
      );
    }
  }, [questionData, selectedLanguage]);

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
        <div className="text-error">Error: {error}</div>
      </div>
    );
  }

  const questionName = params?.questionName;

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
    setTestResults(undefined);

    try {
      if (!questionName) {
        throw new Error("Question name not found in URL");
      }

      const requestPayload = {
        player_id: userSession?.user?.id || "practice-user",
        code: code,
        question_name: questionName,
        language: selectedLanguage,
        timer: timeRef.current,
      };

      const response = await fetch(
        `${process.env.NEXT_PUBLIC_API_BASE_URL}/api/${questionName}/test-sample`,
        {
          method: "POST",
          headers: {
            "Content-Type": "application/json",
          },
          body: JSON.stringify(requestPayload),
        }
      );

      const result = await response.json();
      setTestResults(result);
      setHasResults(true);

      // Show success/error alert
      setAlerts((prev) => [
        ...prev,
        {
          id: `sample-test-${Date.now()}`,
          message: result.success
            ? `✅ Sample tests passed! ${result.total_passed}/${
                result.total_passed + result.total_failed
              } tests passed`
            : `❌ Sample tests failed: ${result.total_passed}/${
                result.total_passed + result.total_failed
              } tests passed`,
          variant: result.success ? "default" : "destructive",
        },
      ]);

      return result;
    } catch (error) {
      const errorResult: TestResultsData = {
        success: false,
        test_results: [],
        total_passed: 0,
        player_name: "",
        total_failed: 0,
        error: error instanceof Error ? error.message : "Unknown error",
        message: "",
        code: "",
        opponent_id: "",
      };
      setTestResults(errorResult);
      setHasResults(true);

      setAlerts((prev) => [
        ...prev,
        {
          id: `error-${Date.now()}`,
          message: `❌ Error running tests: ${errorResult.error}`,
          variant: "destructive",
        },
      ]);

      return errorResult;
    } finally {
      setIsRunning(false);
    }
  };

  const runAllTests = async (code: string): Promise<TestResultsData> => {
    setIsRunning(true);
    setTestResults(undefined);

    try {
      if (!questionName) {
        throw new Error("Question name not found in URL");
      }

      const requestPayload = {
        player_id: userSession?.user?.id || "practice-user",
        code: code,
        question_name: questionName,
        language: selectedLanguage,
        timer: timeRef.current,
      };

      const response = await fetch(
        `${process.env.NEXT_PUBLIC_API_BASE_URL}/api/${questionName}/test`,
        {
          method: "POST",
          headers: {
            "Content-Type": "application/json",
          },
          body: JSON.stringify(requestPayload),
        }
      );

      const result = await response.json();
      setTestResults(result);
      setHasResults(true);

      // Show success/error alert
      setAlerts((prev) => [
        ...prev,
        {
          id: `all-test-${Date.now()}`,
          message: result.success
            ? `🎉 All tests passed! ${result.total_passed}/${
                result.total_passed + result.total_failed
              } tests passed`
            : `📝 Tests completed: ${result.total_passed}/${
                result.total_passed + result.total_failed
              } tests passed`,
          variant: result.success ? "default" : "destructive",
        },
      ]);

      return result;
    } catch (error) {
      const errorResult: TestResultsData = {
        success: false,
        test_results: [],
        player_name: "",
        total_passed: 0,
        total_failed: 0,
        error: error instanceof Error ? error.message : "Unknown error",
        message: "",
        code: "",
        opponent_id: "",
      };
      setTestResults(errorResult);
      setHasResults(true);

      setAlerts((prev) => [
        ...prev,
        {
          id: `error-${Date.now()}`,
          message: `❌ Error running tests: ${errorResult.error}`,
          variant: "destructive",
        },
      ]);

      return errorResult;
    } finally {
      setIsRunning(false);
    }
  };

  const handleCloseResults = () => {
    setTestResults(undefined);
    setHasResults(false);
  };

  const middleWidth = 100 - leftWidth;

  return (
    <div
      ref={containerRef}
      className="flex items-center justify-center w-screen h-screen"
      data-testid="practice-page"
    >
      <StackableAlerts alerts={alerts} setAlerts={setAlerts} />

      <div className="flex w-full h-full">
        {/* Left Column - Question */}
        <QuestionColumn
          questionData={questionData}
          loading={loading}
          width={leftWidth}
        />

        {/* Left Resizer */}
        <div
          className="relative w-1 transition-colors duration-200 cursor-col-resize group"
          style={{ backgroundColor: "var(--border)" }}
          onMouseDown={handleLeftMouseDown}
        >
          <div className="absolute inset-0 w-3 -ml-1" />
          <div
            className="absolute w-1 h-8 transition-colors duration-200 transform -translate-x-1/2 -translate-y-1/2 rounded top-1/2 left-1/2"
            style={{
              backgroundColor: "var(--border)",
              opacity: "0.8",
            }}
          />
        </div>

        {/* Middle Column - Editor (now takes all remaining space) */}
        <div className="h-full" style={{ width: `${middleWidth}%` }}>
          <EditorWithTerminal
            code={userCode}
            onCodeChange={(value) => {
              const newCode = value || "";
              setUserCode(newCode);
            }}
            language={getLanguageConfig(selectedLanguage).monacoLanguage}
            theme={monacoTheme}
            onRunCode={runSampleTests}
            selectedLanguage={selectedLanguage}
            onLanguageChange={handleLanguageChange}
            onRun={() => runSampleTests(userCode)}
            onSubmit={() => runAllTests(userCode)}
            testResults={testResults}
            isRunning={isRunning}
            hasResults={hasResults}
            onCloseResults={handleCloseResults}
          />
        </div>
      </div>
    </div>
  );
}
