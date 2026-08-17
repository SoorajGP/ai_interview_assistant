'use client';

import React from 'react';
import type { Difficulty, HistoryItem, LostMark } from '@/types/interview';
import styles from './WrapUp.module.css';

interface Props {
    totalScore: number;
    totalPossible: number;
    percentage: number;
    verdict: string;
    history: HistoryItem[];
    lostMarks: LostMark[];
    onRestart: () => void;
}

const VERDICT_COLOR: Record<string, string> = {
    'STRONG HIRE': 'var(--pass)',
    'LEANING HIRE': 'var(--signal)',
    'NO HIRE': 'var(--fail)',
};

const DIFFICULTY_SHORT: Record<Difficulty, string> = {
    Easy: 'E',
    Medium: 'M',
    Hard: 'H',
};

export default function WrapUp({
    totalScore,
    totalPossible,
    percentage,
    verdict,
    history,
    lostMarks,
    onRestart,
}: Props) {
    const verdictColor = VERDICT_COLOR[verdict] ?? 'var(--text-pri)';
    const passedMedium = percentage >= 70;

    return (
        <div className={styles.root}>
            <div className={styles.inner}>
                {/* Header */}
                <div className={styles.header}>
                    <span className={styles.chip}>SESSION COMPLETE</span>

                    <div className={styles.scoreBlock}>
                        <span className={styles.scoreFraction}>
                            {totalScore}
                            <span className={styles.scoreSep}>/</span>
                            <span className={styles.scorePoss}>{totalPossible}</span>
                        </span>
                        <div className={styles.scoreMeta}>
                            <span className={styles.pct}>{percentage.toFixed(1)}%</span>
                            <span
                                className={styles.verdict}
                                style={{ color: verdictColor, borderColor: `${verdictColor}30` }}
                            >
                                {verdict}
                            </span>
                        </div>
                    </div>

                    <div className={styles.statusLine}>
                        <div
                            className={styles.statusBar}
                            style={{
                                background: `linear-gradient(to right, ${verdictColor} ${percentage}%, var(--border) ${percentage}%)`
                            }}
                        />
                    </div>
                </div>

                <div className={styles.divider} />

                {/* Summary stats */}
                <div className={styles.stats}>
                    <div className={styles.stat}>
                        <span className={styles.statLabel}>QUESTIONS</span>
                        <span className={styles.statVal}>{history.length}</span>
                    </div>
                    <div className={styles.stat}>
                        <span className={styles.statLabel}>MARKS LOST</span>
                        <span className={styles.statVal}>{lostMarks.reduce((s, r) => s + r.lost, 0)}</span>
                    </div>
                    <div className={styles.stat}>
                        <span className={styles.statLabel}>MEDIUM THRESHOLD</span>
                        <span className={styles.statVal} style={{ color: passedMedium ? 'var(--pass)' : 'var(--fail)' }}>
                            {passedMedium ? 'PASSED' : 'FAILED'}
                        </span>
                    </div>
                    <div className={styles.stat}>
                        <span className={styles.statLabel}>PHASES COMPLETED</span>
                        <span className={styles.statVal}>
                            {percentage >= 70 ? '3' : '2'} / 3
                        </span>
                    </div>
                </div>

                <div className={styles.divider} />

                {/* Chronological breakdown */}
                <div className={styles.sectionLabel}>QUESTION BREAKDOWN</div>

                <div className={styles.breakdownList}>
                    {history.map((item, i) => {
                        const scoreColor =
                            item.score >= 7
                                ? 'var(--pass)'
                                : item.score >= 4
                                    ? 'var(--signal)'
                                    : 'var(--fail)';

                        return (
                            <div key={i} className={styles.breakdownRow}>
                                <div className={styles.bRowLeft}>
                                    <span
                                        className={styles.bDiffTag}
                                        data-difficulty={item.difficulty.toLowerCase()}
                                    >
                                        {DIFFICULTY_SHORT[item.difficulty]}
                                    </span>
                                    <div className={styles.bContent}>
                                        <p className={styles.bQuestion}>{item.question}</p>
                                        <p className={styles.bFeedback}>{item.feedback}</p>
                                    </div>
                                </div>
                                <div className={styles.bScore} style={{ color: scoreColor }}>
                                    {item.score}<span className={styles.bScoreDenom}>/10</span>
                                </div>
                            </div>
                        );
                    })}
                </div>

                <div className={styles.divider} />

                {/* Restart */}
                <div className={styles.footer}>
                    <button className={styles.restartBtn} onClick={onRestart}>
                        START NEW SESSION
                    </button>
                    <span className={styles.footerNote}>
                        Your session data is local and will not persist after refresh.
                    </span>
                </div>
            </div>
        </div>
    );
}
