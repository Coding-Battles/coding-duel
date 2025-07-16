"use client";
import TypeIt from "typeit-react";
import { useGameContext } from "@/app/game-setup/layout";
import { Button } from "@/components/ui/button";
import { useEffect, useState } from "react";
import { useSession, getAvatarUrl } from "@/lib/auth-client";
import AvatarCard from "./AvatarCard";
import OpponentPlaceholder from "./OpponentPlaceholder";

interface CustomUser {
  username?: string;
  name?: string;
  image?: string;
  id?: string;
  selectedPfp?: number;
}

interface QueueWaitingRoomProps {
  onCancel?: () => void;
}

export default function QueueWaitingRoom({ onCancel }: QueueWaitingRoomProps) {
  const context = useGameContext();
  const { data: session } = useSession();
  const [key, setKey] = useState(0); // used to loop the type animation
  const [timer, setTimer] = useState(0);
  const [playerFound, setPlayerFound] = useState(false);
  const [recentMessages, setRecentMessages] = useState<string[]>([]);

  // Enhanced queue messages
  const queueMessages = [
    // Classic roasts (improved)
    "Lowering standards to underground levels...",
    "Finding someone who codes with their feet...",
    "Looking for victims... I mean opponents...",
    "Difficulty: Tutorial mode activated...",
    "Still no brave souls...",
    "Even the tumbleweeds left...",
    "Bots are too embarrassed to match you...",
    "Maybe try Scratch instead?",
    "Your LinkedIn skills section is showing...",
    "Loading your inevitable defeat...",
    "Charging up the biggest L in history...",
    "Buffering your coaching session...",
    "Questioning your CS degree...",
    "Googling 'how to change careers'...",

    // New personality-driven additions
    "Searching for someone who peaked in high school...",
    "Finding a worthy sacrifice...",
    "Looking for free rating points...",
    "Scanning for Stack Overflow warriors...",
    "Your mom called, she's proud anyway...",
    "Calculating your therapy costs...",
    "Activating god mode (for your opponent)...",
    "Warning: May cause existential crisis...",
    "Preparing your participation trophy...",
    "Searching databases for easier opponents...",
    "Your browser history is concerning...",
    "Loading your villain origin story...",
    "Summoning the coding gods for mercy...",
    "Buffering your 'it worked on my machine' excuse...",
    "Generating your post-match copypasta...",
    "Your IDE is filing a restraining order...",
    "Preparing the rubber ducky for emotional support...",
    "Activating imposter syndrome... complete.",
    "Your keyboard is applying for hazard pay...",
    "Loading your 'I'm actually a designer' speech...",

    // Meta/self-aware roasts
    "These messages are funnier than your code...",
    "Reading this is the highlight of your day...",
    "At least you're consistent... at losing...",
    "Your opponent is still installing Node.js...",
    "They're probably Googling 'what is leetcode'...",
    "Someone's about to discover they're not built different...",
    "Preparing to humble another main character...",
    "Your confidence expires in 3... 2... 1...",
    "Plot twist: You're about to get schooled...",
    "Narrator: 'It was not, in fact, easy'...",
  ];

  // Match found messages
  const matchFoundMessages = [
    "Found someone.",
    "Opponent located.",
    "Match found. Good luck.",
    "Someone took the bait.",
    "Connecting...",
    "Found your nemesis.",
    "Opponent acquired.",
    "Time to code.",
    "Let's see what you got.",
    "Game on.",
    "Found a challenger.",
    "Ready to rumble?",
    "Showtime.",
    "Opponent found. Try not to embarrass yourself.",
    "Let the games begin.",
  ];

  // Anti-repetition message selection
  const getRandomMessage = (messageArray: string[]) => {
    // Filter out recently shown messages
    const availableMessages = messageArray.filter(
      (msg) => !recentMessages.includes(msg)
    );

    // If all messages were recent, reset the recent list
    if (availableMessages.length === 0) {
      setRecentMessages([]);
      const randomIndex = Math.floor(Math.random() * messageArray.length);
      const selectedMessage = messageArray[randomIndex];
      setRecentMessages([selectedMessage]);
      return selectedMessage;
    }

    // Pick from available messages
    const randomIndex = Math.floor(Math.random() * availableMessages.length);
    const selectedMessage = availableMessages[randomIndex];

    // Track this message (keep last 6 messages)
    setRecentMessages((prev) => [...prev, selectedMessage].slice(-6));

    return selectedMessage;
  };

  // Get queue message
  const getQueueMessage = () => getRandomMessage(queueMessages);

  // Get match found message
  const getMatchFoundMessage = () => getRandomMessage(matchFoundMessages);

  // Helper function to get user avatar with proper fallbacks
  const getUserAvatar = () => {
    // Try context user first, then session user
    const user = context?.user || (session?.user as CustomUser);
    return getAvatarUrl(user);
  };

  // Timer effect - must be before conditional returns
  useEffect(() => {
    if (!context?.socket) return;

    const interval = setInterval(() => {
      setTimer((prev) => prev + 1);
    }, 1000);

    return () => {
      clearInterval(interval);
    };
  }, [context?.socket]);

  // Update playerFound when opponent data is available
  useEffect(() => {
    if (context?.opponent?.image_url && context?.opponent?.name) {
      setPlayerFound(true);
    } else {
      setPlayerFound(false);
    }
  }, [context?.opponent?.image_url, context?.opponent?.name]);

  if (!context) {
    return (
      <div className="flex h-[100%] w-[100%] items-center justify-center">
        <p className="text-error">Game context is not available.</p>
      </div>
    );
  }

  const { opponent } = context;

  return (
    <div className="flex h-[100%] w-[100%] flex-col border border-border rounded-lg overflow-hidden">
      {/* Header with Status and Cancel */}
      <div className="flex flex-col sm:flex-row items-start sm:items-center justify-between p-4 border-b border-foreground/10 gap-3 sm:gap-4">
        <div className="flex flex-col sm:flex-row items-start sm:items-center gap-3 sm:gap-4">
          <div className="flex items-center gap-2">
            <div className="w-3 h-3 rounded-full bg-error" />
            <div className="w-3 h-3 rounded-full bg-accent" />
            <div className="w-3 h-3 rounded-full bg-success" />
          </div>
          <div className="flex flex-col sm:flex-row items-start sm:items-center gap-2 sm:gap-4 text-sm">
            <span className="text-foreground/60">
              Time:{" "}
              <span className="font-mono text-foreground">
                {Math.floor(timer / 60)}:{timer % 60 < 10 && 0}
                {timer % 60}
              </span>
            </span>
            {!playerFound ? (
              <div className="flex items-center">
                <div className="bg-background border border-border border-b-0 rounded-t-md px-3 py-1.5 text-xs font-medium text-accent flex items-center gap-2 relative">
                  <div className="w-2 h-2 rounded-full bg-accent" />
                  <span>finding_queue</span>
                  <div className="absolute -bottom-px left-0 right-0 h-px bg-background" />
                </div>
              </div>
            ) : (
              <div className="flex items-center">
                <div className="bg-background border border-border border-b-0 rounded-t-md px-3 py-1.5 text-xs font-medium text-success flex items-center gap-2 relative">
                  <div className="w-2 h-2 rounded-full bg-success" />
                  <span>match.found</span>
                  <div className="absolute -bottom-px left-0 right-0 h-px bg-background" />
                </div>
              </div>
            )}
          </div>
        </div>

        {/* Cancel Button in Header */}
        {onCancel && (
          <Button onClick={onCancel} variant="outline" size="sm">
            Cancel
          </Button>
        )}
      </div>

      {/* Status Display */}
      <div className="flex justify-center p-4">
        <div className="text-center font-mono text-sm bg-foreground/5 px-4 py-2 rounded-lg whitespace-nowrap min-w-[20rem]">
          <div className="text-accent">
            {!playerFound ? (
              <TypeIt
                key={key} // use key to reset TypeIt instance
                options={{
                  speed: 50,
                  deleteSpeed: 30,
                }}
                getBeforeInit={(instance) => {
                  const message1 = getQueueMessage();
                  const message2 = getQueueMessage();
                  instance
                    .type(`<span style="color: orange;">${message1}</span>`)
                    .pause(400)
                    .delete(message1.length)
                    .type(`<span style="color: orange;">${message2}</span>`)
                    .pause(600)
                    .delete(message2.length)
                    .exec(() => {
                      setKey((prevKey) => prevKey + 1); // trigger re-render to reset TypeIt
                    });
                  return instance;
                }}
              />
            ) : (
              <TypeIt
                options={{
                  speed: 50,
                  deleteSpeed: 30,
                }}
                getBeforeInit={(instance) => {
                  const matchMessage = getMatchFoundMessage();
                  instance
                    .type(`<span style="color: orange;">${matchMessage}</span>`)
                    .pause(2000)
                    .exec(() => {
                      // Navigate to game with question name from match_found event
                      // This will be handled by the layout's match_found listener
                    });
                  return instance;
                }}
              />
            )}
          </div>
        </div>
      </div>

      {/* Main Battle Area */}
      <div className="flex-1 flex items-center justify-center p-4">
        <div className="flex flex-col md:flex-row items-center gap-12 md:gap-20 lg:gap-32 w-full max-w-6xl">
          {/* User Avatar */}
          <div className="flex-shrink-0">
            <AvatarCard
              src={getUserAvatar()}
              alt={`${
                (context?.user as CustomUser)?.username ||
                context?.user?.name ||
                (session?.user as CustomUser)?.username ||
                session?.user?.name ||
                "User"
              } Avatar`}
              name={
                (context?.user as CustomUser)?.username ||
                context?.user?.name ||
                (session?.user as CustomUser)?.username ||
                session?.user?.name ||
                "Guest"
              }
              size="lg"
              player="player1"
            />
          </div>

          {/* VS Section */}
          <div className="flex flex-col items-center gap-4 flex-shrink-0">
            <div className="text-2xl md:text-4xl font-bold text-foreground/60">
              VS
            </div>
          </div>

          {/* Opponent Avatar */}
          <div className="flex-shrink-0">
            {opponent.image_url && opponent.name && playerFound ? (
              <AvatarCard
                src={opponent.image_url}
                alt={`${opponent.name} Avatar`}
                name={opponent.name}
                size="lg"
                player="player2"
              />
            ) : (
              <OpponentPlaceholder size="lg" />
            )}
          </div>
        </div>
      </div>
    </div>
  );
}
