// Shared TypeScript types for the AI Interview Assistant frontend

export type Difficulty = 'Easy' | 'Medium' | 'Hard';

export type AppPhase = 'domain_select' | 'interviewing' | 'wrapup';

export interface StartResponse {
    session_id: string;
    domain: string;
    difficulty: Difficulty;
    question: string;
    q_num: number;
    phase_total: number;
    is_complete: boolean;
}

export interface SubmitResponse {
    score: number;
    feedback: string;
    is_complete: boolean;
    verdict: string | null;
    total_score: number;
    total_possible: number;
    percentage: number | null;
    history: HistoryItem[] | null;
    lost_marks: LostMark[] | null;
    phase_message: string;
    next_question: string | null;
    difficulty: Difficulty;
    q_num: number | null;
    phase_total: number | null;
}

export interface HistoryItem {
    question: string;
    user_answer: string;
    score: number;
    feedback: string;
    difficulty: Difficulty;
}

export interface LostMark {
    question: string;
    score: number;
    lost: number;
    difficulty: Difficulty;
}

export interface SessionSnapshot {
    domain: string;
    difficulty: Difficulty;
    question: string;
    q_num: number;
    phase_total: number;
    total_score: number;
    total_possible: number;
    is_complete: boolean;
    verdict: string | null;
}

export interface EvaluationResult {
    score: number;
    feedback: string;
}
