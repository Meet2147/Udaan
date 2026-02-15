'use client';

import Hls from 'hls.js';
import { useEffect, useRef, useState } from 'react';
import { api } from '@/lib/api';
import { authHeader } from '@/lib/auth';
import WatermarkOverlay from './WatermarkOverlay';

type Props = {
  lectureId: number;
  onProgress?: (current: number, duration: number) => void;
};

export default function VideoPlayer({ lectureId, onProgress }: Props) {
  const videoRef = useRef<HTMLVideoElement>(null);
  const [url, setUrl] = useState('');
  const [watermark, setWatermark] = useState('');
  const [error, setError] = useState('');

  useEffect(() => {
    let interval: ReturnType<typeof setInterval>;

    async function load() {
      setError('');
      const res = await fetch(`${process.env.NEXT_PUBLIC_API_URL}/lectures/${lectureId}/play`, {
        headers: { ...authHeader() },
      });
      if (!res.ok) {
        const txt = await res.text();
        setError(txt || 'Unable to load lecture');
        return;
      }
      const data = await res.json();
      setUrl(data.signed_url);
      setWatermark(`${data.watermark_text} | Course ${data.watermark_course}`);

      interval = setInterval(() => {
        const d = new Date().toISOString();
        setWatermark((prev) => `${prev.split('|')[0].trim()} | ${d}`);
      }, 5000);
    }

    load();

    return () => {
      if (interval) clearInterval(interval);
    };
  }, [lectureId]);

  useEffect(() => {
    if (!url || !videoRef.current) return;

    if (Hls.isSupported() && url.endsWith('.m3u8')) {
      const hls = new Hls();
      hls.loadSource(url);
      hls.attachMedia(videoRef.current);
      return () => hls.destroy();
    }

    videoRef.current.src = url;
  }, [url]);

  useEffect(() => {
    const onVisibility = () => {
      if (document.hidden && videoRef.current) {
        videoRef.current.pause();
      }
    };

    document.addEventListener('visibilitychange', onVisibility);
    return () => document.removeEventListener('visibilitychange', onVisibility);
  }, []);

  const onTimeUpdate = async () => {
    if (!videoRef.current) return;
    const seconds = Math.floor(videoRef.current.currentTime);
    const duration = Math.floor(videoRef.current.duration || 0);
    if (onProgress && duration > 0) {
      onProgress(seconds, duration);
    }
    if (seconds % 10 === 0) {
      await api(`/lectures/${lectureId}/progress`, {
        method: 'POST',
        body: JSON.stringify({ watched_seconds: seconds }),
      }).catch(() => null);
    }
  };

  return (
    <div
      className="relative"
      onContextMenu={(e) => e.preventDefault()}
      onKeyDown={(e) => {
        if (e.key === 'F12' || (e.ctrlKey && e.shiftKey && ['I', 'J', 'C'].includes(e.key))) e.preventDefault();
      }}
    >
      {error ? (
        <div className="card border border-red-200 bg-red-50 text-red-700">
          {error.includes('Not enrolled') ? 'Not enrolled or not approved yet.' : error}
        </div>
      ) : (
        <>
          <video
            ref={videoRef}
            controls
            className="w-full rounded-lg bg-black"
            onTimeUpdate={onTimeUpdate}
          />
          {watermark && <WatermarkOverlay text={watermark} />}
        </>
      )}
    </div>
  );
}
