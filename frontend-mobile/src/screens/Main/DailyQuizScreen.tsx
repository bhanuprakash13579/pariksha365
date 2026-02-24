import React from 'react';
import { View, Text, ScrollView, TouchableOpacity } from 'react-native';
import { Ionicons } from '@expo/vector-icons';
import { styles, COLORS } from '../../styles/theme';

export default function DailyQuizScreen({ navigation }: any) {
    const dailyQuizzes = [
        { title: 'Current Affairs - Oct 25', time: '10 Mins', attempts: '4.2k', xp: '+20 XP', completed: false, tag: 'GK' },
        { title: 'English Vocab Mini', time: '5 Mins', attempts: '12k', xp: '+10 XP', completed: true, tag: 'English' },
        { title: 'Quant Speed Test', time: '15 Mins', attempts: '8k', xp: '+30 XP', completed: false, tag: 'Quant' },
        { title: 'Indian Polity Quick Revision', time: '10 Mins', attempts: '3.5k', xp: '+15 XP', completed: false, tag: 'Polity' },
    ];

    return (
        <ScrollView style={styles.container}>
            <View style={styles.contentPadAlt}>
                {/* Streaks Banner */}
                <View style={[styles.card, { backgroundColor: '#111827', flexDirection: 'row', alignItems: 'center', marginTop: 0 }]}>
                    <View style={{ width: 50, height: 50, borderRadius: 25, backgroundColor: 'rgba(249, 115, 22, 0.2)', alignItems: 'center', justifyContent: 'center' }}>
                        <Ionicons name="flame" size={28} color={COLORS.primary} />
                    </View>
                    <View style={{ flex: 1, marginLeft: 15 }}>
                        <Text style={{ color: COLORS.white, fontSize: 18, fontWeight: 'bold' }}>3 Day Streak! 🔥</Text>
                        <Text style={{ color: '#9ca3af', fontSize: 13, marginTop: 4 }}>Complete a daily quiz to extend your streak.</Text>
                    </View>
                </View>

                {/* Boost Rank Call to Action */}
                <View style={[styles.infoBox, { flexDirection: 'row', alignItems: 'center', backgroundColor: '#eef2ff', borderColor: '#c7d2fe', padding: 20 }]}>
                    <Ionicons name="flash" size={32} color="#4f46e5" />
                    <View style={{ marginLeft: 15, flex: 1 }}>
                        <Text style={{ fontSize: 16, fontWeight: 'bold', color: '#312e81' }}>Boost Your Rank</Text>
                        <Text style={{ color: '#4338ca', fontSize: 13, marginTop: 4 }}>Complete daily micro-quizzes to earn XP and extend your learning streak.</Text>
                    </View>
                </View>

                <Text style={[styles.sectionTitle, { marginTop: 25 }]}>Live Today</Text>

                {dailyQuizzes.map((quiz, i) => (
                    <TouchableOpacity key={i} style={[styles.card, { flexDirection: 'column', alignItems: 'stretch' }]}>
                        <View style={styles.flexRowBetween}>
                            <View style={{ flexDirection: 'row', alignItems: 'center' }}>
                                <View style={{ backgroundColor: quiz.completed ? '#dcfce7' : '#e0e7ff', paddingHorizontal: 10, paddingVertical: 4, borderRadius: 12 }}>
                                    <Text style={{ color: quiz.completed ? '#166534' : '#4338ca', fontSize: 10, fontWeight: 'bold' }}>{quiz.tag}</Text>
                                </View>
                                <Text style={{ color: COLORS.textSub, fontSize: 12, marginLeft: 10 }}>{quiz.time}</Text>
                            </View>
                            <Text style={{ color: quiz.completed ? COLORS.textSub : COLORS.primary, fontSize: 12, fontWeight: 'bold' }}>
                                {quiz.completed ? 'Completed' : quiz.xp}
                            </Text>
                        </View>

                        <Text style={{ fontSize: 16, fontWeight: 'bold', color: COLORS.text, marginTop: 15 }}>{quiz.title}</Text>

                        <View style={[styles.flexRowBetween, { marginTop: 15 }]}>
                            <View style={{ flexDirection: 'row', alignItems: 'center' }}>
                                <Ionicons name="people" size={14} color={COLORS.textSub} />
                                <Text style={{ color: COLORS.textSub, fontSize: 12, marginLeft: 5 }}>{quiz.attempts} attempted today</Text>
                            </View>

                            <TouchableOpacity
                                style={{
                                    backgroundColor: quiz.completed ? '#f3f4f6' : COLORS.primary,
                                    paddingVertical: 8,
                                    paddingHorizontal: 20,
                                    borderRadius: 8
                                }}
                            >
                                <Text style={{ color: quiz.completed ? '#9ca3af' : COLORS.white, fontWeight: 'bold' }}>
                                    {quiz.completed ? 'Review' : 'Start'}
                                </Text>
                            </TouchableOpacity>
                        </View>
                    </TouchableOpacity>
                ))}
            </View>
        </ScrollView>
    );
}
