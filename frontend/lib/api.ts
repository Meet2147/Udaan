'use client';

import { authHeader } from './auth';

export async function api(path: string, options: RequestInit = {}) {
  const isForm = options.body instanceof FormData;
  const headers: HeadersInit = {
    ...authHeader(),
    ...(options.headers || {}),
  };

  if (!isForm) {
    (headers as Record<string, string>)['Content-Type'] = 'application/json';
  }

  const res = await fetch(`${process.env.NEXT_PUBLIC_API_URL}${path}`, {
    ...options,
    headers,
    cache: 'no-store',
  });

  if (!res.ok) {
    const txt = await res.text();
    throw new Error(txt || 'Request failed');
  }

  const ctype = res.headers.get('content-type') || '';
  if (ctype.includes('application/json')) return res.json();
  return res;
}
