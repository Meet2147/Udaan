'use client';

import { FormEvent, useEffect, useState } from 'react';
import { api } from '@/lib/api';
import { fetchMe } from '@/lib/auth';

export default function SuperAdminPage() {
  const [ok, setOk] = useState(false);
  const [orgs, setOrgs] = useState<any[]>([]);
  const [orgName, setOrgName] = useState('');
  const [plan, setPlan] = useState('launch');
  const [adminForm, setAdminForm] = useState({
    orgId: '',
    full_name: '',
    email: '',
    phone: '',
    password: '',
  });
  const [message, setMessage] = useState('');

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

  if (!ok) return <p>Loading...</p>;

  const createOrg = async (e: FormEvent) => {
    e.preventDefault();
    setMessage('');
    try {
      await api('/superadmin/orgs', {
        method: 'POST',
        body: JSON.stringify({ name: orgName, plan }),
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
    try {
      await api(`/superadmin/orgs/${adminForm.orgId}/admins`, {
        method: 'POST',
        body: JSON.stringify({
          full_name: adminForm.full_name,
          email: adminForm.email,
          phone: adminForm.phone,
          password: adminForm.password,
          grade_or_standard: 'NA',
        }),
      });
      setAdminForm({ orgId: '', full_name: '', email: '', phone: '', password: '' });
      setMessage('Admin created.');
    } catch (err: any) {
      setMessage(err.message || 'Failed to create admin');
    }
  };

  return (
    <div className="space-y-6">
      <div className="panel p-5">
        <div className="label">SuperAdmin</div>
        <div className="mt-2 text-2xl font-semibold">Organization Management</div>
        <div className="mt-2 text-sm text-slate-600">Create tutor organizations and manage admin seats by plan.</div>
        {message && <div className="mt-3 text-sm text-blue-700">{message}</div>}
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
            </div>
          ))}
          {orgs.length === 0 && <div className="list-card text-sm text-slate-600">No organizations yet.</div>}
        </div>
      </div>
    </div>
  );
}
