'use client';

import { useEffect, useState } from 'react';
import { api } from '@/lib/api';
import { Bars, Sparkline } from '@/components/Charts';

export default function StudentDashboard() {
  const [progress, setProgress] = useState<any[]>([]);

  useEffect(() => {
    api('/progress').then(setProgress).catch(() => setProgress([]));
  }, []);

  const avg = progress.length
    ? Math.round(progress.reduce((acc, p) => acc + p.completed_percent, 0) / progress.length)
    : 0;

  return (
    <div className="space-y-6">
      <div className="panel p-5">
        <div className="label">Learning</div>
        <div className="mt-2 text-3xl font-semibold">Your Studio Progress</div>
        <div className="mt-6 grid lg:grid-cols-3 gap-4">
          <div className="kpi">
            <div className="text-xs text-slate-500">Average Completion</div>
            <div className="text-3xl font-semibold">{avg}%</div>
            <div className="mt-2 text-xs text-slate-500">Across all courses</div>
          </div>
          <div className="kpi">
            <div className="text-xs text-slate-500">Courses Enrolled</div>
            <div className="text-3xl font-semibold">{progress.length}</div>
            <div className="mt-2 text-xs text-slate-500">Keep your streak going</div>
          </div>
          <div className="kpi">
            <div className="text-xs text-slate-500">Weekly Practice</div>
            <Sparkline points={[6, 12, 8, 14, 16, 22, 18, 26]} />
            <div className="mt-1 text-xs text-slate-500">Minutes spent</div>
          </div>
        </div>
      </div>

      <div className="panel p-5">
        <div className="label">Course Progress</div>
        <div className="mt-2 text-xl font-semibold">Completion by Course</div>
        <div className="mt-4 grid md:grid-cols-2 gap-4">
          {progress.map((p) => (
            <div key={p.course_id} className="list-card">
              <div className="flex items-center justify-between">
                <div>
                  <div className="text-sm text-slate-500">{p.level || 'Category'}</div>
                  <div className="text-lg font-semibold">{p.course_title}</div>
                </div>
                <div className="chip">{p.certificate_available ? 'Certificate ready' : 'In progress'}</div>
              </div>
              <div className="mt-3">
                <Bars data={[{ label: 'Complete', value: p.completed_percent }]} max={100} />
              </div>
            </div>
          ))}
          {progress.length === 0 && (
            <div className="list-card text-sm text-slate-600">No courses yet. Enroll to see progress here.</div>
          )}
        </div>
      </div>
    </div>
  );
}
