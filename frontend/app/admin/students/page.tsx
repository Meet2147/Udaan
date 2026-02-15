'use client';

import Link from 'next/link';
import { useEffect, useState } from 'react';
import { api } from '@/lib/api';

export default function StudentsPage() {
  const [students, setStudents] = useState<any[]>([]);
  const [pending, setPending] = useState<any[]>([]);
  const [allEnrollments, setAllEnrollments] = useState<any[]>([]);
  const [error, setError] = useState('');

  const load = () => {
    setError('');
    api('/admin/students').then(setStudents).catch(() => setStudents([]));
    api('/admin/enrollments?status=pending')
      .then(setPending)
      .catch((e) => {
        setPending([]);
        setError(e?.message || 'Failed to load enrollment requests.');
      });
    api('/admin/enrollments')
      .then(setAllEnrollments)
      .catch(() => setAllEnrollments([]));
  };

  useEffect(() => {
    load();
  }, []);

  const approve = async (row: any) => {
    await api('/admin/enrollments', {
      method: 'POST',
      body: JSON.stringify({ student_id: row.student_id, course_id: row.course_id }),
    });
    load();
  };

  const reject = async (row: any) => {
    await api(`/admin/enrollments/${row.id}`, { method: 'DELETE' });
    load();
  };

  return (
    <div className="space-y-6">
      <section className="panel p-5 space-y-3">
        <div className="flex items-center justify-between">
          <div>
            <div className="label">Admin Studio</div>
            <h1 className="text-2xl font-semibold">Enrollment Requests</h1>
          </div>
          <div className="chip">{pending.length} pending</div>
        </div>
        {error && <p className="text-sm text-red-600">{error}</p>}
        {pending.length === 0 && <p className="text-sm text-slate-600">No pending requests.</p>}
        {pending.map((p) => (
          <div key={p.id} className="list-card flex items-center justify-between">
            <div>
              <p className="font-medium">{p.student_name} → {p.course_title}</p>
              <p className="text-xs">{p.student_email} | {p.course_level}</p>
            </div>
            <div className="flex gap-2">
              <button className="btn-primary" onClick={() => approve(p)}>Approve</button>
              <button className="btn-ghost" onClick={() => reject(p)}>Reject</button>
            </div>
          </div>
        ))}
        {pending.length === 0 && allEnrollments.length > 0 && (
          <div className="list-card text-sm text-slate-600">
            Requests exist but none are pending. Latest enrollment status:
            {allEnrollments.slice(0, 3).map((e) => (
              <div key={e.id} className="mt-2">
                {e.student_name} → {e.course_title} ({e.status})
              </div>
            ))}
          </div>
        )}
      </section>

      <section className="panel p-5 space-y-3">
        <div className="flex items-center justify-between">
          <h2 className="text-xl font-semibold">Students</h2>
          <div className="chip">{students.length} total</div>
        </div>
        {students.map((s) => (
          <div key={s.id} className="list-card flex items-center justify-between">
            <div>
              <p className="font-medium">{s.full_name}</p>
              <p className="text-xs">{s.email} | {s.phone} | {s.grade_or_standard}</p>
            </div>
            <Link className="btn-ghost" href={`/admin/students/${s.id}`}>View</Link>
          </div>
        ))}
        {students.length === 0 && <div className="list-card text-sm text-slate-600">No students yet.</div>}
      </section>
    </div>
  );
}
