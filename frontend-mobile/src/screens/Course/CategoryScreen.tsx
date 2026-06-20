import React, { useState, useEffect } from 'react';
import { View, Text, ScrollView, TouchableOpacity, ActivityIndicator } from 'react-native';
import { Ionicons } from '@expo/vector-icons';
import { ExamStructureAPI } from '../../services/api';
import { styles, COLORS } from '../../styles/theme';

type TestTab = 'MOCK' | 'PYQ';

export default function CategoryScreen({ navigation, route }: any) {
    const { categoryTitle, subcategories, initialTab } = route.params;
    const [tests, setTests] = useState<any[]>([]);
    const [loading, setLoading] = useState(true);
    const [testTab, setTestTab] = useState<TestTab>(initialTab || 'PYQ');

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
            {/* Compact header: back ➜ title + subtitle on one row */}
            <View style={{ backgroundColor: COLORS.headerBg, paddingTop: 50, paddingBottom: 12, paddingHorizontal: 12 }}>
                <View style={{ flexDirection: 'row', alignItems: 'center' }}>
                    <TouchableOpacity
                        onPress={() => navigation.goBack()}
                        style={{ width: 36, height: 36, borderRadius: 18, alignItems: 'center', justifyContent: 'center', backgroundColor: 'rgba(255,255,255,0.08)' }}
                    >
                        <Ionicons name="arrow-back" size={20} color={COLORS.white} />
                    </TouchableOpacity>
                    <View style={{ flex: 1, marginLeft: 12 }}>
                        <Text style={{ color: COLORS.white, fontSize: 18, fontWeight: '800' }} numberOfLines={1}>{categoryTitle}</Text>
                        <Text style={{ color: 'rgba(255,255,255,0.65)', fontSize: 11, marginTop: 2 }}>
                            {pyqCount + mockCount} tests · {pyqCount} PYQ · {mockCount} Mock
                        </Text>
                    </View>
                </View>

                {/* Subcategory chips — tighter and inside the header band so they're visually grouped with the title */}
                <ScrollView
                    horizontal
                    showsHorizontalScrollIndicator={false}
                    style={{ marginTop: 14 }}
                    contentContainerStyle={{ paddingRight: 12 }}
                >
                    {(subcategories || []).map((sub: any) => {
                        const active = activeSubId === sub.id;
                        return (
                            <TouchableOpacity
                                key={sub.id}
                                onPress={() => setActiveSubId(sub.id)}
                                style={{
                                    paddingHorizontal: 14, paddingVertical: 7,
                                    backgroundColor: active ? COLORS.white : 'rgba(255,255,255,0.08)',
                                    borderRadius: 16, marginRight: 8,
                                }}>
                                <Text style={{
                                    color: active ? COLORS.primary : 'rgba(255,255,255,0.9)',
                                    fontWeight: active ? '800' : '600',
                                    fontSize: 12,
                                    letterSpacing: 0.2,
                                }}>{sub.name}</Text>
                            </TouchableOpacity>
                        );
                    })}
                </ScrollView>
            </View>

            {/* Mock / PYQ segmented control — sits just below the header band */}
            <View style={{ flexDirection: 'row', backgroundColor: '#f3f4f6', marginHorizontal: 12, marginTop: 12, borderRadius: 10, padding: 3 }}>
                {(['PYQ', 'MOCK'] as TestTab[]).map(tab => {
                    const active = testTab === tab;
                    return (
                        <TouchableOpacity
                            key={tab}
                            onPress={() => setTestTab(tab)}
                            style={{
                                flex: 1, paddingVertical: 7, borderRadius: 8, alignItems: 'center',
                                backgroundColor: active ? COLORS.white : 'transparent',
                                shadowColor: active ? '#000' : 'transparent',
                                shadowOpacity: active ? 0.08 : 0,
                                shadowOffset: { width: 0, height: 1 },
                                shadowRadius: 3, elevation: active ? 1 : 0,
                            }}>
                            <Text style={{ fontWeight: '700', color: active ? COLORS.primary : COLORS.textSub, fontSize: 12 }}>
                                {tab === 'PYQ' ? `Previous Year · ${pyqCount}` : `Mock Tests · ${mockCount}`}
                            </Text>
                        </TouchableOpacity>
                    );
                })}
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
