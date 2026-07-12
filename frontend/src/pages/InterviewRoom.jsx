import React, { useState, useEffect, useRef, useCallback } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import interviewService from '../services/interviewService';
import AvatarAnimated from '../components/AvatarAnimated';
import ScoreGauge from '../components/ScoreGauge';

const TIMER_DURATION = 120;

export default function InterviewRoom() {
  const { id } = useParams();
  const navigate = useNavigate();
  const [interview, setInterview] = useState(null);
  const [currentQ, setCurrentQ] = useState(null);
  const [answer, setAnswer] = useState('');
  const [liveTranscript, setLiveTranscript] = useState('');
  const [mode, setMode] = useState('text'); // 'text' or 'voice'
  const [aiState, setAiState] = useState('idle');
  const [listening, setListening] = useState(false);
  const [answered, setAnswered] = useState(0);
  const [total, setTotal] = useState(10);
  const [skipped, setSkipped] = useState(0);
  const [evaluation, setEvaluation] = useState(null);
  const [completed, setCompleted] = useState(false);
  const [finalScore, setFinalScore] = useState(null);
  const [report, setReport] = useState(null);
  const [error, setError] = useState('');
  const [timer, setTimer] = useState(TIMER_DURATION);
  const [timerActive, setTimerActive] = useState(false);
  const [showEval, setShowEval] = useState(false);
  const [webcamStream, setWebcamStream] = useState(null);
  const [webcamError, setWebcamError] = useState(false);

  const recognitionRef = useRef(null);
  const timerRef = useRef(null);
  const videoRef = useRef(null);

  useEffect(() => {
    // Try webcam
    if (navigator.mediaDevices?.getUserMedia) {
      navigator.mediaDevices.getUserMedia({ video: true, audio: false })
        .then(stream => { setWebcamStream(stream); if (videoRef.current) videoRef.current.srcObject = stream; })
        .catch(() => setWebcamError(true));
    } else { setWebcamError(true); }

    // Load interview first question
    loadState();
    return () => {
      if (recognitionRef.current) recognitionRef.current.abort();
      if (timerRef.current) clearInterval(timerRef.current);
      if (webcamStream) webcamStream.getTracks().forEach(t => t.stop());
    };
  }, [id]);

  const loadState = async () => {
    try {
      const state = await interviewService.getState(id);
      setAnswered(state.answered || 0);
      setTotal(state.total || 10);
      setSkipped(state.skipped || 0);
      if (state.status === 'completed') {
        setCompleted(true);
        const r = await interviewService.getReport(id);
        setReport(r);
        setFinalScore({ overall_score: r.overall_score, technical_score: r.technical_score, communication_score: r.communication_score, confidence_score: r.confidence_score, recommendation: r.recommendation });
        return;
      }
    } catch {}
    // Start interview if no state
    try {
      const res = await interviewService.start(null, null);
      setInterview(res);
      setCurrentQ(res.current_question);
      setTotal(res.total_questions);
    } catch (err) { setError('Failed to start interview'); }
  };

  const startTimer = () => {
    setTimer(TIMER_DURATION);
    setTimerActive(true);
    if (timerRef.current) clearInterval(timerRef.current);
    timerRef.current = setInterval(() => {
      setTimer(prev => {
        if (prev <= 1) { clearInterval(timerRef.current); setTimerActive(false); return 0; }
        return prev - 1;
      });
    }, 1000);
  };

  const stopTimer = () => {
    if (timerRef.current) clearInterval(timerRef.current);
    setTimerActive(false);
  };

  const speakQuestion = useCallback((text) => {
    if (!window.speechSynthesis) return;
    window.speechSynthesis.cancel();
    const utt = new SpeechSynthesisUtterance(text);
    const voices = window.speechSynthesis.getVoices();
    const female = voices.find(v => v.name.includes('Samantha') || v.name.includes('Female') || v.name.includes('Zira') || v.name.includes('Google UK English Female'));
    if (female) utt.voice = female;
    utt.rate = 0.95; utt.pitch = 1.05;
    utt.onstart = () => setAiState('speaking');
    utt.onend = () => { setAiState('listening'); startListening(); };
    window.speechSynthesis.speak(utt);
  }, []);

  const startListening = useCallback(() => {
    const SR = window.SpeechRecognition || window.webkitSpeechRecognition;
    if (!SR) { setMode('text'); return; }
    const rec = new SR();
    rec.continuous = true; rec.interimResults = true; rec.lang = 'en-US';
    rec.onresult = (e) => {
      let fin = '', interim = '';
      for (let i = e.resultIndex; i < e.results.length; i++) {
        if (e.results[i].isFinal) fin += e.results[i][0].transcript;
        else interim += e.results[i][0].transcript;
      }
      setLiveTranscript(interim);
      if (fin) setAnswer(prev => (prev + ' ' + fin).trim());
    };
    rec.onend = () => setListening(false);
    recognitionRef.current = rec;
    rec.start();
    setListening(true);
  }, []);

  const stopListening = () => {
    if (recognitionRef.current) {
      try { recognitionRef.current.stop(); } catch {}
      recognitionRef.current = null;
    }
    setListening(false);
    setAiState('idle');
  };

  const toggleMode = (newMode) => {
    stopListening();
    window.speechSynthesis.cancel();
    setMode(newMode);
    setAiState('idle');
  };

  const startVoiceMode = () => {
    setMode('voice');
    if (currentQ) speakQuestion(currentQ.question_text);
  };

  const handleSubmitAnswer = async () => {
    if (!currentQ || !answer.trim()) return;
    stopTimer();
    stopListening();
    window.speechSynthesis.cancel();
    setAiState('idle');

    try {
      const res = await interviewService.submitAnswer(id, currentQ.id, answer);
      setEvaluation(res.evaluation);
      setShowEval(true);
      setAnswered(res.answered || answered + 1);

      if (res.interview_complete) {
        setCompleted(true);
        setFinalScore(res.total_score);
        const r = await interviewService.getReport(id);
        setReport(r);
        setFinalScore(r);
      } else if (res.next_question) {
        setCurrentQ(res.next_question);
        setAnswer('');
        setLiveTranscript('');
        setTimeout(() => {
          if (mode === 'voice') speakQuestion(res.next_question.question_text);
          startTimer();
        }, 2000);
      }
    } catch (err) { setError('Failed to submit answer'); }
  };

  const handleSkip = async () => {
    if (skipped >= 1 || !currentQ) return;
    stopTimer(); stopListening(); window.speechSynthesis.cancel();
    setAiState('idle');
    try {
      const res = await interviewService.skip(id, currentQ.id);
      setSkipped(res.skipped);
      setAnswered(res.answered);
      if (res.interview_complete) {
        setCompleted(true);
        const r = await interviewService.getReport(id);
        setFinalScore(r);
        setReport(r);
      } else if (res.next_question) {
        setCurrentQ(res.next_question);
        setAnswer('');
        setLiveTranscript('');
        setTimeout(() => {
          if (mode === 'voice') speakQuestion(res.next_question.question_text);
          startTimer();
        }, 2000);
      }
    } catch (err) { setError('Skip failed'); }
  };

  const handleComplete = async () => {
    try {
      await interviewService.complete(id);
      const r = await interviewService.getReport(id);
      setFinalScore(r);
      setReport(r);
    } catch {}
  };

  const handleFinish = () => navigate(`/interview/result/${id}`);

  const handleStartAnswer = () => {
    setAnswer('');
    setShowEval(false);
    setEvaluation(null);
    startTimer();
    if (mode === 'voice' && currentQ) speakQuestion(currentQ.question_text);
  };

  const timerColor = timer > 60 ? '#22c55e' : timer > 30 ? '#eab308' : '#ef4444';
  const progress = total > 0 ? (answered / total) * 100 : 0;

  if (error) {
    return <div style={{ padding: 40, textAlign: 'center', color: '#ef4444' }}>{error}<br /><button onClick={loadState} style={{ marginTop: 16, padding: '10px 24px', background: '#6366f1', color: '#fff', border: 'none', borderRadius: 8, cursor: 'pointer' }}>Retry</button></div>;
  }

  return (
    <div style={{ minHeight: 'calc(100vh - 60px)', display: 'flex', background: '#0f0f1a' }}>
      {/* Left Sidebar */}
      <div style={{ width: 300, background: '#1e293b', padding: 24, borderRight: '1px solid #334155', display: 'flex', flexDirection: 'column', gap: 24 }}>
        <AvatarAnimated state={aiState} />
        
        {webcamStream && !webcamError && (
          <div style={{ borderRadius: 12, overflow: 'hidden', background: '#0f0f1a' }}>
            <video ref={videoRef} autoPlay muted playsInline style={{ width: '100%', borderRadius: 12, transform: 'scaleX(-1)' }} />
          </div>
        )}

        {/* Progress */}
        <div>
          <div style={{ display: 'flex', justifyContent: 'space-between', marginBottom: 8, fontSize: '0.85rem' }}>
            <span style={{ color: '#94a3b8' }}>Progress</span>
            <span style={{ color: '#6366f1', fontWeight: 600 }}>{answered}/{total}</span>
          </div>
          <div style={{ height: 8, background: '#0f0f1a', borderRadius: 4, overflow: 'hidden' }}>
            <div style={{ height: '100%', width: `${progress}%`, background: '#6366f1', borderRadius: 4, transition: 'width 0.5s' }} />
          </div>
        </div>

        {/* Timer */}
        {timerActive && (
          <div style={{ textAlign: 'center' }}>
            <div style={{ fontSize: '2.5rem', fontWeight: 800, color: timerColor, fontVariantNumeric: 'tabular-nums' }}>
              {Math.floor(timer / 60)}:{String(timer % 60).padStart(2, '0')}
            </div>
            <div style={{ color: '#64748b', fontSize: '0.8rem' }}>Remaining</div>
          </div>
        )}

        {/* Scores preview */}
        {evaluation && (
          <div style={{ background: '#0f0f1a', borderRadius: 10, padding: 16 }}>
            <div style={{ fontSize: '0.85rem', color: '#94a3b8', marginBottom: 8 }}>Last Answer</div>
            <ScoreGauge score={evaluation.score || 0} size={100} label="Score" color={evaluation.score >= 80 ? '#22c55e' : evaluation.score >= 60 ? '#eab308' : '#ef4444'} />
          </div>
        )}

        <div style={{ fontSize: '0.8rem', color: '#64748b', textAlign: 'center' }}>
          {skipped}/1 skips used
        </div>
      </div>

      {/* Main Content */}
      <div style={{ flex: 1, padding: 32, display: 'flex', flexDirection: 'column' }}>
        {completed ? (
          /* COMPLETED SCREEN */
          <div style={{ maxWidth: 600, margin: '0 auto', textAlign: 'center', paddingTop: 60 }}>
            <div style={{ fontSize: '3rem', marginBottom: 16 }}>🎉</div>
            <h2 style={{ marginBottom: 8 }}>Interview Complete!</h2>
            <p style={{ color: '#94a3b8', marginBottom: 32 }}>Here's your performance summary</p>
            
            {finalScore && (
              <div style={{ display: 'flex', justifyContent: 'center', gap: 40, marginBottom: 32 }}>
                <ScoreGauge score={finalScore.overall_score || 0} size={160} label="Overall" color={finalScore.overall_score >= 80 ? '#22c55e' : finalScore.overall_score >= 60 ? '#eab308' : '#ef4444'} />
              </div>
            )}

            {finalScore && (
              <div style={{ display: 'flex', gap: 16, justifyContent: 'center', marginBottom: 32, flexWrap: 'wrap' }}>
                {[
                  { label: 'Technical', score: finalScore.technical_score, color: '#6366f1' },
                  { label: 'Communication', score: finalScore.communication_score, color: '#8b5cf6' },
                  { label: 'Confidence', score: finalScore.confidence_score, color: '#a855f7' },
                ].map((s, i) => (
                  <div key={i} style={{ background: '#1e293b', padding: '16px 24px', borderRadius: 12, border: '1px solid #334155', minWidth: 120 }}>
                    <div style={{ fontSize: '1.5rem', fontWeight: 700, color: s.score >= 80 ? '#22c55e' : s.score >= 60 ? '#eab308' : '#ef4444' }}>{s.score.toFixed(0)}%</div>
                    <div style={{ color: '#94a3b8', fontSize: '0.8rem' }}>{s.label}</div>
                  </div>
                ))}
              </div>
            )}

            {finalScore?.recommendation && (
              <div style={{
                display: 'inline-block', padding: '8px 24px', borderRadius: 20, fontWeight: 600,
                background: finalScore.recommendation === 'highly_recommended' ? '#22c55e22' : finalScore.recommendation === 'recommended' ? '#6366f122' : finalScore.recommendation === 'consider_review' ? '#eab30822' : '#ef444422',
                color: finalScore.recommendation === 'highly_recommended' ? '#22c55e' : finalScore.recommendation === 'recommended' ? '#6366f1' : finalScore.recommendation === 'consider_review' ? '#eab308' : '#ef4444',
                border: `1px solid ${finalScore.recommendation === 'highly_recommended' ? '#22c55e' : finalScore.recommendation === 'recommended' ? '#6366f1' : finalScore.recommendation === 'consider_review' ? '#eab308' : '#ef4444'}`,
                marginBottom: 32,
              }}>
                {finalScore.recommendation.replace(/_/g, ' ').replace(/\b\w/g, l => l.toUpperCase())}
              </div>
            )}

            {report?.summary && (
              <p style={{ color: '#94a3b8', marginBottom: 32, lineHeight: 1.6 }}>{report.summary}</p>
            )}

            <div style={{ display: 'flex', gap: 12, justifyContent: 'center' }}>
              <button onClick={handleFinish} style={{ padding: '14px 32px', background: '#6366f1', color: '#fff', border: 'none', borderRadius: 8, fontWeight: 600, cursor: 'pointer', fontSize: '0.95rem' }}>View Full Report</button>
              <button onClick={() => navigate('/interview/start')} style={{ padding: '14px 32px', background: 'transparent', color: '#6366f1', border: '1px solid #6366f1', borderRadius: 8, fontWeight: 600, cursor: 'pointer', fontSize: '0.95rem' }}>New Interview</button>
            </div>
          </div>
        ) : !currentQ ? (
          /* START SCREEN */
          <div style={{ maxWidth: 500, margin: '0 auto', textAlign: 'center', paddingTop: 60 }}>
            <h2 style={{ marginBottom: 16 }}>Ready for your interview?</h2>
            <p style={{ color: '#94a3b8', marginBottom: 32, lineHeight: 1.7 }}>
              You'll answer 10 questions. Each question has a {TIMER_DURATION}-second timer.
              You can use <strong>Voice Mode</strong> (speak your answers) or <strong>Text Mode</strong> (type them). Max 1 skip.
            </p>
            <div style={{ display: 'flex', gap: 12, justifyContent: 'center', marginBottom: 24 }}>
              <button onClick={() => { toggleMode('text'); handleStartAnswer(); }} style={{ padding: '14px 32px', background: '#6366f1', color: '#fff', border: 'none', borderRadius: 8, fontWeight: 600, cursor: 'pointer' }}>Text Mode</button>
              <button onClick={() => { setMode('voice'); startVoiceMode(); }} style={{ padding: '14px 32px', background: 'transparent', color: '#6366f1', border: '1px solid #6366f1', borderRadius: 8, fontWeight: 600, cursor: 'pointer' }}>Voice Mode 🎤</button>
            </div>
          </div>
        ) : (
          /* QUESTION SCREEN */
          <>
            {/* Mode toggle */}
            <div style={{ display: 'flex', gap: 8, marginBottom: 20 }}>
              <button onClick={() => toggleMode('text')} style={{ padding: '6px 16px', borderRadius: 6, border: 'none', cursor: 'pointer', background: mode === 'text' ? '#6366f1' : '#334155', color: '#fff', fontSize: '0.8rem', fontWeight: 500 }}>⌨ Text</button>
              <button onClick={() => toggleMode('voice')} style={{ padding: '6px 16px', borderRadius: 6, border: 'none', cursor: 'pointer', background: mode === 'voice' ? '#6366f1' : '#334155', color: '#fff', fontSize: '0.8rem', fontWeight: 500 }}>🎤 Voice</button>
            </div>

            {/* Question */}
            <div style={{ background: '#1e293b', borderRadius: 16, padding: 24, border: '1px solid #334155', marginBottom: 20 }}>
              <div style={{ display: 'flex', gap: 8, marginBottom: 12 }}>
                <span style={{ padding: '2px 10px', borderRadius: 12, background: '#6366f122', color: '#6366f1', fontSize: '0.75rem', fontWeight: 500 }}>Q{currentQ.order_index}</span>
                <span style={{ padding: '2px 10px', borderRadius: 12, background: '#8b5cf622', color: '#8b5cf6', fontSize: '0.75rem', fontWeight: 500 }}>{currentQ.question_type}</span>
                <span style={{ padding: '2px 10px', borderRadius: 12, background: '#a855f722', color: '#a855f7', fontSize: '0.75rem', fontWeight: 500 }}>{currentQ.difficulty}</span>
              </div>
              <h3 style={{ color: '#e2e8f0', lineHeight: 1.6 }}>{currentQ.question_text}</h3>
              {currentQ.follow_up && (
                <p style={{ color: '#64748b', fontSize: '0.85rem', marginTop: 12, fontStyle: 'italic' }}>Follow-up: {currentQ.follow_up}</p>
              )}
            </div>

            {/* Answer area */}
            {mode === 'voice' ? (
              <div style={{ background: '#1e293b', borderRadius: 16, padding: 24, border: '1px solid #334155', marginBottom: 20, minHeight: 150 }}>
                <div style={{ display: 'flex', justifyContent: 'space-between', marginBottom: 12 }}>
                  <span style={{ color: '#94a3b8', fontSize: '0.85rem' }}>Voice Answer</span>
                  <span style={{ color: listening ? '#22c55e' : '#64748b', fontSize: '0.8rem' }}>{listening ? '🔴 Recording...' : '⚪ Not recording'}</span>
                </div>
                <div style={{ color: '#e2e8f0', lineHeight: 1.6, minHeight: 60 }}>
                  {answer || <span style={{ color: '#475569' }}>Speak your answer...</span>}
                </div>
                {liveTranscript && (
                  <div style={{ color: '#64748b', fontStyle: 'italic', fontSize: '0.85rem', marginTop: 8 }}>{liveTranscript}</div>
                )}
                <div style={{ display: 'flex', gap: 8, marginTop: 16 }}>
                  {!listening ? (
                    <button onClick={() => { startListening(); setAiState('listening'); }} style={{ padding: '8px 16px', background: '#22c55e', color: '#fff', border: 'none', borderRadius: 8, cursor: 'pointer', fontSize: '0.85rem' }}>🎤 Start Recording</button>
                  ) : (
                    <button onClick={() => { stopListening(); setAiState('idle'); }} style={{ padding: '8px 16px', background: '#ef4444', color: '#fff', border: 'none', borderRadius: 8, cursor: 'pointer', fontSize: '0.85rem' }}>⏹ Stop Recording</button>
                  )}
                  <button onClick={() => speakQuestion(currentQ.question_text)} style={{ padding: '8px 16px', background: '#6366f1', color: '#fff', border: 'none', borderRadius: 8, cursor: 'pointer', fontSize: '0.85rem' }}>🔊 Replay</button>
                </div>
              </div>
            ) : (
              <div style={{ background: '#1e293b', borderRadius: 16, padding: 24, border: '1px solid #334155', marginBottom: 20 }}>
                <label style={{ display: 'block', color: '#94a3b8', fontSize: '0.85rem', marginBottom: 8 }}>Your Answer</label>
                <textarea value={answer} onChange={e => setAnswer(e.target.value)} rows={5}
                  placeholder="Type your answer here..." style={{
                    width: '100%', padding: 12, background: '#0f0f1a', border: '1px solid #334155',
                    borderRadius: 8, color: '#e2e8f0', fontSize: '0.9rem', resize: 'vertical', fontFamily: 'inherit',
                  }} />
              </div>
            )}

            {/* Evaluation panel */}
            {showEval && evaluation && (
              <div style={{ background: '#1e293b', borderRadius: 16, padding: 24, border: '1px solid #334155', marginBottom: 20 }}>
                <h3 style={{ marginBottom: 16 }}>Evaluation</h3>
                <div style={{ display: 'flex', gap: 24, alignItems: 'center', marginBottom: 16 }}>
                  <ScoreGauge score={evaluation.score || 0} size={120} label={evaluation.label} color={evaluation.score >= 80 ? '#22c55e' : evaluation.score >= 60 ? '#eab308' : '#ef4444'} />
                  <div style={{ flex: 1 }}>
                    <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr 1fr', gap: 8 }}>
                      {[{l:'Technical',v:evaluation.technical_accuracy},{l:'Completeness',v:evaluation.completeness},{l:'Depth',v:evaluation.depth},{l:'Communication',v:evaluation.communication},{l:'Confidence',v:evaluation.confidence},{l:'Relevance',v:evaluation.relevance}].map((c,i) => (
                        <div key={i} style={{ background: '#0f0f1a', padding: '8px 12px', borderRadius: 8, textAlign: 'center' }}>
                          <div style={{ fontSize: '1rem', fontWeight: 700, color: (c.v*10) >= 70 ? '#22c55e' : (c.v*10) >= 50 ? '#eab308' : '#ef4444' }}>{(c.v*10).toFixed(0)}%</div>
                          <div style={{ fontSize: '0.7rem', color: '#64748b' }}>{c.l}</div>
                        </div>
                      ))}
                    </div>
                  </div>
                </div>
                <p style={{ color: '#94a3b8', fontSize: '0.9rem', lineHeight: 1.6 }}>{evaluation.feedback}</p>
                {evaluation.missing_keywords?.length > 0 && (
                  <div style={{ marginTop: 8 }}>
                    <span style={{ color: '#eab308', fontSize: '0.8rem' }}>Missing: {evaluation.missing_keywords.join(', ')}</span>
                  </div>
                )}
              </div>
            )}

            {/* Action buttons */}
            <div style={{ display: 'flex', gap: 12 }}>
              <button onClick={handleSubmitAnswer} disabled={!answer.trim()}
                style={{ flex: 1, padding: '14px', background: answer.trim() ? '#6366f1' : '#334155', color: '#fff', border: 'none', borderRadius: 8, fontSize: '0.95rem', fontWeight: 600, cursor: answer.trim() ? 'pointer' : 'not-allowed' }}>
                {showEval ? 'Next Question →' : 'Submit Answer'}
              </button>
              <button onClick={handleSkip} disabled={skipped >= 1}
                style={{ padding: '14px 24px', background: skipped >= 1 ? '#334155' : '#1e293b', color: skipped >= 1 ? '#475569' : '#eab308', border: `1px solid ${skipped >= 1 ? '#334155' : '#eab308'}`, borderRadius: 8, fontWeight: 600, cursor: skipped >= 1 ? 'not-allowed' : 'pointer', fontSize: '0.9rem' }}>
                Skip {skipped >= 1 ? '(used)' : ''}
              </button>
            </div>
          </>
        )}
      </div>
    </div>
  );
}
