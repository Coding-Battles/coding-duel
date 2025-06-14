import { auth } from "@/lib/auth";
import { redirect } from "next/navigation";

export async function GET() {
  const { url } = await auth.createSocialAuthorizationURL("google", {
    redirectTo: "/auth/google/callback",
  });

  return redirect(url);
}
