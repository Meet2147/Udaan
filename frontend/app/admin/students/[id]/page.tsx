'use client';

import { useEffect, useState, use } from 'react';
import { api } from '@/lib/api';

export default function StudentDetail({ params }: { params: Promise<{ id: string }> }) {
  const { id } = use(params);
  const [data, setData] = useState<any>(null);

  useEffect(() => {
    api(`/admin/students/${id}/progress`).then(setData).catch(() => setData(null));
  }, [id]);

  if (!data) return <p>Loading...</p>;

  return (
    <div className="space-y-6">
      <div className="panel p-5">
        <div className="label">Student Profile</div>
        <div className="mt-2 text-2xl font-semibold">{data.student.name}</div>
        <div className="text-sm text-slate-500">{data.student.email}</div>
      </div>

      <div className="panel p-5 space-y-3">
        <div className="flex items-center justify-between">
          <div className="text-xl font-semibold">Progress</div>
          <div className="chip">{data.progress.length} lectures</div>
        </div>
        {data.progress.map((p: any, i: number) => (
          <div key={i} className="list-card">
            <div className="flex items-center justify-between">
              <div>
                <div className="text-sm text-slate-500">{p.course}</div>
                <div className="text-lg font-semibold">{p.lecture_title}</div>
              </div>
              <div className="chip">{p.completed ? 'Completed' : 'In progress'}</div>
            </div>
            <div className="mt-2 text-xs text-slate-500">Watched: {p.watched_seconds}s</div>
          </div>
        ))}
        {data.progress.length === 0 && (
          <div className="list-card text-sm text-slate-600">No lecture progress yet.</div>
        )}
      </div>
    </div>
  );
}
