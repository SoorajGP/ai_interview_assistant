'use client';

import React from 'react';
import type { Difficulty } from '@/types/interview';
import styles from './InterviewRoom.module.css';

interface Props {
    question: string;
    difficulty: Difficulty;
    qNum: number;
    phaseTotal: number;
    phaseMessage: string;
}

const DIFFICULTY_LIMITS: Record<Difficulty, number> = {
    Easy: 5,
    Medium: 8,
    Hard: 5,
};

const PHASE_ORDER: Difficulty[] = ['Easy', 'Medium', 'Hard'];

export default function ContextPane({ question, difficulty, qNum, phaseTotal, phaseMessage }: Props) {
    const progress = phaseTotal > 0 ? (qNum - 1) / phaseTotal : 0;

    return (
        <div className={styles.contextPane}>
            {/* Phase tracker */}
            <div className={styles.phaseTracker}>
                <div className={styles.difficultyRow}>
                    <span
                        className={styles.difficultyBadge}
                        data-difficulty={difficulty.toLowerCase()}
                    >
                        <span className={styles.difficultyDot} />
                        {difficulty.toUpperCase()}
                    </span>
                    <span className={styles.phaseFlow}>
                        {PHASE_ORDER.map((p, i) => (
                            <React.Fragment key={p}>
                                <span
                                    className={styles.phaseStep}
                                    data-active={p === difficulty}
                                    data-done={PHASE_ORDER.indexOf(difficulty) > i}
                                >
                                    {p.slice(0, 3).toUpperCase()}
                                </span>
                                {i < 2 && <span className={styles.phaseArrow}>›</span>}
                            </React.Fragment>
                        ))}
                    </span>
                </div>

                {/* Progress bar */}
                <div className={styles.progressWrap}>
                    <div className={styles.progressTrack}>
                        <div
                            className={styles.progressFill}
                            style={{ width: `${progress * 100}%` }}
                        />
                    </div>
                    <span className={styles.progressLabel}>
                        {qNum - 1} / {phaseTotal}
                    </span>
                </div>
            </div>

            {/* Question number tag */}
            <div className={styles.qMeta}>
                <span className={styles.qTag}>Q{qNum}</span>
                <span className={styles.qSep}>/</span>
                <span className={styles.qTotal}>{phaseTotal}</span>
            </div>

            {/* The question */}
            <p className={`${styles.questionText} animate-slide-up`}>
                {question}
            </p>

            {/* Phase message (transition announcement) */}
            {phaseMessage && (
                <div className={`${styles.phaseMsg} animate-fade-in`}>
                    <span className={styles.phaseMsgDot} />
                    {phaseMessage}
                </div>
            )}

            {/* Phase limits legend */}
            <div className={styles.phaseLimits}>
                {PHASE_ORDER.map((p) => (
                    <div key={p} className={styles.limitItem} data-active={p === difficulty}>
                        <span className={styles.limitLabel}>{p.slice(0, 3).toUpperCase()}</span>
                        <span className={styles.limitVal}>{DIFFICULTY_LIMITS[p]}Q</span>
                    </div>
                ))}
            </div>
        </div>
    );
}
