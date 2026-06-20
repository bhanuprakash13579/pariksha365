import React, { useState, useEffect } from 'react';
import { View, Text, ScrollView, TouchableOpacity, ActivityIndicator, Image } from 'react-native';
import { Ionicons, MaterialCommunityIcons } from '@expo/vector-icons';
import { LinearGradient } from 'expo-linear-gradient';
import { getCategoryAsset } from '../../utils/categoryAssets';
import { CategoryAPI } from '../../services/api';
import { styles, COLORS } from '../../styles/theme';
import GlobalHeader from '../../components/GlobalHeader';
import ProfileDrawer from '../../components/ProfileDrawer';

export default function HomeScreen({ navigation, route }: any) {
    const isGuest = route.params?.isGuest || false;
    const [categories, setCategories] = useState<any[]>([]);
    const [loading, setLoading] = useState(true);
    const [drawerVisible, setDrawerVisible] = useState(false);

    useEffect(() => {
        CategoryAPI.list()
            .then(res => setCategories(res.data))
            .catch(err => console.error(err))
            .finally(() => setLoading(false));
    }, []);

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
                        start={{ x: 0, y: 0 }}
                        end={{ x: 1, y: 1 }}
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
                        {/* ── Mock Tests Section ── */}
                        <SectionRow
                            title="Mock Tests"
                            icon="create-outline"
                            iconBg="#eff6ff"
                            iconColor="#3b82f6"
                            categories={categories}
                            cardAccent={['#3b82f6', '#6366f1']}
                            badgeBg="#eff6ff"
                            badgeText="#3b82f6"
                            badgeLabel="MOCK"
                            onPress={(cat: any) => goToCategory(cat, 'MOCK')}
                        />

                        {/* ── Previous Year Papers Section ── */}
                        <SectionRow
                            title="Previous Year Papers"
                            icon="library-outline"
                            iconBg="#fef3c7"
                            iconColor="#d97706"
                            categories={categories}
                            cardAccent={['#f59e0b', '#ef4444']}
                            badgeBg="#fef3c7"
                            badgeText="#b45309"
                            badgeLabel="PYQ"
                            onPress={(cat: any) => goToCategory(cat, 'PYQ')}
                        />

                        {/* ── Browse All Exams ── */}
                        <View style={{ flexDirection: 'row', alignItems: 'center', marginBottom: 14 }}>
                            <View style={{ flex: 1, height: 1, backgroundColor: '#e5e7eb' }} />
                            <Text style={{ color: COLORS.textSub, fontSize: 12, fontWeight: '600', paddingHorizontal: 12 }}>ALL EXAMS</Text>
                            <View style={{ flex: 1, height: 1, backgroundColor: '#e5e7eb' }} />
                        </View>

                        <View style={[styles.gridContainer, { paddingHorizontal: 5 }]}>
                            {categories.map(cat => {
                                const asset = getCategoryAsset(cat.name);
                                return (
                                    <TouchableOpacity
                                        key={cat.id}
                                        style={{ width: '48%', marginBottom: 15 }}
                                        onPress={() => goToCategory(cat, 'PYQ')}
                                        activeOpacity={0.8}
                                    >
                                        <LinearGradient
                                            colors={asset.colors}
                                            start={{ x: 0, y: 0 }}
                                            end={{ x: 1, y: 1 }}
                                            style={[styles.categoryGridCard, { width: '100%', marginBottom: 0, backgroundColor: 'transparent', overflow: 'hidden' }]}
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

function SectionRow({ title, icon, iconBg, iconColor, categories, cardAccent, badgeBg, badgeText, badgeLabel, onPress }: any) {
    return (
        <View style={{ marginBottom: 28 }}>
            {/* Section header */}
            <View style={{ flexDirection: 'row', alignItems: 'center', marginBottom: 12 }}>
                <View style={{ width: 32, height: 32, borderRadius: 10, backgroundColor: iconBg, alignItems: 'center', justifyContent: 'center', marginRight: 10 }}>
                    <Ionicons name={icon} size={18} color={iconColor} />
                </View>
                <Text style={{ fontSize: 16, fontWeight: '800', color: '#111827', letterSpacing: -0.3 }}>{title}</Text>
            </View>

            {/* Horizontal exam cards */}
            <ScrollView horizontal showsHorizontalScrollIndicator={false} contentContainerStyle={{ paddingRight: 20 }}>
                {categories.map((cat: any) => {
                    const asset = getCategoryAsset(cat.name);
                    return (
                        <TouchableOpacity
                            key={cat.id}
                            onPress={() => onPress(cat)}
                            activeOpacity={0.85}
                            style={{ marginRight: 12, width: 150 }}
                        >
                            <LinearGradient
                                colors={cardAccent}
                                start={{ x: 0, y: 0 }}
                                end={{ x: 1, y: 1 }}
                                style={{
                                    borderRadius: 16,
                                    padding: 14,
                                    minHeight: 110,
                                    justifyContent: 'space-between',
                                    overflow: 'hidden',
                                    shadowColor: cardAccent[0],
                                    shadowOpacity: 0.35,
                                    shadowRadius: 8,
                                    shadowOffset: { width: 0, height: 4 },
                                    elevation: 5,
                                }}
                            >
                                {/* Watermark icon */}
                                <View style={{ position: 'absolute', right: -10, bottom: -10, opacity: 0.12 }}>
                                    {asset.iconFamily === 'MaterialCommunityIcons' ? (
                                        <MaterialCommunityIcons name={asset.iconName as any} size={70} color="white" />
                                    ) : (
                                        <Ionicons name={asset.iconName as any} size={70} color="white" />
                                    )}
                                </View>

                                {/* Badge */}
                                <View style={{ backgroundColor: 'rgba(255,255,255,0.25)', alignSelf: 'flex-start', paddingHorizontal: 8, paddingVertical: 3, borderRadius: 6 }}>
                                    <Text style={{ color: 'white', fontSize: 9, fontWeight: '800', letterSpacing: 0.5 }}>{badgeLabel}</Text>
                                </View>

                                {/* Exam name */}
                                <Text style={{ color: 'white', fontSize: 14, fontWeight: '800', lineHeight: 19, marginTop: 8 }} numberOfLines={3}>
                                    {cat.name}
                                </Text>
                            </LinearGradient>
                        </TouchableOpacity>
                    );
                })}
            </ScrollView>
        </View>
    );
}
