import React, { useState, useEffect } from 'react';
import { View, Text, ScrollView, TouchableOpacity, ActivityIndicator } from 'react-native';
import { Ionicons } from '@expo/vector-icons';
import { styles, COLORS } from '../../styles/theme';
import { UserAPI } from '../../services/api';

export default function MyLearningScreen({ navigation }: any) {
    const [enrolledCourses, setEnrolledCourses] = useState<any[]>([]);
    const [loading, setLoading] = useState(true);

    useEffect(() => {
        const fetchEnrollments = async () => {
            try {
                const res = await UserAPI.getEnrollments();
                setEnrolledCourses(res.data);
            } catch (err) {
                console.error("Failed to fetch enrollments:", err);
            } finally {
                setLoading(false);
            }
        };
        fetchEnrollments();
    }, []);

    if (loading) {
        return (
            <View style={[styles.container, { justifyContent: 'center', alignItems: 'center' }]}>
                <ActivityIndicator size="large" color={COLORS.primary} />
            </View>
        );
    }

    return (
        <ScrollView style={styles.container}>
            <View style={styles.contentPadAlt}>
                <Text style={[styles.sectionTitle, { marginTop: 15 }]}>Active Enrollments</Text>
                {enrolledCourses.map((course: any) => (
                    <TouchableOpacity key={course.id} style={styles.card} onPress={() => navigation.navigate('CourseDetail', { courseId: course.id })}>
                        <View style={{ flex: 1, marginRight: 15 }}>
                            <Text style={styles.cardTitle}>{course.title}</Text>
                            <View style={styles.progressBarBg}>
                                <View style={[styles.progressBarFill, { width: '0%' as any }]} />
                            </View>
                            <Text style={styles.metricText}>Expires in: {course.validity_days} days</Text>
                        </View>
                        <Ionicons name="chevron-forward" size={24} color={COLORS.primary} />
                    </TouchableOpacity>
                ))}

                {enrolledCourses.length === 0 && (
                    <Text style={{ textAlign: 'center', color: COLORS.textSub, marginTop: 20 }}>You have not enrolled in any courses yet.</Text>
                )}
            </View>
        </ScrollView>
    );
}
