// app/actions/toggleTheme.ts
'use server';

import { cookies } from 'next/headers';

export async function toggleTheme() {
  const theme = (await cookies()).get('theme')?.value || 'light';
  const newTheme = theme === 'dark' ? 'light' : 'dark';
  (await cookies()).set('theme', newTheme);
}
