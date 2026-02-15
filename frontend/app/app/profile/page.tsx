'use client';

import { useEffect, useState } from 'react';
import { fetchMe } from '@/lib/auth';

export default function ProfilePage() {
  const [me, setMe] = useState<any>(null);

  useEffect(() => {
    fetchMe().then(setMe);
  }, []);

  if (!me) return <p>Loading...</p>;

  return (
    <div className="card space-y-1">
      <h1 className="text-xl font-semibold">Profile</h1>
      <p>Name: {me.full_name}</p>
      <p>Email: {me.email}</p>
      <p>Phone: {me.phone}</p>
      <p>Grade: {me.grade_or_standard}</p>
    </div>
  );
}
