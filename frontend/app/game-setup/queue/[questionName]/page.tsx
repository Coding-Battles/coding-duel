// This file was moved from in-game/page.tsx to [questionName]/page.tsx for dynamic routing.
"use client";
import { QuestionData, TestResultsData, CustomUser, OpponentData, ProgrammingLanguage } from "@/shared/types";
import EditorWithTerminal from "@/components/EditorWithTerminal";
import { Language, getLanguageConfig } from "@/types/languages";
import { useParams, useRouter } from "next/navigation";
import React, { useCallback, useEffect, useRef, useState } from "react";
import { useGameContext } from "../../layout";
import { useSession } from "@/lib/auth-client";
import { StackableAlerts } from "@/components/ui/alert";
// Removed useTheme import - now using dark mode only
import FinishedPage from "@/components/FinishedPage";

import DuelInfo from "@/components/DuelInfo";
import {
  transformLeetCodeHtml,
  getDifficultyClass,
} from "@/lib/leetcode-html-transformer";

type AlertType = { id: string; message: string; variant?: string };

// Dummy data - User wins scenario
export const dummyUserWinsData = {
  opponent: {
    image_url: "https://images.unsplash.com/photo-1472099645785-5658abf4ff4e?w=150&h=150&fit=crop&crop=face",
    name: "Alex Thompson"
  } as OpponentData,
  
  user: {
    id: "user123",
    name: "John Doe",
    email: "john@example.com"
  } as CustomUser,
  
  opponentStats: {
    player_name: "Alex Thompson",
    implement_time: 165, // Changed from "2:45" to a number (e.g., seconds)
    complexity: "O(n²)",
    final_time: 165.8,
    success: true,
    test_results: [],
    total_passed: 0,
    total_failed: 0,
    error: "",
    message: "",
    code: "",
    opponent_id: "opponent123"
  } as TestResultsData,
  
  userStats: {
    player_name: "John Doe",
    implement_time: 132, // Changed from "2:12" (string) to 132 (number, e.g., seconds)
    complexity: "O(n log n)",
    final_time: 132.5,
    success: true,
    test_results: [],
    total_passed: 0,
    total_failed: 0,
    error: "",
    message: "",
    code: "",
    opponent_id: ""
  } as TestResultsData
};

const debugFinishedPage = false; // Set to true to debug FinishedPage component

export default function InGamePage() {
  // ALL HOOKS MUST BE DECLARED AT THE TOP - NO CONDITIONAL LOGIC BEFORE HOOKS
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
  const [rightWidth, setRightWidth] = useState(25);
  const [gameFinished, setGameFinished] = React.useState(false);
  const [isRunning, setIsRunning] = React.useState(false);
  const [hasResults, setHasResults] = React.useState(false);
  const [opponentStatus, setOpponentStatus] = React.useState<string | null>(
    null
  );
  const [gameStartTime, setGameStartTime] = React.useState<number | null>(null);
  const [isGameStarted, setIsGameStarted] = React.useState(false);
  const [gameEndData, setGameEndData] = React.useState<any>(null); // Store complete game end info

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

  // Function to emit code updates - we'll set this up later
  const emitCodeUpdateRef = useRef<((code: string) => void) | null>(null);
  // Function to emit instant code updates
  const emitInstantCodeUpdateRef = useRef<((code: string, reason: string) => void) | null>(null);
  // Refs to always have current values (avoid stale closures)
  const questionDataRef = useRef<QuestionData | null>(null);
  const userCodeRef = useRef<string>("");

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

    const handleGameCompleted = (data: any) => {
      console.log("🏆 [GAME END DEBUG] Game completed data:", data);

      // Store complete game end data for FinishedPage
      setGameEndData(data);

      setAlerts((prev) => [
        ...prev,
        {
          id: `game-completed-${Date.now()}-${Math.random()}`,
          message: data.message || "Game completed!",
          variant: data.winner_id === userSession?.user?.id ? "default" : "destructive",
        },
      ]);

      // Show finished page immediately (no 5 second delay)
      setGameFinished(true);
    };

    session.on("opponent_submitted", handleOpponentSubmitted);
    session.on("game_completed", handleGameCompleted);

    return () => {
      console.log("Cleaning up socket listeners");
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
        console.log("🚀 [QUESTION DEBUG] Starting to fetch question:", questionName);
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
        console.log("🚀 [QUESTION DEBUG] Question data loaded successfully:", !!data, "starter_code keys:", Object.keys(data?.starter_code || {}));
        setQuestionData(data);
        questionDataRef.current = data;
      } catch (err) {
        console.error("🚀 [QUESTION DEBUG] Failed to fetch question:", err);
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
      console.warn("🚀 [QUESTION DEBUG] No question name in params:", params);
    }
  }, [params?.questionName]);

  useEffect(() => {
    console.log("🚀 [USERCODE DEBUG] useEffect triggered - questionData:", !!questionData, "selectedLanguage:", selectedLanguage);
    if (questionData && questionData.starter_code) {
      const starterCode = questionData.starter_code[selectedLanguage];
      console.log("🚀 [USERCODE DEBUG] Found starter code for", selectedLanguage, ":", !!starterCode, "length:", starterCode?.length);
      if (starterCode) {
        setUserCode(starterCode);
        userCodeRef.current = starterCode;
        console.log("🚀 [USERCODE DEBUG] Set userCode to starter code");
      }
    } else {
      console.warn("🚀 [USERCODE DEBUG] Missing questionData or starter_code:", {
        questionData: !!questionData,
        starter_code: !!questionData?.starter_code,
        selectedLanguage
      });
    }
  }, [questionData, selectedLanguage]);

  // Join game room and set up debounced code update function
  useEffect(() => {
    if (context?.socket && context.gameId && userSession?.user?.id) {
      // Set up socket event listeners for timer synchronization
      context.socket.on("game_joined", (data: { game_id: string; start_time?: number | null }) => {
        console.log("🚀 [TIMER DEBUG] Received game_joined event:", data);
        if (data.start_time) {
          console.log("🚀 [TIMER DEBUG] Game already started, setting start time:", data.start_time);
          setGameStartTime(data.start_time);
          setIsGameStarted(true);
        }
      });

      context.socket.on("game_start", (data: { game_id: string; start_time: number }) => {
        console.log("🚀 [TIMER DEBUG] Received game_start event:", data);
        console.log("🚀 [TIMER DEBUG] Setting gameStartTime to:", data.start_time, "and isGameStarted to: true");
        setGameStartTime(data.start_time);
        setIsGameStarted(true);
        
        // Emit instant code update when timer starts
        // Use refs to avoid stale closure issues
        const attemptInstantUpdate = (attempt = 1, maxAttempts = 5) => {
          // Access current values from refs (not closure variables)
          const currentUserCode = userCodeRef.current;
          const currentQuestionData = questionDataRef.current;
          const codeToSend = currentUserCode || (currentQuestionData?.starter_code?.[selectedLanguage] || "");
          
          if (emitInstantCodeUpdateRef.current && codeToSend && currentQuestionData) {
            console.log("🚀 [INSTANT DEBUG] Emitting instant code update on timer start (attempt", attempt, "), code length:", codeToSend.length);
            console.log("🚀 [INSTANT DEBUG] Current userCode from ref:", currentUserCode?.substring(0, 50) + "...");
            console.log("🚀 [INSTANT DEBUG] Selected language:", selectedLanguage);
            emitInstantCodeUpdateRef.current(codeToSend, "timer_start");
          } else if (attempt < maxAttempts) {
            console.warn("🚀 [INSTANT DEBUG] Attempt", attempt, "failed - userCodeRef:", !!currentUserCode, "questionDataRef:", !!currentQuestionData, "emitRef:", !!emitInstantCodeUpdateRef.current, "- retrying in 500ms");
            setTimeout(() => attemptInstantUpdate(attempt + 1, maxAttempts), 500);
          } else {
            console.error("🚀 [INSTANT DEBUG] Failed to send instant update after", maxAttempts, "attempts - userCodeRef:", !!currentUserCode, "questionDataRef:", !!currentQuestionData, "emitRef:", !!emitInstantCodeUpdateRef.current);
          }
        };
        
        setTimeout(() => attemptInstantUpdate(), 1000);
      });

      // Join the game room first
      console.log("🚀 [JOIN DEBUG] Emitting join_game event with:", {
        game_id: context.gameId,
        player_id: userSession.user.id
      });
      context.socket.emit("join_game", {
        game_id: context.gameId,
        player_id: userSession.user.id
      });

      // Set up simple code update function (no debouncing - backend handles timing)
      emitCodeUpdateRef.current = (code: string) => {
        // Only emit if we have all required data and the socket is connected
        if (context.socket && context.socket.connected && context.gameId && userSession?.user?.id) {
          context.socket.emit("code_update", {
            game_id: context.gameId,
            player_id: userSession.user.id,
            code: code,
            language: selectedLanguage
          });
        }
      };

      // Set up instant code update function (bypasses 30-second delay)
      emitInstantCodeUpdateRef.current = (code: string, reason: string) => {
        // Only emit if we have all required data and the socket is connected
        if (context.socket && context.socket.connected && context.gameId && userSession?.user?.id) {
          context.socket.emit("instant_code_update", {
            game_id: context.gameId,
            player_id: userSession.user.id,
            code: code,
            language: selectedLanguage,
            reason: reason
          });
        }
      };
    }
    
    // Cleanup on unmount or dependencies change
    return () => {
      if (context?.socket) {
        context.socket.off("game_joined");
        context.socket.off("game_start");
      }
    };
  }, [context?.socket, context?.gameId, userSession?.user?.id, selectedLanguage]);

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
  const questionName = params?.questionName;

  const handleLanguageChange = (language: Language) => {
    setSelectedLanguage(language);
    if (questionData && questionData.starter_code) {
      const starterCode = questionData.starter_code[language];
      if (starterCode) {
        setUserCode(starterCode);
        
        // Update ref
        userCodeRef.current = starterCode;
        
        // Check if we're in the first 30 seconds and emit instant update
        if (gameStartTime && isGameStarted) {
          const currentTime = Date.now();
          const gameElapsedSeconds = (currentTime - gameStartTime * 1000) / 1000;
          
          if (gameElapsedSeconds < 30 && emitInstantCodeUpdateRef.current) {
            console.log("🚀 [INSTANT DEBUG] Emitting instant code update on language switch in first 30s");
            emitInstantCodeUpdateRef.current(starterCode, "language_switch_early");
          }
        }
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
    <div ref={containerRef} className="flex items-center justify-center w-screen h-screen">
      <StackableAlerts alerts={alerts} setAlerts={setAlerts} />

      {!debugFinishedPage && <>{!gameFinished ? (
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
                const newCode = value || "";
                setUserCode(newCode);
                userCodeRef.current = newCode;
                if (emitCodeUpdateRef.current) {
                  emitCodeUpdateRef.current(newCode);
                }
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
              {/* Add timer state logging */}
              {console.log("🚀 [TIMER DEBUG] Passing to DuelInfo - gameStartTime:", gameStartTime, "isGameStarted:", isGameStarted)}
              <DuelInfo
                timeRef={timeRef}
                opponentData={context.opponent}
                user={context.user ?? undefined}
                socket={context.socket ?? undefined}
                gameId={context.gameId ?? undefined}
                starterCode={questionData?.starter_code?.[selectedLanguage] || ""}
                selectedLanguage={selectedLanguage}
                gameStartTime={gameStartTime}
                isGameStarted={isGameStarted}
              />
            </div>
          </div>
        </div>
      ) : (
        gameEndData && (
          <FinishedPage
            opponent={context.opponent}
            user={context.user}
            gameEndData={gameEndData}
            userStats={testResults}
            opponentStats={opponentTestStatsRef.current}
          />
        )
      )}
      </>
    }

    {debugFinishedPage && 
      <FinishedPage
        opponent={dummyUserWinsData.opponent}
        user={dummyUserWinsData.user}
        opponentStats={dummyUserWinsData.opponentStats}
        userStats={dummyUserWinsData.userStats}
      />
    }
    </div>
  );
}
