'use client';

import React, { RefObject } from 'react';
import styles from './InterviewRoom.module.css';

interface EvalResult {
    score: number;
    feedback: string;
}

interface Props {
    answer: string;
    onAnswerChange: (val: string) => void;
    onSubmit: () => void;
    evaluating: boolean;
    evalResult: EvalResult | null;
    error: string | null;
    textareaRef: RefObject<HTMLTextAreaElement | null>;
}

export default function WorkspacePane({
    answer,
    onAnswerChange,
    onSubmit,
    evaluating,
    evalResult,
    error,
    textareaRef,
}: Props) {
    const scoreColor =
        evalResult
            ? evalResult.score >= 7
                ? 'var(--pass)'
                : evalResult.score >= 4
                    ? 'var(--signal)'
                    : 'var(--fail)'
            : 'var(--text-pri)';

    return (
        <div className={styles.workspacePane}>
            {/* Textarea */}
            <div className={styles.textareaWrap}>
                <textarea
                    ref={textareaRef}
                    className={styles.textarea}
                    value={answer}
                    onChange={(e) => onAnswerChange(e.target.value)}
                    placeholder="Type your answer here…"
                    disabled={evaluating || !!evalResult}
                    onKeyDown={(e) => {
                        if (e.key === 'Enter' && (e.metaKey || e.ctrlKey)) {
                            e.preventDefault();
                            onSubmit();
                        }
                    }}
                    aria-label="Your answer"
                />
                <span className={styles.textareaHint}>
                    {evaluating || evalResult ? '' : '⌘↵ to submit'}
                </span>
            </div>

            {/* Submit row */}
            <div className={styles.submitRow}>
                {error && (
                    <span className={styles.submitError}>{error}</span>
                )}
                <button
                    className={`${styles.submitBtn} ${evaluating ? styles.submitBtnLoading : ''}`}
                    onClick={onSubmit}
                    disabled={evaluating || !!evalResult || !answer.trim()}
                    aria-label={evaluating ? 'Evaluating answer' : 'Submit answer'}
                >
                    {evaluating ? (
                        <span className={styles.submitBtnLoadingText}>
                            <span className={`${styles.evalDot} animate-pulse`} />
                            EVALUATING
                        </span>
                    ) : (
                        'SUBMIT ANSWER'
                    )}
                </button>
            </div>

            {/* Evaluation result */}
            {evalResult && (
                <div className={`${styles.evalBlock} animate-slide-up`}>
                    <div className={styles.evalDivider} />

                    <div className={styles.evalScore} style={{ color: scoreColor }}>
                        {evalResult.score}
                        <span className={styles.evalScoreSep}>/</span>
                        <span className={styles.evalScoreMax}>10</span>
                    </div>

                    <p className={styles.evalFeedback}>{evalResult.feedback}</p>

                    <span className={styles.evalNext}>
                        Next question loading…
                    </span>
                </div>
            )}
        </div>
    );
}
