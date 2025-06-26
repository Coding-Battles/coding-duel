import type { Metadata } from "next";
import { Geist, Geist_Mono } from "next/font/google";
import "./globals.css";
import {NightModeButton} from "@/components/NightModeButton";
import { cookies, headers } from 'next/headers';
import {auth} from "@/lib/auth";
import { SessionProvider } from "@/components/SessionProvider";



const geistSans = Geist({
  variable: "--font-geist-sans",
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


export default async function RootLayout({
  children,
}: Readonly<{
  children: React.ReactNode;
}>) {
  const cookieStore = await cookies();
  const theme = cookieStore.get('theme')?.value || 'light';

  const sessionData = await auth.api.getSession({
    headers: await headers()
  })

  const sessionUser = sessionData?.user || null;

  return (
    <html lang="en" className={theme === 'dark' ? 'dark' : ''}>
      <body
        className={`${geistSans.variable} ${geistMono.variable} antialiased`}
      >
        <NightModeButton/>
        <SessionProvider sessionUser={sessionUser}>
          {children}
        </SessionProvider>
      </body>
    </html>
  );
}
