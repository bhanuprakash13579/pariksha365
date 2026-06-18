import React, { useState, useEffect, useRef, useCallback } from 'react';
import { View, Text, ScrollView, TouchableOpacity, ActivityIndicator, SafeAreaView } from 'react-native';
import { Ionicons } from '@expo/vector-icons';
import { SvgXml } from 'react-native-svg';
import { QuizAPI, PrivateModuleAPI } from '../../services/api';
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
    const [submitting, setSubmitting] = useState(false);
    const [timeLeft, setTimeLeft] = useState(QUIZ_DURATION);
    const timerRef = useRef<ReturnType<typeof setInterval> | null>(null);

    useEffect(() => {
        // Reset state whenever subject/module/limit changes (catches re-navigate with same params)
        setCurrentIdx(0);
        setSelectedAnswers({});
        setSubmitted(false);
        setScorecard(null);
        setLoading(true);

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
                console.error("Failed to fetch quiz:", err);
            } finally {
                setLoading(false);
            }
        };
        fetchQuiz();
    }, [subject, limit, moduleSlug, weakTopicMode]);

    // Start countdown once questions load
    useEffect(() => {
        if (!loading && questions.length > 0 && !submitted) {
            setTimeLeft(QUIZ_DURATION);
            timerRef.current = setInterval(() => {
                setTimeLeft(prev => {
                    if (prev <= 1) {
                        clearInterval(timerRef.current!);
                        return 0;
                    }
                    return prev - 1;
                });
            }, 1000);
        }
        return () => { if (timerRef.current) clearInterval(timerRef.current); };
    }, [loading, questions.length]);

    // Auto-submit when timer hits 0
    useEffect(() => {
        if (timeLeft === 0 && !submitted && !loading && questions.length > 0) {
            handleSubmit();
        }
    }, [timeLeft]);

    // Stop timer after submit
    useEffect(() => {
        if (submitted && timerRef.current) {
            clearInterval(timerRef.current);
        }
    }, [submitted]);

    const formatTime = (secs: number) => {
        const m = Math.floor(secs / 60).toString().padStart(2, '0');
        const s = (secs % 60).toString().padStart(2, '0');
        return `${m}:${s}`;
    };

    const selectOption = (optionIndex: number) => {
        if (submitted) return;
        setSelectedAnswers(prev => ({ ...prev, [currentIdx]: optionIndex }));
    };

    const goNext = () => {
        if (currentIdx < questions.length - 1) setCurrentIdx(prev => prev + 1);
    };

    const goPrev = () => {
        if (currentIdx > 0) setCurrentIdx(prev => prev - 1);
    };

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
            // Scorecard from server failed — show basic local tally so user still sees a result
            let correct = 0, wrong = 0, skipped = 0;
            questions.forEach((q, idx) => {
                const sel = selectedAnswers[idx];
                if (sel === undefined || sel === null) { skipped++; return; }
                if (q.options[sel]?.is_correct) correct++; else wrong++;
            });
            setScorecard({
                correct, wrong, skipped,
                total: questions.length,
                score_percentage: questions.length > 0 ? Math.round((correct / questions.length) * 100) : 0,
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
                <Text style={{ color: '#6b7280', marginTop: 4, textAlign: 'center' }}>Try a different category or check back later.</Text>
                <TouchableOpacity onPress={() => navigation.goBack()}
                    style={{ marginTop: 20, backgroundColor: COLORS.primary, paddingHorizontal: 24, paddingVertical: 12, borderRadius: 10 }}>
                    <Text style={{ color: '#fff', fontWeight: 'bold' }}>Go Back</Text>
                </TouchableOpacity>
            </SafeAreaView>
        );
    }

    // ─── SCORECARD VIEW ───
    if (submitted && scorecard) {
        const scorePct = scorecard.score_percentage || Math.round((scorecard.correct / scorecard.total) * 100);
        const isGood = scorePct >= 70;
        return (
            <SafeAreaView style={{ flex: 1, backgroundColor: '#f9fafb' }}>
                <ScrollView contentContainerStyle={{ padding: 20, paddingTop: 40 }}>
                    {/* Score Circle */}
                    <View style={{ alignItems: 'center', marginBottom: 30 }}>
                        <View style={{
                            width: 120, height: 120, borderRadius: 60,
                            backgroundColor: isGood ? '#f0fdf4' : '#fff7ed',
                            borderWidth: 4, borderColor: isGood ? '#22c55e' : COLORS.primary,
                            alignItems: 'center', justifyContent: 'center', marginBottom: 16,
                        }}>
                            <Text style={{ fontSize: 36, fontWeight: '900', color: isGood ? '#16a34a' : '#c2410c' }}>{scorePct}%</Text>
                        </View>
                        <Text style={{ fontSize: 22, fontWeight: '800', color: '#111827' }}>
                            {isGood ? '🎉 Great Job!' : '📊 Keep Practicing!'}
                        </Text>
                        <Text style={{ color: '#6b7280', marginTop: 4, textAlign: 'center' }}>
                            You answered {scorecard.correct} out of {scorecard.total} correctly
                        </Text>
                    </View>

                    {/* Stats Cards */}
                    <View style={{ flexDirection: 'row', gap: 8, marginBottom: 20 }}>
                        {[
                            { label: 'Correct', value: scorecard.correct, color: '#22c55e', bg: '#f0fdf4' },
                            { label: 'Wrong', value: scorecard.wrong, color: '#ef4444', bg: '#fef2f2' },
                            { label: 'Skipped', value: scorecard.skipped, color: '#6b7280', bg: '#f3f4f6' },
                        ].map((item, idx) => (
                            <View key={idx} style={{
                                flex: 1, backgroundColor: item.bg, borderRadius: 14, padding: 16, alignItems: 'center',
                            }}>
                                <Text style={{ fontSize: 28, fontWeight: '900', color: item.color }}>{item.value}</Text>
                                <Text style={{ fontSize: 11, fontWeight: '600', color: '#9ca3af', marginTop: 4 }}>{item.label}</Text>
                            </View>
                        ))}
                    </View>

                    {/* Focus Areas */}
                    {scorecard.focus_areas?.length > 0 && (
                        <View style={{ marginBottom: 20 }}>
                            <Text style={{ fontSize: 16, fontWeight: 'bold', color: '#111827', marginBottom: 10 }}>🎯 Focus Areas</Text>
                            {scorecard.focus_areas.map((area: string, idx: number) => (
                                <View key={idx} style={{
                                    backgroundColor: '#fff', borderRadius: 10, padding: 12, marginBottom: 6,
                                    borderWidth: 1, borderColor: '#fecaca', flexDirection: 'row', alignItems: 'center',
                                }}>
                                    <Ionicons name="flag" size={14} color="#ef4444" style={{ marginRight: 8 }} />
                                    <Text style={{ color: '#374151', fontSize: 13, fontWeight: '500' }}>{area}</Text>
                                </View>
                            ))}
                        </View>
                    )}

                    {/* Nudge Message */}
                    {scorecard.nudge_message && (
                        <View style={{
                            backgroundColor: '#eff6ff', borderWidth: 1, borderColor: '#bfdbfe',
                            borderRadius: 12, padding: 14, marginBottom: 20,
                        }}>
                            <Text style={{ color: '#1e40af', fontSize: 13, fontWeight: '500' }}>💡 {scorecard.nudge_message}</Text>
                        </View>
                    )}

                    {/* Actions */}
                    <TouchableOpacity
                        onPress={() => navigation.goBack()}
                        style={{
                            backgroundColor: COLORS.primary, borderRadius: 14, paddingVertical: 16, alignItems: 'center', marginBottom: 10,
                            shadowColor: COLORS.primary, shadowOpacity: 0.3, shadowRadius: 8, shadowOffset: { width: 0, height: 4 }, elevation: 5,
                        }}
                    >
                        <Text style={{ color: '#fff', fontWeight: '700', fontSize: 16 }}>Back to Categories</Text>
                    </TouchableOpacity>

                    {/* Review Toggle */}
                    <TouchableOpacity
                        onPress={() => setShowReview(v => !v)}
                        style={{ borderRadius: 14, paddingVertical: 14, alignItems: 'center', marginBottom: 16, borderWidth: 1, borderColor: '#e5e7eb', backgroundColor: '#fff' }}
                    >
                        <Text style={{ color: '#374151', fontWeight: '600', fontSize: 14 }}>{showReview ? '▲ Hide Review' : '📋 Review Answers'}</Text>
                    </TouchableOpacity>

                    {showReview && questions.map((q, idx) => {
                        const selIdx = selectedAnswers[idx];
                        return (
                            <View key={q.id} style={{ backgroundColor: '#fff', borderRadius: 14, padding: 16, marginBottom: 12, borderWidth: 1, borderColor: '#e5e7eb' }}>
                                <Text style={{ fontSize: 13, fontWeight: '600', color: '#111827', marginBottom: 10, lineHeight: 20 }}>
                                    {idx + 1}. {q.question_text}
                                </Text>
                                {q.options.map((opt, i) => {
                                    const isCorrect = opt.is_correct;
                                    const isSelected = selIdx === i;
                                    const bg = isCorrect ? '#f0fdf4' : isSelected ? '#fef2f2' : '#f9fafb';
                                    const border = isCorrect ? '#22c55e' : isSelected ? '#ef4444' : '#e5e7eb';
                                    return (
                                        <View key={i} style={{ flexDirection: 'row', alignItems: 'flex-start', backgroundColor: bg, borderWidth: 1, borderColor: border, borderRadius: 8, paddingHorizontal: 10, paddingVertical: 8, marginBottom: 6 }}>
                                            <Text style={{ fontSize: 12, fontWeight: 'bold', color: '#6b7280', marginRight: 6, marginTop: 1 }}>{String.fromCharCode(65 + i)}.</Text>
                                            <Text style={{ fontSize: 12, color: '#374151', flex: 1, lineHeight: 18 }}>{opt.option_text}</Text>
                                            {isCorrect && <Text style={{ color: '#16a34a', fontWeight: 'bold', fontSize: 14, marginLeft: 4 }}>✓</Text>}
                                            {isSelected && !isCorrect && <Text style={{ color: '#dc2626', fontWeight: 'bold', fontSize: 14, marginLeft: 4 }}>✗</Text>}
                                        </View>
                                    );
                                })}
                                {q.explanation ? (
                                    <View style={{ backgroundColor: '#eff6ff', borderRadius: 8, padding: 10, marginTop: 8, borderWidth: 1, borderColor: '#bfdbfe' }}>
                                        <Text style={{ fontSize: 12, color: '#1e40af' }}>💡</Text>
                                        {renderExplanationMobile(q.explanation, { fontSize: 12, color: '#1e40af' })}
                                    </View>
                                ) : null}
                                {q.explanation_svg ? (
                                    <SvgXml xml={q.explanation_svg} width="100%" height={200} style={{ marginTop: 10 }} />
                                ) : null}
                            </View>
                        );
                    })}
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
            {/* Header */}
            <View style={{
                backgroundColor: '#fff', paddingHorizontal: 16, paddingVertical: 12,
                borderBottomWidth: 1, borderBottomColor: '#e5e7eb',
                flexDirection: 'row', alignItems: 'center', justifyContent: 'space-between',
            }}>
                <TouchableOpacity onPress={() => navigation.goBack()}>
                    <Ionicons name="close" size={24} color="#374151" />
                </TouchableOpacity>
                <Text style={{ fontSize: 15, fontWeight: 'bold', color: '#111827', flex: 1, textAlign: 'center', marginHorizontal: 8 }} numberOfLines={1}>{title}</Text>
                <View style={{ flexDirection: 'row', alignItems: 'center' }}>
                    <View style={{
                        backgroundColor: timeLeft < 60 ? '#fee2e2' : '#f3f4f6',
                        paddingHorizontal: 7, paddingVertical: 3, borderRadius: 8, marginRight: 8,
                    }}>
                        <Text style={{ fontSize: 12, fontWeight: 'bold', color: timeLeft < 60 ? '#dc2626' : '#374151' }}>
                            ⏱ {formatTime(timeLeft)}
                        </Text>
                    </View>
                    <Text style={{ fontSize: 13, color: '#6b7280', fontWeight: '600' }}>
                        {currentIdx + 1}/{questions.length}
                    </Text>
                </View>
            </View>

            {/* Progress Bar */}
            <View style={{ height: 3, backgroundColor: '#e5e7eb' }}>
                <View style={{
                    height: 3, backgroundColor: COLORS.primary,
                    width: `${((currentIdx + 1) / questions.length) * 100}%`,
                }} />
            </View>

            <ScrollView style={{ flex: 1 }} contentContainerStyle={{ padding: 16, paddingBottom: 80 }}>
                {/* Question */}
                <View style={{ backgroundColor: '#fff', borderRadius: 16, padding: 20, marginBottom: 16, borderWidth: 1, borderColor: '#f3f4f6' }}>
                    <Text style={{ fontSize: 15, fontWeight: '500', color: '#111827', lineHeight: 25 }}>
                        {currentQ.question_text}
                    </Text>
                </View>

                {/* Diagram */}
                {currentQ.diagram_svg && (
                    <SvgXml xml={currentQ.diagram_svg} width="100%" height={200}
                        style={{ marginBottom: 16 }} />
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
            }}>
                <TouchableOpacity
                    onPress={goPrev}
                    disabled={currentIdx === 0}
                    style={{
                        flex: 1, flexDirection: 'row', alignItems: 'center', justifyContent: 'center',
                        paddingVertical: 12, backgroundColor: currentIdx === 0 ? '#f3f4f6' : '#fff', borderRadius: 12, marginRight: 8,
                        borderWidth: 1, borderColor: '#e5e7eb', opacity: currentIdx === 0 ? 0.5 : 1,
                    }}
                >
                    <Ionicons name="chevron-back" size={16} color="#4b5563" />
                    <Text style={{ color: '#4b5563', fontWeight: 'bold', fontSize: 14, marginLeft: 4 }}>Previous</Text>
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
                        {submitting ? <ActivityIndicator color="#fff" /> :
                            <Text style={{ color: '#fff', fontWeight: 'bold', fontSize: 14 }}>Submit ({answeredCount}/{questions.length})</Text>}
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
