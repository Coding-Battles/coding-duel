import { createAuthClient } from "better-auth/react";

export const authClient = createAuthClient({
  baseURL: process.env.NEXT_PUBLIC_BETTER_AUTH_URL || "http://localhost:3000",
});

export const signInWithGoogle = async () => {
  const data = await authClient.signIn.social({
    provider: "google",
    callbackURL: window.location.origin,
  });

  return data;
};

export const updateUserProfile = async (profileData: { username?: string; selectedPfp?: number }) => {
  try {
    // Filter out undefined values
    const updateData = Object.fromEntries(
      Object.entries(profileData).filter(([, value]) => value !== undefined)
    );
    
    const result = await authClient.updateUser(updateData);
    return result;
  } catch (error) {
    console.error("Failed to update user profile:", error);
    throw error;
  }
};

export const { useSession, signOut, getSession } = authClient;
