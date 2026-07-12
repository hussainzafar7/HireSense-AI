import React from 'react';
import { RadialBarChart, RadialBar, PolarAngleAxis } from 'recharts';

export default function ScoreGauge({ score = 0, size = 200, label = 'Score', color = '#6366f1' }) {
  const data = [{ name: label, value: score, fill: color }];
  const getTextColor = score >= 80 ? '#22c55e' : score >= 60 ? '#eab308' : '#ef4444';

  return (
    <div style={{ textAlign: 'center' }}>
      <RadialBarChart width={size} height={size} data={data} cx="50%" cy="50%" innerRadius="60%" outerRadius="85%" barSize={12} startAngle={180} endAngle={0}>
        <PolarAngleAxis type="number" domain={[0, 100]} angleAxisId={0} tick={false} />
        <RadialBar dataKey="value" cornerRadius={6} background={{ fill: '#1e293b' }} />
        <text x={size / 2} y={size / 2 - 8} textAnchor="middle" fontSize={size * 0.22} fontWeight={700} fill={getTextColor}>{score.toFixed(0)}%</text>
        <text x={size / 2} y={size / 2 + 22} textAnchor="middle" fontSize={14} fill="#94a3b8">{label}</text>
      </RadialBarChart>
    </div>
  );
}
