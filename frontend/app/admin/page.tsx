'use client';

import { useEffect, useState } from 'react';
import { api } from '@/lib/api';
import { Bars, Donut, Sparkline } from '@/components/Charts';

export default function AdminDashboard() {
  const [d, setD] = useState<any>(null);

  useEffect(() => {
    api('/admin/dashboard').then(setD).catch(() => setD(null));
  }, []);

  if (!d) return <p>Loading...</p>;

  const trend = [12, 18, 14, 25, 22, 28, 35, 40];
  const completion = d.progress_distribution.completed_percent;
  const incomplete = d.progress_distribution.incomplete_percent;

  return (
    <div className="space-y-6">
      <div className="panel p-5">
        <div className="label">Admin Studio</div>
        <div className="mt-2 text-3xl font-semibold">Performance Overview</div>
        <div className="mt-6 grid lg:grid-cols-3 gap-4">
          <div className="kpi">
            <div className="text-xs text-slate-500">Total Students</div>
            <div className="text-3xl font-semibold">{d.total_students}</div>
            <div className="mt-2 text-xs text-slate-500">All time</div>
          </div>
          <div className="kpi">
            <div className="text-xs text-slate-500">Enrolled Students</div>
            <div className="text-3xl font-semibold">{d.enrolled_students}</div>
            <div className="mt-2 text-xs text-slate-500">Active + completed</div>
          </div>
          <div className="kpi">
            <div className="text-xs text-slate-500">Weekly Engagement</div>
            <Sparkline points={trend} />
            <div className="mt-1 text-xs text-slate-500">Lectures watched</div>
          </div>
        </div>
      </div>

      <div className="grid lg:grid-cols-[1.1fr_0.9fr] gap-6">
        <div className="panel p-5">
          <div className="label">Progress Mix</div>
          <div className="mt-2 text-xl font-semibold">Completion Distribution</div>
          <div className="mt-4">
            <Bars
              label="Course completion buckets"
              data={[
                { label: 'Completed', value: completion },
                { label: 'In Progress', value: incomplete },
              ]}
              max={100}
            />
          </div>
        </div>

        <div className="panel p-5">
          <div className="label">Outcome</div>
          <div className="mt-2 text-xl font-semibold">Completion Rate</div>
          <div className="mt-4">
            <Donut value={completion} label="Courses completed" />
          </div>
          <div className="mt-4 text-xs text-slate-500">
            Aim to keep completion above 70% with timely feedback and nudges.
          </div>
        </div>
      </div>
    </div>
  );
}
