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
}

export default function CodeEditor({
  value = "# Start typing...",
  onChange,
  language = "python",
  theme = "vs-dark",
  height = "100%",
  width = "100%",
  className = "",
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
      />
    </div>
  );
}

export { CodeEditor };
