// This file was moved from in-game/page.tsx to [questionName]/page.tsx for dynamic routing.
"use client";
import { QuestionData } from "@/types/question";
import EditorWithTerminal from "@/components/EditorWithTerminal";
import { Language, getLanguageConfig } from "@/types/languages";
import { TestResultsData } from "@/components/TestResults";
import { useParams, useRouter } from "next/navigation";
import React, { useCallback, useEffect, useRef, useState } from "react";
import { useGameContext } from "../../layout";
import { useSession } from "@/lib/auth-client";
import { StackableAlerts } from "@/components/ui/alert";
import { useTheme } from "next-themes";
import GameTimer from "@/components/GameTimer";
import FinishedPage from "@/components/FinishedPage";
import {
  dummyOpponent,
  dummyOpponentStats,
  dummyUser,
  dummyUserStats,
} from "@/components/dummyData/FinishedPageData";

const TestFinishedPage = true;

import DuelInfo from "@/components/DuelInfo";
import {
  transformLeetCodeHtml,
  getDifficultyClass,
} from "@/lib/leetcode-html-transformer";

type AlertType = { id: string; message: string; variant?: string };

export default function InGamePage() {
  // ALL HOOKS MUST BE DECLARED AT THE TOP - NO CONDITIONAL LOGIC BEFORE HOOKS
  const { resolvedTheme } = useTheme();
  const monacoTheme = resolvedTheme === "dark" ? "vs-dark" : "vs";

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
  const [rightWidth, setRightWidth] = useState(25);
  const [gameFinished, setGameFinished] = React.useState(false);
  const [isRunning, setIsRunning] = React.useState(false);
  const [hasResults, setHasResults] = React.useState(false);
  const [opponentStatus, setOpponentStatus] = React.useState<string | null>(
    null
  );

  // All useRef hooks
  const opponentTestStatsRef = useRef<TestResultsData | undefined>(undefined);
  const timeRef = useRef<number>(0);
  const isDraggingLeft = useRef(false);
  const isDraggingRight = useRef(false);
  const containerRef = useRef<HTMLDivElement>(null);

  // All useContext hooks
  const context = useGameContext();
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

  const handleRightMouseDown = useCallback(
    (e: React.MouseEvent<HTMLDivElement>) => {
      isDraggingRight.current = true;
      e.preventDefault();
    },
    []
  );

  const handleMouseMove = useCallback((e: MouseEvent) => {
    if (!containerRef.current) return;

    const containerRect = containerRef.current.getBoundingClientRect();
    const containerWidth = containerRect.width;
    const mouseX = e.clientX - containerRect.left;
    const percentage = (mouseX / containerWidth) * 100;

    if (isDraggingLeft.current) {
      const newLeftWidth = Math.min(Math.max(percentage, 20), 60);
      setLeftWidth(newLeftWidth);
    } else if (isDraggingRight.current) {
      const rightPercentage =
        ((containerWidth - mouseX) / containerWidth) * 100;
      const newRightWidth = Math.min(Math.max(rightPercentage, 15), 40);
      setRightWidth(newRightWidth);
    }
  }, []);

  const handleMouseUp = useCallback(() => {
    isDraggingLeft.current = false;
    isDraggingRight.current = false;
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
    const session = context?.socket;
    if (!session) {
      console.warn("Socket not ready yet, waiting...");
      return;
    }

    const handleOpponentSubmitted = (data: TestResultsData) => {
      console.log(
        "🔍 [OPPONENT DEBUG] Frontend received opponent_submitted event"
      );
      console.log("🔍 [OPPONENT DEBUG] Data:", data);

      if (data.success) {
        setOpponentStatus(
          `🎉 Opponent finished! All ${data.total_passed} tests passed (${
            data.complexity || "N/A"
          } complexity)`
        );
      } else {
        setOpponentStatus(
          `⚠️ Opponent submitted: ${data.total_passed}/${
            data.total_passed + data.total_failed
          } tests passed`
        );
      }

      setAlerts((prev) => [
        ...prev,
        {
          id: `opponent-${Date.now()}-${Math.random()}`,
          message: `Opponent ${data.opponent_id} submitted code: ${data.message}`,
          variant: "default",
        },
      ]);

      opponentTestStatsRef.current = data;
    };

    const handleGameCompleted = (data: { message: string }) => {
      console.log("Game completed data:", data);

      setAlerts((prev) => [
        ...prev,
        {
          id: `game-completed-${Date.now()}-${Math.random()}`,
          message: `Game completed: ${data.message}`,
          variant: "destructive",
        },
      ]);

      setTimeout(() => {
        setGameFinished(true);
      }, 5000);
    };

    session.on("opponent_submitted", handleOpponentSubmitted);
    session.on("game_completed", handleGameCompleted);

    return () => {
      session.off("opponent_submitted", handleOpponentSubmitted);
      session.off("game_completed", handleGameCompleted);
    };
  }, [context?.socket]);

  useEffect(() => {
    if (!context) {
      console.warn("Game context not ready yet, waiting...");
      return;
    }

    if (context && !context.socket && !context.loading) {
      console.log(
        "Context is stable but socket is missing, redirecting to queue"
      );
      router.push("/queue");
    }
  }, [context, router]);

  useEffect(() => {
    const questionName = params?.questionName;
    const fetchQuestion = async () => {
      try {
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
        setQuestionData(data);
      } catch (err) {
        setError(
          err instanceof Error ? err.message : "Failed to load question"
        );
      } finally {
        setLoading(false);
      }
    };

    if (questionName) {
      fetchQuestion();
    }
  }, [params?.questionName]);

  useEffect(() => {
    if (questionData && questionData.starter_code) {
      const starterCode = questionData.starter_code[selectedLanguage];
      if (starterCode) {
        setUserCode(starterCode);
      }
    }
  }, [questionData, selectedLanguage]);

  // NOW all conditional returns can happen AFTER all hooks are declared
  if (!context) {
    return <div>Loading game context...</div>;
  }

  if (context.loading) {
    return <div>Connecting to game...</div>;
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
        <div className="text-error">Error: {error}</div>
      </div>
    );
  }

  // Rest of your component logic...
  const { socket } = context;
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
        player_id: "sample-test-user",
        code: code,
        question_name: questionName,
        language: selectedLanguage,
        timer: timeRef.current,
      };

      const response = await fetch(
        `${process.env.NEXT_PUBLIC_API_BASE_URL}/api/run-sample-tests`,
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
      return errorResult;
    } finally {
      setIsRunning(false);
    }
  };

  const runAllTests = async (code: string): Promise<TestResultsData> => {
    setIsRunning(true);
    setTestResults(undefined);

    try {
      const playerId = context.isAnonymous
        ? context.anonymousId
        : userSession?.user?.id;

      if (!playerId) {
        throw new Error("Player ID not found. Please refresh and try again.");
      }

      if (!context.gameId) {
        throw new Error("Game ID not found. Please return to the queue.");
      }

      const response = await fetch(
        `${process.env.NEXT_PUBLIC_API_BASE_URL}/api/${context.gameId}/run-all-tests`,
        {
          method: "POST",
          headers: {
            "Content-Type": "application/json",
          },
          body: JSON.stringify({
            player_id: playerId,
            code: code,
            question_name: questionName,
            language: selectedLanguage,
            timer: Math.floor(timeRef.current),
          }),
        }
      );

      const result = await response.json();
      setTestResults(result);
      setHasResults(true);
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
      return errorResult;
    } finally {
      setIsRunning(false);
    }
  };

  const handleCloseResults = () => {
    setTestResults(undefined);
    setHasResults(false);
  };

  const middleWidth = 100 - leftWidth - rightWidth;

  console.log("context: ", context);
  return (
    <div ref={containerRef} className="flex w-screen h-screen">
      <StackableAlerts alerts={alerts} setAlerts={setAlerts} />

      {!gameFinished ? (
        <div className="flex w-full h-full">
          {/* Left Column - Question */}
          <div
            className="relative overflow-y-auto border-r"
            style={{ width: `${leftWidth}%` }}
          >
            <div className="p-4">
              {questionData ? (
                <div className="space-y-4">
                  <div className="flex items-center gap-3 mb-4">
                    <h2 className="text-xl font-bold">{questionData.title}</h2>
                    <span
                      className={getDifficultyClass(questionData.difficulty)}
                    >
                      {questionData.difficulty}
                    </span>
                  </div>
                  <div
                    className="text-sm prose-sm prose max-w-none"
                    dangerouslySetInnerHTML={{
                      __html: transformLeetCodeHtml(
                        questionData.description_html
                      ),
                    }}
                  />
                </div>
              ) : (
                <div>Loading question...</div>
              )}
            </div>
          </div>

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

          {/* Middle Column - Editor */}
          <div className="h-full" style={{ width: `${middleWidth}%` }}>
            <EditorWithTerminal
              code={userCode}
              onCodeChange={(value) => {
                setUserCode(value || "");
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

          {/* Right Resizer */}
          <div
            className="relative w-1 transition-colors duration-200 cursor-col-resize group"
            style={{ backgroundColor: "var(--border)" }}
            onMouseDown={handleRightMouseDown}
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

          {/* Right Column - DuelInfo */}
          <div
            className="relative overflow-y-auto"
            style={{ width: `${rightWidth}%` }}
          >
            <div className="p-4">
              {opponentStatus && (
                <div className="p-3 mb-4 border rounded-lg bg-accent/10 border-accent/20">
                  <p className="text-sm font-medium text-accent">
                    {opponentStatus}
                  </p>
                </div>
              )}
              <DuelInfo
                timeRef={timeRef}
                opponentData={context.opponent}
                user={context.user ?? undefined}
                socket={context.socket ?? undefined}
                gameId={context.gameId ?? undefined}
              />
            </div>
          </div>
        </div>
      ) : (
        opponentTestStatsRef.current &&
        testResults && (
          <FinishedPage
            opponent={context.opponent}
            user={context.user}
            opponentStats={opponentTestStatsRef.current}
            userStats={testResults}
          />
        )
      )}
    </div>
  );
}
