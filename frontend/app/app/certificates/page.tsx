'use client';

import { useEffect, useState } from 'react';
import { api } from '@/lib/api';
import { authHeader } from '@/lib/auth';

export default function CertificatesPage() {
  const [certs, setCerts] = useState<any[]>([]);

  useEffect(() => {
    api('/certificates').then(setCerts).catch(() => setCerts([]));
  }, []);

  const download = async (id: number) => {
    const res = await fetch(`${process.env.NEXT_PUBLIC_API_URL}/certificates/${id}/download`, {
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
    <div className="space-y-4">
      <h1 className="text-2xl font-semibold">Certificates</h1>
      {certs.map((c) => (
        <div key={c.id} className="card flex items-center justify-between">
          <div>
            <p className="font-medium">{c.certificate_no}</p>
            <p className="text-xs text-slate-500">Issued: {new Date(c.issued_at).toLocaleString()}</p>
          </div>
          <button className="btn-ghost" onClick={() => download(c.id)}>Download</button>
        </div>
      ))}
    </div>
  );
}
