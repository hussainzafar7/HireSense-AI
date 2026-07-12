import React from 'react';

const styles = {
  container: { display: 'flex', flexDirection: 'column', alignItems: 'center', gap: '16px' },
  avatarWrap: { position: 'relative', width: 140, height: 140 },
  glowRing: {
    position: 'absolute', inset: -8, borderRadius: '50%',
    transition: 'all 0.5s ease', opacity: 0.6,
  },
  avatar: {
    width: '100%', height: '100%', borderRadius: '50%',
    background: 'linear-gradient(135deg, #6366f1, #8b5cf6)',
    display: 'flex', alignItems: 'center', justifyContent: 'center',
    fontSize: '3rem', fontWeight: 700, color: '#fff',
    position: 'relative', zIndex: 1,
  },
  bars: { display: 'flex', gap: '4px', alignItems: 'center', height: 30 },
  bar: { width: 4, borderRadius: 2, background: '#6366f1' },
};

export default function AvatarAnimated({ state = 'idle' }) {
  const isSpeaking = state === 'speaking';
  const isListening = state === 'listening';

  const ringColor = isSpeaking ? '#6366f1' : isListening ? '#22c55e' : '#334155';
  const ringAnim = isSpeaking || isListening ? { animation: 'pulse 1.5s ease-in-out infinite' } : {};

  return (
    <div style={styles.container}>
      <div style={styles.avatarWrap}>
        <div style={{ ...styles.glowRing, background: ringColor, borderRadius: '50%', ...ringAnim }} />
        <div style={styles.avatar}>
          <span>AI</span>
        </div>
      </div>
      <div style={styles.bars}>
        {[1,2,3,4,5,6,7].map(i => (
          <div key={i} style={{
            ...styles.bar,
            height: isSpeaking ? 12 + Math.sin(i * 1.2) * 10 : 4,
            animation: isSpeaking ? `wave ${0.6 + i * 0.1}s ease-in-out infinite` : 'none',
          }} />
        ))}
      </div>
      <div style={{ fontSize: '0.85rem', color: ringColor, fontWeight: 600 }}>
        {isSpeaking ? 'Speaking...' : isListening ? 'Listening...' : 'Ready'}
      </div>
      <style>{`
        @keyframes pulse {
          0%, 100% { transform: scale(1); opacity: 0.6; }
          50% { transform: scale(1.1); opacity: 0.3; }
        }
        @keyframes wave {
          0%, 100% { transform: scaleY(0.5); }
          50% { transform: scaleY(1.5); }
        }
      `}</style>
    </div>
  );
}
