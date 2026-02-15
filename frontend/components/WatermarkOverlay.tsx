'use client';

type Props = {
  text: string;
};

export default function WatermarkOverlay({ text }: Props) {
  const rows = new Array(4).fill(0);
  return (
    <div className="pointer-events-none absolute inset-0 overflow-hidden">
      {rows.map((_, i) => (
        <div
          key={i}
          className="absolute text-white/35 text-xs font-semibold whitespace-nowrap"
          style={{
            top: `${10 + i * 22}%`,
            left: '-20%',
            width: '140%',
            transform: 'rotate(-16deg)',
            animation: `slide ${18 + i * 2}s linear infinite`,
          }}
        >
          {`${text} • ${text} • ${text} • ${text} • ${text}`}
        </div>
      ))}
      <style jsx>{`
        @keyframes slide {
          from { transform: translateX(0) rotate(-16deg); }
          to { transform: translateX(20%) rotate(-16deg); }
        }
      `}</style>
    </div>
  );
}
