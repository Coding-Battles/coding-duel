"use client";

import { Editor } from "@monaco-editor/react";

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
  disableCopyPaste = false,
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
            vertical: 'auto',
            horizontal: 'auto',
          },
          automaticLayout: true,
          minimap: { enabled: false },
          wordWrap: 'on',
          fontSize: 14,
          lineNumbers: 'on',
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
        onMount={(editor, monaco) => {
          if (disableCopyPaste) {
            editor.addCommand(monaco.KeyMod.CtrlCmd | monaco.KeyCode.KeyC, () => {});
            editor.addCommand(monaco.KeyMod.CtrlCmd | monaco.KeyCode.KeyV, () => {});
            editor.addCommand(monaco.KeyMod.CtrlCmd | monaco.KeyCode.KeyX, () => {});
            editor.addCommand(monaco.KeyMod.CtrlCmd | monaco.KeyCode.KeyA, () => {});
          }
        }}
      />
    </div>
  );
}

export { CodeEditor };
