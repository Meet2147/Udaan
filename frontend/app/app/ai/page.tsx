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
  const [config, setConfig] = useState<any>(null);
  const [codingPrompt, setCodingPrompt] = useState('');
  const [codingReply, setCodingReply] = useState('');
  const [topic, setTopic] = useState('');
  const [flashcards, setFlashcards] = useState<any[]>([]);
  const [quiz, setQuiz] = useState<any[]>([]);
  const [plan, setPlan] = useState('');

  const load = () => api('/ai/history').then(setHistory).catch(() => setHistory([]));

  useEffect(() => {
    load();
    api('/ai/config').then(setConfig).catch(() => setConfig(null));
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

  const canDraw = !!config?.ai?.drawing;
  const canCode = !!config?.ai?.coding;
  const canGeneral = !!config?.ai?.general;
  const credits = config?.credits ?? 0;

  return (
    <div className="space-y-6">
      <div className="panel p-5">
        <div className="label">AI Hub</div>
        <div className="mt-2 text-2xl font-semibold">Tools for your learning genre</div>
        <div className="mt-1 text-sm text-slate-600">Your AI features are enabled by your organization.</div>
        {config && (
          <div className="mt-3 flex flex-wrap gap-2 text-xs">
            <span className="chip">Genre: {config.genre || 'general'}</span>
            <span className="chip">Credits: {credits}</span>
          </div>
        )}
      </div>

      <div className="grid lg:grid-cols-2 gap-6">
        <div className={`panel p-5 space-y-3 ${!canDraw ? 'opacity-60' : ''}`}>
          <div className="text-xl font-semibold">Drawing Reference (AI)</div>
          {!canDraw && <div className="text-sm text-slate-600">Ask your admin to enable Drawing AI for this organization.</div>}
          {canDraw && (
            <form className="space-y-3" onSubmit={onUpload}>
              <input className="input" type="file" name="image" accept="image/*" required />
              <select className="input" value={preset} onChange={(e) => setPreset(e.target.value)}>
                {presets.map(([k, v]) => <option key={k} value={k}>{v}</option>)}
              </select>
              <input className="input" placeholder="Optional prompt" value={prompt} onChange={(e) => setPrompt(e.target.value)} />
              <button className="btn-primary" type="submit" disabled={credits <= 0}>
                {credits > 0 ? 'Transform' : 'No credits'}
              </button>
              {credits <= 0 && <div className="text-xs text-slate-500">No drawing credits left.</div>}
            </form>
          )}
        </div>

        <div className={`panel p-5 space-y-3 ${!canCode ? 'opacity-60' : ''}`}>
          <div className="text-xl font-semibold">Coding Pair (AI)</div>
          {!canCode && <div className="text-sm text-slate-600">Ask your admin to enable Coding AI for this organization.</div>}
          {canCode && (
            <>
              <textarea className="input" placeholder="Ask DSA or coding help" value={codingPrompt} onChange={(e) => setCodingPrompt(e.target.value)} />
              <button
                className="btn-primary"
                onClick={async () => {
                  const res = await api('/ai/coding', { method: 'POST', body: JSON.stringify({ prompt: codingPrompt }) });
                  setCodingReply(res.reply);
                }}
              >
                Ask AI
              </button>
              {codingReply && <div className="list-card text-sm text-slate-600">{codingReply}</div>}
            </>
          )}
        </div>
      </div>

      <div className={`panel p-5 space-y-3 ${!canGeneral ? 'opacity-60' : ''}`}>
        <div className="text-xl font-semibold">General Study Tools</div>
        {!canGeneral && <div className="text-sm text-slate-600">Ask your admin to enable General AI for this organization.</div>}
        {canGeneral && (
          <div className="grid md:grid-cols-3 gap-3">
            <div className="list-card space-y-2">
              <div className="text-sm font-semibold">Flashcards</div>
              <input className="input" placeholder="Topic" value={topic} onChange={(e) => setTopic(e.target.value)} />
              <button
                className="btn-ghost"
                onClick={async () => {
                  const res = await api('/ai/general/flashcards', { method: 'POST', body: JSON.stringify({ topic }) });
                  setFlashcards(res.cards || []);
                }}
              >
                Generate
              </button>
              {flashcards.map((c, i) => (
                <div key={i} className="text-xs text-slate-600">Q: {c.q} A: {c.a}</div>
              ))}
            </div>

            <div className="list-card space-y-2">
              <div className="text-sm font-semibold">Quiz</div>
              <input className="input" placeholder="Topic" value={topic} onChange={(e) => setTopic(e.target.value)} />
              <button
                className="btn-ghost"
                onClick={async () => {
                  const res = await api('/ai/general/quiz', { method: 'POST', body: JSON.stringify({ topic }) });
                  setQuiz(res.questions || []);
                }}
              >
                Generate
              </button>
              {quiz.map((q, i) => (
                <div key={i} className="text-xs text-slate-600">{q.q}</div>
              ))}
            </div>

            <div className="list-card space-y-2">
              <div className="text-sm font-semibold">Study Plan</div>
              <textarea className="input" placeholder="Semester schedule" value={plan} onChange={(e) => setPlan(e.target.value)} />
              <button
                className="btn-ghost"
                onClick={async () => {
                  const res = await api('/ai/general/study-plan', { method: 'POST', body: JSON.stringify({ details: plan }) });
                  setPlan(res.plan || plan);
                }}
              >
                Generate
              </button>
              {plan && <div className="text-xs text-slate-600">{plan}</div>}
            </div>
          </div>
        )}
      </div>

      <div className="panel p-5">
        <div className="text-xl font-semibold">History</div>
        <div className="mt-4 grid md:grid-cols-3 gap-4">
          {history.map((h) => (
            <div key={h.id} className="card">
              <p className="text-xs text-slate-500">{h.preset}</p>
              <img src={`${process.env.NEXT_PUBLIC_API_URL}/media/file/${h.output_image_path}`} alt="output" className="rounded mt-2" />
            </div>
          ))}
        </div>
      </div>
    </div>
  );
}
