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

export const getUserProfile = async (): Promise<{ username?: string; selectedPfp?: number } | null> => {
  try {
    const session = await getSession();
    console.log("Full session data:", session);
    
    if (!session?.data?.user) {
      console.log("No session or user data found");
      return null;
    }
    
    console.log("User object:", session.data.user);
    
    // Extract profile data from user object
    const user = session.data.user as { username?: string; selectedPfp?: number };
    const { username, selectedPfp } = user;
    
    console.log("Extracted profile data:", { username, selectedPfp });
    
    return {
      ...(username && { username }),
      ...(selectedPfp !== undefined && { selectedPfp })
    };
  } catch (error) {
    console.error("Failed to get user profile:", error);
    return null;
  }
};

export const { useSession, signOut, getSession } = authClient;
