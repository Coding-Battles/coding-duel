// This file was moved from in-game/page.tsx to [questionName]/page.tsx for dynamic routing.
"use client";
import { QuestionData } from "@/types/question";
import EditorWithTerminal from "@/components/EditorWithTerminal";
import { Language, getLanguageConfig } from "@/types/languages";
import { TestResultsData } from "@/components/TestResults";
import { useParams, useRouter } from "next/navigation";
import React, { useEffect, useRef } from "react";
import { useGameContext } from "../../layout";
import { useSession } from "@/lib/auth-client";
import { StackableAlerts } from "@/components/ui/alert";
import { useTheme } from "next-themes";
import GameTimer from "@/components/GameTimer";
import FinishedPage from "@/components/FinishedPage";
import { dummyOpponent, dummyOpponentStats, dummyUser, dummyUserStats } from "@/components/dummyData/FinishedPageData";

const TestFinishedPage = true;

import DuelInfo from "@/components/DuelInfo";
import {
  transformLeetCodeHtml,
  getDifficultyClass,
} from "@/lib/leetcode-html-transformer";

export default function InGamePage() {
  const { resolvedTheme } = useTheme();
  const monacoTheme = resolvedTheme === "dark" ? "vs-dark" : "vs";
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
  const opponentTestStatsRef = useRef<TestResultsData | undefined>(undefined);

  const context = useGameContext();
  const router = useRouter();
  const params = useParams();
  const questionName = params?.questionName;
  type AlertType = { id: string; message: string; variant?: string };
  const [alerts, setAlerts] = React.useState<AlertType[]>([]);
  const timeRef = useRef<number>(0);

  console.log(testResults)

  // Initialize timer
  useEffect(() => {
    timeRef.current = 0;
  }, []);
  const [gameFinished, setGameFinished] = React.useState(false);
  const [isRunning, setIsRunning] = React.useState(false);
  const [hasResults, setHasResults] = React.useState(false);
  const [opponentStatus, setOpponentStatus] = React.useState<string | null>(null);

  const session = context?.socket;
  const { data: userSession } = useSession();

  console.log("InGamePage session:", userSession);

  console.log("id:", context?.anonymousId);
  console.log("is anonymous:", context?.isAnonymous);

  useEffect(() => {
    if (!session) {
      console.warn("Socket not ready yet, waiting...");
      return;
    }

    const handleOpponentSubmitted = (data: TestResultsData) => {
      console.log("🔍 [OPPONENT DEBUG] Frontend received opponent_submitted event");
      console.log("🔍 [OPPONENT DEBUG] Data:", data);
      console.log("🔍 [OPPONENT DEBUG] Message:", data.message);
      console.log("🔍 [OPPONENT DEBUG] Success:", data.success);
      console.log("🔍 [OPPONENT DEBUG] Total passed:", data.total_passed);
      console.log("🔍 [OPPONENT DEBUG] Opponent ID:", data.opponent_id);
      
      // Set permanent opponent status
      if (data.success) {
        setOpponentStatus(`🎉 Opponent finished! All ${data.total_passed} tests passed (${data.complexity || 'N/A'} complexity)`);
      } else {
        setOpponentStatus(`⚠️ Opponent submitted: ${data.total_passed}/${data.total_passed + data.total_failed} tests passed`);
      }
      
      setAlerts((prev) => [
        ...prev,
        {
          id: `opponent-${Date.now()}-${Math.random()}`, // Generate unique ID
          message: `Opponent ${data.opponent_id} submitted code: ${data.message}`,
          variant: "default",
        },
      ]);

      opponentTestStatsRef.current = data;
      console.log("🔍 [OPPONENT DEBUG] Alert added and opponentTestStatsRef updated");
    };

    const handleGameCompleted = (data: { message: string }) => {
      console.log("Game completed data:", data);

      setAlerts((prev) => [
        ...prev,
        {
          id: `game-completed-${Date.now()}-${Math.random()}`, // Generate unique ID
          message: `Game completed: ${data.message}`,
          variant: "destructive",
        },
      ]);

      setTimeout(() => {
        console.log("userSession:", userSession);
        console.log("opponentTestStatsRef:", opponentTestStatsRef.current);
        console.log("testResults:", testResults);
        setGameFinished(true);
      }, 5000);
    };

    session.on("opponent_submitted", handleOpponentSubmitted);
    session.on("game_completed", handleGameCompleted);

    // Cleanup function
    return () => {
      session.off("opponent_submitted", handleOpponentSubmitted);
      session.off("game_completed", handleGameCompleted);
    };
  }, [session]);

  useEffect(() => {
    if (!context) {
      console.warn("Game context not ready yet, waiting...");
      return;
    }
    
    // Only redirect if we're sure the context is stable but invalid
    if (context && !context.socket && !context.loading) {
      console.log("Context is stable but socket is missing, redirecting to queue");
      router.push("/queue");
    }
  }, [context, router]);

  useEffect(() => {
    const fetchQuestion = async () => {
      try {
        setLoading(true);
        if (!questionName)
          throw new Error(
            "No question name found in URL. Please check the URL and try again."
          );
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
  useEffect(() => {
    if (questionData && questionData.starter_code) {
      const starterCode = questionData.starter_code[selectedLanguage];
      if (starterCode) {
        setUserCode(starterCode);
      }
    }
  }, [questionData, selectedLanguage]);

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
      console.log("🔍 Debug info:", {
        questionName,
        selectedLanguage,
        codeLength: code?.length || 0,
        timerValue: timeRef.current,
      });

      if (!questionName) {
        throw new Error("Question name not found in URL");
      }

      const requestPayload = {
        player_id: "sample-test-user", // For sample tests, use a generic ID
        code: code,
        question_name: questionName,
        language: selectedLanguage,
        timer: timeRef.current,
      };

      console.log("🚀 Request payload:", requestPayload);
      console.log(
        "🌐 API URL:",
        `${process.env.NEXT_PUBLIC_API_BASE_URL}/run-sample-tests`
      );

      const response = await fetch(
        `${process.env.NEXT_PUBLIC_API_BASE_URL}/run-sample-tests`,
        {
          method: "POST",
          headers: {
            "Content-Type": "application/json",
          },
          body: JSON.stringify(requestPayload),
        }
      );

      const result = await response.json();
      console.log("Test execution result:", result);
      setTestResults(result);
      setHasResults(true);
      return result;
    } catch (error) {
      console.log("Error running tests:", error);
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
    setTestResults(undefined); // Clear previous results for immediate feedback

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

      console.log("Request body:", {
        player_id: playerId,
        code: code,
        question_name: questionName,
        language: selectedLanguage,
        timer: timeRef.current,
      });
      const response = await fetch(
        `${process.env.NEXT_PUBLIC_API_BASE_URL}/${context.gameId}/run-all-tests`, //have to pass in gameId so that the game room can be pinged
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
      console.log("Full test execution result:", result);
      setTestResults(result);
      setHasResults(true);
      return result;
    } catch (error) {
      console.log("Error running all tests:", error);
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

  return (
    <div className="flex w-screen h-screen">
      <StackableAlerts alerts={alerts} setAlerts={setAlerts} />

      {!gameFinished ? (
        <div className="flex w-full h-full">
          {/* Left Column - Question */}
          <div className="w-1/3 overflow-y-auto border-r">
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

          {/* Middle Column - Editor */}
          <div className="flex-1 h-full">
            <EditorWithTerminal
              code={userCode}
              onCodeChange={(value) => {
                setUserCode(value || "");
                console.log("User code:", value);
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

          {/* Right Column - DuelInfo */}
          <div className="w-1/4 overflow-y-auto border-l">
            <div className="p-4">
              {/* Permanent opponent status display */}
              {opponentStatus && (
                <div className="p-3 mb-4 border border-blue-200 rounded-lg bg-blue-50 dark:bg-blue-900/20 dark:border-blue-800">
                  <p className="text-sm font-medium text-blue-800 dark:text-blue-200">
                    {opponentStatus}
                  </p>
                </div>
              )}
              <DuelInfo timeRef={timeRef} />
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
