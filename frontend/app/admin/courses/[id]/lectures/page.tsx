'use client';

import { FormEvent, useEffect, useState, use } from 'react';
import { authHeader } from '@/lib/auth';
import { api } from '@/lib/api';

export default function AdminLectures({ params }: { params: Promise<{ id: string }> }) {
  const { id } = use(params);
  const courseId = Number(id);
  const [lectures, setLectures] = useState<any[]>([]);
  const [title, setTitle] = useState('');
  const [uploadingId, setUploadingId] = useState<number | null>(null);
  const [uploadName, setUploadName] = useState('');

  const load = () => api(`/admin/courses/${courseId}/lectures`).then(setLectures).catch(() => setLectures([]));

  useEffect(() => {
    load();
  }, [courseId]);

  const create = async (e: FormEvent) => {
    e.preventDefault();
    await api(`/admin/courses/${courseId}/lectures`, {
      method: 'POST',
      body: JSON.stringify({ title, order_index: lectures.length + 1 }),
    });
    setTitle('');
    load();
  };

  const upload = async (lectureId: number, file: File) => {
    const fd = new FormData();
    fd.append('video', file);
    setUploadingId(lectureId);
    setUploadName(file.name);
    await fetch(`${process.env.NEXT_PUBLIC_API_URL}/admin/lectures/${lectureId}/upload`, {
      method: 'POST',
      headers: { ...authHeader() },
      body: fd,
    }).finally(() => {
      setUploadingId(null);
      setUploadName('');
    });
    load();
  };

  return (
    <div className="space-y-6">
      <div className="panel p-5">
        <div className="label">Curriculum Builder</div>
        <div className="mt-2 text-2xl font-semibold">Create a Lecture</div>
        <form className="mt-4 grid gap-3" onSubmit={create}>
          <input className="input" placeholder="Lecture title" value={title} onChange={(e) => setTitle(e.target.value)} required />
          <button className="btn-primary justify-center">Add Lecture</button>
        </form>
      </div>

      <div className="panel p-5 space-y-4">
        <div className="flex items-center justify-between">
          <div>
            <div className="label">Course Structure</div>
            <div className="text-xl font-semibold">Lectures</div>
          </div>
          <div className="chip">{lectures.length} items</div>
        </div>

        {lectures.length === 0 && (
          <div className="list-card text-sm text-slate-600">No lectures yet. Add your first lecture above.</div>
        )}

        {lectures.map((l) => (
          <div key={l.id} className="list-card">
            <div className="flex flex-col md:flex-row md:items-center md:justify-between gap-3">
              <div>
                <div className="text-sm text-slate-500">Lecture {l.order_index}</div>
                <div className="text-lg font-semibold">{l.title}</div>
                <div className="text-xs text-slate-500">Duration: {l.duration_sec || 0}s</div>
                <div className="mt-1 text-xs">
                  {l.video_key ? (
                    <span className="chip">Video uploaded</span>
                  ) : (
                    <span className="chip">No video</span>
                  )}
                </div>
              </div>

              <div className="uploader md:w-[320px]">
                <div className="text-sm font-semibold">Upload Content</div>
                <div className="text-xs text-slate-500">MP4 or HLS packages. Students will stream securely.</div>
                <label className="btn-ghost justify-center cursor-pointer">
                  Choose file
                  <input
                    type="file"
                    accept="video/*"
                    className="hidden"
                    onChange={(e) => {
                      const file = e.target.files?.[0];
                      if (file) upload(l.id, file);
                    }}
                  />
                </label>
                <div className="text-xs text-slate-600">
                  {uploadingId === l.id ? `Uploading: ${uploadName}` : (l.video_key || 'No file selected')}
                </div>
              </div>
            </div>
          </div>
        ))}
      </div>
    </div>
  );
}
