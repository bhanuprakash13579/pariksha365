import React, { useState, useEffect } from 'react';
import { View, Text, ScrollView, TouchableOpacity, ActivityIndicator } from 'react-native';
import { Ionicons } from '@expo/vector-icons';
import { CourseAPI } from '../../services/api';
import { styles, COLORS } from '../../styles/theme';

export default function HomeScreen({ navigation, route }: any) {
    const isGuest = route.params?.isGuest || false;
    const [courses, setCourses] = useState<any[]>([]);
    const [loading, setLoading] = useState(true);

    useEffect(() => {
        const fetchCourses = async () => {
            try {
                const res = await CourseAPI.list();
                setCourses(res.data);
            } catch (err) {
                console.error(err);
            } finally {
                setLoading(false);
            }
        };
        fetchCourses();
    }, []);

    return (
        <View style={styles.container}>
            <View style={styles.header}>
                <Text style={styles.greeting}>Hi Aspirant!</Text>
                <Text style={styles.subGreeting}>Ready to crack your exam?</Text>
            </View>
            <ScrollView contentContainerStyle={styles.contentPadAlt}>
                <Text style={styles.sectionTitle}>Available Courses & Test Series</Text>
                {loading ? <ActivityIndicator size="large" color={COLORS.primary} style={{ marginTop: 20 }} /> : null}

                {courses.map(course => (
                    <TouchableOpacity key={course.id} style={styles.card} onPress={() => navigation.navigate('CourseDetail', { courseId: course.id })}>
                        <View style={{ flex: 1, marginRight: 15 }}>
                            <Text style={styles.cardTitle}>{course.title}</Text>
                            <Text style={styles.tag}>{course.category || 'General'} • {course.validity_days} Days Validity</Text>
                            <Text style={{ marginTop: 8, color: COLORS.textSub, fontSize: 13 }} numberOfLines={2}>{course.description}</Text>
                        </View>
                        <View style={{ alignItems: 'flex-end' }}>
                            <Text style={styles.price}>{course.price > 0 ? `₹${course.price}` : 'FREE'}</Text>
                            <Ionicons name="chevron-forward" size={20} color={COLORS.textSub} style={{ marginTop: 10 }} />
                        </View>
                    </TouchableOpacity>
                ))}
                {courses.length === 0 && !loading && (
                    <Text style={{ textAlign: 'center', color: COLORS.textSub, marginTop: 20 }}>No courses available yet.</Text>
                )}
            </ScrollView>
        </View>
    );
}
