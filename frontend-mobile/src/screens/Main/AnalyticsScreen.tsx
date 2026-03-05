import React, { useState, useEffect } from 'react';
import { View, Text, ScrollView, Dimensions, ActivityIndicator, TouchableOpacity } from 'react-native';
import { BarChart } from 'react-native-chart-kit';
import { styles, COLORS } from '../../styles/theme';
import { Ionicons } from '@expo/vector-icons';
import { AnalyticsAPI } from '../../services/api';

const screenWidth = Dimensions.get("window").width;

export default function AnalyticsScreen({ navigation }: any) {
    const [hierarchy, setHierarchy] = useState<any[]>([]);
    const [selectedCategory, setSelectedCategory] = useState<string | null>(null);
    const [selectedCourse, setSelectedCourse] = useState<string | null>(null);
    const [selectedScope, setSelectedScope] = useState<string>('overall');

    const [analyticsData, setAnalyticsData] = useState<any>(null);
    const [loading, setLoading] = useState(true);
    const [expandedSubjects, setExpandedSubjects] = useState<Set<string>>(new Set());

    const toggleSubject = (subject: string) => {
        setExpandedSubjects(prev => {
            const next = new Set(prev);
            if (next.has(subject)) next.delete(subject); else next.add(subject);
            return next;
        });
    };

    // Initial Fetch for Hierarchy
    useEffect(() => {
        const fetchHierarchy = async () => {
            try {
                const res = await AnalyticsAPI.getHierarchy();
                if (res.data && res.data.length > 0) {
                    setHierarchy(res.data);
                    setSelectedCategory(res.data[0].category_name);
                    if (res.data[0].courses.length > 0) {
                        setSelectedCourse(res.data[0].courses[0].course_id);
                    }
                } else {
                    setLoading(false);
                }
            } catch (err) {
                console.error("Failed to fetch analytics hierarchy:", err);
                setLoading(false);
            }
        };
        fetchHierarchy();
    }, []);

    // Change Course -> Reset Scope
    useEffect(() => {
        setSelectedScope('overall');
    }, [selectedCourse]);

    // Fetch Analytics Data when Course or Scope changes
    useEffect(() => {
        if (!selectedCourse) return;

        const fetchAnalytics = async () => {
            setLoading(true);
            try {
                let res;
                if (selectedScope === 'overall') {
                    res = await AnalyticsAPI.getCourseOverallAnalytics(selectedCourse);
                } else {
                    res = await AnalyticsAPI.getSpecificTestAnalytics(selectedCourse, selectedScope);
                }
                setAnalyticsData(res.data);
            } catch (err) {
                console.error("Failed to fetch analytics data:", err);
                setAnalyticsData(null);
            } finally {
                setLoading(false);
            }
        };
        fetchAnalytics();
    }, [selectedCourse, selectedScope]);

    if (loading && hierarchy.length === 0) {
        return (
            <View style={[styles.container, { justifyContent: 'center', alignItems: 'center' }]}>
                <ActivityIndicator size="large" color={COLORS.primary} />
            </View>
        );
    }

    if (hierarchy.length === 0) {
        return (
            <View style={[styles.container, { justifyContent: 'center', alignItems: 'center', padding: 20 }]}>
                <Ionicons name="stats-chart" size={64} color={COLORS.border} />
                <Text style={{ textAlign: 'center', color: COLORS.textSub, marginTop: 20, fontSize: 16 }}>
                    You need to enroll in a course and attempt a test to see your performance analytics.
                </Text>
            </View>
        );
    }

    const currentCategoryObj = hierarchy.find(c => c.category_name === selectedCategory);
    const courses = currentCategoryObj ? currentCategoryObj.courses : [];

    const hasData = analyticsData?.subject_performances && analyticsData.subject_performances.length > 0;

    const chartData = hasData ? {
        labels: analyticsData.subject_performances.map((s: any) => s.subject.length > 5 ? s.subject.substring(0, 4) + '..' : s.subject),
        datasets: [{ data: analyticsData.subject_performances.map((s: any) => s.accuracy_percentage) }]
    } : { labels: ["No Data"], datasets: [{ data: [0] }] };

    const chartConfig = {
        backgroundGradientFrom: "#ffffff",
        backgroundGradientTo: "#ffffff",
        color: (opacity = 1) => `rgba(234, 88, 12, ${opacity})`, // orange-600
        labelColor: (opacity = 1) => `rgba(107, 114, 128, ${opacity})`,
        strokeWidth: 2,
        barPercentage: 0.5,
        fillShadowGradientFrom: COLORS.primary,
        fillShadowGradientFromOpacity: 0.8,
        fillShadowGradientTo: COLORS.primary,
        fillShadowGradientToOpacity: 0.8,
        useShadowColorFromDataset: false,
        decimalPlaces: 0
    };

    return (
        <ScrollView style={styles.container}>
            <View style={[styles.contentPadAlt, { paddingBottom: 40, paddingTop: 10 }]}>

                {/* TIER 1: Categories */}
                <ScrollView horizontal showsHorizontalScrollIndicator={false} style={{ marginBottom: 15 }}>
                    {hierarchy.map((cat, idx) => (
                        <TouchableOpacity
                            key={idx}
                            onPress={() => {
                                setSelectedCategory(cat.category_name);
                                if (cat.courses.length > 0) {
                                    setSelectedCourse(cat.courses[0].course_id);
                                }
                            }}
                            style={{
                                paddingHorizontal: 16,
                                paddingVertical: 8,
                                borderBottomWidth: selectedCategory === cat.category_name ? 2 : 0,
                                borderBottomColor: COLORS.primary,
                                marginRight: 10
                            }}
                        >
                            <Text style={{
                                color: selectedCategory === cat.category_name ? COLORS.primary : COLORS.textSub,
                                fontWeight: 'bold',
                                fontSize: 15
                            }}>
                                {cat.category_name}
                            </Text>
                        </TouchableOpacity>
                    ))}
                </ScrollView>

                {/* TIER 2: Courses */}
                {courses.length > 0 && (
                    <ScrollView horizontal showsHorizontalScrollIndicator={false} style={{ marginBottom: 15 }}>
                        {courses.map((course: any) => (
                            <TouchableOpacity
                                key={course.course_id}
                                onPress={() => setSelectedCourse(course.course_id)}
                                style={{
                                    paddingHorizontal: 16,
                                    paddingVertical: 8,
                                    backgroundColor: course.course_id === selectedCourse ? COLORS.primary : '#f3f4f6',
                                    borderRadius: 20,
                                    marginRight: 10
                                }}
                            >
                                <Text style={{ color: course.course_id === selectedCourse ? COLORS.white : COLORS.text, fontWeight: '600', fontSize: 14 }}>
                                    {course.title.length > 25 ? course.title.substring(0, 25) + '...' : course.title}
                                </Text>
                            </TouchableOpacity>
                        ))}
                    </ScrollView>
                )}

                {loading ? (
                    <View style={{ height: 300, justifyContent: 'center', alignItems: 'center' }}>
                        <ActivityIndicator size="large" color={COLORS.primary} />
                    </View>
                ) : analyticsData ? (
                    <>
                        {/* TIER 3: Scope Selector (Overall vs Test 1 vs Test 2) */}
                        <Text style={[styles.sectionTitle, { fontSize: 13, marginTop: 5, color: COLORS.textSub }]}>ANALYSIS SCOPE</Text>
                        <ScrollView horizontal showsHorizontalScrollIndicator={false} style={{ marginBottom: 20 }}>
                            <TouchableOpacity
                                onPress={() => setSelectedScope('overall')}
                                style={{
                                    paddingHorizontal: 14,
                                    paddingVertical: 6,
                                    backgroundColor: selectedScope === 'overall' ? '#111827' : '#e5e7eb',
                                    borderRadius: 12,
                                    marginRight: 8
                                }}
                            >
                                <Text style={{ color: selectedScope === 'overall' ? '#fff' : '#4b5563', fontWeight: 'bold', fontSize: 13 }}>
                                    Overall Course
                                </Text>
                            </TouchableOpacity>

                            {analyticsData.available_tests?.map((t: any) => (
                                <TouchableOpacity
                                    key={t.course_id}
                                    onPress={() => setSelectedScope(t.course_id)}
                                    style={{
                                        paddingHorizontal: 14,
                                        paddingVertical: 6,
                                        backgroundColor: selectedScope === t.course_id ? '#111827' : '#e5e7eb',
                                        borderRadius: 12,
                                        marginRight: 8
                                    }}
                                >
                                    <Text style={{ color: selectedScope === t.course_id ? '#fff' : '#4b5563', fontWeight: 'bold', fontSize: 13 }}>
                                        {t.title.length > 15 ? t.title.substring(0, 15) + '..' : t.title}
                                    </Text>
                                </TouchableOpacity>
                            ))}
                            {/* If specific test is selected and we don't have available_tests array, show the fallback */}
                            {selectedScope !== 'overall' && !analyticsData.available_tests && (
                                <TouchableOpacity
                                    style={{
                                        paddingHorizontal: 14,
                                        paddingVertical: 6,
                                        backgroundColor: '#111827',
                                        borderRadius: 12,
                                        marginRight: 8
                                    }}
                                >
                                    <Text style={{ color: '#fff', fontWeight: 'bold', fontSize: 13 }}>
                                        {analyticsData.test_title ? (analyticsData.test_title.length > 15 ? analyticsData.test_title.substring(0, 15) + '..' : analyticsData.test_title) : 'Current Test'}
                                    </Text>
                                </TouchableOpacity>
                            )}
                        </ScrollView>

                        {/* Intelligent Insights */}
                        {analyticsData.insights?.map((insight: string, idx: number) => {
                            const isAlert = insight.includes('Focus Alert');
                            return (
                                <View key={idx} style={{
                                    backgroundColor: isAlert ? '#fff7ed' : '#f0fdf4',
                                    borderColor: isAlert ? '#fed7aa' : '#bbf7d0',
                                    borderWidth: 1,
                                    borderRadius: 12,
                                    padding: 15,
                                    flexDirection: 'row',
                                    alignItems: 'flex-start',
                                    marginBottom: 15
                                }}>
                                    <View style={{
                                        backgroundColor: isAlert ? '#ffedd5' : '#dcfce3',
                                        padding: 6,
                                        borderRadius: 20,
                                        marginRight: 10
                                    }}>
                                        <Ionicons name={isAlert ? "warning" : "checkmark-circle"} size={20} color={isAlert ? '#ea580c' : '#16a34a'} />
                                    </View>
                                    <Text style={{ flex: 1, color: isAlert ? '#9a3412' : '#166534', fontSize: 14, lineHeight: 20 }}>
                                        {insight}
                                    </Text>
                                </View>
                            );
                        })}

                        {hasData ? (
                            <>
                                {/* Bar Chart */}
                                <Text style={[styles.sectionTitle, { marginTop: 10 }]}>Subject Accuracy (%)</Text>
                                <View style={[styles.chartWrapper, { padding: 0, paddingRight: 15, paddingTop: 15, marginBottom: 20 }]}>
                                    <BarChart
                                        style={{ marginVertical: 8, borderRadius: 16 }}
                                        data={chartData}
                                        width={screenWidth - 40}
                                        height={220}
                                        yAxisLabel=""
                                        yAxisSuffix="%"
                                        chartConfig={chartConfig}
                                        verticalLabelRotation={0}
                                        fromZero={true}
                                        showValuesOnTopOfBars={true}
                                    />
                                </View>

                                {/* Hero Metrics Grid */}
                                <View style={{ flexDirection: 'row', justifyContent: 'space-between', marginBottom: 20 }}>
                                    {selectedScope === 'overall' ? (
                                        <>
                                            <View style={{ flex: 1, backgroundColor: '#4f46e5', padding: 20, borderRadius: 16, marginRight: 10 }}>
                                                <Text style={{ color: '#c7d2fe', fontSize: 12, fontWeight: 'bold', marginBottom: 5 }}>PERCENTILE</Text>
                                                <Text style={{ color: 'white', fontSize: 32, fontWeight: '900' }}>{analyticsData.course_percentile}</Text>
                                            </View>
                                            <View style={{ flex: 1, backgroundColor: '#f3f4f6', padding: 20, borderRadius: 16, borderWidth: 1, borderColor: '#e5e7eb' }}>
                                                <Text style={{ color: '#6b7280', fontSize: 12, fontWeight: 'bold', marginBottom: 5 }}>ACCURACY</Text>
                                                <Text style={{ color: '#111827', fontSize: 32, fontWeight: '900' }}>{analyticsData.overall_accuracy}%</Text>
                                            </View>
                                        </>
                                    ) : (
                                        <>
                                            <View style={{ flex: 1, backgroundColor: COLORS.primary, padding: 20, borderRadius: 16, marginRight: 10 }}>
                                                <Text style={{ color: '#ffedd5', fontSize: 12, fontWeight: 'bold', marginBottom: 5 }}>TEST RANK</Text>
                                                <Text style={{ color: 'white', fontSize: 32, fontWeight: '900' }}>#{analyticsData.rank}</Text>
                                            </View>
                                            <View style={{ flex: 1, backgroundColor: '#f3f4f6', padding: 20, borderRadius: 16, borderWidth: 1, borderColor: '#e5e7eb' }}>
                                                <Text style={{ color: '#6b7280', fontSize: 12, fontWeight: 'bold', marginBottom: 5 }}>PERCENTILE</Text>
                                                <Text style={{ color: '#111827', fontSize: 32, fontWeight: '900' }}>{analyticsData.percentile}</Text>
                                            </View>
                                        </>
                                    )}
                                </View>

                                {/* Detailed Subject + Topic Breakdown */}
                                <Text style={[styles.sectionTitle, { marginTop: 10 }]}>Subject & Topic Breakdown</Text>
                                {analyticsData.subject_performances.map((subject: any, idx: number) => {
                                    const isExpanded = expandedSubjects.has(subject.subject);
                                    const hasTopics = subject.topics && subject.topics.length > 0;
                                    return (
                                        <View key={idx} style={{ marginBottom: 10 }}>
                                            <TouchableOpacity
                                                onPress={() => hasTopics && toggleSubject(subject.subject)}
                                                style={[styles.card, { paddingVertical: 14, flexDirection: 'row', alignItems: 'center', marginBottom: 0 }]}
                                            >
                                                {hasTopics && (
                                                    <Ionicons name={isExpanded ? 'chevron-down' : 'chevron-forward'} size={18} color="#9ca3af" style={{ marginRight: 8 }} />
                                                )}
                                                <View style={{ flex: 1 }}>
                                                    <Text style={[styles.cardTitle, { fontSize: 15 }]}>{subject.subject}</Text>
                                                    <View style={{ flexDirection: 'row', marginTop: 4 }}>
                                                        <Text style={{ fontSize: 12, color: '#10b981', marginRight: 10 }}>{subject.correct} Correct</Text>
                                                        <Text style={{ fontSize: 12, color: '#ef4444', marginRight: 10 }}>{subject.incorrect} Wrong</Text>
                                                        <Text style={{ fontSize: 12, color: '#6b7280' }}>{subject.skipped} Skipped</Text>
                                                    </View>
                                                </View>
                                                <View style={{ backgroundColor: subject.accuracy_percentage >= 60 ? '#d1fae5' : '#fee2e2', paddingHorizontal: 12, paddingVertical: 6, borderRadius: 20 }}>
                                                    <Text style={{ fontSize: 14, fontWeight: 'bold', color: subject.accuracy_percentage >= 60 ? '#065f46' : '#991b1b' }}>
                                                        {Math.round(subject.accuracy_percentage)}%
                                                    </Text>
                                                </View>
                                            </TouchableOpacity>

                                            {/* Topic drilldown */}
                                            {isExpanded && hasTopics && (
                                                <View style={{ backgroundColor: '#f9fafb', borderBottomLeftRadius: 12, borderBottomRightRadius: 12, paddingHorizontal: 16, paddingVertical: 10, marginTop: -5, borderWidth: 1, borderColor: '#f3f4f6', borderTopWidth: 0 }}>
                                                    {subject.topics.map((tp: any, tidx: number) => (
                                                        <View key={tidx} style={{ flexDirection: 'row', alignItems: 'center', justifyContent: 'space-between', paddingVertical: 8 }}>
                                                            <View style={{ flexDirection: 'row', alignItems: 'center', flex: 1 }}>
                                                                <View style={{ width: 6, height: 6, borderRadius: 3, backgroundColor: tp.accuracy_percentage >= 70 ? '#10b981' : tp.accuracy_percentage >= 40 ? '#f97316' : '#ef4444', marginRight: 8 }} />
                                                                <Text style={{ fontSize: 13, color: '#374151' }}>{tp.topic}</Text>
                                                                <Text style={{ fontSize: 11, color: '#9ca3af', marginLeft: 6 }}>({tp.correct}/{tp.total_questions})</Text>
                                                            </View>
                                                            <View style={{ flexDirection: 'row', alignItems: 'center' }}>
                                                                <Text style={{ fontSize: 12, fontWeight: 'bold', color: tp.accuracy_percentage >= 70 ? '#059669' : tp.accuracy_percentage >= 40 ? '#ea580c' : '#dc2626' }}>
                                                                    {Math.round(tp.accuracy_percentage)}%
                                                                </Text>
                                                                {tp.accuracy_percentage < 60 && (
                                                                    <View style={{ backgroundColor: '#fee2e2', paddingHorizontal: 6, paddingVertical: 2, borderRadius: 4, marginLeft: 6 }}>
                                                                        <Text style={{ fontSize: 10, fontWeight: 'bold', color: '#dc2626' }}>Weak</Text>
                                                                    </View>
                                                                )}
                                                            </View>
                                                        </View>
                                                    ))}
                                                </View>
                                            )}
                                        </View>
                                    );
                                })}
                            </>
                        ) : (
                            <View style={{ alignItems: 'center', backgroundColor: '#ffffff', padding: 30, borderRadius: 16, borderWidth: 1, borderColor: '#e5e7eb', marginTop: 10 }}>
                                <Ionicons name="document-text-outline" size={48} color="#9ca3af" />
                                <Text style={{ color: '#6b7280', marginTop: 15, textAlign: 'center', lineHeight: 22 }}>
                                    You haven't attempted any tests in this scope yet. Check back later!
                                </Text>
                            </View>
                        )}
                    </>
                ) : null}

            </View>
        </ScrollView>
    );
}
