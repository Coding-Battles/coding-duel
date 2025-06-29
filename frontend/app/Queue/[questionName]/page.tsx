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
import { AlertTriangle, Check } from "lucide-react";
import { useParams, useRouter } from "next/navigation";
import React, { useEffect, useRef } from "react";
import { useGameContext } from "../layout";
import { useSessionContext } from "@/components/SessionProvider";
import { Socket } from "socket.io-client";
import { Alert, AlertDescription, AlertTitle, StackableAlerts } from "@/components/ui/alert";
import {motion} from "framer-motion";
import GameTimer from "@/components/GameTimer";

type OpponentSubmittedMessage = {
  message: string;
  opponent_id: string;
  status: boolean;
  total_tests: number | null;
};


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

  const socketRef = useRef<Socket | null>(null);
  const context = useGameContext();
  const router = useRouter();
  const params = useParams();
  const questionName = params?.questionName;
  type AlertType = { id: string; message: string; variant?: string };
  const [alerts, setAlerts] = React.useState<AlertType[]>([]);
  const timeRef = useRef<number>(0);
  const [gameFinished, setGameFinished] = React.useState(false);

  const session = context?.socket
  const userSession = useSessionContext();

  console.log("InGamePage session:", userSession);

  console.log("id:", context?.anonymousId);
  console.log("is anonymous:", context?.isAnonymous);

  useEffect(() => {
    if(!session) {
      console.error("No session found, redirecting to queue");
      router.push("/queue");
      return;
    } 

    const handleOpponentSubmitted = (data: OpponentSubmittedMessage) => {
      console.log("Opponent submitted data:", data);
      setAlerts((prev) => [
        ...prev,
        {
          id: `opponent-${Date.now()}-${Math.random()}`, // Generate unique ID
          message: `Opponent ${data.opponent_id} submitted code: ${data.message}`,
          variant: 'default'
        }
      ]);
    };

    const handleGameCompleted = (data: {message: string}) => {
      console.log("Game completed data:", data);
      setGameFinished(true);

      setAlerts((prev) => [
        ...prev,
        {
          id: `game-completed-${Date.now()}-${Math.random()}`, // Generate unique ID
          message: `Game completed: ${data.message}`,
          variant: 'destructive'
        }
      ]);
    };

    session.on("opponent_submitted", handleOpponentSubmitted);
    session.on("game_completed", handleGameCompleted);

      // Cleanup function
    return () => {
      session.off("opponent_submitted", handleOpponentSubmitted);
      session.off("game_completed", handleGameCompleted);
    };
  }, [session])
  

 useEffect(() => {
    if (!context) {
      router.push("/queue");
    }
  }, [context, router]);

  useEffect(() => {
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
  useEffect(() => {
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
            timer: timeRef.current,
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
        error: error instanceof Error ? error.message : "Unknown error",
        message: "",
        code: "",
        opponent_id: ""
      };
      setTestResults(errorResult);
      return errorResult;
    }
  };

  const runAllTests = async (code: string): Promise<TestResultsData> => {
    try {
      const playerId = context.isAnonymous ? context.anonymousId : userSession?.id;
      console.log("Request body:", {
        player_id: playerId,
        code: code,
        question_name: questionName,
        language: selectedLanguage,
        timer: timeRef.current
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
            timer: Math.floor(timeRef.current)
          }),
        }
      );


      const result = await response.json();
      console.log("Full test execution result:", result);
      setTestResults(result);
      return result;
    } catch (error) {
      console.error("Error running all tests:", error);
      const errorResult: TestResultsData = {
        success: false,
        test_results: [],
        total_passed: 0,
        total_failed: 0,
        error: error instanceof Error ? error.message : "Unknown error",
        message: "",
        code: "",
        opponent_id: ""
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
          <header className="flex h-16 shrink-0 justify-between items-center gap-2 border-b px-4 z-60">
            <SidebarTrigger className="-ml-1" />
            <h1 className="text-lg font-semibold">BATTLE</h1>
            {gameFinished ? <GameTimer timeRef={timeRef}/> : <span></span>}
          </header>
          <StackableAlerts alerts={alerts} setAlerts={setAlerts}/>
          <div className="flex flex-1 flex-col gap-4 p-4">
            <div className="flex h-[100%] w-[100%]">
              <div className="flex-1 w-full h-full max-w-2xl">
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
                />
              </div>
            </div>
          </div>
        </SidebarInset>
      </SidebarProvider>
    </div>
  );
}
