import React, { useState, useEffect } from 'react';
import { View, Text, ScrollView, TouchableOpacity, ActivityIndicator, SafeAreaView } from 'react-native';
import { Ionicons } from '@expo/vector-icons';
import { QuizAPI } from '../../services/api';
import { COLORS } from '../../styles/theme';

interface QuizQuestion {
    id: string;
    question_text: string;
    options: { option_text: string; is_correct?: boolean }[];
    subject?: string;
    topic?: string;
}

export default function QuizSessionScreen({ navigation, route }: any) {
    const { subject, limit = 10, title = 'Daily Quiz' } = route.params || {};

    const [questions, setQuestions] = useState<QuizQuestion[]>([]);
    const [currentIdx, setCurrentIdx] = useState(0);
    const [selectedAnswers, setSelectedAnswers] = useState<Record<number, number | null>>({});
    const [loading, setLoading] = useState(true);
    const [submitted, setSubmitted] = useState(false);
    const [scorecard, setScorecard] = useState<any>(null);
    const [submitting, setSubmitting] = useState(false);

    useEffect(() => {
        const fetchQuiz = async () => {
            try {
                const res = await QuizAPI.getDailyQuiz(subject, limit);
                setQuestions(res.data?.questions || res.data || []);
            } catch (err) {
                console.error("Failed to fetch quiz:", err);
            } finally {
                setLoading(false);
            }
        };
        fetchQuiz();
    }, [subject, limit]);

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
            const res = await QuizAPI.submitQuiz(answersPayload);
            setScorecard(res.data);
            setSubmitted(true);
        } catch (err) {
            console.error("Failed to submit quiz:", err);
            // Compute locally as fallback
            let correct = 0, wrong = 0, skipped = 0;
            questions.forEach((q, idx) => {
                const sel = selectedAnswers[idx];
                if (sel === undefined || sel === null) { skipped++; return; }
                if (q.options[sel]?.is_correct) correct++; else wrong++;
            });
            setScorecard({
                correct, wrong, skipped,
                total: questions.length,
                score_percentage: Math.round((correct / questions.length) * 100),
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
                <Text style={{ fontSize: 15, fontWeight: 'bold', color: '#111827' }}>{title}</Text>
                <Text style={{ fontSize: 13, color: '#6b7280', fontWeight: '600' }}>
                    {currentIdx + 1}/{questions.length}
                </Text>
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
                    <Text style={{ fontSize: 15, fontWeight: '500', color: '#111827', lineHeight: 24 }}>
                        {currentQ.question_text}
                    </Text>
                </View>

                {/* Options */}
                {currentQ.options.map((opt, i) => {
                    const isSelected = selectedAnswers[currentIdx] === i;
                    return (
                        <TouchableOpacity
                            key={i}
                            onPress={() => selectOption(i)}
                            activeOpacity={0.7}
                            style={{
                                flexDirection: 'row', alignItems: 'center',
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
                                alignItems: 'center', justifyContent: 'center', marginRight: 12,
                            }}>
                                {isSelected && <View style={{ width: 7, height: 7, borderRadius: 3.5, backgroundColor: '#fff' }} />}
                            </View>
                            <Text style={{ fontSize: 14, fontWeight: isSelected ? '600' : '400', color: isSelected ? '#9a3412' : '#374151', flex: 1 }}>
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
