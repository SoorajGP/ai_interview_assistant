'use client';

import React, { useState } from 'react';
import type { AppPhase, Difficulty, HistoryItem, LostMark, StartResponse } from '@/types/interview';
import DomainSelect from '@/components/DomainSelect/DomainSelect';
import InterviewRoom from '@/components/InterviewRoom/InterviewRoom';
import WrapUp from '@/components/WrapUp/WrapUp';

interface WrapUpData {
  totalScore: number;
  totalPossible: number;
  percentage: number;
  verdict: string;
  history: HistoryItem[];
  lostMarks: LostMark[];
}

interface SessionData {
  sessionId: string;
  domain: string;
  question: string;
  difficulty: Difficulty;
  qNum: number;
  phaseTotal: number;
}

export default function HomePage() {
  const [phase, setPhase] = useState<AppPhase>('domain_select');
  const [session, setSession] = useState<SessionData | null>(null);
  const [wrapUp, setWrapUp] = useState<WrapUpData | null>(null);

  const handleSessionStart = (res: StartResponse) => {
    setSession({
      sessionId: res.session_id,
      domain: res.domain,
      question: res.question,
      difficulty: res.difficulty,
      qNum: res.q_num,
      phaseTotal: res.phase_total,
    });
    setPhase('interviewing');
  };

  const handleComplete = (data: WrapUpData) => {
    setWrapUp(data);
    setPhase('wrapup');
  };

  const handleRestart = () => {
    setSession(null);
    setWrapUp(null);
    setPhase('domain_select');
  };

  return (
    <>
      {phase === 'domain_select' && (
        <DomainSelect onSessionStart={handleSessionStart} />
      )}

      {phase === 'interviewing' && session && (
        <InterviewRoom
          sessionId={session.sessionId}
          domain={session.domain}
          initialQuestion={session.question}
          initialDifficulty={session.difficulty}
          initialQNum={session.qNum}
          initialPhaseTotal={session.phaseTotal}
          onComplete={handleComplete}
        />
      )}

      {phase === 'wrapup' && wrapUp && (
        <WrapUp
          totalScore={wrapUp.totalScore}
          totalPossible={wrapUp.totalPossible}
          percentage={wrapUp.percentage}
          verdict={wrapUp.verdict}
          history={wrapUp.history}
          lostMarks={wrapUp.lostMarks}
          onRestart={handleRestart}
        />
      )}
    </>
  );
}
