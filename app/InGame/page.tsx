"use client"
import { Editor } from '@monaco-editor/react'
import React from 'react'

export default function InGamePage() {
  return(
    <div className="flex h-[100%] items-center justify-center w-[100%]">
      <Editor
        height="80%"
        width={"40%"}
        defaultLanguage="javascript"
        defaultValue="// Start typing..."
        theme="vs-light"
      />
      <textarea className='h-[80%] w-[40%]'/>{/*FOR TERMINAL*/}
    </div>
  )
}
