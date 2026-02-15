'use client';

import { use, useState } from 'react';
import VideoPlayer from '@/components/VideoPlayer';
import { api } from '@/lib/api';

export default function LecturePage({ params }: { params: Promise<{ id: string }> }) {
  const { id } = use(params);
  const lectureId = Number(id);
  const [isCompleteReady, setIsCompleteReady] = useState(false);

  return (
    <div className="space-y-4">
      <h1 className="text-2xl font-semibold">Lecture Player</h1>
      <VideoPlayer
        lectureId={lectureId}
        onProgress={(current, duration) => {
          if (duration > 0 && current >= duration) {
            setIsCompleteReady(true);
          }
        }}
      />
      {isCompleteReady && (
        <button
          className="btn-primary"
          onClick={async () => {
            await api(`/lectures/${lectureId}/complete`, { method: 'POST' });
            alert('Marked complete');
          }}
        >
          Mark Complete
        </button>
      )}
    </div>
  );
}
