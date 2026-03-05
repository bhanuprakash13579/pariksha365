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
        const fetchCategories = async () => {
            try {
                const res = await CategoryAPI.list();
                setCategories(res.data);
            } catch (err) {
                console.error(err);
            } finally {
                setLoading(false);
            }
        };
        fetchCategories();
    }, []);

    return (
        <View style={styles.container}>
            <GlobalHeader onOpenDrawer={() => setDrawerVisible(true)} />

            <ScrollView contentContainerStyle={styles.contentPadAlt}>
                {/* Mobile Daily Quiz Hero Banner */}
                <TouchableOpacity
                    activeOpacity={0.9}
                    onPress={() => navigation.navigate('DailyQuiz')}
                    style={{ marginBottom: 20, marginTop: 10, shadowColor: '#f97316', shadowOpacity: 0.3, shadowRadius: 10, shadowOffset: { width: 0, height: 4 }, elevation: 8 }}
                >
                    <LinearGradient
                        colors={['#f97316', '#ec4899']}
                        start={{ x: 0, y: 0 }}
                        end={{ x: 1, y: 1 }}
                        style={{ borderRadius: 20, padding: 20, overflow: 'hidden', flexDirection: 'row', alignItems: 'center' }}
                    >
                        {/* Decorative background blobs */}
                        <View style={{ position: 'absolute', top: -30, right: -20, width: 120, height: 120, borderRadius: 60, backgroundColor: 'rgba(255,255,255,0.15)' }} />
                        <View style={{ position: 'absolute', bottom: -20, right: 40, width: 80, height: 80, borderRadius: 40, backgroundColor: 'rgba(255,255,255,0.1)' }} />
                        <View style={{ position: 'absolute', top: 20, left: -20, width: 60, height: 60, borderRadius: 30, backgroundColor: 'rgba(255,255,255,0.1)' }} />

                        {/* Icon */}
                        <View style={{ width: 50, height: 50, borderRadius: 15, backgroundColor: 'rgba(255,255,255,0.25)', alignItems: 'center', justifyContent: 'center', marginRight: 15 }}>
                            <Ionicons name="flash" size={28} color="white" />
                        </View>

                        {/* Content */}
                        <View style={{ flex: 1 }}>
                            <View style={{ flexDirection: 'row', alignItems: 'center', marginBottom: 4 }}>
                                <View style={{ width: 6, height: 6, borderRadius: 3, backgroundColor: '#4ade80', marginRight: 6 }} />
                                <Text style={{ color: 'rgba(255,255,255,0.9)', fontSize: 10, fontWeight: 'bold', textTransform: 'uppercase', letterSpacing: 1 }}>Live Challenge</Text>
                            </View>
                            <Text style={{ color: 'white', fontSize: 20, fontWeight: '900', marginBottom: 2, letterSpacing: -0.5 }}>Play Daily Quiz</Text>
                            <Text style={{ color: 'rgba(255,255,255,0.85)', fontSize: 12, fontWeight: '500' }}>Maintain your prep streak 🔥</Text>
                        </View>

                        {/* Arrow */}
                        <View style={{ width: 32, height: 32, borderRadius: 16, backgroundColor: 'white', alignItems: 'center', justifyContent: 'center', shadowColor: '#000', shadowOpacity: 0.1, shadowRadius: 3, elevation: 2 }}>
                            <Ionicons name="arrow-forward" size={18} color="#f97316" />
                        </View>

                    </LinearGradient>
                </TouchableOpacity>

                <Text style={[styles.sectionTitle, { fontSize: 16, color: COLORS.textSub }]}>| Explore All Categories</Text>

                {loading ? <ActivityIndicator size="large" color={COLORS.primary} style={{ marginTop: 20 }} /> : null}

                <View style={[styles.gridContainer, { paddingHorizontal: 5 }]}>
                    {categories.map(cat => {
                        const asset = getCategoryAsset(cat.name);
                        return (
                            <TouchableOpacity
                                key={cat.id}
                                style={{ width: '48%', marginBottom: 15 }}
                                onPress={() => navigation.navigate('Category', { categoryTitle: cat.name, subcategories: cat.subcategories })}
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
                                        <Text style={[styles.categoryGridTitle, { color: '#111827', fontSize: 16 }]} numberOfLines={2}>
                                            {cat.name}
                                        </Text>
                                    </View>

                                    {/* Oversized Background Watermark Icon (Simulating 3D Illustration) */}
                                    {!cat.image_url && (
                                        <View style={{ position: 'absolute', right: -15, bottom: -15, opacity: 0.15, transform: [{ rotate: '-15deg' }], zIndex: 1 }}>
                                            {asset.iconFamily === 'MaterialCommunityIcons' ? (
                                                <MaterialCommunityIcons name={asset.iconName as any} size={90} color={asset.iconColor} />
                                            ) : (
                                                <Ionicons name={asset.iconName as any} size={90} color={asset.iconColor} />
                                            )}
                                        </View>
                                    )}

                                    {/* Small Crisp Icon */}
                                    <View style={[styles.categoryIconWrap, { backgroundColor: 'rgba(255,255,255,0.6)', zIndex: 2, shadowColor: '#000', shadowOpacity: 0.1, shadowRadius: 3, elevation: 2 }]}>
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
                {categories.length === 0 && !loading && (
                    <Text style={{ textAlign: 'center', color: COLORS.textSub, marginTop: 20 }}>No categories available yet.</Text>
                )}
            </ScrollView>

            <ProfileDrawer visible={drawerVisible} onClose={() => setDrawerVisible(false)} isGuest={isGuest} />
        </View>
    );
}
