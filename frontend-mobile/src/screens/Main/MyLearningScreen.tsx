import React from 'react';
import { View, Text, ScrollView, TouchableOpacity } from 'react-native';
import { Ionicons } from '@expo/vector-icons';
import { styles, COLORS } from '../../styles/theme';

export default function MyLearningScreen({ navigation }: any) {
    // Dummy enrolled data for now
    const ENROLLED_COURSES = [
        { id: '1', title: 'SSC CGL Full Strategy Pack', progress: '40%' },
        { id: '2', title: 'RRB NTPC Previous Years', progress: '12%' }
    ];

    return (
        <ScrollView style={styles.container}>
            <View style={styles.contentPadAlt}>
                <Text style={[styles.sectionTitle, { marginTop: 15 }]}>Active Enrollments</Text>
                {ENROLLED_COURSES.map(course => (
                    <TouchableOpacity key={course.id} style={styles.card} onPress={() => navigation.navigate('CourseDetail', { courseId: course.id })}>
                        <View style={{ flex: 1, marginRight: 15 }}>
                            <Text style={styles.cardTitle}>{course.title}</Text>
                            <View style={styles.progressBarBg}>
                                <View style={[styles.progressBarFill, { width: course.progress as any }]} />
                            </View>
                            <Text style={styles.metricText}>Progress: {course.progress}</Text>
                        </View>
                        <Ionicons name="chevron-forward" size={24} color={COLORS.primary} />
                    </TouchableOpacity>
                ))}

                {ENROLLED_COURSES.length === 0 && (
                    <Text style={{ textAlign: 'center', color: COLORS.textSub, marginTop: 20 }}>You have not enrolled in any courses yet.</Text>
                )}
            </View>
        </ScrollView>
    );
}
