"use client";

import { Editor } from "@monaco-editor/react";
import type { editor } from "monaco-editor";

interface CodeEditorProps {
  value?: string;
  onChange?: (value: string | undefined) => void;
  language?: string;
  theme?: string;
  height?: string;
  width?: string;
  className?: string;
  disableCopyPaste?: boolean;
}

export default function CodeEditor({
  value = "# Start typing...",
  onChange,
  language = "python",
  theme = "vs-dark",
  height = "100%",
  width = "100%",
  className = "",
  disableCopyPaste = false, //set to true in production
}: CodeEditorProps) {
  return (
    <div className={className} style={{ height, width }}>
      <Editor
      
        height="100%"
        width="100%"
        language={language}
        value={value}
        theme={theme}
        onChange={onChange}
        options={{
          scrollBeyondLastLine: false,
          scrollbar: {
            vertical: "auto",
            horizontal: "auto",
          },
          automaticLayout: true,
          minimap: { enabled: false },
          wordWrap: "on",
          fontSize: 14,
          lineNumbers: "on",
          glyphMargin: false,
          folding: true,
          lineDecorationsWidth: 0,
          lineNumbersMinChars: 3,
          contextmenu: !disableCopyPaste,
          quickSuggestions: !disableCopyPaste,
          suggestOnTriggerCharacters: !disableCopyPaste,
          parameterHints: { enabled: !disableCopyPaste },
          wordBasedSuggestions: "off",
        }}
        onMount={(editorInstance, monaco) => {
          // Expose editor to window for Cypress testing
          if (typeof window !== "undefined") {
            (
              window as typeof window & {
                __monacoEditor?: editor.IStandaloneCodeEditor;
                __monacoMountTime?: number;
                __monacoMountCount?: number;
              }
            ).__monacoEditor = editorInstance;

            // Add mount tracking for debugging
            (window as any).__monacoMountTime = Date.now();
            (window as any).__monacoMountCount =
              ((window as any).__monacoMountCount || 0) + 1;
          }

          console.log("🔧 Monaco Editor onMount called");
          console.log("Monaco window object:", window);
          console.log("Monaco editor exposed:", (window as any).__monacoEditor);
          console.log("Monaco editor instance methods:", {
            setValue: typeof editorInstance.setValue,
            getValue: typeof editorInstance.getValue,
          });
          console.log("Mount count:", (window as any).__monacoMountCount);

          if (disableCopyPaste) {
            editorInstance.addCommand(
              monaco.KeyMod.CtrlCmd | monaco.KeyCode.KeyC,
              () => {}
            );
            editorInstance.addCommand(
              monaco.KeyMod.CtrlCmd | monaco.KeyCode.KeyV,
              () => {}
            );
            editorInstance.addCommand(
              monaco.KeyMod.CtrlCmd | monaco.KeyCode.KeyX,
              () => {}
            );
            editorInstance.addCommand(
              monaco.KeyMod.CtrlCmd | monaco.KeyCode.KeyA,
              () => {}
            );
          }
        }}
      />
    </div>
  );
}

export { CodeEditor };
