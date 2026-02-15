'use client';

import { FormEvent, useState } from 'react';

export default function SignupPage() {
  const [form, setForm] = useState({
    full_name: '',
    email: '',
    phone: '',
    grade_or_standard: '',
    password: '',
  });
  const [msg, setMsg] = useState('');

  const onSubmit = async (e: FormEvent) => {
    e.preventDefault();
    setMsg('');
    const res = await fetch(`${process.env.NEXT_PUBLIC_API_URL}/auth/signup`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(form),
    });
    setMsg(res.ok ? 'Signup successful. Login now.' : 'Signup failed.');
  };

  return (
    <div className="max-w-5xl mx-auto grid lg:grid-cols-[1.1fr_0.9fr] gap-6 items-stretch">
      <div className="panel p-6">
        <div className="label">Student Onboarding</div>
        <h1 className="mt-2 text-3xl font-semibold">Start learning with Udaan</h1>
        <p className="mt-2 text-sm text-slate-600">
          Join structured drawing courses and track your progress with certificates.
        </p>
        <div className="mt-6 grid md:grid-cols-2 gap-4">
          <div className="list-card">
            <div className="text-xs text-slate-500">Elementary</div>
            <div className="mt-1 text-lg font-semibold">Foundations</div>
          </div>
          <div className="list-card">
            <div className="text-xs text-slate-500">Intermediate</div>
            <div className="mt-1 text-lg font-semibold">Depth + Value</div>
          </div>
        </div>
      </div>

      <form className="panel p-6 space-y-3" onSubmit={onSubmit}>
        <div className="text-xl font-semibold">Student Signup</div>
        <input className="input" placeholder="Full Name" required value={form.full_name} onChange={(e) => setForm({ ...form, full_name: e.target.value })} />
        <input className="input" placeholder="Email" required value={form.email} onChange={(e) => setForm({ ...form, email: e.target.value })} />
        <input className="input" placeholder="Phone" required value={form.phone} onChange={(e) => setForm({ ...form, phone: e.target.value })} />
        <input className="input" placeholder="Grade / Standard" required value={form.grade_or_standard} onChange={(e) => setForm({ ...form, grade_or_standard: e.target.value })} />
        <input className="input" type="password" placeholder="Password" required value={form.password} onChange={(e) => setForm({ ...form, password: e.target.value })} />
        <button className="btn-primary w-full" type="submit">Create Account</button>
        {msg && <p className="text-sm">{msg}</p>}
      </form>
    </div>
  );
}
