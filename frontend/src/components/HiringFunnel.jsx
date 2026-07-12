import React from 'react';
import { BarChart, Bar, XAxis, YAxis, Tooltip, ResponsiveContainer, LabelList } from 'recharts';

export default function HiringFunnel({ data }) {
  if (!data) return null;
  const chartData = [
    { name: 'Applied', value: data.applied || 0, fill: '#6366f1' },
    { name: 'Interviewed', value: data.interviewed || 0, fill: '#8b5cf6' },
    { name: 'Score ≥60', value: data.score_ge_60 || 0, fill: '#a855f7' },
    { name: 'Score ≥80', value: data.score_ge_80 || 0, fill: '#22c55e' },
  ];

  return (
    <div style={{ background: '#1e293b', borderRadius: '12px', padding: '24px', border: '1px solid #334155' }}>
      <h3 style={{ marginBottom: 20, color: '#e2e8f0', fontSize: '1rem' }}>Hiring Funnel</h3>
      <ResponsiveContainer width="100%" height={300}>
        <BarChart data={chartData} layout="vertical" margin={{ left: 100 }}>
          <XAxis type="number" tick={{ fill: '#64748b', fontSize: 12 }} />
          <YAxis type="category" dataKey="name" tick={{ fill: '#cbd5e1', fontSize: 12 }} />
          <Tooltip contentStyle={{ background: '#1e293b', border: '1px solid #334155', borderRadius: 8, color: '#e2e8f0' }} />
          <Bar dataKey="value" radius={[0, 6, 6, 0]} barSize={24}>
            <LabelList dataKey="value" position="right" fill="#94a3b8" fontSize={12} fontWeight={600} />
          </Bar>
        </BarChart>
      </ResponsiveContainer>
    </div>
  );
}
