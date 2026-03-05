import { useState, useEffect, useCallback, useRef } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import { AttemptAPI, api } from '../services/api';

const API_BASE = import.meta.env.VITE_API_URL?.replace('/api/v1', '') || 'http://localhost:8000';

interface Question {
    id: string;
    question_text: string;
    image_url?: string;
    options: { option_text: string, is_correct?: boolean }[];
}

interface Section {
    id: string;
    name: string;
    marks_per_question: number;
    questions: Question[];
}

// Timer persistence helpers
const TIMER_KEY = 'pariksha365_timer';
const saveTimerState = (attemptId: string, startTime: number, totalSeconds: number, pausedElapsed: number) => {
    localStorage.setItem(TIMER_KEY, JSON.stringify({ attemptId, startTime, totalSeconds, pausedElapsed }));
};
const loadTimerState = (attemptId: string) => {
    try {
        const raw = localStorage.getItem(TIMER_KEY);
        if (!raw) return null;
        const data = JSON.parse(raw);
        if (data.attemptId !== attemptId) return null;
        return data as { attemptId: string; startTime: number; totalSeconds: number; pausedElapsed: number };
    } catch { return null; }
};
const clearTimerState = () => localStorage.removeItem(TIMER_KEY);

// Track visited questions
const VISITED_KEY = 'pariksha365_visited';

export const MockTestInterface = () => {
    const { testId } = useParams<{ testId: string }>();
    const navigate = useNavigate();

    const [sections, setSections] = useState<Section[]>([]);
    const [currentSectionIdx, setCurrentSectionIdx] = useState(0);
    const [currentQuestionIdx, setCurrentQuestionIdx] = useState(0);
    const [answers, setAnswers] = useState<Record<string, number | null>>({});
    const [markedForReview, setMarkedForReview] = useState<Set<string>>(new Set());
    const [visitedQuestions, setVisitedQuestions] = useState<Set<string>>(new Set());
    const [attemptId, setAttemptId] = useState<string | null>(null);
    const [loading, setLoading] = useState(true);
    const [submitting, setSubmitting] = useState(false);
    const [timeLeft, setTimeLeft] = useState(0);
    const timeLeftRef = useRef(0);
    const timerDisplayRef = useRef<HTMLSpanElement>(null);
    const timerContainerRef = useRef<HTMLDivElement>(null);
    const [testTitle, setTestTitle] = useState('');
    const [negMarking, setNegMarking] = useState(0.25);
    const [isPaused, setIsPaused] = useState(false);
    const [showMobilePalette, setShowMobilePalette] = useState(false);

    const pausedAtRef = useRef<number>(0);
    const timerStartRef = useRef<number>(Date.now());

    // Per-question time tracking
    const questionStartTimeRef = useRef<number>(Date.now());
    const questionTimeMapRef = useRef<Record<string, number>>({}); // questionId -> accumulated seconds
    const TIME_MAP_KEY = 'pariksha365_qtimes';

    // Flush time for the current question (called when navigating away or submitting)
    const flushTimeForCurrentQuestion = useCallback(async () => {
        const q = sections[currentSectionIdx]?.questions?.[currentQuestionIdx];
        if (!q || !attemptId || isPaused) return;
        const elapsed = Math.round((Date.now() - questionStartTimeRef.current) / 1000);
        if (elapsed <= 0) return;
        // Accumulate locally
        questionTimeMapRef.current[q.id] = (questionTimeMapRef.current[q.id] || 0) + elapsed;
        // Persist to localStorage
        try { localStorage.setItem(TIME_MAP_KEY, JSON.stringify(questionTimeMapRef.current)); } catch (e) { console.error(e); }
        try {
            await AttemptAPI.saveAnswer(attemptId, {
                question_id: q.id,
                selected_option_index: answers[q.id] !== undefined ? answers[q.id] : null,
                time_spent_seconds: elapsed
            });
        } catch (err) { console.error('Failed to save time:', err); }
        // Reset timer for next question
        questionStartTimeRef.current = Date.now();
    }, [sections, currentSectionIdx, currentQuestionIdx, attemptId, isPaused, answers]);

    const handleSubmit = useCallback(async (autoSubmit = false) => {
        if (!attemptId || submitting) return;
        if (!autoSubmit && !confirm('Are you sure you want to submit? You cannot change answers after submission.')) return;
        setSubmitting(true);
        try {
            // Flush time for the last question before submitting
            await flushTimeForCurrentQuestion();
            await AttemptAPI.submit(attemptId);
            clearTimerState();
            localStorage.removeItem(VISITED_KEY);
            localStorage.removeItem(TIME_MAP_KEY);
            navigate(`/results/${attemptId}`);
        } catch (err) {
            console.error("Failed to submit:", err);
            alert("Submission failed. Please try again.");
        } finally {
            setSubmitting(false);
        }
    }, [attemptId, submitting, flushTimeForCurrentQuestion, navigate]);

    // Load test and start/resume attempt
    useEffect(() => {
        if (!testId) { setLoading(false); return; }
        const init = async () => {
            try {
                // Start or resume attempt (This now also returns the Test details, including cdn_url)
                const attemptRes = await AttemptAPI.start(testId);
                const aid = attemptRes.data.id;
                setAttemptId(aid);

                // Now that Attempt is tracking us, download the actual Questions JSON from Cloudflare (or fallback to backend)
                const cdnUrl = attemptRes.data.test_series?.cdn_url;
                let testData;

                if (cdnUrl) {
                    try {
                        // Direct pull from Edge CDN
                        const cdnRes = await fetch(cdnUrl);
                        testData = await cdnRes.json();
                    } catch (e) {
                        console.error("CDN fetch failed, falling back to backend", e);
                        const fallbackRes = await api.get(`/tests/${testId}`);
                        testData = fallbackRes.data;
                    }
                } else {
                    // Fallback for older tests that haven't been published to R2 yet
                    const testRes = await api.get(`/tests/${testId}`);
                    testData = testRes.data;
                }

                setTestTitle(testData.title || 'Mock Test');
                setNegMarking(testData.negative_marking || 0.25);
                const durationSecs = (testData.sections?.reduce((sum: number, s: any) => sum + (s.time_limit_minutes || 0), 0) || 60) * 60;
                setSections(testData.sections || []);

                try {
                    const answersRes = await AttemptAPI.getAnswers(aid);
                    if (answersRes.data && answersRes.data.length > 0) {
                        const restoredAnswers: Record<string, number | null> = {};
                        const restoredVisited = new Set<string>();
                        answersRes.data.forEach((a: any) => {
                            restoredAnswers[a.question_id] = a.selected_option_index !== undefined ? a.selected_option_index : null;
                            restoredVisited.add(a.question_id);
                        });
                        setAnswers(restoredAnswers);
                        setVisitedQuestions(prev => new Set([...prev, ...restoredVisited]));
                    }
                } catch (e) { console.error('Failed to restore answers:', e); }

                // Restore timer from localStorage
                const saved = loadTimerState(aid);
                if (saved) {
                    const elapsed = (Date.now() - saved.startTime) / 1000 + saved.pausedElapsed;
                    const remaining = Math.max(0, Math.floor(saved.totalSeconds - elapsed));
                    setTimeLeft(remaining);
                    timeLeftRef.current = remaining;
                    timerStartRef.current = saved.startTime;
                } else {
                    setTimeLeft(durationSecs);
                    timeLeftRef.current = durationSecs;
                    timerStartRef.current = Date.now();
                    saveTimerState(aid, Date.now(), durationSecs, 0);
                }

                // Restore visited questions from localStorage
                try {
                    const visitedRaw = localStorage.getItem(VISITED_KEY);
                    if (visitedRaw) setVisitedQuestions(prev => new Set([...prev, ...JSON.parse(visitedRaw)]));
                } catch (e) { console.error('Failed to parse visited questions:', e); }
                // Restore question time map
                try {
                    const timeRaw = localStorage.getItem('pariksha365_qtimes');
                    if (timeRaw) questionTimeMapRef.current = JSON.parse(timeRaw);
                } catch (e) { console.error('Failed to parse time map:', e); }
            } catch (err) {
                console.error("Failed to load test:", err);
            } finally {
                setLoading(false);
            }
        };
        init();
    }, [testId]);

    // Mark current question as visited + reset question timer
    useEffect(() => {
        const q = sections[currentSectionIdx]?.questions?.[currentQuestionIdx];
        if (q) {
            // Reset question-level timer when landing on a new question
            questionStartTimeRef.current = Date.now();
            if (!visitedQuestions.has(q.id)) {
                setVisitedQuestions(prev => {
                    const next = new Set(prev);
                    next.add(q.id);
                    try { localStorage.setItem(VISITED_KEY, JSON.stringify([...next])); } catch (e) { console.error(e); }
                    return next;
                });
            }
        }
    }, [currentSectionIdx, currentQuestionIdx, sections, visitedQuestions]);

    // Timer countdown — uses refs + direct DOM update to avoid re-rendering the entire component every second
    useEffect(() => {
        if (timeLeftRef.current <= 0 || !attemptId || isPaused) return;
        const timer = setInterval(() => {
            timeLeftRef.current -= 1;
            // Update display directly via DOM
            if (timerDisplayRef.current) {
                timerDisplayRef.current.textContent = formatTime(timeLeftRef.current);
            }
            // Flash red when < 5 min
            if (timerContainerRef.current) {
                if (timeLeftRef.current < 300) {
                    timerContainerRef.current.className = 'flex items-center gap-2 px-4 py-2 rounded-lg font-mono text-lg font-black tracking-wider bg-red-600/80 text-red-100 animate-pulse';
                }
            }
            if (timeLeftRef.current <= 0) {
                clearInterval(timer);
                handleSubmit(true);
            }
        }, 1000);
        return () => clearInterval(timer);
    }, [attemptId, isPaused, handleSubmit]);

    // Auto-pause on tab switch or minimize to enforce exam integrity
    useEffect(() => {
        const handleVisibilityChange = async () => {
            if (document.hidden && !isPaused && !submitting && attemptId) {
                // Auto-pause exactly when leaving
                await flushTimeForCurrentQuestion();
                setIsPaused(true);
                pausedAtRef.current = Date.now();
            }
        };
        document.addEventListener('visibilitychange', handleVisibilityChange);
        return () => document.removeEventListener('visibilitychange', handleVisibilityChange);
    }, [isPaused, submitting, attemptId, flushTimeForCurrentQuestion]);

    // Pause/Resume handlers
    const handlePause = async () => {
        // Flush time spent so far before pausing
        await flushTimeForCurrentQuestion();
        setIsPaused(true);
        pausedAtRef.current = Date.now();
    };

    const handleResume = () => {
        setIsPaused(false);
        // Reset question start timer so the paused duration isn't counted
        questionStartTimeRef.current = Date.now();

        // Adjust the start time to account for pause duration
        if (attemptId) {
            const pauseDuration = Date.now() - pausedAtRef.current;
            const saved = loadTimerState(attemptId);
            if (saved) {
                const newPausedElapsed = saved.pausedElapsed - (pauseDuration / 1000);
                saveTimerState(attemptId, saved.startTime, saved.totalSeconds, newPausedElapsed);
            }
        }
    };

    const formatTime = (secs: number) => {
        const h = Math.floor(secs / 3600);
        const m = Math.floor((secs % 3600) / 60);
        const s = secs % 60;
        if (h > 0) return `${h.toString().padStart(2, '0')}:${m.toString().padStart(2, '0')}:${s.toString().padStart(2, '0')}`;
        return `${m.toString().padStart(2, '0')}:${s.toString().padStart(2, '0')}`;
    };

    const currentSection = sections[currentSectionIdx];
    const currentQuestion = currentSection?.questions?.[currentQuestionIdx];
    const totalQuestions = sections.reduce((sum, s) => sum + (s.questions?.length || 0), 0);

    const getFlatIndex = (sIdx: number, qIdx: number) => {
        let flat = 0;
        for (let i = 0; i < sIdx; i++) flat += sections[i].questions?.length || 0;
        return flat + qIdx;
    };

    // Question status helper
    const getQuestionStatus = (qId: string): 'not-visited' | 'not-answered' | 'answered' | 'marked' | 'answered-marked' => {
        const isAnswered = answers[qId] !== undefined && answers[qId] !== null;
        const isMarked = markedForReview.has(qId);
        const isVisited = visitedQuestions.has(qId);
        if (isAnswered && isMarked) return 'answered-marked';
        if (isMarked) return 'marked';
        if (isAnswered) return 'answered';
        if (isVisited) return 'not-answered';
        return 'not-visited';
    };

    const statusColors: Record<string, string> = {
        'not-visited': 'bg-gray-200 text-gray-600 border-gray-300',
        'not-answered': 'bg-red-500 text-white border-red-600',
        'answered': 'bg-green-500 text-white border-green-600',
        'marked': 'bg-purple-500 text-white border-purple-600',
        'answered-marked': 'bg-green-500 text-white border-purple-600 ring-2 ring-purple-400',
    };

    // Stats
    const getStats = () => {
        let answered = 0, notAnswered = 0, marked = 0, notVisited = 0;
        sections.forEach(s => s.questions?.forEach(q => {
            const status = getQuestionStatus(q.id);
            if (status === 'answered' || status === 'answered-marked') answered++;
            else if (status === 'not-answered') notAnswered++;
            if (status === 'marked' || status === 'answered-marked') marked++;
            if (status === 'not-visited') notVisited++;
        }));
        return { answered, notAnswered, marked, notVisited };
    };

    const selectOption = useCallback(async (optionIndex: number) => {
        if (!currentQuestion || !attemptId) return;
        setAnswers(prev => ({ ...prev, [currentQuestion.id]: optionIndex }));
        // Compute time spent on this question so far
        const elapsed = Math.round((Date.now() - questionStartTimeRef.current) / 1000);
        questionTimeMapRef.current[currentQuestion.id] = (questionTimeMapRef.current[currentQuestion.id] || 0) + elapsed;
        try { localStorage.setItem(TIME_MAP_KEY, JSON.stringify(questionTimeMapRef.current)); } catch { }
        try {
            await AttemptAPI.saveAnswer(attemptId, {
                question_id: currentQuestion.id,
                selected_option_index: optionIndex,
                time_spent_seconds: elapsed
            });
        } catch (err) { console.error("Failed to save answer:", err); }
        // Reset timer (user might change answer on same question)
        questionStartTimeRef.current = Date.now();
    }, [currentQuestion, attemptId]);

    const clearSelection = () => {
        if (!currentQuestion) return;
        setAnswers(prev => ({ ...prev, [currentQuestion.id]: null }));
    };

    const toggleMark = () => {
        if (!currentQuestion) return;
        setMarkedForReview(prev => {
            const next = new Set(prev);
            if (next.has(currentQuestion.id)) next.delete(currentQuestion.id);
            else next.add(currentQuestion.id);
            return next;
        });
    };

    const goNext = async () => {
        if (!currentSection) return;
        await flushTimeForCurrentQuestion();
        if (currentQuestionIdx < (currentSection.questions?.length || 0) - 1) {
            setCurrentQuestionIdx(prev => prev + 1);
        } else if (currentSectionIdx < sections.length - 1) {
            setCurrentSectionIdx(prev => prev + 1);
            setCurrentQuestionIdx(0);
        }
    };

    const goPrev = async () => {
        if (currentQuestionIdx === 0 && currentSectionIdx === 0) return;
        await flushTimeForCurrentQuestion();
        if (currentQuestionIdx > 0) {
            setCurrentQuestionIdx(prev => prev - 1);
        } else if (currentSectionIdx > 0) {
            setCurrentSectionIdx(prev => prev - 1);
            const prevSection = sections[currentSectionIdx - 1];
            setCurrentQuestionIdx((prevSection.questions?.length || 1) - 1);
        }
    };


    const jumpToQuestion = async (sIdx: number, qIdx: number) => {
        await flushTimeForCurrentQuestion();
        setCurrentSectionIdx(sIdx);
        setCurrentQuestionIdx(qIdx);
        setShowMobilePalette(false);
    };

    if (loading) {
        return (
            <div className="min-h-screen bg-gray-100 flex items-center justify-center">
                <div className="text-center">
                    <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-orange-600 mx-auto"></div>
                    <p className="mt-4 text-gray-500 font-medium">Loading test...</p>
                </div>
            </div>
        );
    }

    if (!testId || sections.length === 0) {
        return (
            <div className="min-h-screen bg-gray-100 flex items-center justify-center">
                <div className="text-center max-w-md bg-white p-8 rounded-xl shadow-sm border">
                    <h2 className="text-xl font-bold text-gray-900 mb-2">No test loaded</h2>
                    <p className="text-gray-500 mb-4">Navigate to a test from your dashboard to start.</p>
                    <button onClick={() => navigate('/dashboard')} className="bg-orange-600 text-white px-6 py-2 rounded-lg font-bold">
                        Go to Dashboard
                    </button>
                </div>
            </div>
        );
    }

    const stats = getStats();

    // ─── Palette content (inline JSX, NOT a component, to preserve scroll position across re-renders) ───
    const paletteContent = (
        <>
            {/* Legend */}
            <div className="p-4 border-b border-gray-200 bg-gray-50">
                <div className="grid grid-cols-2 gap-2 text-xs">
                    <div className="flex items-center gap-2"><span className="w-5 h-5 rounded bg-green-500 inline-block"></span> Answered ({stats.answered})</div>
                    <div className="flex items-center gap-2"><span className="w-5 h-5 rounded bg-red-500 inline-block"></span> Not Answered ({stats.notAnswered})</div>
                    <div className="flex items-center gap-2"><span className="w-5 h-5 rounded bg-purple-500 inline-block"></span> Marked ({stats.marked})</div>
                    <div className="flex items-center gap-2"><span className="w-5 h-5 rounded bg-gray-200 border border-gray-300 inline-block"></span> Not Visited ({stats.notVisited})</div>
                </div>
            </div>

            {/* Section-wise question buttons */}
            <div className="flex-1 overflow-y-auto p-4">
                {sections.map((sec, sIdx) => (
                    <div key={sec.id} className="mb-5">
                        <p className="text-xs font-bold text-gray-500 uppercase mb-2 tracking-wider">{sec.name}</p>
                        <div className="grid grid-cols-5 gap-2">
                            {sec.questions?.map((q, qIdx) => {
                                const status = getQuestionStatus(q.id);
                                const isCurrent = sIdx === currentSectionIdx && qIdx === currentQuestionIdx;
                                return (
                                    <button
                                        key={q.id}
                                        onClick={() => jumpToQuestion(sIdx, qIdx)}
                                        className={`w-9 h-9 rounded text-xs font-bold flex items-center justify-center border transition-all
                                            ${statusColors[status]}
                                            ${isCurrent ? 'ring-2 ring-orange-500 ring-offset-1 scale-110' : 'hover:scale-105'}
                                        `}
                                    >
                                        {getFlatIndex(sIdx, qIdx) + 1}
                                    </button>
                                );
                            })}
                        </div>
                    </div>
                ))}
            </div>

            {/* Submit button at bottom of palette */}
            <div className="p-4 border-t border-gray-200 bg-white">
                <button
                    onClick={() => handleSubmit()}
                    disabled={submitting}
                    className="w-full bg-red-600 hover:bg-red-700 text-white font-bold py-3 rounded-lg text-sm transition-colors disabled:opacity-50"
                >
                    {submitting ? 'Submitting...' : 'Submit Test'}
                </button>
            </div>
        </>
    );

    return (
        <div className="flex flex-col h-screen bg-gray-100">
            {/* ─── Header ─── */}
            <header className="sticky top-0 z-50 bg-slate-800 text-white shadow-lg">
                <div className="flex items-center justify-between px-4 py-2.5">
                    {/* Left: Test title */}
                    <div className="flex items-center gap-3 min-w-0">
                        <button onClick={() => { if (confirm('Leave test? Your progress is saved.')) navigate('/dashboard'); }} className="text-gray-300 hover:text-white flex-shrink-0">
                            <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M10 19l-7-7m0 0l7-7m-7 7h18" /></svg>
                        </button>
                        <div className="min-w-0">
                            <h1 className="text-sm font-bold truncate">{testTitle}</h1>
                            <p className="text-[10px] text-gray-400 truncate">{currentSection?.name || ''} • Q{getFlatIndex(currentSectionIdx, currentQuestionIdx) + 1} of {totalQuestions}</p>
                        </div>
                    </div>

                    {/* Center: Timer */}
                    <div className="flex items-center gap-3">
                        <div ref={timerContainerRef} className={`flex items-center gap-2 px-4 py-2 rounded-lg font-mono text-lg font-black tracking-wider ${timeLeft < 300 ? 'bg-red-600/80 text-red-100 animate-pulse' : 'bg-slate-700 text-white'}`}>
                            <svg className="w-4 h-4" fill="currentColor" viewBox="0 0 20 20"><path fillRule="evenodd" d="M10 18a8 8 0 100-16 8 8 0 000 16zm1-12a1 1 0 10-2 0v4a1 1 0 00.293.707l2.828 2.829a1 1 0 101.415-1.415L11 9.586V6z" clipRule="evenodd" /></svg>
                            <span ref={timerDisplayRef}>{formatTime(timeLeft)}</span>
                        </div>
                    </div>

                    {/* Right: Pause + Submit */}
                    <div className="flex items-center gap-2">
                        <button
                            onClick={handlePause}
                            className="hidden sm:flex items-center gap-1.5 bg-slate-700 hover:bg-slate-600 px-3 py-2 rounded-lg text-xs font-bold transition-colors"
                        >
                            <svg className="w-4 h-4" fill="currentColor" viewBox="0 0 20 20"><path fillRule="evenodd" d="M18 10a8 8 0 11-16 0 8 8 0 0116 0zM7 8a1 1 0 012 0v4a1 1 0 11-2 0V8zm5-1a1 1 0 00-1 1v4a1 1 0 102 0V8a1 1 0 00-1-1z" clipRule="evenodd" /></svg>
                            Pause
                        </button>
                        <button
                            onClick={() => handleSubmit()}
                            className="hidden sm:flex items-center gap-1.5 bg-red-600 hover:bg-red-700 px-3 py-2 rounded-lg text-xs font-bold transition-colors"
                        >
                            Submit
                        </button>
                        {/* Mobile palette toggle */}
                        <button onClick={() => setShowMobilePalette(!showMobilePalette)} className="md:hidden bg-slate-700 hover:bg-slate-600 p-2 rounded-lg">
                            <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M4 6a2 2 0 012-2h2a2 2 0 012 2v2a2 2 0 01-2 2H6a2 2 0 01-2-2V6zM14 6a2 2 0 012-2h2a2 2 0 012 2v2a2 2 0 01-2 2h-2a2 2 0 01-2-2V6zM4 16a2 2 0 012-2h2a2 2 0 012 2v2a2 2 0 01-2 2H6a2 2 0 01-2-2v-2zM14 16a2 2 0 012-2h2a2 2 0 012 2v2a2 2 0 01-2 2h-2a2 2 0 01-2-2v-2z" /></svg>
                        </button>
                    </div>
                </div>

                {/* Section tabs */}
                <div className="flex overflow-x-auto border-t border-slate-700 scrollbar-hide">
                    {sections.map((section, idx) => (
                        <button key={section.id} onClick={() => { setCurrentSectionIdx(idx); setCurrentQuestionIdx(0); }}
                            className={`flex-none px-5 py-2.5 text-xs font-bold uppercase tracking-wide border-b-2 transition-colors ${idx === currentSectionIdx ? 'border-orange-500 text-orange-400 bg-slate-700/50' : 'border-transparent text-gray-400 hover:text-gray-300'}`}>
                            {section.name}
                        </button>
                    ))}
                </div>
            </header>

            {/* ─── Main Content: Question + Sidebar ─── */}
            <div className="flex-1 flex overflow-hidden">
                {/* Question Area */}
                <main className="flex-1 overflow-y-auto pb-24 md:pb-4">
                    {currentQuestion && (
                        <>
                            {/* Question meta bar */}
                            <div className="flex justify-between items-center px-5 py-3 bg-white border-b border-gray-200 text-sm">
                                <div className="flex items-center gap-2">
                                    <span className="bg-orange-100 text-orange-700 px-2.5 py-1 rounded-lg font-black text-sm">
                                        Q.{getFlatIndex(currentSectionIdx, currentQuestionIdx) + 1}
                                    </span>
                                    <span className="text-gray-500 font-medium">{currentSection?.name}</span>
                                </div>
                                <div className="flex items-center gap-3 text-xs font-bold">
                                    <span className="text-green-600 bg-green-50 px-2 py-1 rounded">+{currentSection?.marks_per_question || 1}</span>
                                    <span className="text-red-500 bg-red-50 px-2 py-1 rounded">-{negMarking}</span>
                                </div>
                            </div>

                            {/* Question body */}
                            <div className="p-5 md:p-8 bg-white mx-0 md:mx-4 md:mt-4 md:rounded-xl md:shadow-sm md:border border-gray-100">
                                <div className="text-base md:text-lg font-medium text-gray-900 leading-relaxed mb-6 prose prose-sm max-w-none"
                                    dangerouslySetInnerHTML={{ __html: currentQuestion.question_text.replace(/\*\*(.*?)\*\*/g, '<b>$1</b>').replace(/\n/g, '<br />') }} />

                                {currentQuestion.image_url && (
                                    <img src={currentQuestion.image_url.startsWith('http') ? currentQuestion.image_url : `${API_BASE}${currentQuestion.image_url}`}
                                        alt="Question" className="max-w-full rounded-lg mb-6 border" />
                                )}

                                <div className="space-y-3">
                                    {currentQuestion.options.map((opt, i) => (
                                        <label key={i}
                                            className={`flex items-center p-4 border-2 rounded-xl transition-all cursor-pointer ${answers[currentQuestion.id] === i
                                                ? 'bg-orange-50 border-orange-500 shadow-md'
                                                : 'bg-white border-gray-200 hover:border-orange-300 hover:bg-orange-25'
                                                }`}
                                            onClick={() => selectOption(i)}>
                                            <div className={`w-6 h-6 rounded-full border-2 flex-shrink-0 flex items-center justify-center mr-4 ${answers[currentQuestion.id] === i ? 'border-orange-600 bg-orange-600' : 'border-gray-300 bg-white'}`}>
                                                {answers[currentQuestion.id] === i && <div className="w-2.5 h-2.5 rounded-full bg-white"></div>}
                                            </div>
                                            <span className={`text-sm md:text-base font-medium ${answers[currentQuestion.id] === i ? 'text-orange-900' : 'text-gray-700'}`}>
                                                <span className="font-bold text-gray-400 mr-2">{String.fromCharCode(65 + i)}.</span>
                                                {opt.option_text}
                                            </span>
                                        </label>
                                    ))}
                                </div>
                            </div>

                            {/* Desktop action buttons below question */}
                            <div className="hidden md:flex items-center justify-between px-4 py-4 mt-2">
                                <div className="flex gap-2">
                                    <button onClick={clearSelection}
                                        className="px-4 py-2.5 bg-white border border-gray-300 rounded-lg text-sm font-semibold text-gray-600 hover:bg-gray-50 transition-colors">
                                        Clear Response
                                    </button>
                                    <button onClick={toggleMark}
                                        className={`px-4 py-2.5 rounded-lg text-sm font-semibold transition-colors border ${currentQuestion && markedForReview.has(currentQuestion.id)
                                            ? 'bg-purple-100 border-purple-300 text-purple-700'
                                            : 'bg-purple-50 border-purple-200 text-purple-600 hover:bg-purple-100'
                                            }`}>
                                        {currentQuestion && markedForReview.has(currentQuestion.id) ? '★ Marked' : '☆ Mark for Review'}
                                    </button>
                                </div>
                                <div className="flex gap-2">
                                    <button onClick={goPrev}
                                        className="px-5 py-2.5 bg-white border border-gray-300 rounded-lg text-sm font-semibold text-gray-600 hover:bg-gray-50 transition-colors">
                                        ← Previous
                                    </button>
                                    <button onClick={goNext}
                                        className="px-5 py-2.5 bg-orange-600 hover:bg-orange-700 text-white rounded-lg text-sm font-bold transition-colors shadow-md shadow-orange-600/20">
                                        Save & Next →
                                    </button>
                                </div>
                            </div>
                        </>
                    )}
                </main>

                {/* ─── Desktop Sidebar: Question Palette (always visible on md+) ─── */}
                <aside className="hidden md:flex flex-col w-72 lg:w-80 bg-white border-l border-gray-200 shadow-inner">
                    {paletteContent}
                </aside>
            </div>

            {/* ─── Mobile Footer ─── */}
            <footer className="md:hidden fixed bottom-0 w-full bg-white border-t border-gray-200 shadow-[0_-4px_12px_rgba(0,0,0,0.08)] z-30">
                <div className="flex px-3 py-2.5 gap-2">
                    <button onClick={goPrev}
                        className="flex-1 flex items-center justify-center gap-1 py-2.5 bg-gray-100 hover:bg-gray-200 rounded-xl transition-colors border border-gray-200">
                        <svg className="w-4 h-4 text-gray-500" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M15 19l-7-7 7-7" /></svg>
                        <span className="text-xs font-bold text-gray-600">Prev</span>
                    </button>
                    <button onClick={clearSelection}
                        className="flex-1 flex items-center justify-center gap-1 py-2.5 bg-gray-100 hover:bg-gray-200 rounded-xl transition-colors border border-gray-200">
                        <span className="text-xs font-bold text-gray-600">Clear</span>
                    </button>
                    <button onClick={toggleMark}
                        className={`flex-1 flex items-center justify-center gap-1 py-2.5 rounded-xl transition-colors border ${currentQuestion && markedForReview.has(currentQuestion.id)
                            ? 'bg-purple-100 border-purple-300' : 'bg-purple-50 border-purple-200'}`}>
                        <span className="text-xs font-bold text-purple-700">Mark</span>
                    </button>
                    <button onClick={goNext}
                        className="flex-[2] flex items-center justify-center gap-1 py-2.5 bg-orange-600 hover:bg-orange-700 rounded-xl transition-colors shadow-lg shadow-orange-600/30">
                        <span className="text-xs font-bold text-white">Save & Next</span>
                        <svg className="w-4 h-4 text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 5l7 7-7 7" /></svg>
                    </button>
                </div>
            </footer>

            {/* ─── Mobile Palette Bottom Sheet ─── */}
            {showMobilePalette && (
                <div className="md:hidden fixed inset-0 z-40 bg-black/50" onClick={() => setShowMobilePalette(false)}>
                    <div className="absolute bottom-0 inset-x-0 bg-white rounded-t-2xl max-h-[75vh] overflow-hidden flex flex-col animate-slide-up"
                        onClick={e => e.stopPropagation()}>
                        <div className="flex items-center justify-between p-4 border-b border-gray-200">
                            <h3 className="text-lg font-bold text-gray-900">Question Palette</h3>
                            <button onClick={() => setShowMobilePalette(false)} className="p-1 rounded-full hover:bg-gray-100">
                                <svg className="w-5 h-5 text-gray-500" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M6 18L18 6M6 6l12 12" /></svg>
                            </button>
                        </div>
                        <div className="flex-1 overflow-y-auto flex flex-col">
                            {paletteContent}
                        </div>
                    </div>
                </div>
            )}

            {/* ─── Pause Overlay ─── */}
            {isPaused && (
                <div className="fixed inset-0 z-50 bg-slate-900/90 backdrop-blur-sm flex items-center justify-center">
                    <div className="bg-white rounded-2xl p-8 text-center max-w-sm mx-4 shadow-2xl">
                        <div className="w-16 h-16 bg-orange-100 rounded-full flex items-center justify-center mx-auto mb-4">
                            <svg className="w-8 h-8 text-orange-600" fill="currentColor" viewBox="0 0 20 20"><path fillRule="evenodd" d="M18 10a8 8 0 11-16 0 8 8 0 0116 0zM7 8a1 1 0 012 0v4a1 1 0 11-2 0V8zm5-1a1 1 0 00-1 1v4a1 1 0 102 0V8a1 1 0 00-1-1z" clipRule="evenodd" /></svg>
                        </div>
                        <h2 className="text-2xl font-black text-gray-900 mb-2">Test Paused</h2>
                        <p className="text-gray-500 mb-1">Time remaining: <span className="font-bold text-gray-900">{formatTime(timeLeft)}</span></p>
                        <p className="text-gray-500 mb-4 text-sm">Questions answered: <span className="font-bold text-gray-900">{stats.answered}/{totalQuestions}</span></p>
                        <div className="flex items-center gap-2 bg-green-50 border border-green-200 rounded-lg px-3 py-2 mb-6">
                            <svg className="w-4 h-4 text-green-600 flex-shrink-0" fill="currentColor" viewBox="0 0 20 20"><path fillRule="evenodd" d="M10 18a8 8 0 100-16 8 8 0 000 16zm3.707-9.293a1 1 0 00-1.414-1.414L9 10.586 7.707 9.293a1 1 0 00-1.414 1.414l2 2a1 1 0 001.414 0l4-4z" clipRule="evenodd" /></svg>
                            <p className="text-green-700 text-xs font-medium text-left">Your progress is saved. You can exit and resume this test later.</p>
                        </div>
                        <button
                            onClick={handleResume}
                            className="w-full bg-orange-600 hover:bg-orange-700 text-white font-black py-3.5 rounded-xl text-lg transition-colors shadow-lg shadow-orange-600/30 mb-3"
                        >
                            ▶ Resume Test
                        </button>
                        <button
                            onClick={() => navigate('/dashboard')}
                            className="w-full bg-gray-100 hover:bg-gray-200 text-gray-700 font-bold py-3 rounded-xl text-sm transition-colors border border-gray-200"
                        >
                            ← Exit to Dashboard
                        </button>
                    </div>
                </div>
            )}

            <style>{`
                .scrollbar-hide::-webkit-scrollbar { display: none; }
                .scrollbar-hide { -ms-overflow-style: none; scrollbar-width: none; }
                @keyframes slide-up { from { transform: translateY(100%); } to { transform: translateY(0); } }
                .animate-slide-up { animation: slide-up 0.3s ease-out; }
            `}</style>
        </div>
    );
};
