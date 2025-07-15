"use client";
import { Button } from "@/components/ui/button";
import { Editor } from "@monaco-editor/react";
import { Check } from "lucide-react";
import React from "react";
import { useGameContext } from "../../layout";
import { useRouter } from "next/navigation";
import {
  SidebarInset,
  SidebarProvider,
  SidebarTrigger,
} from "@/components/ui/sidebar";
import { InGameSideBar } from "@/components/inGameSideBar";
import { QuestionData } from "@/types/question";

export default function InGamePage() {
  const [userCode, setUserCode] = React.useState<string>(
    "// Start typing your code here..."
  );
  const [questionData, setQuestionData] = React.useState<QuestionData | null>(
    null
  );
  const [loading, setLoading] = React.useState(true);
  const [error, setError] = React.useState<string | null>(null);

  const context = useGameContext();
  const router = useRouter();

  React.useEffect(() => {
    if (!context) {
      router.push("/queue");
    }
  }, [context, router]);

  React.useEffect(() => {
    const fetchQuestion = async () => {
      try {
        setLoading(true);
        const response = await fetch(
          `${process.env.NEXT_PUBLIC_API_BASE_URL}/get-question/two-sum`
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
  }, []);

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
        <div className="text-error">Error: {error}</div>
      </div>
    );
  }

  const { socket } = context;

  const runCode = async () => {
    try {
      const response = await fetch(
        `${process.env.NEXT_PUBLIC_API_BASE_URL}/run_code`,
        {
          method: "POST",
          headers: {
            "Content-Type": "application/json",
          },
          body: JSON.stringify({
            code: userCode,
            input: "2",
          }),
        }
      );

      const result = await response.json();
      console.log("Code execution result:", result);
    } catch (error) {
      console.error("Error running code:", error);
    }
  };
  return (
    <div className="flex h-[100%] w-[100%] w-max-screen">
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
              <div className="flex gap-2 justify-self-end absolute top-4 right-4 z-10">
                <Button className="text-foreground border-foreground border-2 cursor-pointer bg-transparent hover:bg-foreground/10">
                  Run
                </Button>
                <Button
                  className="text-success border-success border-2 cursor-pointer bg-transparent hover:bg-success/10"
                  onClick={runCode}
                >
                  <Check />
                  Submit
                </Button>
              </div>
              <Editor
                height="100%"
                width="100%"
                defaultLanguage="python"
                defaultValue="# Start typing..."
                theme="vs-dark"
                onChange={(value) => {
                  setUserCode(value || "");
                  console.log("User code:", value);
                }}
              />
            </div>
          </div>
        </SidebarInset>
      </SidebarProvider>
    </div>
  );
}
