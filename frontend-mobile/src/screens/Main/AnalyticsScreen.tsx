import React, { useState, useEffect } from 'react';
import { View, Text, ScrollView, Dimensions, ActivityIndicator, TouchableOpacity } from 'react-native';
import { BarChart } from 'react-native-chart-kit';
import { styles, COLORS } from '../../styles/theme';
import { Ionicons } from '@expo/vector-icons';
import { AnalyticsAPI, UserAPI } from '../../services/api';

const screenWidth = Dimensions.get("window").width;

export default function AnalyticsScreen({ navigation }: any) {
    const [enrollments, setEnrollments] = useState<any[]>([]);
    const [selectedCourseId, setSelectedCourseId] = useState<string | null>(null);
    const [analytics, setAnalytics] = useState<any>(null);
    const [loading, setLoading] = useState(true);

    useEffect(() => {
        const fetchInitialData = async () => {
            try {
                const res = await UserAPI.getEnrollments();
                if (res.data && res.data.length > 0) {
                    setEnrollments(res.data);
                    setSelectedCourseId(res.data[0].id);
                } else {
                    setLoading(false);
                }
            } catch (err) {
                console.error(err);
                setLoading(false);
            }
        };
        fetchInitialData();
    }, []);

    useEffect(() => {
        if (!selectedCourseId) return;
        const fetchAnalytics = async () => {
            setLoading(true);
            try {
                const res = await AnalyticsAPI.getSeriesAnalytics(selectedCourseId);
                setAnalytics(res.data);
            } catch (err) {
                console.error(err);
            } finally {
                setLoading(false);
            }
        };
        fetchAnalytics();
    }, [selectedCourseId]);

    if (loading && !analytics) {
        return (
            <View style={[styles.container, { justifyContent: 'center', alignItems: 'center' }]}>
                <ActivityIndicator size="large" color={COLORS.primary} />
            </View>
        );
    }

    if (enrollments.length === 0) {
        return (
            <View style={[styles.container, { justifyContent: 'center', alignItems: 'center', padding: 20 }]}>
                <Ionicons name="stats-chart" size={64} color={COLORS.border} />
                <Text style={{ textAlign: 'center', color: COLORS.textSub, marginTop: 20, fontSize: 16 }}>
                    You need to enroll in a course to see your performance analytics.
                </Text>
            </View>
        );
    }

    const hasData = analytics && analytics.subject_performances && analytics.subject_performances.length > 0;

    const data = hasData ? {
        labels: analytics.subject_performances.map((s: any) => s.subject.length > 7 ? s.subject.substring(0, 6) + '..' : s.subject),
        datasets: [{ data: analytics.subject_performances.map((s: any) => s.accuracy_percentage) }]
    } : { labels: ["No Data"], datasets: [{ data: [0] }] };

    // Find the weakest subject for the nudge banner
    let weakestSubject = null;
    if (hasData) {
        weakestSubject = [...analytics.subject_performances].sort((a, b) => a.accuracy_percentage - b.accuracy_percentage)[0];
    }

    const chartConfig = {
        backgroundGradientFrom: "#ffffff",
        backgroundGradientTo: "#ffffff",
        color: (opacity = 1) => `rgba(249, 115, 22, ${opacity})`,
        labelColor: (opacity = 1) => `rgba(107, 114, 128, ${opacity})`,
        strokeWidth: 2,
        barPercentage: 0.5,
        fillShadowGradientFrom: COLORS.primary,
        fillShadowGradientFromOpacity: 0.8,
        fillShadowGradientTo: COLORS.primary,
        fillShadowGradientToOpacity: 0.8,
        useShadowColorFromDataset: false
    };

    return (
        <ScrollView style={styles.container}>
            <View style={[styles.contentPadAlt, { paddingBottom: 40 }]}>

                {/* Course Selection Chips */}
                {enrollments.length > 1 && (
                    <ScrollView horizontal showsHorizontalScrollIndicator={false} style={{ marginBottom: 15, marginTop: 10 }}>
                        {enrollments.map(course => (
                            <TouchableOpacity
                                key={course.id}
                                onPress={() => setSelectedCourseId(course.id)}
                                style={{
                                    paddingHorizontal: 16,
                                    paddingVertical: 8,
                                    backgroundColor: course.id === selectedCourseId ? COLORS.primary : '#f3f4f6',
                                    borderRadius: 20,
                                    marginRight: 10
                                }}
                            >
                                <Text style={{ color: course.id === selectedCourseId ? COLORS.white : COLORS.text, fontWeight: 'bold' }}>
                                    {course.title.length > 20 ? course.title.substring(0, 20) + '...' : course.title}
                                </Text>
                            </TouchableOpacity>
                        ))}
                    </ScrollView>
                )}

                {/* Nudge Banner */}
                {weakestSubject && weakestSubject.accuracy_percentage < 60 && (
                    <View style={[styles.infoBox, { backgroundColor: '#fff7ed', borderColor: '#fed7aa', flexDirection: 'row', alignItems: 'center' }]}>
                        <Ionicons name="bulb-outline" size={24} color={COLORS.primary} />
                        <Text style={[styles.infoText, { color: '#c2410c', marginLeft: 10, flex: 1, lineHeight: 20 }]}>
                            Focus Alert: Your accuracy in {weakestSubject.subject} is <Text style={{ fontWeight: 'bold' }}>{weakestSubject.accuracy_percentage}%</Text>. Review your study notes before re-attempting!
                        </Text>
                    </View>
                )}

                <Text style={[styles.sectionTitle, { marginTop: hasData ? 25 : 10 }]}>Subject Accuracy (%)</Text>

                {hasData ? (
                    <>
                        <View style={[styles.chartWrapper, { padding: 0, paddingRight: 15, paddingTop: 15 }]}>
                            <BarChart
                                style={{ marginVertical: 8, borderRadius: 16 }}
                                data={data}
                                width={screenWidth - 40}
                                height={240}
                                yAxisLabel=""
                                yAxisSuffix="%"
                                chartConfig={chartConfig}
                                verticalLabelRotation={0}
                                fromZero={true}
                                showValuesOnTopOfBars={true}
                            />
                        </View>

                        <Text style={[styles.sectionTitle, { marginTop: 25 }]}>Detailed Subject Breakdown</Text>
                        {analytics.subject_performances.map((subject: any, idx: number) => (
                            <View key={idx} style={[styles.card, { paddingVertical: 12, marginBottom: 10 }]}>
                                <View style={{ flex: 1 }}>
                                    <Text style={styles.cardTitle}>{subject.subject}</Text>
                                    <Text style={styles.metricText}>Questions Attempted: {subject.total_questions}</Text>
                                </View>
                                <Text style={[styles.scoreText, { fontSize: 16, color: subject.accuracy_percentage >= 60 ? COLORS.success : COLORS.error }]}>
                                    {subject.accuracy_percentage}%
                                </Text>
                            </View>
                        ))}
                    </>
                ) : (
                    <View style={{ alignItems: 'center', backgroundColor: '#ffffff', padding: 30, borderRadius: 16, borderWidth: 1, borderColor: '#e5e7eb', marginTop: 10 }}>
                        <Ionicons name="document-text-outline" size={48} color="#9ca3af" />
                        <Text style={{ color: '#6b7280', marginTop: 15, textAlign: 'center', lineHeight: 22 }}>
                            You haven't attempted any tests in this series yet. Take a test to unlock your performance analytics!
                        </Text>
                    </View>
                )}

            </View>
        </ScrollView>
    );
}
