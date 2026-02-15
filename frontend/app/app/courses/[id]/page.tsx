'use client';

import Link from 'next/link';
import { useEffect, useState, use } from 'react';
import { api } from '@/lib/api';
import { loadRazorpay } from '@/lib/razorpay';

export default function CourseDetail({ params }: { params: Promise<{ id: string }> }) {
  const { id } = use(params);
  const [data, setData] = useState<any>(null);

  useEffect(() => {
    api(`/courses/${id}`).then(setData).catch(() => setData(null));
  }, [id]);

  if (!data) return <p>Loading...</p>;

  const enroll = async () => {
    const res = await api(`/courses/${id}/enroll`, { method: 'POST' });
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
          const updated = await api(`/courses/${id}`);
          setData(updated);
          alert('Payment successful. Enrollment activated.');
        },
        theme: { color: '#111827' },
      };
      const rz = new (window as any).Razorpay(options);
      rz.open();
      return;
    }
    const updated = await api(`/courses/${id}`);
    setData(updated);
    alert('Enrollment requested. Admin approval may be required.');
  };

  return (
    <div className="space-y-4">
      <h1 className="text-2xl font-semibold">{data.course.title}</h1>
      <p>{data.course.description}</p>
      <p className="text-sm">Price: {data.course.price_inr ? `₹${data.course.price_inr}` : 'Free'}</p>
      <p className="text-sm">Enrollment: {data.enrolled ? 'Approved' : data.enrollment_status || 'Not enrolled'}</p>
      {!data.enrolled && (
        <button className="btn-primary" onClick={enroll}>Enroll Now</button>
      )}
      <div className="space-y-2">
        {data.lectures.map((l: any) => (
          <div key={l.id} className="card flex items-center justify-between">
            <div>
              <p className="font-medium">{l.order_index}. {l.title}</p>
              <p className="text-xs text-slate-600">{l.duration_sec}s</p>
            </div>
            <Link href={`/app/lectures/${l.id}`} className="btn-primary">Open</Link>
          </div>
        ))}
      </div>
    </div>
  );
}
