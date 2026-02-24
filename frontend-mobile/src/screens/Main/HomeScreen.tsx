import React, { useState, useEffect } from 'react';
import { View, Text, ScrollView, TouchableOpacity, ActivityIndicator } from 'react-native';
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
                <Text style={[styles.sectionTitle, { fontSize: 16, color: COLORS.textSub, marginTop: 10 }]}>| Explore All Categories</Text>

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
                                    <View style={{ zIndex: 2, paddingRight: 10 }}>
                                        <Text style={[styles.categoryGridTitle, { color: '#111827', fontSize: 16 }]} numberOfLines={2}>
                                            {cat.name}
                                        </Text>
                                    </View>

                                    {/* Oversized Background Watermark Icon (Simulating 3D Illustration) */}
                                    <View style={{ position: 'absolute', right: -15, bottom: -15, opacity: 0.15, transform: [{ rotate: '-15deg' }], zIndex: 1 }}>
                                        {asset.iconFamily === 'MaterialCommunityIcons' ? (
                                            <MaterialCommunityIcons name={asset.iconName as any} size={90} color={asset.iconColor} />
                                        ) : (
                                            <Ionicons name={asset.iconName as any} size={90} color={asset.iconColor} />
                                        )}
                                    </View>

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
