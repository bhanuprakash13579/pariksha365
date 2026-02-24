import React, { useState, useEffect } from 'react';
import { View, Text, ScrollView, TouchableOpacity, ActivityIndicator } from 'react-native';
import { Ionicons } from '@expo/vector-icons';
import { CourseAPI } from '../../services/api';
import { styles, COLORS } from '../../styles/theme';
import GlobalHeader from '../../components/GlobalHeader';
import ProfileDrawer from '../../components/ProfileDrawer';

const EXAM_CATEGORIES = [
    { id: '1', title: 'UPSC Civil Services', icon: 'ribbon-outline' },
    { id: '2', title: 'State Govt. Exams', icon: 'business-outline' },
    { id: '3', title: 'SSC Exams', icon: 'hammer-outline' },
    { id: '4', title: 'Railways', icon: 'train-outline' },
    { id: '5', title: 'Defence Exams', icon: 'shield-checkmark-outline' },
    { id: '6', title: 'Teaching Exams', icon: 'book-outline' },
];

export default function HomeScreen({ navigation, route }: any) {
    const isGuest = route.params?.isGuest || false;
    const [courses, setCourses] = useState<any[]>([]);
    const [loading, setLoading] = useState(true);
    const [drawerVisible, setDrawerVisible] = useState(false);

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
            <GlobalHeader onOpenDrawer={() => setDrawerVisible(true)} />

            <ScrollView contentContainerStyle={styles.contentPadAlt}>
                <Text style={[styles.sectionTitle, { fontSize: 16, color: COLORS.textSub, marginTop: 10 }]}>| Explore All Categories</Text>

                <View style={styles.gridContainer}>
                    {EXAM_CATEGORIES.map(cat => (
                        <TouchableOpacity
                            key={cat.id}
                            style={styles.categoryGridCard}
                            onPress={() => navigation.navigate('Category', { categoryTitle: cat.title })}
                        >
                            <Text style={styles.categoryGridTitle}>{cat.title}</Text>
                            <View style={styles.categoryIconWrap}>
                                <Ionicons name={cat.icon as any} size={18} color={COLORS.textSub} />
                            </View>
                        </TouchableOpacity>
                    ))}
                </View>

                <Text style={[styles.sectionTitle, { marginTop: 20 }]}>Popular Courses & Test Series</Text>
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

            <ProfileDrawer visible={drawerVisible} onClose={() => setDrawerVisible(false)} isGuest={isGuest} />
        </View>
    );
}
