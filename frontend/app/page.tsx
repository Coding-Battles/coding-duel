import Link from "next/link";
import GoogleSignInButton from "@/components/GoogleSignInButton";
import { Button } from "@/components/ui/button";
import { FeatureBoxes } from "@/components/FeatureBoxes";

const features = [
  {
    icon: (
      <svg
        className="w-6 h-6 text-accent"
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
    ),
    title: "Real-time coding battles",
    description: "Face off against other developers in live coding challenges",
    image: "/images/InGameExample1.PNG", // Replace with actual image path
    size: "large",
  },
  {
    icon: (
      <svg
        className="w-6 h-6 text-accent"
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
    ),
    title: "Multiple difficulty levels",
    description: "Choose from easy, medium, or hard coding challenges",
    image: "/images/difficulty-levels.png",
    size: "medium",
  },
  {
    icon: (
      <svg
        className="w-6 h-6 text-accent"
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
    ),
    title: "Track your coding progress",
    description: "Monitor your wins, losses, and skill improvement over time",
    image: "/images/progress-tracking.png",
    size: "medium",
  },
  {
    icon: (
      <svg
        className="w-6 h-6 text-accent"
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
    ),
    title: "Compete with developers worldwide",
    description: "Challenge coders from around the globe in epic battles",
    image: "/images/global-competition.png",
    size: "large",
  },
];

const getFeatureClass = (size: string) => {
  switch (size) {
    case "small":
      return {
        containerSize: "max-w-md",
      };
    case "medium":
      return {
        containerSize: "max-w-2xl",
      };
    case "large":
      return {
        containerSize: "max-w-4xl",
      };
    default:
      return getFeatureClass("medium");
  }
};

export default function HomePage() {
  // Server component - all static content server-rendered
  // Only GoogleSignInButton hydrates as client island
  return (
    <div className="relative min-h-screen overflow-hidden bg-background text-foreground">
      {/* Subtle Matrix-inspired Background Pattern */}
      {/* <div
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
      /> */}
      {/* Above-the-fold Hero Section - Server Rendered */}
      <section className="relative flex items-center justify-center min-h-screen px-6">
        <div className="container relative mx-auto lg:mx-0 lg:w-full">
          <div className="grid items-center grid-cols-1 gap-12 lg:grid-cols-[1fr_2fr] h-[80%]">
            {/* Left Column - Content */}
            <div className="text-center lg:text-left">
              <h1
                className="mb-6 text-5xl md:text-6xl lg:text-7xl font-extrabold leading-tight 
                          text-transparent bg-clip-text bg-gradient-to-r from-player1 to-player2
                          drop-shadow-[0_2px_10px_rgba(255,0,128,0.6)] animate-fade-in"
              >
                Coding Duels
              </h1>

              <div className="mb-8 text-lg italic font-semibold tracking-wide md:text-xl text-foreground/80 animate-pulse">
                Touch grass later 🌿💻
              </div>

              {/* Sign In Section - Client Island */}
              <div className="grid items-center max-w-md grid-cols-2 gap-4 mx-auto lg:mx-0">
                <Link
                  href="guestlogin"
                  className="w-auto px-4 py-1 font-medium text-center border-2 rounded-lg outline-border"
                >
                  Play as Guest
                </Link>
                <GoogleSignInButton className="w-auto py-4 text-lg font-medium">
                  Sign in with Google
                </GoogleSignInButton>
              </div>
            </div>

            {/* Right Column - Demo Video */}
            <div className="relative order-first w-full h-full lg:order-last">
              {/* First image with P1 label */}
              <div className="absolute invisible lg:visible top-0 w-full lg:-top-30 lg:-left-15 xl:left-15 xl:-top-40 xl:w-[80%]">
                <img
                  src={"/images/InGameExample1.PNG"}
                  alt="In game example 1"
                  className="w-full h-auto border-2 border-solid rounded-lg shadow-lg border-player1 aspect-auto"
                />
                <span className="absolute invisible px-1 font-medium lg:visible -top-6 right-2 bg-player1 text-foreground">
                  P1
                </span>
              </div>

              {/* Second image with P2 label */}
              <div className="absolute invisible w-full lg:visible lg:-bottom-30 lg:right-0 xl:-bottom-40 xl:w-[80%]">
                <img
                  src={"/images/InGameExample2.PNG"}
                  alt="In game example 2"
                  className="w-full h-auto border-2 border-solid rounded-lg shadow-lg border-player2 aspect-auto"
                />
                <span className="absolute px-1 font-medium -top-6 right-2 bg-player2 text-foreground">
                  P2
                </span>
              </div>
            </div>
          </div>
        </div>
      </section>

      {/* Below-the-fold Content Section - Server Rendered */}
      <section className="w-auto h-auto px-6 pt-10 pb-20 lg:px-2 wavyDiv bg-background2">
        <div className="container w-full mx-auto">
          <div className="flex flex-col gap-8">
            <FeatureBoxes
              icon={features[0].icon}
              title={features[0].title}
              description={features[0].description}
              image={features[0].image}
              size={features[0].size}
              index={0}
            />
            <div className="flex flex-col justify-between gap-8 lg:flex-row">
              <FeatureBoxes
                icon={features[1].icon}
                title={features[1].title}
                description={features[1].description}
                image={features[1].image}
                size={features[1].size}
                index={1}
              />
              <FeatureBoxes
                icon={features[2].icon}
                title={features[2].title}
                description={features[2].description}
                image={features[2].image}
                size={features[2].size}
                index={2}
              />
            </div>
            <FeatureBoxes
              icon={features[3].icon}
              title={features[3].title}
              description={features[3].description}
              image={features[3].image}
              size={features[3].size}
              index={3}
            />
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
