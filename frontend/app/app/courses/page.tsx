'use client';

import Link from 'next/link';
import { useEffect, useState } from 'react';
import { api } from '@/lib/api';
import { loadRazorpay } from '@/lib/razorpay';

export default function CoursesPage() {
  const [courses, setCourses] = useState<any[]>([]);

  useEffect(() => {
    api('/courses').then(setCourses).catch(() => setCourses([]));
  }, []);

  const enroll = async (course: any) => {
    const res = await api(`/courses/${course.id}/enroll`, { method: 'POST' });
    if (res.payment) {
      const ok = await loadRazorpay();
      if (!ok) {
        alert('Unable to load payment gateway.');
        return;
      }
      const options = {
        key: res.payment.key_id,
        amount: res.payment.amount,
        currency: res.payment.currency,
        order_id: res.payment.order_id,
        name: res.payment.name,
        description: res.payment.description,
        handler: async (response: any) => {
          await api('/payments/verify', {
            method: 'POST',
            body: JSON.stringify({
              order_id: response.razorpay_order_id,
              payment_id: response.razorpay_payment_id,
              signature: response.razorpay_signature,
            }),
          });
          alert('Payment successful. Enrollment activated.');
        },
        theme: { color: '#111827' },
      };
      const rz = new (window as any).Razorpay(options);
      rz.open();
      return;
    }
    alert('Enrollment requested. Admin approval may be required.');
  };

  return (
    <div className="space-y-4">
      <h1 className="text-2xl font-semibold">Courses</h1>
      <div className="grid md:grid-cols-2 gap-4">
        {courses.map((c) => (
          <div key={c.id} className="card space-y-2">
            <div className="text-xs uppercase text-slate-500">{c.level}</div>
            <h3 className="font-semibold">{c.title}</h3>
            <p className="text-sm text-slate-700">{c.description}</p>
            <div className="text-sm text-slate-500">Price: {c.price_inr ? `₹${c.price_inr}` : 'Free'}</div>
            <div className="flex gap-2">
              <button className="btn-primary" onClick={() => enroll(c)}>Enroll</button>
              <Link href={`/app/courses/${c.id}`} className="btn-ghost">View</Link>
            </div>
          </div>
        ))}
      </div>
    </div>
  );
}
