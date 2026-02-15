'use client';

import { FormEvent, useEffect, useState } from 'react';
import { fetchMe, saveTokens } from '@/lib/auth';

export default function LoginPage() {
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [err, setErr] = useState('');

  useEffect(() => {
    fetchMe().then((u) => {
      if (u?.role === 'super_admin') {
        window.location.href = '/superadmin';
      } else if (u?.role === 'admin') {
        window.location.href = '/admin';
      } else if (u?.role === 'student') {
        window.location.href = '/app';
      }
    });
  }, []);

  const onSubmit = async (e: FormEvent) => {
    e.preventDefault();
    setErr('');
    const res = await fetch(`${process.env.NEXT_PUBLIC_API_URL}/auth/login`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ email, password }),
    });

    if (!res.ok) {
      setErr('Invalid login');
      return;
    }

    const tokens = await res.json();
    saveTokens(tokens);

    const me = await fetch(`${process.env.NEXT_PUBLIC_API_URL}/me`, {
      headers: { Authorization: `Bearer ${tokens.access_token}` },
    }).then((r) => r.json());

    if (me.role === 'super_admin') {
      window.location.href = '/superadmin';
    } else if (me.role === 'admin') {
      window.location.href = '/admin';
    } else {
      window.location.href = '/app';
    }
  };

  return (
    <div className="max-w-4xl mx-auto grid md:grid-cols-[1.1fr_0.9fr] gap-6 items-stretch">
      <div className="panel p-6 flex flex-col justify-between">
        <div>
          <div className="label">Welcome Back</div>
          <h1 className="mt-2 text-3xl font-semibold">Continue your creative journey</h1>
          <p className="mt-2 text-sm text-slate-600">
            Sign in to manage courses, review enrollment requests, or resume your lessons.
          </p>
        </div>
        <div className="mt-8 grid grid-cols-2 gap-4">
          <div className="list-card">
            <div className="text-xs text-slate-500">Admin Studio</div>
            <div className="mt-1 text-lg font-semibold">Dashboard</div>
          </div>
          <div className="list-card">
            <div className="text-xs text-slate-500">Student App</div>
            <div className="mt-1 text-lg font-semibold">Learn</div>
          </div>
        </div>
      </div>

      <form className="panel p-6 space-y-3" onSubmit={onSubmit}>
        <div className="text-xl font-semibold">Login</div>
        <input className="input" placeholder="Email" value={email} onChange={(e) => setEmail(e.target.value)} required />
        <input className="input" type="password" placeholder="Password" value={password} onChange={(e) => setPassword(e.target.value)} required />
        {err && <p className="text-red-600 text-sm">{err}</p>}
        <button className="btn-primary w-full" type="submit">Login</button>
        <div className="text-xs text-slate-500">
          Use your student or admin credentials. Admins can manage enrollments and content.
        </div>
      </form>
    </div>
  );
}
