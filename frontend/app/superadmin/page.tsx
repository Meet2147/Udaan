'use client';

import { FormEvent, useEffect, useState } from 'react';
import { api } from '@/lib/api';
import { fetchMe } from '@/lib/auth';

export default function SuperAdminPage() {
  const [ok, setOk] = useState(false);
  const [orgs, setOrgs] = useState<any[]>([]);
  const [orgName, setOrgName] = useState('');
  const [plan, setPlan] = useState('launch');
  const [genre, setGenre] = useState('general');
  const [features, setFeatures] = useState({ drawing: false, coding: false, general: true });
  const [editOrgId, setEditOrgId] = useState('');
  const [editGenre, setEditGenre] = useState('general');
  const [editFeatures, setEditFeatures] = useState({ drawing: false, coding: false, general: true });
  const [adminForm, setAdminForm] = useState({
    orgId: '',
    full_name: '',
    email: '',
    phone: '',
    password: '',
  });
  const [creditForm, setCreditForm] = useState({
    email: '',
    amount: 5,
    reason: 'manual_grant',
  });
  const [message, setMessage] = useState('');
  const [paymentLink, setPaymentLink] = useState('');

  const load = () => api('/superadmin/orgs').then(setOrgs).catch(() => setOrgs([]));

  useEffect(() => {
    fetchMe().then((u) => {
      if (!u || u.role !== 'super_admin') {
        window.location.href = '/login';
      } else {
        setOk(true);
        load();
      }
    });
  }, []);

  useEffect(() => {
    if (!editOrgId && orgs.length) {
      setEditOrgId(String(orgs[0].id));
      return;
    }
    const org = orgs.find((o) => String(o.id) === String(editOrgId));
    if (org) {
      setEditGenre(org.genre || 'general');
      setEditFeatures({
        drawing: !!org.ai_drawing_enabled,
        coding: !!org.ai_coding_enabled,
        general: org.ai_general_enabled !== false,
      });
    }
  }, [editOrgId, orgs]);

  if (!ok) return <p>Loading...</p>;

  const createOrg = async (e: FormEvent) => {
    e.preventDefault();
    setMessage('');
    try {
      await api('/superadmin/orgs', {
        method: 'POST',
        body: JSON.stringify({
          name: orgName,
          plan,
          genre,
          ai_drawing_enabled: features.drawing,
          ai_coding_enabled: features.coding,
          ai_general_enabled: features.general,
        }),
      });
      setOrgName('');
      load();
      setMessage('Organization created.');
    } catch (err: any) {
      setMessage(err.message || 'Failed to create org');
    }
  };

  const createAdmin = async (e: FormEvent) => {
    e.preventDefault();
    setMessage('');
    setPaymentLink('');
    try {
      const res = await api(`/superadmin/orgs/${adminForm.orgId}/admins`, {
        method: 'POST',
        body: JSON.stringify({
          full_name: adminForm.full_name,
          email: adminForm.email,
          phone: adminForm.phone,
          password: adminForm.password,
          grade_or_standard: 'NA',
        }),
      });
      if (res.payment_link_url) setPaymentLink(res.payment_link_url);
      setAdminForm({ orgId: '', full_name: '', email: '', phone: '', password: '' });
      setMessage('Admin created.');
    } catch (err: any) {
      setMessage(err.message || 'Failed to create admin');
    }
  };

  const updateOrg = async (e: FormEvent) => {
    e.preventDefault();
    if (!editOrgId) return;
    setMessage('');
    try {
      await api(`/superadmin/orgs/${editOrgId}`, {
        method: 'PUT',
        body: JSON.stringify({
          genre: editGenre,
          ai_drawing_enabled: editFeatures.drawing,
          ai_coding_enabled: editFeatures.coding,
          ai_general_enabled: editFeatures.general,
        }),
      });
      load();
      setMessage('Organization updated.');
    } catch (err: any) {
      setMessage(err.message || 'Failed to update org');
    }
  };

  const addCredits = async (e: FormEvent) => {
    e.preventDefault();
    setMessage('');
    try {
      await api('/superadmin/credits', {
        method: 'POST',
        body: JSON.stringify({
          email: creditForm.email,
          amount: Number(creditForm.amount),
          reason: creditForm.reason || 'manual_grant',
        }),
      });
      setCreditForm({ email: '', amount: 5, reason: 'manual_grant' });
      setMessage('Credits updated.');
    } catch (err: any) {
      setMessage(err.message || 'Failed to update credits');
    }
  };

  return (
    <div className="space-y-6">
      <div className="panel p-5">
        <div className="label">SuperAdmin</div>
        <div className="mt-2 text-2xl font-semibold">Organization Management</div>
        <div className="mt-2 text-sm text-slate-600">Create tutor organizations and manage admin seats by plan.</div>
        {message && <div className="mt-3 text-sm text-blue-700">{message}</div>}
        {paymentLink && (
          <div className="mt-2 text-sm text-slate-600">
            Payment link: <a className="text-blue-600 underline" href={paymentLink} target="_blank" rel="noreferrer">{paymentLink}</a>
          </div>
        )}
      </div>

      <div className="grid lg:grid-cols-2 gap-6">
        <form className="panel p-5 space-y-3" onSubmit={createOrg}>
          <div className="text-lg font-semibold">Create Organization</div>
          <input className="input" placeholder="Organization name" value={orgName} onChange={(e) => setOrgName(e.target.value)} required />
          <select className="input" value={plan} onChange={(e) => setPlan(e.target.value)}>
            <option value="launch">Launch (1 admin)</option>
            <option value="rise">Rise (10 admins)</option>
            <option value="scale">Scale (25 admins)</option>
          </select>
          <select className="input" value={genre} onChange={(e) => setGenre(e.target.value)}>
            <option value="drawing">Drawing</option>
            <option value="coding">Coding</option>
            <option value="general">General</option>
          </select>
          <div className="grid grid-cols-3 gap-2 text-xs">
            <label className="list-card flex items-center gap-2">
              <input type="checkbox" checked={features.drawing} onChange={(e) => setFeatures({ ...features, drawing: e.target.checked })} />
              Drawing AI
            </label>
            <label className="list-card flex items-center gap-2">
              <input type="checkbox" checked={features.coding} onChange={(e) => setFeatures({ ...features, coding: e.target.checked })} />
              Coding AI
            </label>
            <label className="list-card flex items-center gap-2">
              <input type="checkbox" checked={features.general} onChange={(e) => setFeatures({ ...features, general: e.target.checked })} />
              General AI
            </label>
          </div>
          <button className="btn-primary">Create Org</button>
        </form>

        <form className="panel p-5 space-y-3" onSubmit={createAdmin}>
          <div className="text-lg font-semibold">Create Org Admin</div>
          <select className="input" value={adminForm.orgId} onChange={(e) => setAdminForm({ ...adminForm, orgId: e.target.value })} required>
            <option value="">Select organization</option>
            {orgs.map((o) => (
              <option key={o.id} value={o.id}>{o.name}</option>
            ))}
          </select>
          <input className="input" placeholder="Full name" value={adminForm.full_name} onChange={(e) => setAdminForm({ ...adminForm, full_name: e.target.value })} required />
          <input className="input" placeholder="Email" value={adminForm.email} onChange={(e) => setAdminForm({ ...adminForm, email: e.target.value })} required />
          <input className="input" placeholder="Phone" value={adminForm.phone} onChange={(e) => setAdminForm({ ...adminForm, phone: e.target.value })} required />
          <input className="input" type="password" placeholder="Password" value={adminForm.password} onChange={(e) => setAdminForm({ ...adminForm, password: e.target.value })} required />
          <button className="btn-primary">Create Admin</button>
        </form>
      </div>

      <div className="grid lg:grid-cols-2 gap-6">
        <form className="panel p-5 space-y-3" onSubmit={updateOrg}>
          <div className="text-lg font-semibold">Update Org Features</div>
          <select className="input" value={editOrgId} onChange={(e) => setEditOrgId(e.target.value)} required>
            <option value="">Select organization</option>
            {orgs.map((o) => (
              <option key={o.id} value={o.id}>{o.name}</option>
            ))}
          </select>
          <select className="input" value={editGenre} onChange={(e) => setEditGenre(e.target.value)}>
            <option value="drawing">Drawing</option>
            <option value="coding">Coding</option>
            <option value="general">General</option>
          </select>
          <div className="grid grid-cols-3 gap-2 text-xs">
            <label className="list-card flex items-center gap-2">
              <input type="checkbox" checked={editFeatures.drawing} onChange={(e) => setEditFeatures({ ...editFeatures, drawing: e.target.checked })} />
              Drawing AI
            </label>
            <label className="list-card flex items-center gap-2">
              <input type="checkbox" checked={editFeatures.coding} onChange={(e) => setEditFeatures({ ...editFeatures, coding: e.target.checked })} />
              Coding AI
            </label>
            <label className="list-card flex items-center gap-2">
              <input type="checkbox" checked={editFeatures.general} onChange={(e) => setEditFeatures({ ...editFeatures, general: e.target.checked })} />
              General AI
            </label>
          </div>
          <button className="btn-primary">Save Features</button>
        </form>

        <form className="panel p-5 space-y-3" onSubmit={addCredits}>
          <div className="text-lg font-semibold">Grant Drawing Credits</div>
          <input className="input" placeholder="Student email" value={creditForm.email} onChange={(e) => setCreditForm({ ...creditForm, email: e.target.value })} required />
          <input className="input" type="number" min={-999} max={999} placeholder="Amount" value={creditForm.amount} onChange={(e) => setCreditForm({ ...creditForm, amount: Number(e.target.value) })} required />
          <input className="input" placeholder="Reason (optional)" value={creditForm.reason} onChange={(e) => setCreditForm({ ...creditForm, reason: e.target.value })} />
          <button className="btn-primary">Apply Credits</button>
        </form>
      </div>

      <div className="panel p-5 space-y-3">
        <div className="flex items-center justify-between">
          <div className="text-xl font-semibold">Organizations</div>
          <div className="chip">{orgs.length} total</div>
        </div>
        <div className="grid md:grid-cols-2 gap-4">
          {orgs.map((o) => (
            <div key={o.id} className="list-card">
              <div className="text-sm text-slate-500">Org</div>
              <div className="text-lg font-semibold">{o.name}</div>
              <div className="text-xs text-slate-500">ID: {o.id}</div>
              <div className="mt-2 text-xs text-slate-500">Genre: {o.genre || 'general'}</div>
              <div className="mt-2 flex flex-wrap gap-2 text-xs">
                {o.ai_drawing_enabled && <span className="chip">Drawing AI</span>}
                {o.ai_coding_enabled && <span className="chip">Coding AI</span>}
                {o.ai_general_enabled && <span className="chip">General AI</span>}
              </div>
            </div>
          ))}
          {orgs.length === 0 && <div className="list-card text-sm text-slate-600">No organizations yet.</div>}
        </div>
      </div>
    </div>
  );
}
