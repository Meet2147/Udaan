'use client';

import { useEffect, useState } from 'react';
import { authHeader } from '@/lib/auth';
import { api } from '@/lib/api';

const presets = [
  ['pencil_sketch_outline', 'Pencil Sketch Outline'],
  ['charcoal_shading', 'Charcoal Shading'],
  ['watercolor_wash_reference', 'Watercolor Wash Reference'],
  ['simplified_shapes_block_in', 'Simplified Shapes (Block-in)'],
  ['value_map', 'Value Map'],
];

export default function AIPage() {
  const [preset, setPreset] = useState('pencil_sketch_outline');
  const [prompt, setPrompt] = useState('');
  const [history, setHistory] = useState<any[]>([]);

  const load = () => api('/ai/history').then(setHistory).catch(() => setHistory([]));

  useEffect(() => {
    load();
  }, []);

  const onUpload = async (e: React.FormEvent<HTMLFormElement>) => {
    e.preventDefault();
    const form = e.currentTarget;
    const fd = new FormData(form);
    fd.set('preset', preset);
    fd.set('prompt', prompt);

    const res = await fetch(`${process.env.NEXT_PUBLIC_API_URL}/ai/transform`, {
      method: 'POST',
      headers: { ...authHeader() },
      body: fd,
    });

    if (res.ok) {
      form.reset();
      load();
    }
  };

  return (
    <div className="space-y-4">
      <h1 className="text-2xl font-semibold">AI Reference Transformation</h1>
      <form className="card space-y-3" onSubmit={onUpload}>
        <input className="input" type="file" name="image" accept="image/*" required />
        <select className="input" value={preset} onChange={(e) => setPreset(e.target.value)}>
          {presets.map(([k, v]) => <option key={k} value={k}>{v}</option>)}
        </select>
        <input className="input" placeholder="Optional prompt" value={prompt} onChange={(e) => setPrompt(e.target.value)} />
        <button className="btn-primary" type="submit">Transform</button>
      </form>
      <div className="grid md:grid-cols-3 gap-4">
        {history.map((h) => (
          <div key={h.id} className="card">
            <p className="text-xs text-slate-500">{h.preset}</p>
            <img src={`${process.env.NEXT_PUBLIC_API_URL}/media/file/${h.output_image_path}`} alt="output" className="rounded mt-2" />
          </div>
        ))}
      </div>
    </div>
  );
}
