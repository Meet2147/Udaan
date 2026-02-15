'use client';

import React from 'react';

type DonutProps = {
  value: number;
  size?: number;
  stroke?: number;
  label?: string;
};

export function Donut({ value, size = 120, stroke = 12, label }: DonutProps) {
  const radius = (size - stroke) / 2;
  const circumference = 2 * Math.PI * radius;
  const clamped = Math.max(0, Math.min(100, value));
  const offset = circumference - (clamped / 100) * circumference;

  return (
    <div className="flex items-center gap-4">
      <svg width={size} height={size} className="drop-shadow-sm">
        <circle
          cx={size / 2}
          cy={size / 2}
          r={radius}
          stroke="rgba(0,0,0,0.08)"
          strokeWidth={stroke}
          fill="transparent"
        />
        <circle
          cx={size / 2}
          cy={size / 2}
          r={radius}
          stroke="#1a5cff"
          strokeWidth={stroke}
          fill="transparent"
          strokeLinecap="round"
          strokeDasharray={circumference}
          strokeDashoffset={offset}
          transform={`rotate(-90 ${size / 2} ${size / 2})`}
        />
        <text x="50%" y="50%" dominantBaseline="middle" textAnchor="middle" className="fill-slate-800 text-lg font-semibold">
          {clamped}%
        </text>
      </svg>
      <div>
        {label && <div className="text-sm font-semibold">{label}</div>}
        <div className="text-xs text-slate-500">Completion rate</div>
      </div>
    </div>
  );
}

type BarDatum = { label: string; value: number };

type BarsProps = {
  data: BarDatum[];
  max?: number;
  label?: string;
};

export function Bars({ data, max, label }: BarsProps) {
  const maxValue = max ?? Math.max(1, ...data.map((d) => d.value));
  return (
    <div className="space-y-3">
      {label && <div className="text-sm font-semibold">{label}</div>}
      {data.map((d) => (
        <div key={d.label} className="space-y-1">
          <div className="flex justify-between text-xs text-slate-600">
            <span>{d.label}</span>
            <span>{d.value}%</span>
          </div>
          <div className="h-2 rounded-full bg-black/10 overflow-hidden">
            <div
              className="h-2 rounded-full bg-amber-400"
              style={{ width: `${Math.min(100, Math.round((d.value / maxValue) * 100))}%` }}
            />
          </div>
        </div>
      ))}
    </div>
  );
}

export function Sparkline({ points }: { points: number[] }) {
  const max = Math.max(1, ...points);
  const width = 200;
  const height = 60;
  const step = width / (points.length - 1 || 1);
  const path = points
    .map((p, i) => {
      const x = i * step;
      const y = height - (p / max) * height;
      return `${i === 0 ? 'M' : 'L'}${x},${y}`;
    })
    .join(' ');

  return (
    <svg width={width} height={height} className="text-blue-600">
      <path d={path} fill="none" stroke="currentColor" strokeWidth="3" strokeLinecap="round" />
    </svg>
  );
}
