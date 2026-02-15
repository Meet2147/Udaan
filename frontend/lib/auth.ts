'use client';

import { Tokens, User } from './types';

const TOKEN_KEY = 'udaan_tokens';

export function saveTokens(tokens: Tokens) {
  localStorage.setItem(TOKEN_KEY, JSON.stringify(tokens));
}

export function getTokens(): Tokens | null {
  const raw = localStorage.getItem(TOKEN_KEY);
  return raw ? (JSON.parse(raw) as Tokens) : null;
}

export function clearTokens() {
  localStorage.removeItem(TOKEN_KEY);
}

export function authHeader(): HeadersInit {
  const t = getTokens();
  const headers: Record<string, string> = {};
  if (t?.access_token) headers.Authorization = `Bearer ${t.access_token}`;
  return headers;
}

export async function fetchMe(): Promise<User | null> {
  const res = await fetch(`${process.env.NEXT_PUBLIC_API_URL}/me`, {
    headers: { ...authHeader() },
    cache: 'no-store',
  });
  if (!res.ok) return null;
  return (await res.json()) as User;
}
