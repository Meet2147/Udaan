'use client';

import { useEffect, useState } from 'react';
import { api } from '@/lib/api';
import { authHeader } from '@/lib/auth';

export default function AdminCertificates() {
  const [rows, setRows] = useState<any[]>([]);

  useEffect(() => {
    api('/admin/certificates').then(setRows).catch(() => setRows([]));
  }, []);

  const download = async (id: number) => {
    const res = await fetch(`${process.env.NEXT_PUBLIC_API_URL}/admin/certificates/${id}/download`, {
      headers: { ...authHeader() },
    });
    if (!res.ok) return;
    const blob = await res.blob();
    const href = URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = href;
    a.download = `certificate-${id}.pdf`;
    a.click();
    URL.revokeObjectURL(href);
  };

  return (
    <div className="space-y-6">
      <div className="panel p-5">
        <div className="label">Admin Studio</div>
        <div className="mt-2 text-2xl font-semibold">Certificates</div>
        <div className="mt-4 flex items-center gap-3">
          <div className="chip">{rows.length} issued</div>
          <div className="text-xs text-slate-500">Download and share student completions.</div>
        </div>
      </div>

      <div className="panel p-5 space-y-3">
        {rows.map((r) => (
          <div key={r.id} className="list-card flex items-center justify-between">
            <div>
              <div className="text-xs text-slate-500">Certificate</div>
              <div className="text-lg font-semibold">{r.certificate_no}</div>
              <div className="text-xs text-slate-500">{r.student_name} — {r.course_title}</div>
            </div>
            <button className="btn-ghost" onClick={() => download(r.id)}>Download PDF</button>
          </div>
        ))}
        {rows.length === 0 && (
          <div className="list-card text-sm text-slate-600">No certificates issued yet.</div>
        )}
      </div>
    </div>
  );
}
