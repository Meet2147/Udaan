'use client';

import Link from 'next/link';
import { useEffect, useState } from 'react';
import { fetchMe } from '@/lib/auth';

export default function AdminLayout({ children }: { children: React.ReactNode }) {
  const [ok, setOk] = useState(false);

  useEffect(() => {
    fetchMe().then((u) => {
      if (!u || u.role !== 'admin') {
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
        <div className="label">Admin Studio</div>
        <div className="mt-3 text-xl font-semibold">Control Center</div>
        <div className="mt-4 flex flex-col gap-2 text-sm">
          <Link className="btn-ghost justify-start" href="/admin">Dashboard</Link>
          <Link className="btn-ghost justify-start" href="/admin/courses">Courses</Link>
          <Link className="btn-ghost justify-start" href="/admin/students">Students</Link>
          <Link className="btn-ghost justify-start" href="/admin/certificates">Certificates</Link>
          <Link className="btn-ghost justify-start" href="/admin/settings">Settings</Link>
        </div>
        <div className="mt-6 p-3 rounded-xl bg-blue-50 border border-blue-100 text-xs text-blue-900">
          Tip: review pending enrollments daily to keep student momentum.
        </div>
      </aside>
      <section className="space-y-6">{children}</section>
    </div>
  );
}
