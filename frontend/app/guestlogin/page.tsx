"use client";
import { useRouter } from "next/navigation";
import { useEffect } from "react";
import { signOut } from "@/lib/auth-client";

export default function GuestLoginPage() {
  const router = useRouter();

  useEffect(() => {
    const setupGuestMode = async () => {
      try {
        // Log out any existing user
        await signOut();
        console.log("User logged out for guest mode");
        
        // Clear any existing guest profile
        localStorage.removeItem('guestProfile');
        
        // Small delay to ensure logout is processed
        setTimeout(() => {
          router.push("/profile-setup?guest=true");
        }, 100);
      } catch (error) {
        console.error("Error setting up guest mode:", error);
        // Still proceed to guest setup even if logout fails
        router.push("/profile-setup?guest=true");
      }
    };

    setupGuestMode();
  }, [router]);

  return (
    <div className="min-h-screen bg-background text-foreground flex items-center justify-center">
      <div className="text-center">
        <div className="w-8 h-8 border-2 border-primary border-t-transparent rounded-full animate-spin mx-auto mb-4" />
        <p className="text-foreground/70">Setting up guest mode...</p>
      </div>
    </div>
  );
}