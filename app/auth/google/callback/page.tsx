'use client';

import { useEffect } from 'react';
import { useSearchParams } from 'next/navigation';

export default function GoogleCallback() {
  const searchParams = useSearchParams();

  useEffect(() => {
    const code = searchParams.get('code');
    const state = searchParams.get('state');

    if (window.opener) {
      if (code && state) {
        // For simplicity, we'll just reload the opener window.
        // A more robust solution would be to exchange the code for a session
        // and then post the session back to the opener.
        window.opener.location.reload();
      } else {
        // Handle error case
        console.error('Google callback error: No code or state found');
      }
      window.close();
    }
  }, [searchParams]);

  return (
    <div style={{ padding: '20px', fontFamily: 'sans-serif' }}>
      <h1>Authenticating...</h1>
      <p>Please wait while we authenticate your account.</p>
    </div>
  );
}
