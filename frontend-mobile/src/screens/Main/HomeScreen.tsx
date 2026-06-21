import React, { useState, useEffect } from 'react';
import { View, Text, ScrollView, TouchableOpacity, ActivityIndicator, Image } from 'react-native';
import { Ionicons, MaterialCommunityIcons } from '@expo/vector-icons';
import { LinearGradient } from 'expo-linear-gradient';
import { getCategoryAsset } from '../../utils/categoryAssets';
import { CategoryAPI, UserAPI } from '../../services/api';
import { styles, COLORS } from '../../styles/theme';
import GlobalHeader from '../../components/GlobalHeader';
import ProfileDrawer from '../../components/ProfileDrawer';

export default function HomeScreen({ navigation, route }: any) {
    const isGuest = route.params?.isGuest || false;
    const [categories, setCategories] = useState<any[]>([]);
    const [selectedCategory, setSelectedCategory] = useState<any>(null);
    const [loading, setLoading] = useState(true);
    const [drawerVisible, setDrawerVisible] = useState(false);

    useEffect(() => {
        const fetchData = async () => {
            try {
                const catRes = await CategoryAPI.list();
                const cats: any[] = catRes.data || [];
                setCategories(cats);

                if (!isGuest) {
                    const userRes = await UserAPI.getMe();
                    const selectedId = userRes.data?.selected_exam_category_id;
                    if (selectedId) {
                        const found = cats.find((c: any) => c.id === selectedId);
                        if (found) setSelectedCategory(found);
                    }
                }
            } catch (err) {
                console.error(err);
            } finally {
                setLoading(false);
            }
        };
        fetchData();
    }, [isGuest]);

    const goToCategory = (cat: any, initialTab: 'MOCK' | 'PYQ') => {
        navigation.navigate('Category', {
            categoryTitle: cat.name,
            categoryId: cat.id,
            subcategories: cat.subcategories,
            initialTab,
        });
    };

    return (
        <View style={styles.container}>
            <GlobalHeader onOpenDrawer={() => setDrawerVisible(true)} />

            <ScrollView contentContainerStyle={styles.contentPadAlt} showsVerticalScrollIndicator={false}>

                {/* Daily Quiz Hero Banner */}
                <TouchableOpacity
                    activeOpacity={0.9}
                    onPress={() => navigation.navigate('DailyQuizTab')}
                    style={{ marginBottom: 24, marginTop: 10, shadowColor: '#f97316', shadowOpacity: 0.3, shadowRadius: 10, shadowOffset: { width: 0, height: 4 }, elevation: 8 }}
                >
                    <LinearGradient
                        colors={['#f97316', '#ec4899']}
                        start={{ x: 0, y: 0 }} end={{ x: 1, y: 1 }}
                        style={{ borderRadius: 20, padding: 20, overflow: 'hidden', flexDirection: 'row', alignItems: 'center' }}
                    >
                        <View style={{ position: 'absolute', top: -30, right: -20, width: 120, height: 120, borderRadius: 60, backgroundColor: 'rgba(255,255,255,0.15)' }} />
                        <View style={{ position: 'absolute', bottom: -20, right: 40, width: 80, height: 80, borderRadius: 40, backgroundColor: 'rgba(255,255,255,0.1)' }} />
                        <View style={{ width: 50, height: 50, borderRadius: 15, backgroundColor: 'rgba(255,255,255,0.25)', alignItems: 'center', justifyContent: 'center', marginRight: 15 }}>
                            <Ionicons name="flash" size={28} color="white" />
                        </View>
                        <View style={{ flex: 1 }}>
                            <View style={{ flexDirection: 'row', alignItems: 'center', marginBottom: 4 }}>
                                <View style={{ width: 6, height: 6, borderRadius: 3, backgroundColor: '#4ade80', marginRight: 6 }} />
                                <Text style={{ color: 'rgba(255,255,255,0.9)', fontSize: 10, fontWeight: 'bold', textTransform: 'uppercase', letterSpacing: 1 }}>Live Challenge</Text>
                            </View>
                            <Text style={{ color: 'white', fontSize: 20, fontWeight: '900', marginBottom: 2, letterSpacing: -0.5 }}>Play Daily Quiz</Text>
                            <Text style={{ color: 'rgba(255,255,255,0.85)', fontSize: 12, fontWeight: '500' }}>Maintain your prep streak 🔥</Text>
                        </View>
                        <View style={{ width: 32, height: 32, borderRadius: 16, backgroundColor: 'white', alignItems: 'center', justifyContent: 'center' }}>
                            <Ionicons name="arrow-forward" size={18} color="#f97316" />
                        </View>
                    </LinearGradient>
                </TouchableOpacity>

                {loading ? (
                    <ActivityIndicator size="large" color={COLORS.primary} style={{ marginTop: 20 }} />
                ) : (
                    <>
                        {/* ── Selected Exam Goal ── */}
                        {selectedCategory ? (
                            <View style={{ marginBottom: 28 }}>
                                {/* Header row */}
                                <View style={{ flexDirection: 'row', alignItems: 'center', justifyContent: 'space-between', marginBottom: 14 }}>
                                    <View>
                                        <Text style={{ fontSize: 11, fontWeight: '700', color: '#9ca3af', textTransform: 'uppercase', letterSpacing: 0.8 }}>
                                            Your Exam Goal
                                        </Text>
                                        <Text style={{ fontSize: 20, fontWeight: '800', color: '#111827', marginTop: 2 }}>
                                            {selectedCategory.name}
                                        </Text>
                                    </View>
                                    <TouchableOpacity
                                        onPress={() => navigation.navigate('ChangeExam')}
                                        style={{
                                            paddingHorizontal: 12, paddingVertical: 6,
                                            borderRadius: 10, borderWidth: 1, borderColor: '#e5e7eb',
                                            backgroundColor: '#f9fafb',
                                        }}
                                    >
                                        <Text style={{ fontSize: 12, color: '#6b7280', fontWeight: '600' }}>Change</Text>
                                    </TouchableOpacity>
                                </View>

                                {/* Mock Tests + PYQ cards */}
                                <View style={{ flexDirection: 'row', gap: 12 }}>
                                    <TouchableOpacity
                                        onPress={() => goToCategory(selectedCategory, 'MOCK')}
                                        activeOpacity={0.85}
                                        style={{ flex: 1 }}
                                    >
                                        <LinearGradient
                                            colors={['#3b82f6', '#6366f1']}
                                            start={{ x: 0, y: 0 }} end={{ x: 1, y: 1 }}
                                            style={{
                                                borderRadius: 18, padding: 18, minHeight: 120,
                                                justifyContent: 'space-between', overflow: 'hidden',
                                                shadowColor: '#3b82f6', shadowOpacity: 0.35,
                                                shadowRadius: 10, shadowOffset: { width: 0, height: 4 }, elevation: 5,
                                            }}
                                        >
                                            <View style={{ position: 'absolute', right: -15, bottom: -15, opacity: 0.15 }}>
                                                <Ionicons name="create-outline" size={80} color="white" />
                                            </View>
                                            <View style={{ backgroundColor: 'rgba(255,255,255,0.2)', alignSelf: 'flex-start', paddingHorizontal: 8, paddingVertical: 3, borderRadius: 6 }}>
                                                <Text style={{ color: 'white', fontSize: 9, fontWeight: '800', letterSpacing: 0.5 }}>MOCK</Text>
                                            </View>
                                            <Text style={{ color: 'white', fontSize: 15, fontWeight: '800', marginTop: 24, lineHeight: 20 }}>
                                                Mock Tests
                                            </Text>
                                            <Text style={{ color: 'rgba(255,255,255,0.75)', fontSize: 11, marginTop: 3 }}>Full-length practice</Text>
                                        </LinearGradient>
                                    </TouchableOpacity>

                                    <TouchableOpacity
                                        onPress={() => goToCategory(selectedCategory, 'PYQ')}
                                        activeOpacity={0.85}
                                        style={{ flex: 1 }}
                                    >
                                        <LinearGradient
                                            colors={['#f59e0b', '#ef4444']}
                                            start={{ x: 0, y: 0 }} end={{ x: 1, y: 1 }}
                                            style={{
                                                borderRadius: 18, padding: 18, minHeight: 120,
                                                justifyContent: 'space-between', overflow: 'hidden',
                                                shadowColor: '#f59e0b', shadowOpacity: 0.35,
                                                shadowRadius: 10, shadowOffset: { width: 0, height: 4 }, elevation: 5,
                                            }}
                                        >
                                            <View style={{ position: 'absolute', right: -15, bottom: -15, opacity: 0.15 }}>
                                                <Ionicons name="library-outline" size={80} color="white" />
                                            </View>
                                            <View style={{ backgroundColor: 'rgba(255,255,255,0.2)', alignSelf: 'flex-start', paddingHorizontal: 8, paddingVertical: 3, borderRadius: 6 }}>
                                                <Text style={{ color: 'white', fontSize: 9, fontWeight: '800', letterSpacing: 0.5 }}>PYQ</Text>
                                            </View>
                                            <Text style={{ color: 'white', fontSize: 15, fontWeight: '800', marginTop: 24, lineHeight: 20 }}>
                                                Previous Year Papers
                                            </Text>
                                            <Text style={{ color: 'rgba(255,255,255,0.75)', fontSize: 11, marginTop: 3 }}>Real exam questions</Text>
                                        </LinearGradient>
                                    </TouchableOpacity>
                                </View>
                            </View>
                        ) : !isGuest ? (
                            /* No exam goal set yet */
                            <TouchableOpacity
                                onPress={() => navigation.navigate('ChangeExam')}
                                style={{
                                    backgroundColor: '#fff7ed', borderRadius: 16, padding: 18,
                                    borderWidth: 1, borderColor: '#fed7aa', flexDirection: 'row',
                                    alignItems: 'center', marginBottom: 24,
                                }}
                            >
                                <View style={{ width: 44, height: 44, borderRadius: 12, backgroundColor: '#ffedd5', alignItems: 'center', justifyContent: 'center', marginRight: 12 }}>
                                    <Text style={{ fontSize: 22 }}>🎯</Text>
                                </View>
                                <View style={{ flex: 1 }}>
                                    <Text style={{ fontSize: 15, fontWeight: '700', color: '#111827' }}>Set your exam goal</Text>
                                    <Text style={{ fontSize: 12, color: '#6b7280', marginTop: 2 }}>Personalise your Home and get focused content</Text>
                                </View>
                                <Ionicons name="chevron-forward" size={20} color="#f97316" />
                            </TouchableOpacity>
                        ) : null}

                        {/* ── Browse All Exams ── */}
                        <View style={{ flexDirection: 'row', alignItems: 'center', marginBottom: 14 }}>
                            <View style={{ flex: 1, height: 1, backgroundColor: '#e5e7eb' }} />
                            <Text style={{ color: COLORS.textSub, fontSize: 12, fontWeight: '600', paddingHorizontal: 12 }}>
                                {selectedCategory ? 'ALL EXAMS' : 'CHOOSE AN EXAM'}
                            </Text>
                            <View style={{ flex: 1, height: 1, backgroundColor: '#e5e7eb' }} />
                        </View>

                        <View style={[styles.gridContainer, { paddingHorizontal: 5 }]}>
                            {categories.map(cat => {
                                const asset = getCategoryAsset(cat.name);
                                const isSelected = selectedCategory?.id === cat.id;
                                return (
                                    <TouchableOpacity
                                        key={cat.id}
                                        style={{ width: '48%', marginBottom: 15 }}
                                        onPress={() => goToCategory(cat, 'PYQ')}
                                        activeOpacity={0.8}
                                    >
                                        <LinearGradient
                                            colors={asset.colors}
                                            start={{ x: 0, y: 0 }} end={{ x: 1, y: 1 }}
                                            style={[styles.categoryGridCard, {
                                                width: '100%', marginBottom: 0,
                                                backgroundColor: 'transparent', overflow: 'hidden',
                                                borderWidth: isSelected ? 2 : 0,
                                                borderColor: isSelected ? '#f97316' : 'transparent',
                                            }]}
                                        >
                                            {cat.image_url && (
                                                <Image source={{ uri: cat.image_url }} style={{ position: 'absolute', top: 0, left: 0, right: 0, bottom: 0, opacity: 0.3, width: '100%', height: '100%', resizeMode: 'cover' }} />
                                            )}
                                            <View style={{ zIndex: 2, paddingRight: 10 }}>
                                                <Text style={[styles.categoryGridTitle, { color: '#111827', fontSize: 15 }]} numberOfLines={2}>{cat.name}</Text>
                                            </View>
                                            {!cat.image_url && (
                                                <View style={{ position: 'absolute', right: -15, bottom: -15, opacity: 0.15, transform: [{ rotate: '-15deg' }], zIndex: 1 }}>
                                                    {asset.iconFamily === 'MaterialCommunityIcons' ? (
                                                        <MaterialCommunityIcons name={asset.iconName as any} size={90} color={asset.iconColor} />
                                                    ) : (
                                                        <Ionicons name={asset.iconName as any} size={90} color={asset.iconColor} />
                                                    )}
                                                </View>
                                            )}
                                            <View style={[styles.categoryIconWrap, { backgroundColor: 'rgba(255,255,255,0.6)', zIndex: 2 }]}>
                                                {asset.iconFamily === 'MaterialCommunityIcons' ? (
                                                    <MaterialCommunityIcons name={asset.iconName as any} size={18} color={asset.iconColor} />
                                                ) : (
                                                    <Ionicons name={asset.iconName as any} size={18} color={asset.iconColor} />
                                                )}
                                            </View>
                                            {isSelected && (
                                                <View style={{ position: 'absolute', top: 8, right: 8, backgroundColor: '#f97316', borderRadius: 10, width: 20, height: 20, alignItems: 'center', justifyContent: 'center', zIndex: 3 }}>
                                                    <Ionicons name="checkmark" size={12} color="white" />
                                                </View>
                                            )}
                                        </LinearGradient>
                                    </TouchableOpacity>
                                );
                            })}
                        </View>

                        {categories.length === 0 && (
                            <Text style={{ textAlign: 'center', color: COLORS.textSub, marginTop: 20 }}>No exams available yet.</Text>
                        )}
                    </>
                )}
            </ScrollView>

            <ProfileDrawer visible={drawerVisible} onClose={() => setDrawerVisible(false)} isGuest={isGuest} />
        </View>
    );
}
