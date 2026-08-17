'use client';

import React, { useState, useRef, useEffect, useCallback } from 'react';
import { submitAnswer } from '@/lib/api';
import type { Difficulty, HistoryItem, LostMark, SubmitResponse } from '@/types/interview';
import ContextPane from './ContextPane';
import WorkspacePane from './WorkspacePane';
import styles from './InterviewRoom.module.css';

interface Props {
    sessionId: string;
    domain: string;
    initialQuestion: string;
    initialDifficulty: Difficulty;
    initialQNum: number;
    initialPhaseTotal: number;
    onComplete: (data: {
        totalScore: number;
        totalPossible: number;
        percentage: number;
        verdict: string;
        history: HistoryItem[];
        lostMarks: LostMark[];
    }) => void;
}

interface EvalState {
    score: number;
    feedback: string;
}

export default function InterviewRoom({
    sessionId,
    domain,
    initialQuestion,
    initialDifficulty,
    initialQNum,
    initialPhaseTotal,
    onComplete,
}: Props) {
    const [question, setQuestion] = useState(initialQuestion);
    const [difficulty, setDifficulty] = useState<Difficulty>(initialDifficulty);
    const [qNum, setQNum] = useState(initialQNum);
    const [phaseTotal, setPhaseTotal] = useState(initialPhaseTotal);
    const [answer, setAnswer] = useState('');
    const [evaluating, setEvaluating] = useState(false);
    const [evalResult, setEvalResult] = useState<EvalState | null>(null);
    const [phaseMessage, setPhaseMessage] = useState('');
    const [totalScore, setTotalScore] = useState(0);
    const [totalPossible, setTotalPossible] = useState(0);
    const [error, setError] = useState<string | null>(null);

    // Key to force re-mount of WorkspacePane for animation on new question
    const [questionKey, setQuestionKey] = useState(0);
    const textareaRef = useRef<HTMLTextAreaElement>(null);

    // Focus textarea when new question loads
    useEffect(() => {
        textareaRef.current?.focus();
    }, [questionKey]);

    const handleSubmit = useCallback(async () => {
        if (!answer.trim() || evaluating) return;
        setError(null);
        setEvaluating(true);
        setEvalResult(null);

        try {
            const res: SubmitResponse = await submitAnswer(sessionId, answer.trim());

            setTotalScore(res.total_score);
            setTotalPossible(res.total_possible);
            setEvalResult({ score: res.score, feedback: res.feedback });
            setPhaseMessage(res.phase_message ?? '');

            if (res.is_complete && res.history && res.verdict) {
                // Short delay so user can see the final score before transition
                setTimeout(() => {
                    onComplete({
                        totalScore: res.total_score,
                        totalPossible: res.total_possible,
                        percentage: res.percentage!,
                        verdict: res.verdict!,
                        history: res.history!,
                        lostMarks: res.lost_marks ?? [],
                    });
                }, 2200);
            } else if (res.next_question) {
                // Advance to next question after showing evaluation
                setTimeout(() => {
                    setQuestion(res.next_question!);
                    setDifficulty(res.difficulty);
                    setQNum(res.q_num!);
                    setPhaseTotal(res.phase_total!);
                    setAnswer('');
                    setEvalResult(null);
                    setPhaseMessage('');
                    setEvaluating(false);
                    setQuestionKey((k) => k + 1);
                }, 2400);
                return; // Don't set evaluating to false yet
            }
        } catch (e: unknown) {
            setError(e instanceof Error ? e.message : 'Evaluation failed. Please try again.');
        }

        setEvaluating(false);
    }, [answer, evaluating, sessionId, onComplete]);

    return (
        <div className={styles.root}>
            {/* Top bar */}
            <header className={styles.topBar}>
                <span className={styles.topDomain}>{domain}</span>
                <div className={styles.topScore}>
                    {totalPossible > 0 && (
                        <span className={styles.topScoreVal}>
                            {totalScore} / {totalPossible}
                        </span>
                    )}
                </div>
            </header>

            {/* Split view */}
            <div className={styles.split}>
                <ContextPane
                    key={questionKey}
                    question={question}
                    difficulty={difficulty}
                    qNum={qNum}
                    phaseTotal={phaseTotal}
                    phaseMessage={phaseMessage}
                />

                <div className={styles.centerRule} aria-hidden="true" />

                <WorkspacePane
                    key={`ws-${questionKey}`}
                    answer={answer}
                    onAnswerChange={setAnswer}
                    onSubmit={handleSubmit}
                    evaluating={evaluating}
                    evalResult={evalResult}
                    error={error}
                    textareaRef={textareaRef}
                />
            </div>
        </div>
    );
}
