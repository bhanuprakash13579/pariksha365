import React, { useState, useEffect, useRef } from 'react';
import {
    View, Text, ScrollView, TouchableOpacity, ActivityIndicator,
    SafeAreaView, Modal, Platform,
} from 'react-native';
import { Ionicons } from '@expo/vector-icons';
import { SvgXml } from 'react-native-svg';
import { QuizAPI, PrivateModuleAPI, FlaggedAPI } from '../../services/api';
import { COLORS } from '../../styles/theme';

function renderExplanationMobile(text: string, baseStyle: object) {
    return text.split('\n').map((line, i) => {
        const parts = line.split(/\*\*(.*?)\*\*/g);
        return (
            <Text key={i} style={baseStyle}>
                {parts.map((p, j) => j % 2 === 1
                    ? <Text key={j} style={{ fontWeight: 'bold' }}>{p}</Text>
                    : p
                )}
            </Text>
        );
    });
}

interface QuizQuestion {
    id: string;
    question_text: string;
    diagram_svg?: string;
    explanation?: string;
    explanation_svg?: string;
    options: { option_text: string; is_correct?: boolean }[];
    subject?: string;
    topic?: string;
}

// ── review filter ──────────────────────────────────────────────────────────
type ReviewFilter = 'all' | 'wrong' | 'skipped';

export default function QuizSessionScreen({ navigation, route }: any) {
    const { subject, limit = 10, title = 'Daily Quiz', moduleSlug, weakTopicMode = false } = route.params || {};

    const QUIZ_DURATION = 5 * 60; // 300 seconds
    const [questions, setQuestions] = useState<QuizQuestion[]>([]);
    const [currentIdx, setCurrentIdx] = useState(0);
    const [selectedAnswers, setSelectedAnswers] = useState<Record<number, number | null>>({});
    const [loading, setLoading] = useState(true);
    const [submitted, setSubmitted] = useState(false);
    const [scorecard, setScorecard] = useState<any>(null);
    const [showReview, setShowReview] = useState(false);
    const [reviewFilter, setReviewFilter] = useState<ReviewFilter>('all');
    const [submitting, setSubmitting] = useState(false);
    const [timeLeft, setTimeLeft] = useState(QUIZ_DURATION);
    const [isPaused, setIsPaused] = useState(false);
    const timerRef = useRef<ReturnType<typeof setInterval> | null>(null);
    const [flaggedIds, setFlaggedIds] = useState<Set<string>>(new Set());
    const questionSource = moduleSlug ? 'private_module' : 'quiz';

    // ── load questions ─────────────────────────────────────────────────────
    useEffect(() => {
        setCurrentIdx(0);
        setSelectedAnswers({});
        setSubmitted(false);
        setScorecard(null);
        setLoading(true);
        setIsPaused(false);

        const fetchQuiz = async () => {
            try {
                let res;
                if (moduleSlug) {
                    res = await PrivateModuleAPI.getQuiz(moduleSlug, subject, limit);
                } else if (weakTopicMode) {
                    res = await QuizAPI.getWeakTopicQuiz(limit);
                } else {
                    res = await QuizAPI.getDailyQuiz(subject, limit);
                }
                setQuestions(res.data?.questions || res.data || []);
            } catch (err) {
                console.error('Failed to fetch quiz:', err);
            } finally {
                setLoading(false);
            }
        };
        fetchQuiz();
    }, [subject, limit, moduleSlug, weakTopicMode]);

    // ── timer ──────────────────────────────────────────────────────────────
    useEffect(() => {
        if (!loading && questions.length > 0 && !submitted) {
            setTimeLeft(QUIZ_DURATION);
        }
    }, [loading, questions.length]);

    useEffect(() => {
        if (loading || submitted || questions.length === 0) return;

        if (isPaused) {
            if (timerRef.current) clearInterval(timerRef.current);
            return;
        }

        timerRef.current = setInterval(() => {
            setTimeLeft(prev => {
                if (prev <= 1) {
                    clearInterval(timerRef.current!);
                    return 0;
                }
                return prev - 1;
            });
        }, 1000);

        return () => { if (timerRef.current) clearInterval(timerRef.current); };
    }, [loading, questions.length, submitted, isPaused]);

    // ── auto-submit at 0 ──────────────────────────────────────────────────
    useEffect(() => {
        if (timeLeft === 0 && !submitted && !loading && questions.length > 0) {
            handleSubmit();
        }
    }, [timeLeft]);

    // ── stop timer after submit ────────────────────────────────────────────
    useEffect(() => {
        if (submitted && timerRef.current) clearInterval(timerRef.current);
    }, [submitted]);

    const formatTime = (secs: number) => {
        const m = Math.floor(secs / 60).toString().padStart(2, '0');
        const s = (secs % 60).toString().padStart(2, '0');
        return `${m}:${s}`;
    };

    const togglePause = () => setIsPaused(p => !p);

    // ── local tally (used when server scorecard is missing fields) ─────────
    const computeLocalTally = () => {
        let correct = 0, wrong = 0, skipped = 0;
        questions.forEach((q, idx) => {
            const sel = selectedAnswers[idx];
            if (sel === undefined || sel === null) { skipped++; return; }
            if (q.options[sel]?.is_correct) correct++; else wrong++;
        });
        return { correct, wrong, skipped, total: questions.length };
    };

    const selectOption = (optionIndex: number) => {
        if (submitted) return;
        setSelectedAnswers(prev => ({ ...prev, [currentIdx]: optionIndex }));
    };

    const goNext = () => { if (currentIdx < questions.length - 1) setCurrentIdx(p => p + 1); };
    const goPrev = () => { if (currentIdx > 0) setCurrentIdx(p => p - 1); };

    const handleSubmit = async () => {
        if (submitting) return;
        setSubmitting(true);
        const local = computeLocalTally();
        try {
            const answersPayload = questions.map((q, idx) => ({
                question_id: q.id,
                selected_option_index: selectedAnswers[idx] ?? null,
            }));
            let res;
            if (moduleSlug) {
                res = await PrivateModuleAPI.submitQuiz(moduleSlug, answersPayload);
            } else {
                res = await QuizAPI.submitQuiz(answersPayload);
            }
            // Merge server data with local tally so counts are always present
            const server = res.data || {};
            setScorecard({
                ...server,
                correct: server.correct ?? local.correct,
                wrong: server.wrong ?? local.wrong,
                skipped: server.skipped ?? local.skipped,
                total: server.total ?? local.total,
                score_percentage: server.score_percentage
                    ?? (local.total > 0 ? Math.round((local.correct / local.total) * 100) : 0),
            });
            setSubmitted(true);
        } catch {
            setScorecard({
                ...local,
                score_percentage: local.total > 0 ? Math.round((local.correct / local.total) * 100) : 0,
            });
            setSubmitted(true);
        } finally {
            setSubmitting(false);
        }
    };

    // ── loading ────────────────────────────────────────────────────────────
    if (loading) {
        return (
            <View style={{ flex: 1, backgroundColor: '#f9fafb', justifyContent: 'center', alignItems: 'center' }}>
                <ActivityIndicator size="large" color={COLORS.primary} />
                <Text style={{ color: '#6b7280', marginTop: 12 }}>Loading quiz...</Text>
            </View>
        );
    }

    if (questions.length === 0) {
        return (
            <SafeAreaView style={{ flex: 1, backgroundColor: '#f9fafb', justifyContent: 'center', alignItems: 'center', padding: 20 }}>
                <Ionicons name="help-circle-outline" size={48} color="#9ca3af" />
                <Text style={{ fontSize: 18, fontWeight: 'bold', color: '#111827', marginTop: 12 }}>No Questions Available</Text>
                <Text style={{ color: '#6b7280', marginTop: 4, textAlign: 'center' }}>Try a different category or check back later.</Text>
                <TouchableOpacity onPress={() => navigation.goBack()}
                    style={{ marginTop: 20, backgroundColor: COLORS.primary, paddingHorizontal: 24, paddingVertical: 12, borderRadius: 10 }}>
                    <Text style={{ color: '#fff', fontWeight: 'bold' }}>Go Back</Text>
                </TouchableOpacity>
            </SafeAreaView>
        );
    }

    // ── SCORECARD VIEW ─────────────────────────────────────────────────────
    if (submitted && scorecard) {
        const correct = scorecard.correct ?? 0;
        const wrong = scorecard.wrong ?? 0;
        const skipped = scorecard.skipped ?? 0;
        const total = scorecard.total ?? questions.length;
        const scorePct = scorecard.score_percentage
            ?? (total > 0 ? Math.round((correct / total) * 100) : 0);
        const isGood = scorePct >= 70;

        // Which questions pass the filter
        const filteredIndices = questions
            .map((q, idx) => {
                const sel = selectedAnswers[idx];
                const isSkipped = sel === undefined || sel === null;
                const isWrong = !isSkipped && !q.options[sel!]?.is_correct;
                return { q, idx, isSkipped, isWrong };
            })
            .filter(({ isSkipped, isWrong }) => {
                if (reviewFilter === 'wrong') return isWrong;
                if (reviewFilter === 'skipped') return isSkipped;
                return true;
            });

        return (
            <SafeAreaView style={{ flex: 1, backgroundColor: '#f0f2f5' }}>
                <ScrollView contentContainerStyle={{ paddingBottom: 40 }}>

                    {/* ── Score Header ── */}
                    <View style={{
                        backgroundColor: isGood ? '#16a34a' : COLORS.primary,
                        paddingTop: 32, paddingBottom: 28, paddingHorizontal: 20,
                        alignItems: 'center',
                    }}>
                        <Text style={{ fontSize: 13, color: 'rgba(255,255,255,0.8)', fontWeight: '600', letterSpacing: 1, textTransform: 'uppercase', marginBottom: 8 }}>
                            {title}
                        </Text>
                        <Text style={{ fontSize: 64, fontWeight: '900', color: '#fff', lineHeight: 72 }}>{scorePct}%</Text>
                        <Text style={{ fontSize: 16, color: 'rgba(255,255,255,0.9)', fontWeight: '600', marginTop: 4 }}>
                            {isGood ? '🎉 Excellent!' : scorePct >= 50 ? '👍 Good effort!' : '📚 Keep practicing!'}
                        </Text>
                        <Text style={{ fontSize: 13, color: 'rgba(255,255,255,0.75)', marginTop: 6 }}>
                            {correct} correct out of {total} questions
                        </Text>
                    </View>

                    {/* ── Stats Row ── */}
                    <View style={{ flexDirection: 'row', margin: 16, gap: 10 }}>
                        {[
                            { label: 'Correct', value: correct, color: '#16a34a', bg: '#f0fdf4', border: '#bbf7d0', icon: 'checkmark-circle' },
                            { label: 'Wrong', value: wrong, color: '#dc2626', bg: '#fef2f2', border: '#fecaca', icon: 'close-circle' },
                            { label: 'Skipped', value: skipped, color: '#6b7280', bg: '#f9fafb', border: '#e5e7eb', icon: 'remove-circle' },
                        ].map((item, idx) => (
                            <View key={idx} style={{
                                flex: 1, backgroundColor: item.bg, borderRadius: 16, padding: 16,
                                alignItems: 'center', borderWidth: 1.5, borderColor: item.border,
                            }}>
                                <Ionicons name={item.icon as any} size={24} color={item.color} />
                                <Text style={{ fontSize: 32, fontWeight: '900', color: item.color, marginTop: 6 }}>{item.value}</Text>
                                <Text style={{ fontSize: 11, fontWeight: '700', color: item.color, opacity: 0.8, marginTop: 2 }}>{item.label}</Text>
                            </View>
                        ))}
                    </View>

                    {/* ── Focus Areas ── */}
                    {scorecard.focus_areas?.length > 0 && (
                        <View style={{ marginHorizontal: 16, marginBottom: 12 }}>
                            <Text style={{ fontSize: 14, fontWeight: '800', color: '#111827', marginBottom: 10 }}>🎯 Focus Areas</Text>
                            {scorecard.focus_areas.map((area: string, idx: number) => (
                                <View key={idx} style={{
                                    backgroundColor: '#fff', borderRadius: 10, padding: 12, marginBottom: 6,
                                    borderWidth: 1, borderColor: '#fecaca', flexDirection: 'row', alignItems: 'center',
                                }}>
                                    <Ionicons name="flag" size={14} color="#ef4444" style={{ marginRight: 8 }} />
                                    <Text style={{ color: '#374151', fontSize: 13, fontWeight: '500', flex: 1 }}>{area}</Text>
                                </View>
                            ))}
                        </View>
                    )}

                    {/* ── Nudge ── */}
                    {scorecard.nudge_message && (
                        <View style={{
                            backgroundColor: '#eff6ff', borderWidth: 1, borderColor: '#bfdbfe',
                            borderRadius: 12, padding: 14, marginHorizontal: 16, marginBottom: 12,
                        }}>
                            <Text style={{ color: '#1e40af', fontSize: 13, fontWeight: '500' }}>💡 {scorecard.nudge_message}</Text>
                        </View>
                    )}

                    {/* ── Action Buttons ── */}
                    <View style={{ paddingHorizontal: 16, gap: 10, marginBottom: 16 }}>
                        <TouchableOpacity
                            onPress={() => navigation.goBack()}
                            style={{
                                backgroundColor: COLORS.primary, borderRadius: 14, paddingVertical: 16, alignItems: 'center',
                                shadowColor: COLORS.primary, shadowOpacity: 0.3, shadowRadius: 8, shadowOffset: { width: 0, height: 4 }, elevation: 5,
                            }}
                        >
                            <Text style={{ color: '#fff', fontWeight: '700', fontSize: 16 }}>Back to Categories</Text>
                        </TouchableOpacity>
                    </View>

                    {/* ── Review Section ── */}
                    <TouchableOpacity
                        onPress={() => setShowReview(v => !v)}
                        style={{
                            marginHorizontal: 16, borderRadius: 14, paddingVertical: 14,
                            alignItems: 'center', marginBottom: 12, borderWidth: 1,
                            borderColor: '#e5e7eb', backgroundColor: '#fff',
                            flexDirection: 'row', justifyContent: 'center', gap: 8,
                        }}
                    >
                        <Ionicons name={showReview ? 'chevron-up' : 'list'} size={16} color="#374151" />
                        <Text style={{ color: '#374151', fontWeight: '600', fontSize: 14 }}>
                            {showReview ? 'Hide Review' : 'Review Answers'}
                        </Text>
                    </TouchableOpacity>

                    {showReview && (
                        <View style={{ paddingHorizontal: 16 }}>
                            {/* Filter Tabs */}
                            <View style={{
                                flexDirection: 'row', backgroundColor: '#f3f4f6',
                                borderRadius: 12, padding: 4, marginBottom: 14, gap: 4,
                            }}>
                                {([
                                    { key: 'all', label: `All (${total})` },
                                    { key: 'wrong', label: `Wrong (${wrong})` },
                                    { key: 'skipped', label: `Skipped (${skipped})` },
                                ] as { key: ReviewFilter; label: string }[]).map(tab => (
                                    <TouchableOpacity
                                        key={tab.key}
                                        onPress={() => setReviewFilter(tab.key)}
                                        style={{
                                            flex: 1, paddingVertical: 8, borderRadius: 10, alignItems: 'center',
                                            backgroundColor: reviewFilter === tab.key ? '#fff' : 'transparent',
                                            shadowColor: reviewFilter === tab.key ? '#000' : 'transparent',
                                            shadowOpacity: 0.08, shadowRadius: 4, elevation: reviewFilter === tab.key ? 2 : 0,
                                        }}
                                    >
                                        <Text style={{
                                            fontSize: 12, fontWeight: '700',
                                            color: reviewFilter === tab.key
                                                ? (tab.key === 'wrong' ? '#dc2626' : tab.key === 'skipped' ? '#6b7280' : COLORS.primary)
                                                : '#9ca3af',
                                        }}>
                                            {tab.label}
                                        </Text>
                                    </TouchableOpacity>
                                ))}
                            </View>

                            {filteredIndices.length === 0 ? (
                                <View style={{ alignItems: 'center', padding: 32 }}>
                                    <Ionicons name="checkmark-done-circle" size={48} color="#22c55e" />
                                    <Text style={{ color: '#6b7280', marginTop: 8, fontWeight: '600' }}>
                                        {reviewFilter === 'wrong' ? 'No wrong answers! 🎉' : 'No skipped questions!'}
                                    </Text>
                                </View>
                            ) : (
                                filteredIndices.map(({ q, idx, isSkipped, isWrong }) => {
                                    const selIdx = selectedAnswers[idx];
                                    const isFlagged = flaggedIds.has(q.id);

                                    const toggleFlag = async () => {
                                        try {
                                            if (isFlagged) {
                                                await FlaggedAPI.unflag(questionSource, q.id);
                                                setFlaggedIds(prev => { const s = new Set(prev); s.delete(q.id); return s; });
                                            } else {
                                                await FlaggedAPI.flag(questionSource, q.id);
                                                setFlaggedIds(prev => new Set(prev).add(q.id));
                                            }
                                        } catch { /* silent */ }
                                    };

                                    // Status badge
                                    const status = isSkipped ? 'SKIPPED' : isWrong ? 'WRONG' : 'CORRECT';
                                    const statusColor = isSkipped ? '#6b7280' : isWrong ? '#dc2626' : '#16a34a';
                                    const statusBg = isSkipped ? '#f3f4f6' : isWrong ? '#fef2f2' : '#f0fdf4';

                                    return (
                                        <View key={q.id} style={{
                                            backgroundColor: '#fff', borderRadius: 14, padding: 16,
                                            marginBottom: 12, borderWidth: 1,
                                            borderColor: isWrong ? '#fecaca' : isSkipped ? '#e5e7eb' : '#bbf7d0',
                                        }}>
                                            {/* Question header row */}
                                            <View style={{ flexDirection: 'row', alignItems: 'flex-start', marginBottom: 12 }}>
                                                <View style={{ flex: 1 }}>
                                                    <View style={{ flexDirection: 'row', alignItems: 'center', marginBottom: 6 }}>
                                                        <Text style={{ fontSize: 11, fontWeight: '700', color: statusColor, backgroundColor: statusBg, paddingHorizontal: 8, paddingVertical: 3, borderRadius: 6 }}>
                                                            {status}
                                                        </Text>
                                                        <Text style={{ fontSize: 11, color: '#9ca3af', marginLeft: 6 }}>Q{idx + 1}</Text>
                                                    </View>
                                                    <Text style={{ fontSize: 13, fontWeight: '600', color: '#111827', lineHeight: 20, paddingRight: 8 }}>
                                                        {q.question_text}
                                                    </Text>
                                                </View>
                                                <TouchableOpacity onPress={toggleFlag} hitSlop={{ top: 8, bottom: 8, left: 8, right: 8 }}>
                                                    <Ionicons
                                                        name={isFlagged ? 'bookmark' : 'bookmark-outline'}
                                                        size={22}
                                                        color={isFlagged ? COLORS.primary : '#d1d5db'}
                                                    />
                                                </TouchableOpacity>
                                            </View>

                                            {/* Options */}
                                            {q.options.map((opt, i) => {
                                                const isCorrect = opt.is_correct;
                                                const isSelected = selIdx === i;
                                                const bg = isCorrect ? '#f0fdf4' : isSelected ? '#fef2f2' : '#f9fafb';
                                                const border = isCorrect ? '#22c55e' : isSelected ? '#ef4444' : '#e5e7eb';
                                                return (
                                                    <View key={i} style={{
                                                        flexDirection: 'row', alignItems: 'flex-start', backgroundColor: bg,
                                                        borderWidth: 1.5, borderColor: border, borderRadius: 10,
                                                        paddingHorizontal: 10, paddingVertical: 9, marginBottom: 6,
                                                    }}>
                                                        <Text style={{ fontSize: 12, fontWeight: 'bold', color: '#6b7280', marginRight: 6, marginTop: 1 }}>
                                                            {String.fromCharCode(65 + i)}.
                                                        </Text>
                                                        <Text style={{ fontSize: 12, color: '#374151', flex: 1, lineHeight: 18 }}>{opt.option_text}</Text>
                                                        {isCorrect && <Ionicons name="checkmark-circle" size={16} color="#16a34a" style={{ marginLeft: 4, marginTop: 1 }} />}
                                                        {isSelected && !isCorrect && <Ionicons name="close-circle" size={16} color="#dc2626" style={{ marginLeft: 4, marginTop: 1 }} />}
                                                        {isSkipped && isCorrect && <Text style={{ fontSize: 10, color: '#16a34a', fontWeight: '700', marginLeft: 4, marginTop: 2 }}>ANSWER</Text>}
                                                    </View>
                                                );
                                            })}

                                            {/* Explanation */}
                                            {q.explanation ? (
                                                <View style={{ backgroundColor: '#eff6ff', borderRadius: 10, padding: 12, marginTop: 8, borderWidth: 1, borderColor: '#bfdbfe' }}>
                                                    <Text style={{ fontSize: 11, fontWeight: '700', color: '#1d4ed8', marginBottom: 4 }}>💡 Explanation</Text>
                                                    {renderExplanationMobile(q.explanation, { fontSize: 12, color: '#1e40af', lineHeight: 18 })}
                                                </View>
                                            ) : null}
                                            {q.explanation_svg ? (
                                                <SvgXml xml={q.explanation_svg} width="100%" height={200} style={{ marginTop: 10 }} />
                                            ) : null}
                                        </View>
                                    );
                                })
                            )}
                        </View>
                    )}
                </ScrollView>
            </SafeAreaView>
        );
    }

    // ── QUIZ QUESTION VIEW ─────────────────────────────────────────────────
    const currentQ = questions[currentIdx];
    const answeredCount = Object.values(selectedAnswers).filter(v => v !== null && v !== undefined).length;
    const isLast = currentIdx === questions.length - 1;
    const timerCritical = timeLeft < 60;

    return (
        <SafeAreaView style={{ flex: 1, backgroundColor: '#f9fafb' }}>

            {/* ── Pause Overlay ── */}
            {isPaused && (
                <Modal transparent animationType="fade" visible>
                    <View style={{
                        flex: 1, backgroundColor: 'rgba(0,0,0,0.65)',
                        alignItems: 'center', justifyContent: 'center',
                    }}>
                        <View style={{
                            backgroundColor: '#fff', borderRadius: 24, padding: 32,
                            alignItems: 'center', width: '78%',
                            shadowColor: '#000', shadowOpacity: 0.25, shadowRadius: 20, elevation: 16,
                        }}>
                            <View style={{
                                width: 64, height: 64, borderRadius: 32,
                                backgroundColor: '#f3f4f6', alignItems: 'center', justifyContent: 'center', marginBottom: 16,
                            }}>
                                <Ionicons name="pause" size={32} color={COLORS.primary} />
                            </View>
                            <Text style={{ fontSize: 22, fontWeight: '900', color: '#111827', marginBottom: 6 }}>Quiz Paused</Text>
                            <Text style={{ fontSize: 13, color: '#6b7280', textAlign: 'center', marginBottom: 24 }}>
                                Timer is paused.{'\n'}Resume when you're ready.
                            </Text>
                            <TouchableOpacity
                                onPress={togglePause}
                                style={{
                                    backgroundColor: COLORS.primary, borderRadius: 14,
                                    paddingVertical: 14, paddingHorizontal: 40, alignItems: 'center',
                                    shadowColor: COLORS.primary, shadowOpacity: 0.35, shadowRadius: 8, elevation: 5,
                                }}
                            >
                                <Text style={{ color: '#fff', fontWeight: '800', fontSize: 16 }}>▶ Resume</Text>
                            </TouchableOpacity>
                            <TouchableOpacity
                                onPress={() => navigation.goBack()}
                                style={{ marginTop: 14, paddingVertical: 10, paddingHorizontal: 20 }}
                            >
                                <Text style={{ color: '#9ca3af', fontWeight: '600', fontSize: 13 }}>Exit Quiz</Text>
                            </TouchableOpacity>
                        </View>
                    </View>
                </Modal>
            )}

            {/* ── Header ── */}
            <View style={{
                backgroundColor: '#fff', paddingHorizontal: 16, paddingVertical: 12,
                borderBottomWidth: 1, borderBottomColor: '#e5e7eb',
                flexDirection: 'row', alignItems: 'center', justifyContent: 'space-between',
            }}>
                <TouchableOpacity onPress={() => navigation.goBack()} hitSlop={{ top: 8, bottom: 8, left: 8, right: 8 }}>
                    <Ionicons name="close" size={22} color="#374151" />
                </TouchableOpacity>

                <Text style={{ fontSize: 14, fontWeight: 'bold', color: '#111827', flex: 1, textAlign: 'center', marginHorizontal: 8 }} numberOfLines={1}>
                    {title}
                </Text>

                <View style={{ flexDirection: 'row', alignItems: 'center', gap: 8 }}>
                    {/* Timer */}
                    <View style={{
                        backgroundColor: timerCritical ? '#fee2e2' : '#f3f4f6',
                        paddingHorizontal: 8, paddingVertical: 4, borderRadius: 8,
                        flexDirection: 'row', alignItems: 'center', gap: 3,
                    }}>
                        <Ionicons name="time-outline" size={12} color={timerCritical ? '#dc2626' : '#6b7280'} />
                        <Text style={{ fontSize: 12, fontWeight: 'bold', color: timerCritical ? '#dc2626' : '#374151' }}>
                            {formatTime(timeLeft)}
                        </Text>
                    </View>

                    {/* Pause button */}
                    <TouchableOpacity
                        onPress={togglePause}
                        hitSlop={{ top: 8, bottom: 8, left: 8, right: 8 }}
                        style={{
                            width: 30, height: 30, borderRadius: 15, backgroundColor: '#f3f4f6',
                            alignItems: 'center', justifyContent: 'center',
                        }}
                    >
                        <Ionicons name="pause" size={14} color="#374151" />
                    </TouchableOpacity>

                    <Text style={{ fontSize: 12, color: '#6b7280', fontWeight: '600' }}>
                        {currentIdx + 1}/{questions.length}
                    </Text>
                </View>
            </View>

            {/* ── Progress Bar ── */}
            <View style={{ height: 3, backgroundColor: '#e5e7eb' }}>
                <View style={{
                    height: 3, backgroundColor: COLORS.primary,
                    width: `${((currentIdx + 1) / questions.length) * 100}%`,
                }} />
            </View>

            {/* ── Answered Pill ── */}
            <View style={{ paddingHorizontal: 16, paddingTop: 10, paddingBottom: 4 }}>
                <Text style={{ fontSize: 11, color: '#9ca3af', fontWeight: '600' }}>
                    {answeredCount} of {questions.length} answered
                    {selectedAnswers[currentIdx] !== undefined && selectedAnswers[currentIdx] !== null ? '' : '  ·  Not answered yet'}
                </Text>
            </View>

            <ScrollView style={{ flex: 1 }} contentContainerStyle={{ padding: 16, paddingBottom: 90 }}>
                {/* Question card */}
                <View style={{
                    backgroundColor: '#fff', borderRadius: 16, padding: 20,
                    marginBottom: 16, borderWidth: 1, borderColor: '#f3f4f6',
                    shadowColor: '#000', shadowOpacity: 0.04, shadowRadius: 8, elevation: 2,
                }}>
                    <Text style={{ fontSize: 15, fontWeight: '500', color: '#111827', lineHeight: 25 }}>
                        {currentQ.question_text}
                    </Text>
                </View>

                {/* Diagram */}
                {currentQ.diagram_svg && (
                    <SvgXml xml={currentQ.diagram_svg} width="100%" height={200} style={{ marginBottom: 16 }} />
                )}

                {/* Options */}
                {currentQ.options.map((opt, i) => {
                    const isSelected = selectedAnswers[currentIdx] === i;
                    return (
                        <TouchableOpacity
                            key={i}
                            onPress={() => selectOption(i)}
                            activeOpacity={0.7}
                            style={{
                                flexDirection: 'row', alignItems: 'flex-start',
                                padding: 14, borderRadius: 12, marginBottom: 10,
                                borderWidth: 2,
                                borderColor: isSelected ? COLORS.primary : '#e5e7eb',
                                backgroundColor: isSelected ? '#fff7ed' : '#fff',
                            }}
                        >
                            <View style={{
                                width: 20, height: 20, borderRadius: 10,
                                borderWidth: 2,
                                borderColor: isSelected ? COLORS.primary : '#d1d5db',
                                backgroundColor: isSelected ? COLORS.primary : '#fff',
                                alignItems: 'center', justifyContent: 'center', marginRight: 12, marginTop: 1,
                            }}>
                                {isSelected && <View style={{ width: 7, height: 7, borderRadius: 3.5, backgroundColor: '#fff' }} />}
                            </View>
                            <Text style={{
                                fontSize: 14, fontWeight: isSelected ? '600' : '400',
                                color: isSelected ? '#9a3412' : '#374151', flex: 1, lineHeight: 22,
                            }}>
                                <Text style={{ fontWeight: 'bold', color: '#9ca3af' }}>{String.fromCharCode(65 + i)}. </Text>
                                {opt.option_text}
                            </Text>
                        </TouchableOpacity>
                    );
                })}
            </ScrollView>

            {/* ── Bottom Navigation Bar ── */}
            <View style={{
                flexDirection: 'row', paddingHorizontal: 16, paddingVertical: 12, paddingBottom: 24,
                backgroundColor: '#fff', borderTopWidth: 1, borderTopColor: '#e5e7eb',
                shadowColor: '#000', shadowOpacity: 0.08, shadowRadius: 12, shadowOffset: { width: 0, height: -3 }, elevation: 10,
            }}>
                <TouchableOpacity
                    onPress={goPrev}
                    disabled={currentIdx === 0}
                    style={{
                        flex: 1, flexDirection: 'row', alignItems: 'center', justifyContent: 'center',
                        paddingVertical: 12, backgroundColor: currentIdx === 0 ? '#f3f4f6' : '#fff',
                        borderRadius: 12, marginRight: 8, borderWidth: 1, borderColor: '#e5e7eb',
                        opacity: currentIdx === 0 ? 0.5 : 1,
                    }}
                >
                    <Ionicons name="chevron-back" size={16} color="#4b5563" />
                    <Text style={{ color: '#4b5563', fontWeight: 'bold', fontSize: 14, marginLeft: 4 }}>Prev</Text>
                </TouchableOpacity>

                {isLast ? (
                    <TouchableOpacity
                        onPress={handleSubmit}
                        disabled={submitting}
                        style={{
                            flex: 2, alignItems: 'center', justifyContent: 'center',
                            paddingVertical: 12, backgroundColor: '#dc2626', borderRadius: 12, marginLeft: 8,
                            shadowColor: '#dc2626', shadowOpacity: 0.3, shadowRadius: 6, shadowOffset: { width: 0, height: 3 }, elevation: 5,
                        }}
                    >
                        {submitting
                            ? <ActivityIndicator color="#fff" />
                            : <Text style={{ color: '#fff', fontWeight: 'bold', fontSize: 14 }}>
                                Submit ({answeredCount}/{questions.length})
                            </Text>
                        }
                    </TouchableOpacity>
                ) : (
                    <TouchableOpacity
                        onPress={goNext}
                        style={{
                            flex: 2, flexDirection: 'row', alignItems: 'center', justifyContent: 'center',
                            paddingVertical: 12, backgroundColor: COLORS.primary, borderRadius: 12, marginLeft: 8,
                            shadowColor: COLORS.primary, shadowOpacity: 0.3, shadowRadius: 6, shadowOffset: { width: 0, height: 3 }, elevation: 5,
                        }}
                    >
                        <Text style={{ color: '#fff', fontWeight: 'bold', fontSize: 14 }}>Next</Text>
                        <Ionicons name="chevron-forward" size={16} color="#fff" style={{ marginLeft: 4 }} />
                    </TouchableOpacity>
                )}
            </View>
        </SafeAreaView>
    );
}
