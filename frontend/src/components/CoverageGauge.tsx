import React from 'react';

interface CoverageGaugeProps {
  percentage: number;
  size?: number;
}

export const CoverageGauge: React.FC<CoverageGaugeProps> = ({ percentage, size = 160 }) => {
  const strokeWidth = 12;
  const radius = (size - strokeWidth) / 2;
  const circumference = 2 * Math.PI * radius;
  const strokeDashoffset = circumference - (percentage / 100) * circumference;

  const getColor = (pct: number) => {
    if (pct >= 75) return '#10b981'; // emerald-500
    if (pct >= 50) return '#14b8a6'; // teal-500
    if (pct >= 25) return '#f59e0b'; // amber-500
    return '#64748b'; // slate-500
  };

  const getLabel = (pct: number) => {
    if (pct >= 75) return 'High Public Evidence';
    if (pct >= 50) return 'Moderate Evidence';
    if (pct >= 25) return 'Limited Evidence';
    return 'Low Public Proof';
  };

  const color = getColor(percentage);

  return (
    <div className="flex flex-col items-center justify-center relative">
      <svg width={size} height={size} className="transform -rotate-90">
        {/* Background Track */}
        <circle
          cx={size / 2}
          cy={size / 2}
          r={radius}
          stroke="rgba(30, 41, 59, 0.8)"
          strokeWidth={strokeWidth}
          fill="transparent"
        />
        {/* Progress Arc */}
        <circle
          cx={size / 2}
          cy={size / 2}
          r={radius}
          stroke={color}
          strokeWidth={strokeWidth}
          strokeDasharray={circumference}
          strokeDashoffset={strokeDashoffset}
          strokeLinecap="round"
          fill="transparent"
          style={{ transition: 'stroke-dashoffset 1s ease-in-out' }}
        />
      </svg>

      {/* Center Label */}
      <div className="absolute inset-0 flex flex-col items-center justify-center text-center">
        <span className="text-3xl font-extrabold text-white tracking-tight">
          {percentage}%
        </span>
        <span className="text-[10px] uppercase font-bold tracking-wider text-slate-400 mt-0.5">
          Coverage
        </span>
      </div>

      <span 
        className="mt-2 text-xs font-semibold px-2.5 py-0.5 rounded-full border"
        style={{
          color: color,
          borderColor: `${color}40`,
          backgroundColor: `${color}15`
        }}
      >
        {getLabel(percentage)}
      </span>
    </div>
  );
};
