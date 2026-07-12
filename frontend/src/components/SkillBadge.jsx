import React from 'react';

const colors = ['#6366f1', '#8b5cf6', '#a855f7', '#06b6d4', '#10b981', '#f59e0b', '#ef4444', '#ec4899'];

export default function SkillBadge({ skill, matched = true }) {
  const color = colors[skill.length % colors.length];
  return (
    <span style={{
      display: 'inline-block', padding: '4px 12px', borderRadius: '20px',
      fontSize: '0.8rem', fontWeight: 500,
      background: matched ? `${color}22` : '#334155',
      color: matched ? color : '#94a3b8',
      border: `1px solid ${matched ? color : '#475569'}`,
      margin: '3px',
    }}>
      {skill}
    </span>
  );
}
