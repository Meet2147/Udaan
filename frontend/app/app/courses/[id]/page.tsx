'use client';

import Link from 'next/link';
import { useEffect, useState, use } from 'react';
import { api } from '@/lib/api';

export default function CourseDetail({ params }: { params: Promise<{ id: string }> }) {
  const { id } = use(params);
  const [data, setData] = useState<any>(null);

  useEffect(() => {
    api(`/courses/${id}`).then(setData).catch(() => setData(null));
  }, [id]);

  if (!data) return <p>Loading...</p>;

  return (
    <div className="space-y-4">
      <h1 className="text-2xl font-semibold">{data.course.title}</h1>
      <p>{data.course.description}</p>
      <p className="text-sm">Enrollment: {data.enrolled ? 'Approved' : 'Pending/Not enrolled'}</p>
      <div className="space-y-2">
        {data.lectures.map((l: any) => (
          <div key={l.id} className="card flex items-center justify-between">
            <div>
              <p className="font-medium">{l.order_index}. {l.title}</p>
              <p className="text-xs text-slate-600">{l.duration_sec}s</p>
            </div>
            <Link href={`/app/lectures/${l.id}`} className="btn-primary">Open</Link>
          </div>
        ))}
      </div>
    </div>
  );
}
