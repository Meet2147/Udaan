'use client';

import Link from 'next/link';
import { FormEvent, useEffect, useState } from 'react';
import { api } from '@/lib/api';

export default function AdminCourses() {
  const [courses, setCourses] = useState<any[]>([]);
  const [title, setTitle] = useState('');
  const [level, setLevel] = useState('');
  const [description, setDescription] = useState('');

  const load = () => api('/admin/courses').then(setCourses).catch(() => setCourses([]));

  useEffect(() => {
    load();
  }, []);

  const create = async (e: FormEvent) => {
    e.preventDefault();
    await api('/admin/courses', {
      method: 'POST',
      body: JSON.stringify({ title, level, description }),
    });
    setTitle('');
    setDescription('');
    load();
  };

  return (
    <div className="space-y-6">
      <div className="panel p-5">
        <div className="label">Course Builder</div>
        <div className="mt-2 text-2xl font-semibold">Create a Course</div>
        <form className="mt-4 grid gap-3" onSubmit={create}>
          <input className="input" placeholder="Title" value={title} onChange={(e) => setTitle(e.target.value)} required />
          <input className="input" placeholder="Category (e.g., Portrait, Calligraphy)" value={level} onChange={(e) => setLevel(e.target.value)} required />
          <textarea className="input" placeholder="Description" value={description} onChange={(e) => setDescription(e.target.value)} />
          <button className="btn-primary">Save Course</button>
        </form>
      </div>

      <div className="panel p-5">
        <div className="flex items-center justify-between">
          <div>
            <div className="label">Library</div>
            <div className="text-xl font-semibold">Courses</div>
          </div>
          <div className="chip">{courses.length} total</div>
        </div>

        <div className="mt-4 space-y-3">
          {courses.map((c) => (
            <div key={c.id} className="list-card flex items-center justify-between">
              <div>
                <div className="text-sm text-slate-500 uppercase">{c.level || 'Uncategorized'}</div>
                <div className="text-lg font-semibold">{c.title}</div>
                <div className="text-xs text-slate-500">{c.description || 'No description yet'}</div>
              </div>
              <Link className="btn-ghost" href={`/admin/courses/${c.id}/lectures`}>Manage Lectures</Link>
            </div>
          ))}
          {courses.length === 0 && (
            <div className="list-card text-sm text-slate-600">No courses created yet.</div>
          )}
        </div>
      </div>
    </div>
  );
}
