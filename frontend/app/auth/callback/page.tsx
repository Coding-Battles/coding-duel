import { redirect } from 'next/navigation';
import { headers } from 'next/headers';
import { auth } from '@/lib/auth';

export default async function AuthCallback() {
  const session = await auth.api.getSession({
    headers: await headers()
  });
  
  if (!session?.user) {
    // No session found, redirect back to home page
    console.log('No session found in OAuth callback, redirecting to home');
    redirect('/');
  }
  
  // Check if user has completed their profile
  const { username, selectedPfp } = session.user;
  
  console.log('OAuth callback - user profile check:', { username, selectedPfp });
  
  if (username && selectedPfp !== undefined && selectedPfp !== null) {
    // User has complete profile, redirect to game setup
    console.log('User has complete profile, redirecting to game setup');
    redirect('/game-setup');
  } else {
    // User needs to complete profile setup
    console.log('User needs profile setup, redirecting to profile creation');
    redirect('/profile-setup');
  }
}