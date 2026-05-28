import React, { useState, useEffect } from 'react';
import { View, Text, ScrollView, TouchableOpacity, ActivityIndicator } from 'react-native';
import { Ionicons } from '@expo/vector-icons';
import { ExamStructureAPI } from '../../services/api';
import { styles, COLORS } from '../../styles/theme';

type TestTab = 'MOCK' | 'PYQ';

export default function CategoryScreen({ navigation, route }: any) {
    const { categoryTitle, subcategories } = route.params;
    const [tests, setTests] = useState<any[]>([]);
    const [loading, setLoading] = useState(true);
    const [testTab, setTestTab] = useState<TestTab>('PYQ');

    const [activeSubId, setActiveSubId] = useState<string | null>(
        subcategories && subcategories.length > 0 ? subcategories[0].id : null
    );

    useEffect(() => {
        if (!activeSubId) {
            setLoading(false);
            setTests([]);
            return;
        }
        const fetchTests = async () => {
            setLoading(true);
            try {
                const res = await ExamStructureAPI.listPublishedTests({ subcategory_id: activeSubId });
                setTests(res.data || []);
            } catch (err) {
                console.error(err);
                setTests([]);
            } finally {
                setLoading(false);
            }
        };
        fetchTests();
    }, [activeSubId]);

    const filtered = tests.filter((t: any) => t.test_type === testTab);
    const mockCount = tests.filter((t: any) => t.test_type === 'MOCK').length;
    const pyqCount = tests.filter((t: any) => t.test_type === 'PYQ').length;

    return (
        <View style={styles.container}>
            {/* Header */}
            <View style={[styles.tbHeaderContainer, { paddingTop: 55, paddingBottom: 15 }]}>
                <TouchableOpacity style={styles.tbHeaderLeftBtn} onPress={() => navigation.goBack()}>
                    <Ionicons name="arrow-back" size={24} color={COLORS.white} />
                </TouchableOpacity>
                <Text style={{ flex: 1, color: COLORS.white, fontSize: 18, fontWeight: 'bold', marginLeft: 15 }}>{categoryTitle}</Text>
            </View>

            {/* Subcategory chips */}
            <View style={{ backgroundColor: COLORS.headerBg, paddingBottom: 12 }}>
                <ScrollView horizontal showsHorizontalScrollIndicator={false} contentContainerStyle={{ paddingHorizontal: 15 }}>
                    {(subcategories || []).map((sub: any) => (
                        <TouchableOpacity
                            key={sub.id}
                            onPress={() => setActiveSubId(sub.id)}
                            style={{
                                paddingHorizontal: 16, paddingVertical: 8,
                                backgroundColor: activeSubId === sub.id ? COLORS.primary : COLORS.searchBg,
                                borderRadius: 20, marginRight: 10,
                                borderWidth: 1, borderColor: activeSubId === sub.id ? COLORS.primary : '#3f3f46',
                            }}>
                            <Text style={{ color: activeSubId === sub.id ? COLORS.white : COLORS.iconColor, fontWeight: '600' }}>{sub.name}</Text>
                        </TouchableOpacity>
                    ))}
                </ScrollView>
            </View>

            {/* Mock / PYQ tab toggle */}
            <View style={{ flexDirection: 'row', backgroundColor: '#f3f4f6', margin: 15, borderRadius: 12, padding: 4 }}>
                {(['PYQ', 'MOCK'] as TestTab[]).map(tab => (
                    <TouchableOpacity
                        key={tab}
                        onPress={() => setTestTab(tab)}
                        style={{
                            flex: 1, paddingVertical: 8, borderRadius: 10, alignItems: 'center',
                            backgroundColor: testTab === tab ? COLORS.white : 'transparent',
                            shadowColor: testTab === tab ? '#000' : 'transparent',
                            shadowOpacity: testTab === tab ? 0.08 : 0,
                            shadowRadius: 4, elevation: testTab === tab ? 2 : 0,
                        }}>
                        <Text style={{ fontWeight: '700', color: testTab === tab ? COLORS.primary : COLORS.textSub, fontSize: 13 }}>
                            {tab === 'PYQ' ? `📚 Previous Year (${pyqCount})` : `📝 Mock Tests (${mockCount})`}
                        </Text>
                    </TouchableOpacity>
                ))}
            </View>

            <ScrollView contentContainerStyle={styles.contentPadAlt}>
                {loading
                    ? <ActivityIndicator size="large" color={COLORS.primary} style={{ marginTop: 30 }} />
                    : filtered.length === 0
                        ? (
                            <View style={{ alignItems: 'center', marginTop: 40 }}>
                                <Text style={{ fontSize: 40, marginBottom: 12 }}>{testTab === 'PYQ' ? '📚' : '📝'}</Text>
                                <Text style={{ color: COLORS.textSub, fontSize: 15, textAlign: 'center' }}>
                                    No {testTab === 'PYQ' ? 'Previous Year Papers' : 'Mock Tests'} published yet for this exam.
                                </Text>
                            </View>
                        )
                        : filtered.map((t: any) => (
                            <TouchableOpacity
                                key={t.id}
                                style={[styles.card, { marginBottom: 12 }]}
                                onPress={() => navigation.navigate('MockTest', { testSeriesId: t.id, testTitle: t.title })}
                            >
                                <View style={{ flex: 1 }}>
                                    <View style={{ flexDirection: 'row', alignItems: 'center', marginBottom: 4 }}>
                                        <Text style={{ fontSize: 11, fontWeight: '700', color: testTab === 'PYQ' ? '#3b82f6' : COLORS.primary, backgroundColor: testTab === 'PYQ' ? '#eff6ff' : '#fff7ed', paddingHorizontal: 8, paddingVertical: 2, borderRadius: 6, overflow: 'hidden' }}>
                                            {t.stage_name}
                                        </Text>
                                        {t.paper_date && (
                                            <Text style={{ fontSize: 11, color: COLORS.textSub, marginLeft: 8 }}>{t.paper_date}</Text>
                                        )}
                                    </View>
                                    <Text style={[styles.cardTitle, { marginBottom: 4 }]}>{t.title}</Text>
                                    <View style={{ flexDirection: 'row', gap: 12 }}>
                                        {t.total_duration_minutes != null && (
                                            <Text style={styles.metricText}>⏱ {t.total_duration_minutes} min</Text>
                                        )}
                                        {t.paper_shift && (
                                            <Text style={styles.metricText}>• {t.paper_shift}</Text>
                                        )}
                                    </View>
                                </View>
                                <Ionicons name="chevron-forward" size={20} color={COLORS.textSub} />
                            </TouchableOpacity>
                        ))
                }
            </ScrollView>
        </View>
    );
}
