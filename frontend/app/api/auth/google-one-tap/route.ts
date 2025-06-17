import { NextRequest, NextResponse } from 'next/server';
import { auth } from '@/lib/auth';

export async function POST(request: NextRequest) {
  try {
    const { credential } = await request.json();
    
    if (!credential) {
      return NextResponse.json({ error: 'No credential provided' }, { status: 400 });
    }

    // Verify the Google credential and create session
    const result = await auth.api.signInSocial({
      body: {
        provider: 'google',
        idToken: credential,
      },
    });

    return NextResponse.json({ success: true, data: result });
  } catch (error) {
    console.error('Google One Tap authentication error:', error);
    return NextResponse.json({ error: 'Authentication failed' }, { status: 500 });
  }
}