import React, { useState, useEffect, useRef } from 'react';
import { View, Text, ScrollView, TouchableOpacity, ActivityIndicator, SafeAreaView, Modal } from 'react-native';
import { Ionicons } from '@expo/vector-icons';
import AsyncStorage from '@react-native-async-storage/async-storage';
import { SvgXml } from 'react-native-svg';
import { QuizAPI, PrivateModuleAPI } from '../../services/api';
import { COLORS } from '../../styles/theme';

const BOOKMARK_KEY = 'bookmarked_questions';

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
    difficulty?: string;
    options: { option_text: string; is_correct?: boolean }[];
    subject?: string;
    topic?: string;
    topic_code?: string;
}

export default function QuizSessionScreen({ navigation, route }: any) {
    const {
        subject, limit = 10, title = 'Daily Quiz',
        moduleSlug, weakTopicMode = false, wrongPracticeMode = false,
    } = route.params || {};

    const QUIZ_DURATION = 5 * 60;
    const [questions, setQuestions] = useState<QuizQuestion[]>([]);
    const [currentIdx, setCurrentIdx] = useState(0);
    const [selectedAnswers, setSelectedAnswers] = useState<Record<number, number | null>>({});
    const [loading, setLoading] = useState(true);
    const [submitted, setSubmitted] = useState(false);
    const [scorecard, setScorecard] = useState<any>(null);
    const [showReview, setShowReview] = useState(false);
    const [submitting, setSubmitting] = useState(false);
    const [timeLeft, setTimeLeft] = useState(QUIZ_DURATION);
    const [bookmarked, setBookmarked] = useState<Set<string>>(new Set());
    const [showPalette, setShowPalette] = useState(false);
    const timerRef = useRef<ReturnType<typeof setInterval> | null>(null);

    useEffect(() => {
        AsyncStorage.getItem(BOOKMARK_KEY).then(data => {
            if (data) {
                const list: any[] = JSON.parse(data);
                setBookmarked(new Set(list.map(q => q.id)));
            }
        });
    }, []);

    useEffect(() => {
        setCurrentIdx(0);
        setSelectedAnswers({});
        setSubmitted(false);
        setScorecard(null);
        setLoading(true);

        const fetchQuiz = async () => {
            try {
                let res;
                const bmData = await AsyncStorage.getItem(BOOKMARK_KEY);
                const bmIds: string[] = bmData
                    ? (JSON.parse(bmData) as any[]).map((q: any) => q.id).filter(Boolean)
                    : [];

                if (moduleSlug) {
                    res = await PrivateModuleAPI.getQuiz(moduleSlug, subject, limit);
                } else if (wrongPracticeMode) {
                    res = await QuizAPI.getWrongPractice(limit, bmIds);
                } else if (weakTopicMode) {
                    res = await QuizAPI.getWeakTopicQuiz(limit);
                } else {
                    res = await QuizAPI.getDailyQuiz(subject, limit, bmIds);
                }
                setQuestions(res.data?.questions || res.data || []);
            } catch (err) {
                console.error("Failed to fetch quiz:", err);
            } finally {
                setLoading(false);
            }
        };
        fetchQuiz();
    }, [subject, limit, moduleSlug, weakTopicMode, wrongPracticeMode]);

    useEffect(() => {
        if (!loading && questions.length > 0 && !submitted) {
            setTimeLeft(QUIZ_DURATION);
            timerRef.current = setInterval(() => {
                setTimeLeft(prev => {
                    if (prev <= 1) { clearInterval(timerRef.current!); return 0; }
                    return prev - 1;
                });
            }, 1000);
        }
        return () => { if (timerRef.current) clearInterval(timerRef.current); };
    }, [loading, questions.length]);

    useEffect(() => {
        if (timeLeft === 0 && !submitted && !loading && questions.length > 0) handleSubmit();
    }, [timeLeft]);

    useEffect(() => {
        if (submitted && timerRef.current) clearInterval(timerRef.current);
    }, [submitted]);

    const formatTime = (secs: number) => {
        const m = Math.floor(secs / 60).toString().padStart(2, '0');
        const s = (secs % 60).toString().padStart(2, '0');
        return `${m}:${s}`;
    };

    const toggleBookmark = async (q: QuizQuestion) => {
        const existing = await AsyncStorage.getItem(BOOKMARK_KEY);
        const list: any[] = existing ? JSON.parse(existing) : [];
        const isMarked = bookmarked.has(q.id);
        const updated = isMarked
            ? list.filter(item => item.id !== q.id)
            : [...list, { id: q.id, question_text: q.question_text, options: q.options, explanation: q.explanation, subject: q.subject, topic: q.topic, savedAt: new Date().toISOString() }];
        await AsyncStorage.setItem(BOOKMARK_KEY, JSON.stringify(updated));
        const next = new Set(bookmarked);
        isMarked ? next.delete(q.id) : next.add(q.id);
        setBookmarked(next);
    };

    const selectOption = (optionIndex: number) => {
        if (submitted) return;
        setSelectedAnswers(prev => ({ ...prev, [currentIdx]: optionIndex }));
    };

    const goNext = () => { if (currentIdx < questions.length - 1) setCurrentIdx(p => p + 1); };
    const goPrev = () => { if (currentIdx > 0) setCurrentIdx(p => p - 1); };

    const handleSubmit = async () => {
        setSubmitting(true);
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
            setScorecard(res.data);
            setSubmitted(true);
        } catch (err) {
            console.error("Failed to submit quiz:", err);
            let correct = 0, incorrect = 0, skipped = 0;
            questions.forEach((q, idx) => {
                const sel = selectedAnswers[idx];
                if (sel === undefined || sel === null) { skipped++; return; }
                if (q.options[sel]?.is_correct) correct++; else incorrect++;
            });
            setScorecard({
                correct, incorrect, skipped,
                total: questions.length,
                accuracy: questions.length > 0 ? Math.round((correct / questions.length) * 100) : 0,
            });
            setSubmitted(true);
        } finally {
            setSubmitting(false);
        }
    };

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
                <Text style={{ color: '#6b7280', marginTop: 4, textAlign: 'center' }}>
                    {wrongPracticeMode
                        ? "No wrong answers or bookmarks yet. Keep practising!"
                        : "Try a different category or check back later."}
                </Text>
                <TouchableOpacity onPress={() => navigation.goBack()}
                    style={{ marginTop: 20, backgroundColor: COLORS.primary, paddingHorizontal: 24, paddingVertical: 12, borderRadius: 10 }}>
                    <Text style={{ color: '#fff', fontWeight: 'bold' }}>Go Back</Text>
                </TouchableOpacity>
            </SafeAreaView>
        );
    }

    // ─── SCORECARD VIEW ───
    if (submitted && scorecard) {
        const correct = scorecard.correct ?? 0;
        const incorrect = scorecard.incorrect ?? scorecard.wrong ?? 0;
        const skipped = scorecard.skipped ?? 0;
        const total = scorecard.total ?? questions.length;
        const accuracy = Math.round(scorecard.accuracy ?? scorecard.score_percentage ?? (total > 0 ? (correct / total) * 100 : 0));
        const isGood = accuracy >= 70;
        const weakTopics: any[] = scorecard.weak_topics || [];
        const nudge = scorecard.nudge || scorecard.encouragement || scorecard.nudge_message;

        return (
            <SafeAreaView style={{ flex: 1, backgroundColor: '#f9fafb' }}>
                <ScrollView>
                    {/* ── Result Banner ── */}
                    <View style={{
                        backgroundColor: isGood ? '#f0fdf4' : '#fff7ed',
                        paddingTop: 36, paddingBottom: 28, paddingHorizontal: 24,
                        alignItems: 'center',
                        borderBottomLeftRadius: 28, borderBottomRightRadius: 28,
                    }}>
                        <Text style={{ fontSize: 44, marginBottom: 6 }}>
                            {isGood ? '🎉' : correct === 0 ? '😅' : '💪'}
                        </Text>
                        <View style={{ flexDirection: 'row', alignItems: 'baseline', marginBottom: 4 }}>
                            <Text style={{ fontSize: 42, fontWeight: '900', color: '#111827', lineHeight: 50 }}>{correct}</Text>
                            <Text style={{ fontSize: 20, color: '#9ca3af', fontWeight: '600' }}>/{total}</Text>
                        </View>
                        <Text style={{ fontSize: 13, color: '#6b7280', marginBottom: 14 }}>Questions Correct</Text>

                        <View style={{ width: '100%', height: 8, backgroundColor: 'rgba(0,0,0,0.1)', borderRadius: 4, marginBottom: 6 }}>
                            <View style={{
                                height: 8, borderRadius: 4,
                                backgroundColor: isGood ? '#22c55e' : COLORS.primary,
                                width: `${Math.min(accuracy, 100)}%`,
                            }} />
                        </View>
                        <Text style={{ fontSize: 13, fontWeight: '700', color: isGood ? '#16a34a' : '#c2410c' }}>
                            {accuracy}% Accuracy
                        </Text>
                    </View>

                    <View style={{ padding: 16 }}>
                        {/* ── Correct / Wrong / Skipped ── */}
                        <View style={{ flexDirection: 'row', gap: 8, marginBottom: 16 }}>
                            {[
                                { label: '✓  Correct', value: correct, color: '#16a34a', bg: '#f0fdf4', border: '#bbf7d0' },
                                { label: '✗  Wrong', value: incorrect, color: '#dc2626', bg: '#fef2f2', border: '#fecaca' },
                                { label: '—  Skipped', value: skipped, color: '#6b7280', bg: '#f3f4f6', border: '#e5e7eb' },
                            ].map((item, idx) => (
                                <View key={idx} style={{
                                    flex: 1, backgroundColor: item.bg, borderRadius: 14, padding: 14,
                                    alignItems: 'center', borderWidth: 1, borderColor: item.border,
                                }}>
                                    <Text style={{ fontSize: 26, fontWeight: '900', color: item.color }}>{item.value}</Text>
                                    <Text style={{ fontSize: 11, fontWeight: '700', color: item.color, marginTop: 3 }}>{item.label}</Text>
                                </View>
                            ))}
                        </View>

                        {nudge ? (
                            <View style={{
                                backgroundColor: '#eff6ff', borderWidth: 1, borderColor: '#bfdbfe',
                                borderRadius: 12, padding: 14, marginBottom: 16,
                            }}>
                                <Text style={{ color: '#1e40af', fontSize: 13, fontWeight: '500' }}>💡 {nudge}</Text>
                            </View>
                        ) : null}

                        {/* ── Focus Areas ── */}
                        {weakTopics.length > 0 ? (
                            <View style={{
                                backgroundColor: '#fff', borderRadius: 14, padding: 16, marginBottom: 16,
                                borderWidth: 1, borderColor: '#fecaca',
                            }}>
                                <Text style={{ fontSize: 15, fontWeight: '700', color: '#111827', marginBottom: 12 }}>
                                    🎯 Focus These Areas
                                </Text>
                                {weakTopics.map((wt: any, i: number) => (
                                    <View key={i} style={{
                                        flexDirection: 'row', alignItems: 'center',
                                        paddingVertical: 8,
                                        borderBottomWidth: i < weakTopics.length - 1 ? 1 : 0,
                                        borderBottomColor: '#f3f4f6',
                                    }}>
                                        <View style={{
                                            width: 8, height: 8, borderRadius: 4, marginRight: 10,
                                            backgroundColor: wt.accuracy < 40 ? '#ef4444' : '#f97316',
                                        }} />
                                        <View style={{ flex: 1 }}>
                                            <Text style={{ fontSize: 13, fontWeight: '600', color: '#374151' }}>
                                                {wt.topic || wt.subject}
                                            </Text>
                                            {wt.subject && wt.topic ? (
                                                <Text style={{ fontSize: 11, color: '#9ca3af' }}>{wt.subject}</Text>
                                            ) : null}
                                        </View>
                                        <Text style={{
                                            fontSize: 12, fontWeight: '700',
                                            color: wt.accuracy < 40 ? '#dc2626' : '#ea580c',
                                        }}>{wt.accuracy}%</Text>
                                    </View>
                                ))}
                            </View>
                        ) : null}

                        {/* ── Actions ── */}
                        <TouchableOpacity
                            onPress={() => navigation.goBack()}
                            style={{
                                backgroundColor: COLORS.primary, borderRadius: 14, paddingVertical: 16,
                                alignItems: 'center', marginBottom: 10,
                                shadowColor: COLORS.primary, shadowOpacity: 0.3, shadowRadius: 8,
                                shadowOffset: { width: 0, height: 4 }, elevation: 5,
                            }}
                        >
                            <Text style={{ color: '#fff', fontWeight: '700', fontSize: 16 }}>Back to Categories</Text>
                        </TouchableOpacity>

                        <TouchableOpacity
                            onPress={() => setShowReview(v => !v)}
                            style={{
                                borderRadius: 14, paddingVertical: 14, alignItems: 'center',
                                marginBottom: 20, borderWidth: 1, borderColor: '#e5e7eb', backgroundColor: '#fff',
                            }}
                        >
                            <Text style={{ color: '#374151', fontWeight: '600', fontSize: 14 }}>
                                {showReview ? '▲ Hide Review' : '📋 Review All Answers'}
                            </Text>
                        </TouchableOpacity>

                        {/* ── Question Review ── */}
                        {showReview && questions.map((q, idx) => {
                            const selIdx = selectedAnswers[idx];
                            const isSkipped = selIdx === null || selIdx === undefined;
                            const isCorrect = !isSkipped && !!q.options[selIdx!]?.is_correct;
                            const status = isSkipped ? 'skipped' : isCorrect ? 'correct' : 'wrong';

                            const statusConfig = {
                                correct: { label: '✓  CORRECT', color: '#16a34a', bg: '#f0fdf4', border: '#bbf7d0' },
                                wrong:   { label: '✗  WRONG',   color: '#dc2626', bg: '#fef2f2', border: '#fecaca' },
                                skipped: { label: '—  SKIPPED', color: '#6b7280', bg: '#f3f4f6', border: '#e5e7eb' },
                            }[status];

                            const isMarked = bookmarked.has(q.id);

                            return (
                                <View key={q.id} style={{
                                    backgroundColor: '#fff', borderRadius: 14, padding: 16, marginBottom: 12,
                                    borderWidth: 1, borderColor: statusConfig.border,
                                }}>
                                    <View style={{ flexDirection: 'row', alignItems: 'center', marginBottom: 10 }}>
                                        <View style={{
                                            paddingHorizontal: 9, paddingVertical: 4, borderRadius: 7,
                                            backgroundColor: statusConfig.bg,
                                        }}>
                                            <Text style={{ fontSize: 11, fontWeight: '800', color: statusConfig.color, letterSpacing: 0.3 }}>
                                                {statusConfig.label}
                                            </Text>
                                        </View>
                                        {q.subject ? (
                                            <Text style={{ fontSize: 10, color: '#9ca3af', marginLeft: 8, flex: 1 }} numberOfLines={1}>
                                                {q.subject}{q.topic ? ` · ${q.topic}` : ''}
                                            </Text>
                                        ) : <View style={{ flex: 1 }} />}
                                        <TouchableOpacity onPress={() => toggleBookmark(q)} style={{ padding: 4 }}>
                                            <Ionicons
                                                name={isMarked ? 'bookmark' : 'bookmark-outline'}
                                                size={20}
                                                color={isMarked ? COLORS.primary : '#9ca3af'}
                                            />
                                        </TouchableOpacity>
                                    </View>

                                    <Text style={{ fontSize: 13, fontWeight: '600', color: '#111827', marginBottom: 10, lineHeight: 20 }}>
                                        {idx + 1}. {q.question_text}
                                    </Text>

                                    {q.options.map((opt, i) => {
                                        const isOptCorrect = !!opt.is_correct;
                                        const isOptSelected = selIdx === i;
                                        let bg = '#f9fafb', border = '#e5e7eb', textColor = '#374151';
                                        if (isOptCorrect) { bg = '#f0fdf4'; border = '#22c55e'; textColor = '#15803d'; }
                                        else if (isOptSelected) { bg = '#fef2f2'; border = '#ef4444'; textColor = '#dc2626'; }
                                        return (
                                            <View key={i} style={{
                                                flexDirection: 'row', alignItems: 'flex-start',
                                                backgroundColor: bg, borderWidth: 1, borderColor: border,
                                                borderRadius: 8, paddingHorizontal: 10, paddingVertical: 8, marginBottom: 6,
                                            }}>
                                                <Text style={{ fontSize: 12, fontWeight: 'bold', color: '#9ca3af', marginRight: 6, marginTop: 1 }}>
                                                    {String.fromCharCode(65 + i)}.
                                                </Text>
                                                <Text style={{ fontSize: 12, color: textColor, flex: 1, lineHeight: 18, fontWeight: isOptCorrect || isOptSelected ? '600' : '400' }}>
                                                    {opt.option_text}
                                                </Text>
                                                {isOptCorrect && <Ionicons name="checkmark-circle" size={16} color="#16a34a" style={{ marginLeft: 4, marginTop: 1 }} />}
                                                {isOptSelected && !isOptCorrect && <Ionicons name="close-circle" size={16} color="#dc2626" style={{ marginLeft: 4, marginTop: 1 }} />}
                                            </View>
                                        );
                                    })}

                                    {q.explanation ? (
                                        <View style={{
                                            backgroundColor: '#eff6ff', borderRadius: 8, padding: 10, marginTop: 8,
                                            borderWidth: 1, borderColor: '#bfdbfe',
                                        }}>
                                            {renderExplanationMobile(q.explanation, { fontSize: 12, color: '#1e40af', lineHeight: 18 })}
                                        </View>
                                    ) : null}
                                    {q.explanation_svg ? (
                                        <SvgXml xml={q.explanation_svg} width="100%" height={200} style={{ marginTop: 10 }} />
                                    ) : null}
                                </View>
                            );
                        })}
                    </View>
                </ScrollView>
            </SafeAreaView>
        );
    }

    // ─── QUIZ QUESTION VIEW ───
    const currentQ = questions[currentIdx];
    const answeredCount = Object.values(selectedAnswers).filter(v => v !== null && v !== undefined).length;
    const isLast = currentIdx === questions.length - 1;

    return (
        <SafeAreaView style={{ flex: 1, backgroundColor: '#f9fafb' }}>
            {/* ── Question Palette Modal (SSC CGL style) ── */}
            <Modal visible={showPalette} transparent animationType="slide" onRequestClose={() => setShowPalette(false)}>
                <TouchableOpacity
                    style={{ flex: 1, backgroundColor: 'rgba(0,0,0,0.5)', justifyContent: 'flex-end' }}
                    activeOpacity={1}
                    onPress={() => setShowPalette(false)}
                >
                    <TouchableOpacity activeOpacity={1} onPress={() => {}}>
                        <View style={{
                            backgroundColor: '#fff',
                            borderTopLeftRadius: 24, borderTopRightRadius: 24,
                            padding: 20, paddingBottom: 36,
                        }}>
                            {/* Handle */}
                            <View style={{ width: 40, height: 4, backgroundColor: '#e5e7eb', borderRadius: 2, alignSelf: 'center', marginBottom: 16 }} />

                            <Text style={{ fontSize: 16, fontWeight: '700', color: '#111827', marginBottom: 4 }}>
                                Question Navigator
                            </Text>
                            <Text style={{ fontSize: 12, color: '#6b7280', marginBottom: 16 }}>
                                {answeredCount}/{questions.length} answered · tap any question to jump
                            </Text>

                            {/* Grid */}
                            <View style={{ flexDirection: 'row', flexWrap: 'wrap', gap: 8 }}>
                                {questions.map((q, idx) => {
                                    const isAnswered = selectedAnswers[idx] !== null && selectedAnswers[idx] !== undefined;
                                    const isBookmarkedQ = bookmarked.has(q.id);
                                    const isCurrent = idx === currentIdx;

                                    let bg = '#f3f4f6';
                                    let borderColor = '#e5e7eb';
                                    let textColor = '#6b7280';
                                    let borderWidth = 1;

                                    if (isCurrent) {
                                        bg = COLORS.primary; borderColor = COLORS.primary; textColor = '#fff'; borderWidth = 2;
                                    } else if (isAnswered) {
                                        bg = '#dcfce7'; borderColor = '#22c55e'; textColor = '#16a34a'; borderWidth = 1;
                                    }
                                    if (isBookmarkedQ && !isCurrent) {
                                        borderColor = '#f97316'; borderWidth = 2;
                                    }

                                    return (
                                        <TouchableOpacity
                                            key={idx}
                                            onPress={() => { setCurrentIdx(idx); setShowPalette(false); }}
                                            style={{
                                                width: 44, height: 44, borderRadius: 10,
                                                backgroundColor: bg, borderWidth, borderColor,
                                                alignItems: 'center', justifyContent: 'center',
                                            }}
                                        >
                                            <Text style={{ fontSize: 13, fontWeight: '700', color: textColor }}>{idx + 1}</Text>
                                            {isBookmarkedQ && !isCurrent && (
                                                <View style={{
                                                    position: 'absolute', top: -3, right: -3,
                                                    width: 10, height: 10, borderRadius: 5,
                                                    backgroundColor: '#f97316', borderWidth: 1, borderColor: '#fff',
                                                }} />
                                            )}
                                        </TouchableOpacity>
                                    );
                                })}
                            </View>

                            {/* Legend */}
                            <View style={{ flexDirection: 'row', flexWrap: 'wrap', gap: 16, marginTop: 20, paddingTop: 16, borderTopWidth: 1, borderTopColor: '#f3f4f6' }}>
                                {[
                                    { bg: COLORS.primary, border: COLORS.primary, text: '#fff', label: 'Current' },
                                    { bg: '#dcfce7', border: '#22c55e', text: '#16a34a', label: 'Answered' },
                                    { bg: '#f3f4f6', border: '#e5e7eb', text: '#6b7280', label: 'Not Answered' },
                                    { bg: '#f3f4f6', border: '#f97316', text: '#6b7280', label: 'Bookmarked', dot: true },
                                ].map((item, i) => (
                                    <View key={i} style={{ flexDirection: 'row', alignItems: 'center', gap: 6 }}>
                                        <View style={{
                                            width: 18, height: 18, borderRadius: 4,
                                            backgroundColor: item.bg, borderWidth: 2, borderColor: item.border,
                                        }}>
                                            {item.dot && (
                                                <View style={{
                                                    position: 'absolute', top: -4, right: -4,
                                                    width: 8, height: 8, borderRadius: 4, backgroundColor: '#f97316',
                                                }} />
                                            )}
                                        </View>
                                        <Text style={{ fontSize: 11, color: '#6b7280' }}>{item.label}</Text>
                                    </View>
                                ))}
                            </View>

                            {/* Submit from palette if all answered */}
                            {answeredCount === questions.length && (
                                <TouchableOpacity
                                    onPress={() => { setShowPalette(false); handleSubmit(); }}
                                    style={{
                                        marginTop: 16, backgroundColor: '#dc2626', borderRadius: 12,
                                        paddingVertical: 14, alignItems: 'center',
                                    }}
                                >
                                    <Text style={{ color: '#fff', fontWeight: '700', fontSize: 15 }}>Submit Quiz</Text>
                                </TouchableOpacity>
                            )}
                        </View>
                    </TouchableOpacity>
                </TouchableOpacity>
            </Modal>

            {/* Header */}
            <View style={{
                backgroundColor: '#fff', paddingHorizontal: 16, paddingVertical: 12,
                borderBottomWidth: 1, borderBottomColor: '#e5e7eb',
                flexDirection: 'row', alignItems: 'center', justifyContent: 'space-between',
            }}>
                <TouchableOpacity onPress={() => navigation.goBack()}>
                    <Ionicons name="close" size={24} color="#374151" />
                </TouchableOpacity>
                <Text style={{ fontSize: 15, fontWeight: 'bold', color: '#111827', flex: 1, textAlign: 'center', marginHorizontal: 8 }} numberOfLines={1}>
                    {title}
                </Text>
                <View style={{ flexDirection: 'row', alignItems: 'center', gap: 8 }}>
                    <View style={{
                        backgroundColor: timeLeft < 60 ? '#fee2e2' : '#f3f4f6',
                        paddingHorizontal: 7, paddingVertical: 3, borderRadius: 8,
                    }}>
                        <Text style={{ fontSize: 12, fontWeight: 'bold', color: timeLeft < 60 ? '#dc2626' : '#374151' }}>
                            ⏱ {formatTime(timeLeft)}
                        </Text>
                    </View>
                    {/* Tappable Q counter — opens palette */}
                    <TouchableOpacity
                        onPress={() => setShowPalette(true)}
                        style={{
                            backgroundColor: '#eff6ff', paddingHorizontal: 9, paddingVertical: 4,
                            borderRadius: 8, borderWidth: 1, borderColor: '#bfdbfe',
                        }}
                    >
                        <Text style={{ fontSize: 12, fontWeight: '700', color: '#3b82f6' }}>
                            {currentIdx + 1}/{questions.length}
                        </Text>
                    </TouchableOpacity>
                </View>
            </View>

            {/* Progress Bar */}
            <View style={{ height: 3, backgroundColor: '#e5e7eb' }}>
                <View style={{
                    height: 3, backgroundColor: COLORS.primary,
                    width: `${((answeredCount) / questions.length) * 100}%`,
                }} />
            </View>

            <ScrollView style={{ flex: 1 }} contentContainerStyle={{ padding: 16, paddingBottom: 80 }}>
                <View style={{ backgroundColor: '#fff', borderRadius: 16, padding: 20, marginBottom: 16, borderWidth: 1, borderColor: '#f3f4f6' }}>
                    <Text style={{ fontSize: 15, fontWeight: '500', color: '#111827', lineHeight: 25 }}>
                        {currentQ.question_text}
                    </Text>
                </View>

                {currentQ.diagram_svg && (
                    <SvgXml xml={currentQ.diagram_svg} width="100%" height={200} style={{ marginBottom: 16 }} />
                )}

                {currentQ.options.map((opt, i) => {
                    const isSelected = selectedAnswers[currentIdx] === i;
                    return (
                        <TouchableOpacity
                            key={i}
                            onPress={() => selectOption(i)}
                            activeOpacity={0.7}
                            style={{
                                flexDirection: 'row', alignItems: 'flex-start',
                                padding: 14, borderRadius: 12, marginBottom: 10, borderWidth: 2,
                                borderColor: isSelected ? COLORS.primary : '#e5e7eb',
                                backgroundColor: isSelected ? '#fff7ed' : '#fff',
                            }}
                        >
                            <View style={{
                                width: 20, height: 20, borderRadius: 10,
                                borderWidth: 2, borderColor: isSelected ? COLORS.primary : '#d1d5db',
                                backgroundColor: isSelected ? COLORS.primary : '#fff',
                                alignItems: 'center', justifyContent: 'center', marginRight: 12, marginTop: 1,
                            }}>
                                {isSelected && <View style={{ width: 7, height: 7, borderRadius: 3.5, backgroundColor: '#fff' }} />}
                            </View>
                            <Text style={{ fontSize: 14, fontWeight: isSelected ? '600' : '400', color: isSelected ? '#9a3412' : '#374151', flex: 1, lineHeight: 22 }}>
                                <Text style={{ fontWeight: 'bold', color: '#9ca3af' }}>{String.fromCharCode(65 + i)}. </Text>
                                {opt.option_text}
                            </Text>
                        </TouchableOpacity>
                    );
                })}
            </ScrollView>

            {/* Bottom Bar */}
            <View style={{
                flexDirection: 'row', paddingHorizontal: 16, paddingVertical: 12, paddingBottom: 24,
                backgroundColor: '#fff', borderTopWidth: 1, borderTopColor: '#e5e7eb',
                shadowColor: '#000', shadowOpacity: 0.08, shadowRadius: 12, shadowOffset: { width: 0, height: -3 }, elevation: 10,
                alignItems: 'center',
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

                {/* Bookmark */}
                <TouchableOpacity
                    onPress={() => toggleBookmark(currentQ)}
                    style={{
                        width: 44, height: 44, borderRadius: 12, alignItems: 'center', justifyContent: 'center',
                        borderWidth: 1.5,
                        borderColor: bookmarked.has(currentQ.id) ? COLORS.primary : '#e5e7eb',
                        backgroundColor: bookmarked.has(currentQ.id) ? '#fff7ed' : '#fff',
                        marginRight: 8,
                    }}
                >
                    <Ionicons
                        name={bookmarked.has(currentQ.id) ? 'bookmark' : 'bookmark-outline'}
                        size={20}
                        color={bookmarked.has(currentQ.id) ? COLORS.primary : '#9ca3af'}
                    />
                </TouchableOpacity>

                {isLast ? (
                    <TouchableOpacity
                        onPress={handleSubmit}
                        disabled={submitting}
                        style={{
                            flex: 2, alignItems: 'center', justifyContent: 'center',
                            paddingVertical: 12, backgroundColor: '#dc2626', borderRadius: 12,
                            shadowColor: '#dc2626', shadowOpacity: 0.3, shadowRadius: 6, shadowOffset: { width: 0, height: 3 }, elevation: 5,
                        }}
                    >
                        {submitting ? <ActivityIndicator color="#fff" /> :
                            <Text style={{ color: '#fff', fontWeight: 'bold', fontSize: 14 }}>Submit ({answeredCount}/{questions.length})</Text>}
                    </TouchableOpacity>
                ) : (
                    <TouchableOpacity
                        onPress={goNext}
                        style={{
                            flex: 2, flexDirection: 'row', alignItems: 'center', justifyContent: 'center',
                            paddingVertical: 12, backgroundColor: COLORS.primary, borderRadius: 12,
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
