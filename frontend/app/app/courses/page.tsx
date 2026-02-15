'use client';

import Link from 'next/link';
import { useEffect, useState } from 'react';
import { api } from '@/lib/api';

export default function CoursesPage() {
  const [courses, setCourses] = useState<any[]>([]);

  useEffect(() => {
    api('/courses').then(setCourses).catch(() => setCourses([]));
  }, []);

  const enroll = async (id: number) => {
    await api(`/courses/${id}/enroll`, { method: 'POST' });
    alert('Enrollment requested. Admin approval may be required.');
  };

  return (
    <div className="space-y-4">
      <h1 className="text-2xl font-semibold">Courses</h1>
      <div className="grid md:grid-cols-2 gap-4">
        {courses.map((c) => (
          <div key={c.id} className="card space-y-2">
            <div className="text-xs uppercase text-slate-500">{c.level}</div>
            <h3 className="font-semibold">{c.title}</h3>
            <p className="text-sm text-slate-700">{c.description}</p>
            <div className="flex gap-2">
              <button className="btn-primary" onClick={() => enroll(c.id)}>Enroll</button>
              <Link href={`/app/courses/${c.id}`} className="btn-ghost">View</Link>
            </div>
          </div>
        ))}
      </div>
    </div>
  );
}
