import { createAuthClient } from "better-auth/react";
import { oneTapClient } from "better-auth/client/plugins";

export const authClient = createAuthClient({
  baseURL: process.env.BETTER_AUTH_URL || "http://localhost:3000",
  plugins: [
    oneTapClient({
      clientId: process.env.NEXT_PUBLIC_GOOGLE_CLIENT_ID!,
      autoSelect: false,
      cancelOnTapOutside: true,
      context: "signin"
    })
  ]
});

export const signInWithGoogle = async () => {
  const data = await authClient.signIn.social({
    provider: "google",
  });

  return data;
};

export const initializeGoogleOneTap = async () => {
  try {
    await authClient.oneTap();
  } catch (error) {
    console.error('One Tap initialization error:', error);
  }
};

export const { useSession, signOut, getSession } = authClient;
