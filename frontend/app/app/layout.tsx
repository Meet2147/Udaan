'use client';

import Link from 'next/link';
import { useEffect, useState } from 'react';
import { fetchMe } from '@/lib/auth';

export default function StudentLayout({ children }: { children: React.ReactNode }) {
  const [ok, setOk] = useState(false);

  useEffect(() => {
    fetchMe().then((u) => {
      if (!u || u.role !== 'student') {
        window.location.href = '/login';
      } else {
        setOk(true);
      }
    });
  }, []);

  if (!ok) return <p>Loading...</p>;

  return (
    <div className="grid lg:grid-cols-[260px_1fr] gap-6 page-shell">
      <aside className="panel h-fit p-4">
        <div className="label">Student</div>
        <div className="mt-3 text-xl font-semibold">My Studio</div>
        <div className="mt-4 flex flex-col gap-2 text-sm">
          <Link className="btn-ghost justify-start" href="/app">Dashboard</Link>
          <Link className="btn-ghost justify-start" href="/app/courses">Courses</Link>
          <Link className="btn-ghost justify-start" href="/app/ai">AI Reference</Link>
          <Link className="btn-ghost justify-start" href="/app/certificates">Certificates</Link>
          <Link className="btn-ghost justify-start" href="/app/profile">Profile</Link>
        </div>
        <div className="mt-6 p-3 rounded-xl bg-amber-50 border border-amber-100 text-xs text-amber-900">
          Keep a daily sketch streak for faster progress.
        </div>
      </aside>
      <section className="space-y-6">{children}</section>
    </div>
  );
}
