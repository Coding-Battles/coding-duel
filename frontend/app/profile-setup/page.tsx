"use client";
import { useState, useEffect } from "react";
import { useRouter, useSearchParams } from "next/navigation";
import { useSession } from "@/lib/auth-client";
import { updateUserProfile } from "@/lib/auth-client";
import ProfileCreator from "@/components/ProfileCreator";

export default function ProfileSetupPage() {
  const { data: session, isPending } = useSession();
  const router = useRouter();
  const searchParams = useSearchParams();
  const isGuestMode = searchParams.get('guest') === 'true';
  
  const [username, setUsername] = useState("");
  const [selectedAvatar, setSelectedAvatar] = useState<number | null>(null);
  const [customAvatar, setCustomAvatar] = useState<string | null>(null);
  const [isSaving, setIsSaving] = useState(false);

  // Handle authentication redirect in useEffect to avoid render-time navigation
  // Skip this check for guest mode
  useEffect(() => {
    if (!isGuestMode && !isPending && !session?.user) {
      router.push("/");
    }
  }, [session, isPending, router, isGuestMode]);

  // Show loading state while session is being fetched (skip for guest mode)
  if (!isGuestMode && isPending) {
    return (
      <div className="min-h-screen bg-background text-foreground flex items-center justify-center">
        <div className="text-center">
          <div className="w-8 h-8 border-2 border-primary border-t-transparent rounded-full animate-spin mx-auto mb-4" />
          <p className="text-foreground/70">Loading...</p>
        </div>
      </div>
    );
  }

  // Don't render content if not authenticated (will redirect via useEffect)
  // Skip this check for guest mode
  if (!isGuestMode && !session?.user) {
    return null;
  }

  const handleComplete = async () => {
    if (!username.trim() || selectedAvatar === null) return;

    setIsSaving(true);
    try {
      if (isGuestMode) {
        // Guest mode: Create temporary session data in localStorage
        const guestData = {
          username: username.trim(),
          selectedAvatar,
          isGuest: true,
          guestId: `guest-${Date.now()}-${Math.random().toString(36).substring(2, 9)}`,
        };
        
        localStorage.setItem('guestProfile', JSON.stringify(guestData));
        console.log("Guest profile created:", guestData);
      } else {
        // Authenticated mode: Save to database
        await updateUserProfile({
          username: username.trim(),
          selectedPfp: selectedAvatar ?? undefined,
        });
        console.log("Profile saved successfully");
      }

      // Navigate to game setup
      router.push("/game-setup");
    } catch (error) {
      console.error("Failed to save profile:", error);
      // TODO: Show error message to user
    } finally {
      setIsSaving(false);
    }
  };

  return (
    <div className="min-h-screen bg-background text-foreground px-6 flex items-center">
      <div className="max-w-4xl mx-auto">
        <ProfileCreator
          username={username}
          onUsernameChange={setUsername}
          selectedAvatar={selectedAvatar}
          onAvatarChange={setSelectedAvatar}
          customAvatar={customAvatar}
          onCustomAvatarChange={setCustomAvatar}
          userId={session?.user?.id}
          onComplete={isSaving ? undefined : handleComplete}
          isGuestMode={isGuestMode}
        />

        {isSaving && (
          <div className="text-center mt-4">
            <p className="text-foreground/60">Saving your profile...</p>
          </div>
        )}
      </div>
    </div>
  );
}
