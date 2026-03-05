import React, { useState, useEffect } from 'react';
import { View, Text, ScrollView, TouchableOpacity, ActivityIndicator } from 'react-native';
import { Ionicons } from '@expo/vector-icons';
import { styles, COLORS } from '../../styles/theme';
import { QuizAPI } from '../../services/api';

export default function DailyQuizScreen({ navigation }: any) {
    const [categories, setCategories] = useState<any[]>([]);
    const [streak, setStreak] = useState<any>(null);
    const [weakQuiz, setWeakQuiz] = useState<any>(null);
    const [loading, setLoading] = useState(true);

    useEffect(() => {
        const fetchData = async () => {
            try {
                const [catRes, weakRes] = await Promise.all([
                    QuizAPI.getCategories(),
                    QuizAPI.getWeakTopicQuiz()
                ]);
                setCategories(catRes.data.categories || []);
                setStreak(catRes.data.streak || null);
                setWeakQuiz(weakRes.data || null);
            } catch (err) {
                console.error("Failed to fetch quiz data:", err);
            } finally {
                setLoading(false);
            }
        };
        fetchData();
    }, []);

    const getCategoryEmoji = (key: string): string => {
        const map: Record<string, string> = {
            polity: '⚖️', history: '🏛️', geography: '🌍', economics: '📈',
            general_science: '🔬', reasoning: '🧠', quantitative_aptitude: '📐',
            english: '📖', computer_knowledge: '💻', current_affairs: '📰',
            general_knowledge: '🎓',
        };
        return map[key] || '📚';
    };

    if (loading) {
        return (
            <View style={{ flex: 1, justifyContent: 'center', alignItems: 'center', backgroundColor: '#f9fafb' }}>
                <ActivityIndicator size="large" color={COLORS.primary} />
            </View>
        );
    }

    return (
        <ScrollView style={styles.container}>
            <View style={styles.contentPadAlt}>
                {/* Streak Banner */}
                {streak && (
                    <View style={[styles.card, {
                        backgroundColor: streak.at_risk ? '#ef4444' : streak.current_streak > 0 ? '#f97316' : '#111827',
                        flexDirection: 'row',
                        alignItems: 'center',
                        marginTop: 0
                    }]}>
                        <View style={{
                            width: 50, height: 50, borderRadius: 25,
                            backgroundColor: 'rgba(255,255,255,0.2)',
                            alignItems: 'center', justifyContent: 'center'
                        }}>
                            <Ionicons name="flame" size={28} color="#fff" />
                        </View>
                        <View style={{ flex: 1, marginLeft: 15 }}>
                            <Text style={{ color: '#fff', fontSize: 16, fontWeight: 'bold' }}>
                                {streak.nudge}
                            </Text>
                            <View style={{ flexDirection: 'row', marginTop: 6 }}>
                                <Text style={{ color: 'rgba(255,255,255,0.8)', fontSize: 12 }}>
                                    Current: {streak.current_streak} days
                                </Text>
                                <Text style={{ color: 'rgba(255,255,255,0.8)', fontSize: 12, marginLeft: 15 }}>
                                    Longest: {streak.longest_streak} days
                                </Text>
                            </View>
                        </View>
                    </View>
                )}

                {/* Recommended Weak Topics Quiz */}
                {weakQuiz?.weak_topics?.length > 0 && (
                    <View style={[styles.card, { backgroundColor: '#fff7ed', borderColor: '#fed7aa', borderWidth: 1 }]}>
                        <View style={{ flexDirection: 'row', alignItems: 'center', marginBottom: 12 }}>
                            <View style={{
                                width: 40, height: 40, borderRadius: 12,
                                backgroundColor: '#ffedd5', alignItems: 'center', justifyContent: 'center'
                            }}>
                                <Text style={{ fontSize: 20 }}>🎯</Text>
                            </View>
                            <View style={{ marginLeft: 12, flex: 1 }}>
                                <Text style={{ fontSize: 16, fontWeight: 'bold', color: '#1f2937' }}>
                                    Improve Weak Areas
                                </Text>
                                <Text style={{ fontSize: 12, color: '#6b7280', marginTop: 2 }}>
                                    {weakQuiz.message}
                                </Text>
                            </View>
                        </View>

                        {/* Weak topic pills */}
                        <View style={{ flexDirection: 'row', flexWrap: 'wrap', gap: 6, marginBottom: 12 }}>
                            {weakQuiz.weak_topics.slice(0, 4).map((wt: any, idx: number) => (
                                <View key={idx} style={{
                                    flexDirection: 'row', alignItems: 'center',
                                    backgroundColor: '#fff', paddingHorizontal: 10, paddingVertical: 5,
                                    borderRadius: 16, borderWidth: 1, borderColor: '#fed7aa'
                                }}>
                                    <View style={{
                                        width: 6, height: 6, borderRadius: 3,
                                        backgroundColor: wt.accuracy < 40 ? '#ef4444' : '#f97316',
                                        marginRight: 6
                                    }} />
                                    <Text style={{ fontSize: 11, fontWeight: '600', color: '#374151' }}>
                                        {wt.subject}
                                    </Text>
                                    <Text style={{
                                        fontSize: 11, fontWeight: 'bold', marginLeft: 4,
                                        color: wt.accuracy < 40 ? '#dc2626' : '#ea580c'
                                    }}>
                                        {wt.accuracy}%
                                    </Text>
                                </View>
                            ))}
                        </View>

                        <TouchableOpacity onPress={() => navigation.navigate('QuizSession', { subject: null, title: 'Weak Topic Practice' })} style={{
                            backgroundColor: COLORS.primary, paddingVertical: 12,
                            borderRadius: 12, alignItems: 'center'
                        }}>
                            <Text style={{ color: '#fff', fontWeight: 'bold', fontSize: 14 }}>
                                Start Practice →
                            </Text>
                        </TouchableOpacity>
                    </View>
                )}

                {/* Quiz Categories Grid */}
                <Text style={[styles.sectionTitle, { marginTop: 20 }]}>Daily Quiz Categories</Text>
                <Text style={{ color: '#6b7280', fontSize: 13, marginBottom: 16, marginTop: -8 }}>
                    Choose a subject to practice. 10 random questions daily!
                </Text>

                <View style={{ flexDirection: 'row', flexWrap: 'wrap', justifyContent: 'space-between' }}>
                    {categories.map((cat: any, idx: number) => (
                        <TouchableOpacity
                            key={idx}
                            disabled={!cat.has_questions}
                            onPress={() => navigation.navigate('QuizSession', { subject: cat.key, title: cat.name, limit: 10 })}
                            style={{
                                width: '48%', backgroundColor: cat.has_questions ? '#fff' : '#f3f4f6',
                                borderRadius: 16, padding: 16, marginBottom: 12,
                                borderWidth: 1, borderColor: '#f3f4f6',
                                opacity: cat.has_questions ? 1 : 0.5
                            }}
                        >
                            <Text style={{ fontSize: 28, marginBottom: 8 }}>
                                {getCategoryEmoji(cat.key)}
                            </Text>
                            <Text style={{ fontSize: 15, fontWeight: 'bold', color: '#1f2937' }}>
                                {cat.name}
                            </Text>
                            <Text style={{ fontSize: 12, color: '#9ca3af', marginTop: 2 }}>
                                {cat.question_count > 0 ? `${cat.question_count} questions` : 'Coming soon'}
                            </Text>
                        </TouchableOpacity>
                    ))}
                </View>

                {/* Empty state */}
                {(!weakQuiz?.weak_topics || weakQuiz.weak_topics.length === 0) && (
                    <View style={[styles.card, {
                        backgroundColor: '#eef2ff', borderColor: '#c7d2fe', borderWidth: 1,
                        alignItems: 'center', paddingVertical: 30
                    }]}>
                        <Text style={{ fontSize: 32, marginBottom: 12 }}>📝</Text>
                        <Text style={{ fontSize: 18, fontWeight: 'bold', color: '#1f2937', marginBottom: 6 }}>
                            Take a Mock Test First!
                        </Text>
                        <Text style={{ fontSize: 13, color: '#6b7280', textAlign: 'center', lineHeight: 20 }}>
                            Once you attempt a mock test, we'll create a personalized quiz targeting your weak areas.
                        </Text>
                    </View>
                )}
            </View>
        </ScrollView>
    );
}
