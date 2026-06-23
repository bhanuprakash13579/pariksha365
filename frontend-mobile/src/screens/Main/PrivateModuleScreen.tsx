import React, { useState, useEffect, useCallback } from 'react';
import {
    View, Text, ScrollView, TouchableOpacity,
    ActivityIndicator, SafeAreaView, RefreshControl,
} from 'react-native';
import { Ionicons } from '@expo/vector-icons';
import { useFocusEffect } from '@react-navigation/native';
import { PrivateModuleAPI } from '../../services/api';
import { COLORS } from '../../styles/theme';

interface Subject {
    subject: string;
    question_count: number;
    attempted_count: number;
}

interface Module {
    slug: string;
    name: string;
    description: string;
    subjects: Subject[];
}

const SUBJECT_EMOJI: Record<string, string> = {
    'Industrial Relations': '⚙️',
    'Labour Laws': '⚖️',
    'Social Security': '🛡️',
    'Accounting': '📊',
    'Finance & Accounts': '💰',
    'Economics & Governance': '🏛️',
    'General Awareness': '🌐',
    'English': '📖',
    'Reasoning': '🧠',
    'Quantitative Aptitude': '📐',
    'General Studies': '📚',
};

function getEmoji(subject: string): string {
    return SUBJECT_EMOJI[subject] || '📝';
}

export default function PrivateModuleScreen({ navigation, route }: any) {
    const { slug, moduleName } = route.params || {};

    const [module, setModule] = useState<Module | null>(null);
    const [loading, setLoading] = useState(true);
    const [refreshing, setRefreshing] = useState(false);
    const [error, setError] = useState<string | null>(null);

    const fetchModule = async (isRefresh = false) => {
        if (isRefresh) setRefreshing(true); else setLoading(true);
        setError(null);
        try {
            const res = await PrivateModuleAPI.getModule(slug);
            setModule(res.data);
        } catch (err: any) {
            const msg = err?.response?.data?.detail ?? 'Failed to load module';
            setError(msg);
        } finally {
            setLoading(false);
            setRefreshing(false);
        }
    };

    useFocusEffect(
        useCallback(() => {
            fetchModule();
        }, [slug])
    );

    if (loading) {
        return (
            <View style={{ flex: 1, backgroundColor: '#f9fafb', justifyContent: 'center', alignItems: 'center' }}>
                <ActivityIndicator size="large" color={COLORS.primary} />
                <Text style={{ color: '#6b7280', marginTop: 12 }}>Loading module...</Text>
            </View>
        );
    }

    if (error || !module) {
        return (
            <SafeAreaView style={{ flex: 1, backgroundColor: '#f9fafb', justifyContent: 'center', alignItems: 'center', padding: 24 }}>
                <Ionicons name="lock-closed-outline" size={52} color="#9ca3af" />
                <Text style={{ fontSize: 18, fontWeight: 'bold', color: '#111827', marginTop: 12, textAlign: 'center' }}>
                    {error || 'Module not available'}
                </Text>
                <Text style={{ color: '#6b7280', marginTop: 6, textAlign: 'center' }}>
                    Contact support if you believe you should have access.
                </Text>
                <TouchableOpacity
                    onPress={() => navigation.goBack()}
                    style={{ marginTop: 20, backgroundColor: COLORS.primary, paddingHorizontal: 24, paddingVertical: 12, borderRadius: 10 }}
                >
                    <Text style={{ color: '#fff', fontWeight: 'bold' }}>Go Back</Text>
                </TouchableOpacity>
            </SafeAreaView>
        );
    }

    const totalQuestions = module.subjects.reduce((s, sub) => s + sub.question_count, 0);
    const totalAttempted = module.subjects.reduce((s, sub) => s + sub.attempted_count, 0);
    const overallPct = totalQuestions > 0 ? Math.round((totalAttempted / totalQuestions) * 100) : 0;

    return (
        <SafeAreaView style={{ flex: 1, backgroundColor: '#f9fafb' }}>
            <ScrollView
                contentContainerStyle={{ padding: 16, paddingBottom: 40 }}
                refreshControl={<RefreshControl refreshing={refreshing} onRefresh={() => fetchModule(true)} tintColor={COLORS.primary} />}
            >
                {/* Module Header */}
                <View style={{
                    backgroundColor: '#111827', borderRadius: 20, padding: 20, marginBottom: 20,
                    shadowColor: '#000', shadowOpacity: 0.15, shadowRadius: 10, shadowOffset: { width: 0, height: 4 }, elevation: 6,
                }}>
                    <View style={{ flexDirection: 'row', alignItems: 'center', marginBottom: 8 }}>
                        <View style={{ backgroundColor: COLORS.primary, borderRadius: 10, padding: 8, marginRight: 12 }}>
                            <Ionicons name="briefcase" size={22} color="#fff" />
                        </View>
                        <Text style={{ fontSize: 20, fontWeight: '900', color: '#fff', flex: 1 }}>{module.name}</Text>
                    </View>
                    {module.description ? (
                        <Text style={{ color: '#9ca3af', fontSize: 13, marginBottom: 14 }}>{module.description}</Text>
                    ) : null}

                    {/* Overall progress */}
                    <View style={{ flexDirection: 'row', justifyContent: 'space-between', marginBottom: 6 }}>
                        <Text style={{ color: '#d1d5db', fontSize: 12 }}>Overall progress</Text>
                        <Text style={{ color: '#f97316', fontWeight: 'bold', fontSize: 12 }}>{totalAttempted}/{totalQuestions} ({overallPct}%)</Text>
                    </View>
                    <View style={{ height: 6, backgroundColor: '#374151', borderRadius: 3 }}>
                        <View style={{ height: 6, backgroundColor: COLORS.primary, borderRadius: 3, width: `${overallPct}%` as any }} />
                    </View>
                </View>

                <Text style={{ fontSize: 16, fontWeight: 'bold', color: '#111827', marginBottom: 14 }}>
                    Choose a Subject to Practice
                </Text>

                {module.subjects.map((sub, idx) => {
                    const pct = sub.question_count > 0
                        ? Math.round((sub.attempted_count / sub.question_count) * 100)
                        : 0;
                    const remaining = sub.question_count - sub.attempted_count;
                    return (
                        <TouchableOpacity
                            key={idx}
                            onPress={() => navigation.navigate('PrivateModuleTopics', {
                                slug: module.slug,
                                moduleName: module.name,
                                subject: sub.subject,
                                subjectEmoji: getEmoji(sub.subject),
                            })}
                            activeOpacity={0.85}
                            style={{
                                backgroundColor: '#fff', borderRadius: 16, padding: 16, marginBottom: 12,
                                borderWidth: 1, borderColor: '#f3f4f6',
                                shadowColor: '#000', shadowOpacity: 0.04, shadowRadius: 6, shadowOffset: { width: 0, height: 2 }, elevation: 2,
                            }}
                        >
                            <View style={{ flexDirection: 'row', alignItems: 'center', marginBottom: 10 }}>
                                <Text style={{ fontSize: 28, marginRight: 12 }}>{getEmoji(sub.subject)}</Text>
                                <View style={{ flex: 1 }}>
                                    <Text style={{ fontSize: 15, fontWeight: '700', color: '#111827' }}>{sub.subject}</Text>
                                    <Text style={{ fontSize: 12, color: '#6b7280', marginTop: 2 }}>
                                        {sub.question_count} questions
                                        {remaining > 0 ? ` · ${remaining} remaining today` : ' · All attempted today!'}
                                    </Text>
                                </View>
                                <View style={{
                                    backgroundColor: pct >= 80 ? '#f0fdf4' : '#fff7ed',
                                    borderRadius: 20, paddingHorizontal: 10, paddingVertical: 4,
                                }}>
                                    <Text style={{ fontSize: 12, fontWeight: 'bold', color: pct >= 80 ? '#16a34a' : COLORS.primary }}>
                                        {pct}%
                                    </Text>
                                </View>
                            </View>

                            {/* Progress bar */}
                            <View style={{ height: 4, backgroundColor: '#f3f4f6', borderRadius: 2 }}>
                                <View style={{
                                    height: 4, borderRadius: 2,
                                    backgroundColor: pct >= 80 ? '#22c55e' : COLORS.primary,
                                    width: `${pct}%` as any,
                                }} />
                            </View>

                            <View style={{ flexDirection: 'row', alignItems: 'center', justifyContent: 'flex-end', marginTop: 10 }}>
                                <Text style={{ fontSize: 13, color: COLORS.primary, fontWeight: '600', marginRight: 4 }}>
                                    View Chapters
                                </Text>
                                <Ionicons name="chevron-forward-circle" size={18} color={COLORS.primary} />
                            </View>
                        </TouchableOpacity>
                    );
                })}

                {module.subjects.length === 0 && (
                    <View style={{ alignItems: 'center', paddingTop: 40 }}>
                        <Ionicons name="hourglass-outline" size={48} color="#9ca3af" />
                        <Text style={{ color: '#6b7280', marginTop: 12, textAlign: 'center' }}>
                            No questions available yet. Check back soon!
                        </Text>
                    </View>
                )}
            </ScrollView>
        </SafeAreaView>
    );
}
