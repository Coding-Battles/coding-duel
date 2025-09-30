// app/error.tsx
"use client";

import React from "react";
import Link from "next/link";

export default function GlobalError({ error, reset }: { error: Error; reset: () => void }) {

  return (
    <div className="flex items-center justify-center min-h-screen text-gray-100 bg-gray-900">
      <div className="max-w-md p-6 text-center">
        <h1 className="font-bold text-red-500 text-8xl">500</h1>
        <h2 className="mt-4 text-3xl font-semibold">Internal Server Error</h2>
        <p className="mt-2 text-gray-400">
          Oops! Something went wrong on our end.
        </p>
        <div className="flex flex-col gap-2 mt-6">
          <button
            onClick={() => reset()}
            className="px-4 py-2 text-black bg-yellow-500 rounded hover:bg-yellow-600"
          >
            Retry
          </button>
          <Link href="/">
            <a className="px-4 py-2 text-white bg-blue-600 rounded hover:bg-blue-700">
              Go Back Home
            </a>
          </Link>
        </div>
      </div>
    </div>
  );
}
