import React, { useState, useEffect } from 'react';
import { View, Text, ScrollView, TouchableOpacity, ActivityIndicator } from 'react-native';
import { Ionicons } from '@expo/vector-icons';
import { CourseAPI } from '../../services/api';
import { styles, COLORS } from '../../styles/theme';

const SUB_CATEGORIES: any = {
    'SSC Exams': ['SSC CGL', 'SSC CHSL', 'SSC MTS', 'SSC GD'],
    'UPSC Civil Services': ['UPSC CSE', 'UPSC EPFO (APFC)', 'UPSC CDS'],
    'State Govt. Exams': ['UPPSC', 'BPSC', 'MPSC', 'APPSC', 'TSPSC'],
    'Railways': ['RRB NTPC', 'RRB Group D', 'RRB ALP'],
    'Defence Exams': ['NDA', 'AFCAT', 'Airforce X & Y'],
    'Teaching Exams': ['CTET', 'UPTET', 'KVS', 'Super TET']
};

export default function CategoryScreen({ navigation, route }: any) {
    const { categoryTitle } = route.params;
    const [courses, setCourses] = useState<any[]>([]);
    const [loading, setLoading] = useState(true);
    const [activeSub, setActiveSub] = useState<string | null>(null);

    const subCats = SUB_CATEGORIES[categoryTitle] || ['All Exams'];

    useEffect(() => {
        // In a real app, pass category/sub-category to the API. 
        // Here we fetch all and render as a showcase.
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
    }, [categoryTitle]);

    return (
        <View style={styles.container}>
            {/* Custom Header mimicking Testbook Sub-category */}
            <View style={[styles.tbHeaderContainer, { paddingTop: 55, paddingBottom: 15 }]}>
                <TouchableOpacity style={styles.tbHeaderLeftBtn} onPress={() => navigation.goBack()}>
                    <Ionicons name="arrow-back" size={24} color={COLORS.white} />
                </TouchableOpacity>
                <Text style={{ flex: 1, color: COLORS.white, fontSize: 18, fontWeight: 'bold', marginLeft: 15 }}>{categoryTitle}</Text>
                <TouchableOpacity style={styles.tbHeaderRightBtn}>
                    <Ionicons name="search" size={22} color={COLORS.white} />
                </TouchableOpacity>
            </View>

            {/* Sub Category Horizontal Chips */}
            <View style={{ backgroundColor: COLORS.headerBg, paddingBottom: 15 }}>
                <ScrollView horizontal showsHorizontalScrollIndicator={false} contentContainerStyle={{ paddingHorizontal: 15 }}>
                    {subCats.map((sub: string) => (
                        <TouchableOpacity
                            key={sub}
                            onPress={() => setActiveSub(sub === activeSub ? null : sub)}
                            style={{
                                paddingHorizontal: 16, paddingVertical: 8,
                                backgroundColor: activeSub === sub ? COLORS.primary : COLORS.searchBg,
                                borderRadius: 20, marginRight: 10,
                                borderWidth: 1, borderColor: activeSub === sub ? COLORS.primary : '#3f3f46'
                            }}>
                            <Text style={{ color: activeSub === sub ? COLORS.white : COLORS.iconColor, fontWeight: '600' }}>{sub}</Text>
                        </TouchableOpacity>
                    ))}
                </ScrollView>
            </View>

            <ScrollView contentContainerStyle={styles.contentPadAlt}>
                <Text style={[styles.sectionTitle, { marginTop: 10 }]}>Recommended SuperCoaching</Text>
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
                    <Text style={{ textAlign: 'center', color: COLORS.textSub, marginTop: 20 }}>No courses available in this category.</Text>
                )}
            </ScrollView>
        </View>
    );
}
