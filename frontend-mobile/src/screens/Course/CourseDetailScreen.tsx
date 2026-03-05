import React, { useState, useEffect } from 'react';
import { View, Text, ScrollView, TouchableOpacity, ActivityIndicator, Alert } from 'react-native';
import { Ionicons } from '@expo/vector-icons';
import { CourseAPI } from '../../services/api';
import { styles, COLORS } from '../../styles/theme';

export default function CourseDetailScreen({ navigation, route }: any) {
    const { courseId } = route.params;
    const [course, setCourse] = useState<any>(null);
    const [loading, setLoading] = useState(true);
    const [enrolling, setEnrolling] = useState(false);
    const [enrolled, setEnrolled] = useState(false);

    useEffect(() => {
        const fetchCourse = async () => {
            try {
                const res = await CourseAPI.getById(courseId);
                setCourse(res.data);
            } catch (err) {
                console.error(err);
                Alert.alert('Error', 'Failed to load course details');
                navigation.goBack();
            } finally {
                setLoading(false);
            }
        };
        fetchCourse();
    }, [courseId]);

    const handleEnroll = async () => {
        if (!course) return;
        if (course.price > 0) {
            Alert.alert('Payment', 'Premium course payment is coming soon. Stay tuned!');
            return;
        }
        setEnrolling(true);
        try {
            await CourseAPI.enroll(courseId);
            setEnrolled(true);
            Alert.alert('Success', 'You have been enrolled in this course!');
        } catch (err: any) {
            if (err.response?.status === 409 || err.response?.data?.detail?.includes('already')) {
                setEnrolled(true);
            } else {
                Alert.alert('Error', 'Failed to enroll. Please try again.');
            }
        } finally { setEnrolling(false); }
    };

    if (loading) {
        return (
            <View style={[styles.container, { justifyContent: 'center', alignItems: 'center' }]}>
                <ActivityIndicator size="large" color={COLORS.primary} />
            </View>
        );
    }

    if (!course) return null;

    return (
        <View style={styles.container}>
            <View style={styles.courseHeader}>
                <Text style={styles.courseTitle}>{course.title}</Text>
                <Text style={styles.courseDesc}>{course.description}</Text>
                <View style={{ flexDirection: 'row', justifyContent: 'space-between', marginTop: 15, alignItems: 'center' }}>
                    <Text style={styles.price}>{course.price > 0 ? `₹${course.price}` : 'FREE'}</Text>
                    <TouchableOpacity
                        onPress={handleEnroll}
                        disabled={enrolling || enrolled}
                        style={{
                            backgroundColor: enrolled ? '#22c55e' : COLORS.primary,
                            paddingHorizontal: 20, paddingVertical: 10, borderRadius: 20,
                            opacity: enrolling ? 0.7 : 1,
                        }}
                    >
                        {enrolling ? <ActivityIndicator color="#fff" size="small" /> :
                            <Text style={{ color: 'white', fontWeight: 'bold' }}>
                                {enrolled ? '✓ Enrolled' : course.price > 0 ? 'Buy Pass' : 'Enroll Free'}
                            </Text>}
                    </TouchableOpacity>
                </View>
            </View>

            <ScrollView contentContainerStyle={styles.contentPadAlt}>
                {course.folders?.length === 0 ? (
                    <Text style={{ textAlign: 'center', color: COLORS.textSub, marginTop: 20 }}>No mock tests added yet.</Text>
                ) : (
                    course.folders?.map((folder: any) => (
                        <View key={folder.id} style={{ marginBottom: 20 }}>
                            <View style={{ flexDirection: 'row', alignItems: 'center', marginBottom: 10 }}>
                                <Text style={styles.sectionTitle}>{folder.title}</Text>
                                {folder.is_free && <View style={[styles.freeTag, { marginLeft: 10 }]}><Text style={styles.freeTagText}>FREE</Text></View>}
                            </View>

                            {folder.tests?.length === 0 ? <Text style={styles.metricText}>Empty folder.</Text> : null}

                            {folder.tests?.map((folderTest: any) => {
                                const isLocked = !folder.is_free && course.price > 0; // Simplified lock logic for UI mockup
                                const testData = folderTest.test_series || {};

                                return (
                                    <TouchableOpacity
                                        key={folderTest.id}
                                        style={styles.card}
                                        onPress={() => isLocked ? Alert.alert("Locked", "Please purchase the course pass to unlock.") : navigation.navigate('TestDetail', { test: testData, isGuest: false })}
                                    >
                                        <View style={{ flexDirection: 'row', alignItems: 'center', flex: 1 }}>
                                            <View style={[styles.iconBox, isLocked && styles.iconBoxLocked]}>
                                                <Ionicons name={isLocked ? "lock-closed" : "play"} size={20} color={isLocked ? "#9ca3af" : "#f97316"} />
                                            </View>
                                            <View style={{ flex: 1, marginLeft: 15 }}>
                                                <Text style={[styles.cardTitle, isLocked && { color: '#9ca3af' }]}>{testData.title || 'Mock Test'}</Text>
                                                <View style={styles.metricsRow}>
                                                    <Text style={styles.metricText}>100 Qs • {Math.round((testData.duration_minutes || 60))} Mins</Text>
                                                </View>
                                            </View>
                                        </View>
                                    </TouchableOpacity>
                                );
                            })}
                        </View>
                    ))
                )}
            </ScrollView>
        </View>
    );
}
