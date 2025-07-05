"use client";
import { useState, useEffect } from "react";
import { useRouter } from "next/navigation";
import { useSession } from "@/lib/auth-client";
import { updateUserProfile } from "@/lib/auth-client";
import ProfileCreator from "@/components/ProfileCreator";

export default function ProfileSetupPage() {
  const { data: session, isPending } = useSession();
  const router = useRouter();
  const [username, setUsername] = useState("");
  const [selectedAvatar, setSelectedAvatar] = useState<number | null>(null);
  const [isSaving, setIsSaving] = useState(false);

  // Handle authentication redirect in useEffect to avoid render-time navigation
  useEffect(() => {
    if (!isPending && !session?.user) {
      router.push("/");
    }
  }, [session, isPending, router]);

  // Show loading state while session is being fetched
  if (isPending) {
    return (
      <div className="min-h-screen bg-gray-950 text-white flex items-center justify-center">
        <div className="text-center">
          <div className="w-8 h-8 border-2 border-primary border-t-transparent rounded-full animate-spin mx-auto mb-4" />
          <p className="text-gray-300">Loading...</p>
        </div>
      </div>
    );
  }

  // Don't render content if not authenticated (will redirect via useEffect)
  if (!session?.user) {
    return null;
  }

  const handleComplete = async () => {
    if (!username.trim() || selectedAvatar === null) return;

    setIsSaving(true);
    try {
      // Save profile data
      await updateUserProfile({
        username: username.trim(),
        selectedPfp: selectedAvatar
      });

      console.log("Profile saved successfully");
      
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
    <div className="min-h-screen bg-gray-950 text-white">
      <div className="container mx-auto px-6 py-20">
        <div className="text-center mb-8">
          <h1 className="text-3xl md:text-4xl font-bold mb-4">
            Create Your Profile
          </h1>
          <p className="text-gray-300 text-lg">
            Choose your username and avatar to get started
          </p>
        </div>

        <div className="max-w-4xl mx-auto">
          <ProfileCreator
            username={username}
            onUsernameChange={setUsername}
            selectedAvatar={selectedAvatar}
            onAvatarChange={setSelectedAvatar}
            onComplete={isSaving ? undefined : handleComplete}
          />
          
          {isSaving && (
            <div className="text-center mt-4">
              <p className="text-gray-400">Saving your profile...</p>
            </div>
          )}
        </div>
      </div>
    </div>
  );
}