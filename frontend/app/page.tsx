import Link from "next/link";
import GoogleSignInButton from "@/components/GoogleSignInButton";

export default function HomePage() {
  // Server component - all static content server-rendered
  // Only GoogleSignInButton hydrates as client island
  return (
    <div className="relative min-h-screen overflow-hidden bg-background text-foreground">
      {/* Subtle Matrix-inspired Background Pattern */}
      <div
        className="absolute inset-0 opacity-20"
        style={{
          backgroundImage: `
            radial-gradient(circle at 1px 1px, rgba(34, 197, 94, 0.15) 1px, transparent 0),
            linear-gradient(90deg, transparent 50px, rgba(34, 197, 94, 0.03) 51px, rgba(34, 197, 94, 0.03) 52px, transparent 53px),
            linear-gradient(180deg, transparent 50px, rgba(59, 130, 246, 0.03) 51px, rgba(59, 130, 246, 0.03) 52px, transparent 53px)
          `,
          backgroundSize: "60px 60px, 120px 120px, 80px 80px",
          backgroundPosition: "0 0, 30px 30px, 10px 10px",
        }}
      />
      {/* Above-the-fold Hero Section - Server Rendered */}
      <section className="relative flex items-center justify-center min-h-screen px-6">
        <div className="container relative max-w-6xl mx-auto">
          <div className="grid items-center grid-cols-1 gap-12 lg:grid-cols-2">
            {/* Left Column - Content */}
            <div className="text-center lg:text-left">
              <h1 className="mb-6 text-4xl font-bold leading-tight md:text-5xl lg:text-6xl text-accent">
                Head-to-head algorithm fights
              </h1>
              <div className="mb-8 text-lg font-medium md:text-xl text-foreground/70">
                Touch grass later
              </div>

              {/* Sign In Section - Client Island */}
              <div className="max-w-md mx-auto lg:mx-0">
                <GoogleSignInButton className="w-full py-4 text-lg font-medium">
                  Sign in with Google to start battling
                </GoogleSignInButton>
              </div>
            </div>

            {/* Right Column - Demo Video */}
            <div className="order-first lg:order-last">
              <div
                className="relative overflow-hidden shadow-2xl bg-foreground/10 rounded-xl"
                style={{ aspectRatio: "16/9" }}
              >
                <div className="absolute inset-0 flex items-center justify-center">
                  <div className="text-center">
                    <div className="flex items-center justify-center w-16 h-16 mx-auto mb-4 rounded-full bg-foreground/20">
                      <svg
                        className="w-8 h-8 text-foreground/60"
                        fill="currentColor"
                        viewBox="0 0 24 24"
                      >
                        <path d="M8 5v14l11-7z" />
                      </svg>
                    </div>
                    <p className="text-lg text-foreground/60">
                      Demo Video Coming Soon
                    </p>
                  </div>
                </div>
              </div>
            </div>
          </div>
        </div>
      </section>

      {/* Below-the-fold Content Section - Server Rendered */}
      <section className="px-6 py-20">
        <div className="container max-w-6xl mx-auto">
          {/* Feature Highlights */}
          <div className="mb-12 text-center">
            <h2 className="mb-4 text-3xl font-bold md:text-4xl">
              Why Choose CodeDuel?
            </h2>
            <p className="text-lg text-foreground/60">
              Everything you need for competitive coding
            </p>
          </div>

          <div className="grid grid-cols-1 gap-8 md:grid-cols-2 lg:grid-cols-4">
            <div className="text-center">
              <div className="flex items-center justify-center w-12 h-12 mx-auto mb-4 rounded-lg bg-accent">
                <svg
                  className="w-6 h-6 text-primary-foreground"
                  fill="none"
                  stroke="currentColor"
                  viewBox="0 0 24 24"
                >
                  <path
                    strokeLinecap="round"
                    strokeLinejoin="round"
                    strokeWidth={2}
                    d="M13 10V3L4 14h7v7l9-11h-7z"
                  />
                </svg>
              </div>
              <h3 className="mb-2 text-lg font-semibold">
                Real-time coding battles
              </h3>
              <p className="text-sm text-foreground/60">
                Face off against other developers in live coding challenges
              </p>
            </div>

            <div className="text-center">
              <div className="flex items-center justify-center w-12 h-12 mx-auto mb-4 rounded-lg bg-accent">
                <svg
                  className="w-6 h-6 text-primary-foreground"
                  fill="none"
                  stroke="currentColor"
                  viewBox="0 0 24 24"
                >
                  <path
                    strokeLinecap="round"
                    strokeLinejoin="round"
                    strokeWidth={2}
                    d="M9 19v-6a2 2 0 00-2-2H5a2 2 0 00-2 2v6a2 2 0 002 2h2a2 2 0 002-2zm0 0V9a2 2 0 012-2h2a2 2 0 012 2v10m-6 0a2 2 0 002 2h2a2 2 0 002-2m0 0V5a2 2 0 012-2h2a2 2 0 012 2v14a2 2 0 01-2 2h-2a2 2 0 01-2-2z"
                  />
                </svg>
              </div>
              <h3 className="mb-2 text-lg font-semibold">
                Multiple difficulty levels
              </h3>
              <p className="text-sm text-foreground/60">
                Choose from easy, medium, or hard coding challenges
              </p>
            </div>

            <div className="text-center">
              <div className="flex items-center justify-center w-12 h-12 mx-auto mb-4 rounded-lg bg-accent">
                <svg
                  className="w-6 h-6 text-primary-foreground"
                  fill="none"
                  stroke="currentColor"
                  viewBox="0 0 24 24"
                >
                  <path
                    strokeLinecap="round"
                    strokeLinejoin="round"
                    strokeWidth={2}
                    d="M3.055 11H5a2 2 0 012 2v1a2 2 0 002 2 2 2 0 012 2v2.945M8 3.935V5.5A2.5 2.5 0 0010.5 8h.5a2 2 0 012 2 2 2 0 104 0 2 2 0 012-2h1.064M15 20.488V18a2 2 0 012-2h3.064M21 12a9 9 0 11-18 0 9 9 0 0118 0z"
                  />
                </svg>
              </div>
              <h3 className="mb-2 text-lg font-semibold">
                Compete with developers worldwide
              </h3>
              <p className="text-sm text-foreground/60">
                Challenge coders from around the globe in epic battles
              </p>
            </div>

            <div className="text-center">
              <div className="flex items-center justify-center w-12 h-12 mx-auto mb-4 rounded-lg bg-accent">
                <svg
                  className="w-6 h-6 text-primary-foreground"
                  fill="none"
                  stroke="currentColor"
                  viewBox="0 0 24 24"
                >
                  <path
                    strokeLinecap="round"
                    strokeLinejoin="round"
                    strokeWidth={2}
                    d="M9 19v-6a2 2 0 00-2-2H5a2 2 0 00-2 2v6a2 2 0 002 2h2a2 2 0 002-2zm0 0V9a2 2 0 012-2h2a2 2 0 012 2v10m-6 0a2 2 0 002 2h2a2 2 0 002-2m0 0V5a2 2 0 012-2h2a2 2 0 012 2v14a2 2 0 01-2 2h-2a2 2 0 01-2-2z"
                  />
                </svg>
              </div>
              <h3 className="mb-2 text-lg font-semibold">
                Track your coding progress
              </h3>
              <p className="text-sm text-foreground/60">
                Monitor your wins, losses, and skill improvement over time
              </p>
            </div>
          </div>
        </div>
      </section>

      {/* Footer - Server Rendered */}
      <footer className="px-6 py-12 border-t border-foreground/20">
        <div className="container max-w-6xl mx-auto">
          <div className="flex flex-col items-center justify-between gap-4 md:flex-row">
            <Link href="/" className="flex items-center space-x-2">
              <div className="flex items-center justify-center w-8 h-8 rounded-lg bg-accent">
                <span className="text-lg font-bold text-background">CD</span>
              </div>
              <span className="text-xl font-bold">CodeDuel</span>
            </Link>

            <div className="flex gap-6 text-sm text-foreground/60">
              <a
                href="https://github.com/Andriy3333/coding-duel"
                target="_blank"
                rel="noopener noreferrer"
                className="transition hover:text-foreground"
              >
                GitHub
              </a>
            </div>
          </div>
        </div>
      </footer>
    </div>
  );
}