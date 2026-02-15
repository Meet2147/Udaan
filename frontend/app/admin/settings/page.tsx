'use client';

import { FormEvent, useEffect, useState } from 'react';
import { authHeader } from '@/lib/auth';
import { api } from '@/lib/api';

export default function AdminSettings() {
  const [teacherName, setTeacherName] = useState('');

  useEffect(() => {
    api('/admin/settings/certificate').then((d) => setTeacherName(d.teacher_name)).catch(() => null);
  }, []);

  const onSave = async (e: FormEvent<HTMLFormElement>) => {
    e.preventDefault();
    const fd = new FormData(e.currentTarget);
    fd.set('teacher_name', teacherName);

    await fetch(`${process.env.NEXT_PUBLIC_API_URL}/admin/settings/certificate-signature`, {
      method: 'POST',
      headers: { ...authHeader() },
      body: fd,
    });

    alert('Saved');
  };

  return (
    <div className="space-y-6">
      <div className="panel p-5">
        <div className="label">Branding</div>
        <div className="mt-2 text-2xl font-semibold">Certificate Template</div>
        <div className="mt-1 text-sm text-slate-600">Personalize certificates with your name and signature.</div>
      </div>

      <form className="panel p-5 space-y-3" onSubmit={onSave}>
        <div className="text-sm font-semibold">Teacher Name</div>
        <input className="input" value={teacherName} onChange={(e) => setTeacherName(e.target.value)} placeholder="Teacher name" name="teacher_name" />
        <div className="text-sm font-semibold">Signature Image</div>
        <input className="input" type="file" name="signature" accept="image/*" />
        <button className="btn-primary">Save Template</button>
      </form>
    </div>
  );
}
