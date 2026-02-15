'use client';

import Link from 'next/link';
import { useEffect, useState } from 'react';
import { clearTokens, fetchMe } from '@/lib/auth';

export default function TopNav() {
  const [role, setRole] = useState<string>('');

  useEffect(() => {
    fetchMe().then((u) => setRole(u?.role || ''));
  }, []);

  return (
    <header className="border-b border-black/10 bg-white/70 backdrop-blur sticky top-0 z-30">
      <div className="max-w-6xl mx-auto px-4 py-3 flex items-center justify-between">
        <div className="flex items-center gap-3">
          <div className="h-9 w-9 rounded-xl bg-blue-600 text-white grid place-items-center font-bold">U</div>
          <Link href="/" className="text-lg font-semibold tracking-tight">Udaan</Link>
          {role && (
            <span className="chip">
              {role === 'super_admin' ? 'SuperAdmin' : role === 'admin' ? 'Admin Studio' : 'Student App'}
            </span>
          )}
        </div>
        <div className="flex gap-3 items-center text-sm">
          {role === 'student' && <Link href="/app" className="btn-ghost">Student</Link>}
          {role === 'admin' && <Link href="/admin" className="btn-ghost">Admin</Link>}
          {role === 'super_admin' && <Link href="/superadmin" className="btn-ghost">SuperAdmin</Link>}
          {!role && <Link href="/login" className="btn-primary">Login</Link>}
          {!!role && (
            <button
              className="btn-ghost text-red-600"
              onClick={() => {
                clearTokens();
                window.location.href = '/login';
              }}
            >
              Logout
            </button>
          )}
        </div>
      </div>
    </header>
  );
}
