'use client';

import React, { useEffect, useState } from 'react';
import { getDomains, startSession } from '@/lib/api';
import type { StartResponse } from '@/types/interview';
import styles from './DomainSelect.module.css';

interface Props {
    onSessionStart: (session: StartResponse) => void;
}

export default function DomainSelect({ onSessionStart }: Props) {
    const [domains, setDomains] = useState<string[]>([]);
    const [loading, setLoading] = useState(true);
    const [starting, setStarting] = useState<string | null>(null);
    const [error, setError] = useState<string | null>(null);

    useEffect(() => {
        getDomains()
            .then(setDomains)
            .catch(() => setError('Cannot reach the API server. Make sure the FastAPI server is running on port 8000.'))
            .finally(() => setLoading(false));
    }, []);

    const handleSelect = async (domain: string) => {
        if (starting) return;
        setStarting(domain);
        setError(null);
        try {
            const session = await startSession(domain);
            onSessionStart(session);
        } catch (e: unknown) {
            setError(e instanceof Error ? e.message : 'Failed to start session.');
            setStarting(null);
        }
    };

    return (
        <div className={styles.root}>
            <div className={styles.inner}>
                {/* Header */}
                <div className={styles.header}>
                    <span className={styles.chip}>ADAPTIVE LLM INTERVIEWER</span>
                    <h1 className={styles.title}>SELECT A DOMAIN.</h1>
                    <p className={styles.subtitle}>
                        The system will adapt difficulty based on your performance across
                        three phases — Easy, Medium, and Hard.
                    </p>
                </div>

                {/* Divider */}
                <div className={styles.divider} />

                {/* Domain List */}
                <div className={styles.listWrap}>
                    {loading && (
                        <div className={styles.statusRow}>
                            <span className={`${styles.statusDot} animate-pulse`} />
                            <span className={styles.statusText}>Loading domains…</span>
                        </div>
                    )}

                    {error && (
                        <div className={styles.errorBlock}>
                            <span className={styles.errorIcon}>✕</span>
                            <span>{error}</span>
                        </div>
                    )}

                    {!loading && !error && (
                        <ul className={styles.list} role="listbox" aria-label="Interview domains">
                            {domains.map((domain, i) => (
                                <li
                                    key={domain}
                                    className={`${styles.item} ${starting === domain ? styles.itemActive : ''} ${starting && starting !== domain ? styles.itemDimmed : ''}`}
                                    role="option"
                                    aria-selected={starting === domain}
                                    onClick={() => handleSelect(domain)}
                                    tabIndex={0}
                                    onKeyDown={(e) => e.key === 'Enter' && handleSelect(domain)}
                                >
                                    <span className={styles.itemNum}>
                                        {String(i + 1).padStart(2, '0')}
                                    </span>
                                    <span className={styles.itemName}>{domain}</span>
                                    {starting === domain ? (
                                        <span className={styles.itemLoading}>INITIALIZING ···</span>
                                    ) : (
                                        <span className={styles.itemArrow}>→</span>
                                    )}
                                </li>
                            ))}
                        </ul>
                    )}
                </div>

                {/* Footer meta */}
                <div className={styles.footer}>
                    <span className={styles.footerMeta}>
                        {!loading && !error ? `${domains.length} DOMAINS AVAILABLE` : ''}
                    </span>
                    <span className={styles.footerMeta}>
                        PASS THRESHOLD&nbsp;&nbsp;70%
                    </span>
                    <span className={styles.footerMeta}>
                        PHASES&nbsp;&nbsp;EASY → MEDIUM → HARD
                    </span>
                </div>
            </div>
        </div>
    );
}
