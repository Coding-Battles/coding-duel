import { createAuthClient } from "better-auth/react";

export const authClient = createAuthClient({
  baseURL: process.env.BETTER_AUTH_URL || "http://localhost:3000",
});
export const signInWithGoogle = async () => {
  const data = await authClient.signIn.social({
    provider: "google",
  });

  return data;
};

export const { useSession, signOut, getSession } = authClient;
