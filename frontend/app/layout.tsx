import type { Metadata } from "next";
import { Inter, Geist_Mono } from "next/font/google";
import "./globals.css";
import { Suspense } from "react";
import ThemeWrapper from "@/components/ThereWrapper";

const inter = Inter({
  variable: "--font-inter",
  subsets: ["latin"],
});

const geistMono = Geist_Mono({
  variable: "--font-geist-mono",
  subsets: ["latin"],
});

export const metadata: Metadata = {
  title: "Coding Duels",
  description: "1v1 coding battles",
};

export default function RootLayout({
  children,
}: Readonly<{
  children: React.ReactNode;
}>) {
  return (
    <html lang="en" suppressHydrationWarning>
      <body
        className={`${inter.variable} ${geistMono.variable} antialiased overflow-x-hidden`}
      >
        <Suspense fallback={<div>Loading...</div>}>
          <ThemeWrapper>{children}</ThemeWrapper>
        </Suspense>
      </body>
    </html>
  );
}
