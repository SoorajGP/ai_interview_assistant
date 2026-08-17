/**
 * Typed fetch wrappers for the AI Interview Assistant FastAPI backend.
 * All requests go to http://localhost:8000
 */

import type {
    StartResponse,
    SubmitResponse,
} from '@/types/interview';

const BASE_URL = process.env.NEXT_PUBLIC_API_URL ?? 'http://localhost:8000';

async function apiFetch<T>(path: string, init?: RequestInit): Promise<T> {
    const res = await fetch(`${BASE_URL}${path}`, {
        headers: { 'Content-Type': 'application/json' },
        ...init,
    });

    if (!res.ok) {
        const err = await res.json().catch(() => ({ detail: res.statusText }));
        throw new Error(err.detail ?? 'API request failed');
    }

    return res.json() as Promise<T>;
}

/** GET /api/domains — returns sorted list of available domains */
export async function getDomains(): Promise<string[]> {
    const data = await apiFetch<{ domains: string[] }>('/api/domains');
    return data.domains;
}

/** POST /api/session/start — initializes a new interview session */
export async function startSession(domain: string): Promise<StartResponse> {
    return apiFetch<StartResponse>('/api/session/start', {
        method: 'POST',
        body: JSON.stringify({ domain }),
    });
}

/** POST /api/session/submit — submits an answer for the current question */
export async function submitAnswer(
    session_id: string,
    user_answer: string,
): Promise<SubmitResponse> {
    return apiFetch<SubmitResponse>('/api/session/submit', {
        method: 'POST',
        body: JSON.stringify({ session_id, user_answer }),
    });
}
