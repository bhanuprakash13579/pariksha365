import React, { useState, useEffect } from 'react';
import { View, Text, ScrollView, TouchableOpacity, ActivityIndicator, Alert } from 'react-native';
import { Ionicons } from '@expo/vector-icons';
import { CourseAPI } from '../../services/api';
import { styles, COLORS } from '../../styles/theme';

export default function CourseDetailScreen({ navigation, route }: any) {
    const { courseId } = route.params;
    const [course, setCourse] = useState<any>(null);
    const [loading, setLoading] = useState(true);

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
                    <TouchableOpacity style={{ backgroundColor: COLORS.primary, paddingHorizontal: 20, paddingVertical: 10, borderRadius: 20 }}>
                        <Text style={{ color: 'white', fontWeight: 'bold' }}>Buy Pass</Text>
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
                                const isLocked = !folder.is_free && course.price > 0; // Simplified lock logic for UI UI mockup
                                // In reality, this requires checking the user's enrollment.

                                return (
                                    <TouchableOpacity
                                        key={folderTest.id}
                                        style={styles.card}
                                        onPress={() => isLocked ? Alert.alert("Locked", "Please purchase the course pass to unlock.") : Alert.alert("Test", "Opening test engine...")}
                                    >
                                        <View style={{ flexDirection: 'row', alignItems: 'center', flex: 1 }}>
                                            <View style={[styles.iconBox, isLocked && styles.iconBoxLocked]}>
                                                <Ionicons name={isLocked ? "lock-closed" : "play"} size={20} color={isLocked ? "#9ca3af" : "#f97316"} />
                                            </View>
                                            <View style={{ flex: 1, marginLeft: 15 }}>
                                                <Text style={[styles.cardTitle, isLocked && { color: '#9ca3af' }]}>Mock Test</Text>
                                                <View style={styles.metricsRow}>
                                                    <Text style={styles.metricText}>100 Qs • 60 Mins</Text>
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
