import React, { useState, useEffect } from 'react';
import { View, Text, ScrollView, TouchableOpacity, ActivityIndicator, SafeAreaView } from 'react-native';
import { Ionicons } from '@expo/vector-icons';
import { AnalyticsAPI } from '../../services/api';
import { COLORS } from '../../styles/theme';

export default function PostTestResultsScreen({ navigation, route }: any) {
    const { attemptId } = route.params;
    const [data, setData] = useState<any>(null);
    const [loading, setLoading] = useState(true);
    const [expandedSubjects, setExpandedSubjects] = useState<Set<string>>(new Set());

    const toggleSubject = (subject: string) => {
        setExpandedSubjects(prev => {
            const next = new Set(prev);
            if (next.has(subject)) next.delete(subject); else next.add(subject);
            return next;
        });
    };

    useEffect(() => {
        if (!attemptId) return;
        const fetchData = async () => {
            try {
                const res = await AnalyticsAPI.getPostTestResults(attemptId);
                setData(res.data);
            } catch (err) {
                console.error("Failed to fetch results:", err);
            } finally {
                setLoading(false);
            }
        };
        fetchData();
    }, [attemptId]);

    if (loading) {
        return (
            <View style={{ flex: 1, backgroundColor: '#f9fafb', justifyContent: 'center', alignItems: 'center' }}>
                <ActivityIndicator size="large" color={COLORS.primary} />
                <Text style={{ color: '#6b7280', marginTop: 12 }}>Loading results...</Text>
            </View>
        );
    }

    if (!data) {
        return (
            <View style={{ flex: 1, backgroundColor: '#f9fafb', justifyContent: 'center', alignItems: 'center', padding: 20 }}>
                <Ionicons name="alert-circle-outline" size={48} color="#9ca3af" />
                <Text style={{ fontSize: 18, fontWeight: 'bold', color: '#111827', marginTop: 12 }}>Results Not Found</Text>
                <Text style={{ color: '#6b7280', marginTop: 4, textAlign: 'center' }}>This attempt may not have been submitted yet.</Text>
                <TouchableOpacity onPress={() => navigation.goBack()}
                    style={{ marginTop: 20, backgroundColor: COLORS.primary, paddingHorizontal: 24, paddingVertical: 12, borderRadius: 10 }}>
                    <Text style={{ color: '#fff', fontWeight: 'bold' }}>Go Back</Text>
                </TouchableOpacity>
            </View>
        );
    }

    const getAccuracyColor = (pct: number) => pct >= 70 ? '#22c55e' : pct >= 40 ? '#f97316' : '#ef4444';
    const getAccuracyBg = (pct: number) => pct >= 70 ? '#f0fdf4' : pct >= 40 ? '#fff7ed' : '#fef2f2';

    return (
        <SafeAreaView style={{ flex: 1, backgroundColor: '#f9fafb' }}>
            <ScrollView>
                {/* ─── Hero Section ─── */}
                <View style={{ backgroundColor: '#111827', paddingHorizontal: 20, paddingTop: 16, paddingBottom: 24 }}>
                    {/* Back Button */}
                    <TouchableOpacity onPress={() => navigation.goBack()} style={{ flexDirection: 'row', alignItems: 'center', marginBottom: 16 }}>
                        <Ionicons name="arrow-back" size={18} color="#9ca3af" />
                        <Text style={{ color: '#9ca3af', fontSize: 13, marginLeft: 6 }}>Back to Dashboard</Text>
                    </TouchableOpacity>

                    <Text style={{ color: '#fff', fontSize: 20, fontWeight: 'bold', marginBottom: 4 }}>{data.test_title}</Text>
                    <Text style={{ color: '#9ca3af', fontSize: 12, marginBottom: 20 }}>Test Results & Analysis</Text>

                    {/* Score Cards */}
                    <View style={{ flexDirection: 'row', flexWrap: 'wrap', gap: 8 }}>
                        {[
                            { value: data.total_score, label: 'Score' },
                            { value: `#${data.rank}`, label: 'Rank' },
                            { value: `${data.percentile}%`, label: 'Percentile' },
                            { value: `${data.accuracy}%`, label: 'Accuracy' },
                        ].map((item, idx) => (
                            <View key={idx} style={{
                                width: '48%', backgroundColor: 'rgba(255,255,255,0.1)',
                                borderRadius: 16, padding: 14, alignItems: 'center',
                            }}>
                                <Text style={{ color: '#fff', fontSize: 28, fontWeight: '900' }}>{item.value}</Text>
                                <Text style={{ color: '#9ca3af', fontSize: 10, fontWeight: 'bold', textTransform: 'uppercase', letterSpacing: 1, marginTop: 4 }}>{item.label}</Text>
                            </View>
                        ))}
                    </View>

                    {/* Quick Stats */}
                    <View style={{ flexDirection: 'row', justifyContent: 'center', gap: 20, marginTop: 16 }}>
                        <Text style={{ color: '#4ade80', fontSize: 13, fontWeight: '600' }}>✓ {data.correct_count} Correct</Text>
                        <Text style={{ color: '#f87171', fontSize: 13, fontWeight: '600' }}>✗ {data.incorrect_count} Wrong</Text>
                        <Text style={{ color: '#9ca3af', fontSize: 13, fontWeight: '600' }}>○ {data.skipped_count} Skipped</Text>
                    </View>
                </View>

                <View style={{ padding: 16 }}>
                    {/* Encouragement */}
                    {data.encouragement && (
                        <View style={{
                            backgroundColor: '#fff7ed', borderRadius: 16, padding: 16,
                            borderWidth: 1, borderColor: '#fed7aa', marginBottom: 16, alignItems: 'center',
                        }}>
                            <Text style={{ fontSize: 15, fontWeight: 'bold', color: '#111827', textAlign: 'center' }}>{data.encouragement}</Text>
                        </View>
                    )}

                    {/* Nudges */}
                    {data.nudges?.length > 0 && (
                        <View style={{ marginBottom: 16 }}>
                            <Text style={{ fontSize: 16, fontWeight: 'bold', color: '#111827', marginBottom: 10 }}>Smart Insights</Text>
                            {data.nudges.map((nudge: any, idx: number) => {
                                const colors: Record<string, { bg: string; border: string; text: string }> = {
                                    loss_aversion: { bg: '#fef2f2', border: '#fecaca', text: '#7f1d1d' },
                                    social_proof: { bg: '#eff6ff', border: '#bfdbfe', text: '#1e3a5f' },
                                    progress_anchor: { bg: '#faf5ff', border: '#e9d5ff', text: '#581c87' },
                                    specificity_bias: { bg: '#fff7ed', border: '#fed7aa', text: '#9a3412' },
                                };
                                const c = colors[nudge.type] || { bg: '#f9fafb', border: '#e5e7eb', text: '#374151' };
                                return (
                                    <View key={idx} style={{
                                        backgroundColor: c.bg, borderWidth: 1, borderColor: c.border,
                                        borderRadius: 12, padding: 12, marginBottom: 8, flexDirection: 'row', alignItems: 'center',
                                    }}>
                                        <Text style={{ fontSize: 16, marginRight: 8 }}>{nudge.icon}</Text>
                                        <Text style={{ color: c.text, fontSize: 13, flex: 1 }}>{nudge.message}</Text>
                                    </View>
                                );
                            })}
                        </View>
                    )}

                    {/* Weak Topics */}
                    {data.weak_topics?.length > 0 && (
                        <View style={{ marginBottom: 16 }}>
                            <Text style={{ fontSize: 16, fontWeight: 'bold', color: '#111827', marginBottom: 10 }}>🎯 Areas to Improve</Text>
                            {data.weak_topics.map((wt: any, idx: number) => (
                                <View key={idx} style={{
                                    backgroundColor: '#fff', borderRadius: 12, padding: 14, marginBottom: 8,
                                    borderWidth: 1, borderColor: '#fecaca', flexDirection: 'row', justifyContent: 'space-between', alignItems: 'center',
                                }}>
                                    <View style={{ flex: 1 }}>
                                        <Text style={{ fontSize: 14, fontWeight: 'bold', color: '#111827' }}>{wt.topic}</Text>
                                        <Text style={{ fontSize: 11, color: '#6b7280', marginTop: 2 }}>{wt.subject}</Text>
                                    </View>
                                    <View style={{ alignItems: 'flex-end' }}>
                                        <View style={{
                                            backgroundColor: wt.accuracy < 40 ? '#fef2f2' : '#fff7ed',
                                            paddingHorizontal: 8, paddingVertical: 3, borderRadius: 10,
                                        }}>
                                            <Text style={{ color: wt.accuracy < 40 ? '#b91c1c' : '#c2410c', fontWeight: 'bold', fontSize: 12 }}>
                                                {Math.round(wt.accuracy)}%
                                            </Text>
                                        </View>
                                        <Text style={{ fontSize: 10, color: '#9ca3af', marginTop: 2 }}>{wt.total_attempted} Qs</Text>
                                    </View>
                                </View>
                            ))}
                            <TouchableOpacity
                                onPress={() => navigation.navigate('DailyQuizTab')}
                                style={{
                                    backgroundColor: COLORS.primary, borderRadius: 12, paddingVertical: 14, alignItems: 'center', marginTop: 4,
                                    shadowColor: COLORS.primary, shadowOpacity: 0.3, shadowRadius: 8, shadowOffset: { width: 0, height: 4 }, elevation: 5,
                                }}
                            >
                                <Text style={{ color: '#fff', fontWeight: 'bold', fontSize: 15 }}>Practice Weak Areas →</Text>
                            </TouchableOpacity>
                        </View>
                    )}

                    {/* Strong Topics */}
                    {data.strong_topics?.length > 0 && (
                        <View style={{ marginBottom: 16 }}>
                            <Text style={{ fontSize: 16, fontWeight: 'bold', color: '#111827', marginBottom: 10 }}>💪 Your Strengths</Text>
                            <View style={{ flexDirection: 'row', flexWrap: 'wrap', gap: 6 }}>
                                {data.strong_topics.map((st: any, idx: number) => (
                                    <View key={idx} style={{
                                        backgroundColor: '#f0fdf4', borderWidth: 1, borderColor: '#bbf7d0',
                                        paddingHorizontal: 10, paddingVertical: 6, borderRadius: 20,
                                    }}>
                                        <Text style={{ color: '#166534', fontSize: 12, fontWeight: '600' }}>
                                            {st.topic} ({Math.round(st.accuracy)}%)
                                        </Text>
                                    </View>
                                ))}
                            </View>
                        </View>
                    )}

                    {/* Subject & Topic Breakdown */}
                    {data.subject_performances?.length > 0 && (
                        <View style={{ marginBottom: 20 }}>
                            <Text style={{ fontSize: 16, fontWeight: 'bold', color: '#111827', marginBottom: 10 }}>Subject & Topic Breakdown</Text>
                            {data.subject_performances.map((sub: any, idx: number) => {
                                const isExpanded = expandedSubjects.has(sub.subject);
                                const hasTopics = sub.topics?.length > 0;
                                const acc = sub.accuracy_percentage;
                                return (
                                    <View key={idx} style={{ backgroundColor: '#fff', borderRadius: 16, marginBottom: 8, borderWidth: 1, borderColor: '#f3f4f6', overflow: 'hidden' }}>
                                        <TouchableOpacity
                                            onPress={() => hasTopics && toggleSubject(sub.subject)}
                                            style={{ flexDirection: 'row', justifyContent: 'space-between', alignItems: 'center', padding: 14 }}
                                        >
                                            <View style={{ flexDirection: 'row', alignItems: 'center', flex: 1 }}>
                                                {hasTopics && (
                                                    <Ionicons
                                                        name={isExpanded ? 'chevron-down' : 'chevron-forward'}
                                                        size={14} color="#9ca3af" style={{ marginRight: 8 }}
                                                    />
                                                )}
                                                <View>
                                                    <Text style={{ fontWeight: 'bold', color: '#111827', fontSize: 14 }}>{sub.subject}</Text>
                                                    <Text style={{ fontSize: 11, color: '#6b7280', marginTop: 2 }}>{sub.correct}/{sub.total_questions} correct</Text>
                                                </View>
                                            </View>
                                            <View style={{ flexDirection: 'row', alignItems: 'center', gap: 8 }}>
                                                <View style={{ width: 60, height: 4, backgroundColor: '#f3f4f6', borderRadius: 2 }}>
                                                    <View style={{ height: 4, borderRadius: 2, backgroundColor: getAccuracyColor(acc), width: `${acc}%` }} />
                                                </View>
                                                <View style={{ backgroundColor: getAccuracyBg(acc), paddingHorizontal: 6, paddingVertical: 2, borderRadius: 8 }}>
                                                    <Text style={{ color: getAccuracyColor(acc), fontWeight: 'bold', fontSize: 12 }}>
                                                        {Math.round(acc)}%
                                                    </Text>
                                                </View>
                                            </View>
                                        </TouchableOpacity>

                                        {isExpanded && hasTopics && (
                                            <View style={{ borderTopWidth: 1, borderTopColor: '#f3f4f6', backgroundColor: '#f9fafb', paddingHorizontal: 14, paddingVertical: 8 }}>
                                                {sub.topics.map((tp: any, tidx: number) => (
                                                    <View key={tidx} style={{ flexDirection: 'row', justifyContent: 'space-between', alignItems: 'center', paddingVertical: 6 }}>
                                                        <View style={{ flexDirection: 'row', alignItems: 'center', flex: 1 }}>
                                                            <View style={{ width: 6, height: 6, borderRadius: 3, backgroundColor: getAccuracyColor(tp.accuracy_percentage), marginRight: 8 }} />
                                                            <Text style={{ fontSize: 13, color: '#374151' }}>{tp.topic}</Text>
                                                            <Text style={{ fontSize: 11, color: '#9ca3af', marginLeft: 4 }}>({tp.correct}/{tp.total_questions})</Text>
                                                        </View>
                                                        <Text style={{ fontSize: 12, fontWeight: 'bold', color: getAccuracyColor(tp.accuracy_percentage) }}>
                                                            {Math.round(tp.accuracy_percentage)}%
                                                        </Text>
                                                    </View>
                                                ))}
                                            </View>
                                        )}
                                    </View>
                                );
                            })}
                        </View>
                    )}
                </View>
            </ScrollView>
        </SafeAreaView>
    );
}
