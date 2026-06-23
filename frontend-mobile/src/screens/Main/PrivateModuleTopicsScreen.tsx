import React, { useState, useEffect, useCallback } from 'react';
import {
    View, Text, ScrollView, TouchableOpacity,
    ActivityIndicator, SafeAreaView, RefreshControl,
} from 'react-native';
import { Ionicons } from '@expo/vector-icons';
import { useFocusEffect } from '@react-navigation/native';
import { PrivateModuleAPI } from '../../services/api';
import { COLORS } from '../../styles/theme';

interface Topic {
    topic: string;
    topic_code: string;
    question_count: number;
}

export default function PrivateModuleTopicsScreen({ navigation, route }: any) {
    const { slug, moduleName, subject, subjectEmoji = '📝' } = route.params || {};

    const [topics, setTopics] = useState<Topic[]>([]);
    const [loading, setLoading] = useState(true);
    const [refreshing, setRefreshing] = useState(false);
    const [error, setError] = useState<string | null>(null);

    const fetchTopics = async (isRefresh = false) => {
        if (isRefresh) setRefreshing(true); else setLoading(true);
        setError(null);
        try {
            const res = await PrivateModuleAPI.getSubjectTopics(slug, subject);
            setTopics(res.data?.topics || []);
        } catch (err: any) {
            setError(err?.response?.data?.detail ?? 'Failed to load chapters');
        } finally {
            setLoading(false);
            setRefreshing(false);
        }
    };

    useFocusEffect(useCallback(() => { fetchTopics(); }, [slug, subject]));

    const startTopicQuiz = (topic: string | null) => {
        navigation.navigate('QuizSession', {
            subject,
            title: topic ?? subject,
            limit: 10,
            moduleSlug: slug,
            ...(topic ? { moduleTopic: topic } : {}),
        });
    };

    if (loading) {
        return (
            <View style={{ flex: 1, backgroundColor: '#f9fafb', justifyContent: 'center', alignItems: 'center' }}>
                <ActivityIndicator size="large" color={COLORS.primary} />
            </View>
        );
    }

    if (error) {
        return (
            <SafeAreaView style={{ flex: 1, backgroundColor: '#f9fafb', justifyContent: 'center', alignItems: 'center', padding: 24 }}>
                <Ionicons name="alert-circle-outline" size={48} color="#9ca3af" />
                <Text style={{ fontSize: 16, color: '#374151', marginTop: 12, textAlign: 'center' }}>{error}</Text>
                <TouchableOpacity
                    onPress={() => navigation.goBack()}
                    style={{ marginTop: 20, backgroundColor: COLORS.primary, paddingHorizontal: 24, paddingVertical: 12, borderRadius: 10 }}
                >
                    <Text style={{ color: '#fff', fontWeight: 'bold' }}>Go Back</Text>
                </TouchableOpacity>
            </SafeAreaView>
        );
    }

    const totalQs = topics.reduce((s, t) => s + t.question_count, 0);

    return (
        <SafeAreaView style={{ flex: 1, backgroundColor: '#f9fafb' }}>
            <ScrollView
                contentContainerStyle={{ padding: 16, paddingBottom: 40 }}
                refreshControl={<RefreshControl refreshing={refreshing} onRefresh={() => fetchTopics(true)} tintColor={COLORS.primary} />}
            >
                {/* Subject header */}
                <View style={{
                    backgroundColor: '#111827', borderRadius: 16, padding: 18, marginBottom: 20,
                    shadowColor: '#000', shadowOpacity: 0.12, shadowRadius: 8, shadowOffset: { width: 0, height: 3 }, elevation: 4,
                }}>
                    <Text style={{ fontSize: 26, marginBottom: 6 }}>{subjectEmoji}</Text>
                    <Text style={{ fontSize: 20, fontWeight: '900', color: '#fff' }}>{subject}</Text>
                    <Text style={{ color: '#9ca3af', fontSize: 13, marginTop: 4 }}>
                        {topics.length} chapter{topics.length !== 1 ? 's' : ''} · {totalQs} questions total
                    </Text>
                </View>

                {/* Practice all chapters button */}
                <TouchableOpacity
                    onPress={() => startTopicQuiz(null)}
                    activeOpacity={0.85}
                    style={{
                        backgroundColor: COLORS.primary, borderRadius: 14, padding: 16, marginBottom: 20,
                        flexDirection: 'row', alignItems: 'center',
                        shadowColor: COLORS.primary, shadowOpacity: 0.3, shadowRadius: 8, shadowOffset: { width: 0, height: 3 }, elevation: 4,
                    }}
                >
                    <View style={{ backgroundColor: 'rgba(255,255,255,0.2)', borderRadius: 10, padding: 8, marginRight: 12 }}>
                        <Ionicons name="shuffle" size={20} color="#fff" />
                    </View>
                    <View style={{ flex: 1 }}>
                        <Text style={{ fontSize: 16, fontWeight: '800', color: '#fff' }}>Mixed Practice — All Chapters</Text>
                        <Text style={{ fontSize: 12, color: 'rgba(255,255,255,0.8)', marginTop: 2 }}>
                            10 questions spread across all chapters
                        </Text>
                    </View>
                    <Ionicons name="arrow-forward-circle" size={22} color="#fff" />
                </TouchableOpacity>

                <Text style={{ fontSize: 15, fontWeight: '700', color: '#374151', marginBottom: 12 }}>
                    Or study chapter-by-chapter:
                </Text>

                {topics.map((t, idx) => (
                    <TouchableOpacity
                        key={idx}
                        onPress={() => startTopicQuiz(t.topic)}
                        activeOpacity={0.85}
                        style={{
                            backgroundColor: '#fff', borderRadius: 14, padding: 16, marginBottom: 10,
                            borderWidth: 1, borderColor: '#f3f4f6',
                            flexDirection: 'row', alignItems: 'center',
                            shadowColor: '#000', shadowOpacity: 0.04, shadowRadius: 4, shadowOffset: { width: 0, height: 1 }, elevation: 1,
                        }}
                    >
                        <View style={{
                            width: 40, height: 40, borderRadius: 10,
                            backgroundColor: '#f0f9ff', alignItems: 'center', justifyContent: 'center', marginRight: 14,
                        }}>
                            <Text style={{ fontSize: 16, fontWeight: '700', color: COLORS.primary }}>
                                {idx + 1}
                            </Text>
                        </View>
                        <View style={{ flex: 1 }}>
                            <Text style={{ fontSize: 14, fontWeight: '700', color: '#111827' }} numberOfLines={2}>
                                {t.topic}
                            </Text>
                            <Text style={{ fontSize: 12, color: '#6b7280', marginTop: 3 }}>
                                {t.question_count} question{t.question_count !== 1 ? 's' : ''}
                            </Text>
                        </View>
                        <View style={{ alignItems: 'center' }}>
                            <Ionicons name="play-circle-outline" size={26} color={COLORS.primary} />
                        </View>
                    </TouchableOpacity>
                ))}

                {topics.length === 0 && (
                    <View style={{ alignItems: 'center', paddingTop: 40 }}>
                        <Ionicons name="hourglass-outline" size={48} color="#9ca3af" />
                        <Text style={{ color: '#6b7280', marginTop: 12, textAlign: 'center' }}>
                            No chapters found yet. Check back soon!
                        </Text>
                    </View>
                )}
            </ScrollView>
        </SafeAreaView>
    );
}
