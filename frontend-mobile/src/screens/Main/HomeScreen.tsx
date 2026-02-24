import React, { useState, useEffect } from 'react';
import { View, Text, ScrollView, TouchableOpacity, ActivityIndicator } from 'react-native';
import { Ionicons } from '@expo/vector-icons';
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
                {/* Streaks Banner */}
                <View style={[styles.card, { backgroundColor: '#111827', flexDirection: 'row', alignItems: 'center', marginTop: 10, marginBottom: 15 }]}>
                    <View style={{ width: 50, height: 50, borderRadius: 25, backgroundColor: 'rgba(249, 115, 22, 0.2)', alignItems: 'center', justifyContent: 'center' }}>
                        <Ionicons name="flame" size={28} color={COLORS.primary} />
                    </View>
                    <View style={{ flex: 1, marginLeft: 15 }}>
                        <Text style={{ color: COLORS.white, fontSize: 18, fontWeight: 'bold' }}>3 Day Streak! 🔥</Text>
                        <Text style={{ color: '#9ca3af', fontSize: 13, marginTop: 4 }}>Complete a daily quiz to extend your streak.</Text>
                    </View>
                </View>

                <Text style={[styles.sectionTitle, { fontSize: 16, color: COLORS.textSub, marginTop: 10 }]}>| Explore All Categories</Text>

                {loading ? <ActivityIndicator size="large" color={COLORS.primary} style={{ marginTop: 20 }} /> : null}

                <View style={styles.gridContainer}>
                    {categories.map(cat => (
                        <TouchableOpacity
                            key={cat.id}
                            style={styles.categoryGridCard}
                            onPress={() => navigation.navigate('Category', { categoryTitle: cat.name, subcategories: cat.subcategories })}
                        >
                            <Text style={styles.categoryGridTitle}>{cat.name}</Text>
                            <View style={styles.categoryIconWrap}>
                                <Ionicons name={(cat.icon_name || 'book-outline') as any} size={18} color={COLORS.textSub} />
                            </View>
                        </TouchableOpacity>
                    ))}
                </View>
                {categories.length === 0 && !loading && (
                    <Text style={{ textAlign: 'center', color: COLORS.textSub, marginTop: 20 }}>No categories available yet.</Text>
                )}
            </ScrollView>

            <ProfileDrawer visible={drawerVisible} onClose={() => setDrawerVisible(false)} isGuest={isGuest} />
        </View>
    );
}
