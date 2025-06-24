"use client";
import { Button } from "@/components/ui/button";
import { Editor } from "@monaco-editor/react";
import { Check } from "lucide-react";
import React from "react";
import { useGameContext } from "../layout";
import { useRouter } from "next/navigation";
import { QuestionSidebar } from "@/components/QuestionSidebar";

export default function InGamePage() {
  const [userCode, setUserCode] = React.useState<string>(
    "// Start typing your code here..."
  );
  const context = useGameContext();
  const router = useRouter();

  React.useEffect(() => {
    if (!context) {
      router.push("/queue");
    }
  }, [context, router]);

  if (!context) {
    return <div>Loading...</div>;
  }

  const { socket, loading } = context;

  const runCode = async () => {
    try {
      const response = await fetch(`${process.env.NEXT_PUBLIC_API_BASE_URL}/run_code`, {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify({
          code: userCode,
          input: "2",
        }),
      });

      const result = await response.json();
      console.log("Code execution result:", result);
    } catch (error) {
      console.error("Error running code:", error);
    }
  };
  return (
    <div className="flex h-[100%] items-center justify-center w-[100%]">
      <div className="flex gap-2 justify-self-end absolute top-4 right-4">
        <Button className="text-black border-black border-2 cursor-pointer bg-transparent hover:bg-gray-200">
          Run
        </Button>
        <Button
          className="text-green-300 border-green-300 border-2 cursor-pointer bg-transparent hover:bg-green-100"
          onClick={runCode}
        >
          <Check />
          Submit
        </Button>
      </div>
      <Editor
        height="80%"
        width={"40%"}
        defaultLanguage="python"
        defaultValue="# Start typing..."
        theme="vs-dark"
        onChange={(value) => {
          setUserCode(value || "");
          console.log("User code:", value);
        }}
      />
      <div className="h-[80%] w-[40%]">
        <QuestionSidebar questionName="two_sum" />
      </div>
    </div>
  );
}
