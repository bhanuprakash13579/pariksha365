import React, { useState, useEffect, useCallback } from 'react';
import { View, Text, ScrollView, TouchableOpacity, ActivityIndicator, RefreshControl } from 'react-native';
import { Ionicons } from '@expo/vector-icons';
import { LinearGradient } from 'expo-linear-gradient';
import { useFocusEffect } from '@react-navigation/native';
import { styles, COLORS } from '../../styles/theme';
import { PrivateModuleAPI, AttemptAPI } from '../../services/api';

const MODULE_COLORS: Record<string, [string, string]> = {
    'epfo-apfc': ['#7c3aed', '#a855f7'],
    'ssc-cgl-aao-paper3': ['#0369a1', '#0ea5e9'],
};
const MODULE_ICONS: Record<string, string> = {
    'epfo-apfc': 'shield-checkmark',
    'ssc-cgl-aao-paper3': 'calculator',
};
const DEFAULT_COLORS: [string, string] = ['#374151', '#6b7280'];

export default function MyLearningScreen({ navigation }: any) {
    const [modules, setModules] = useState<any[]>([]);
    const [attempts, setAttempts] = useState<any[]>([]);
    const [loading, setLoading] = useState(true);
    const [refreshing, setRefreshing] = useState(false);

    const fetchAll = async () => {
        try {
            const [modRes, attRes] = await Promise.all([
                PrivateModuleAPI.listMine().catch(() => ({ data: [] })),
                AttemptAPI.list().catch(() => ({ data: [] })),
            ]);
            setModules(modRes.data || []);
            // most recent 5 attempts
            const all = attRes.data || [];
            setAttempts(all.slice(0, 5));
        } catch (err) {
            console.error('MyLearning fetch error:', err);
        } finally {
            setLoading(false);
            setRefreshing(false);
        }
    };

    useFocusEffect(useCallback(() => { fetchAll(); }, []));

    const onRefresh = () => { setRefreshing(true); fetchAll(); };

    if (loading) {
        return (
            <View style={[styles.container, { justifyContent: 'center', alignItems: 'center' }]}>
                <ActivityIndicator size="large" color={COLORS.primary} />
            </View>
        );
    }

    return (
        <ScrollView
            style={styles.container}
            refreshControl={<RefreshControl refreshing={refreshing} onRefresh={onRefresh} tintColor={COLORS.primary} />}
        >
            <View style={styles.contentPadAlt}>

                {/* ── Special Practice Modules ── */}
                <Text style={[styles.sectionTitle, { marginTop: 15, marginBottom: 12 }]}>Special Practice Modules</Text>

                {modules.length === 0 ? (
                    <View style={{ backgroundColor: '#f9fafb', borderRadius: 16, padding: 24, alignItems: 'center', marginBottom: 28 }}>
                        <Ionicons name="lock-closed-outline" size={36} color="#9ca3af" />
                        <Text style={{ color: '#6b7280', fontSize: 14, fontWeight: '600', marginTop: 10, textAlign: 'center' }}>
                            No special modules unlocked yet
                        </Text>
                        <Text style={{ color: '#9ca3af', fontSize: 12, textAlign: 'center', marginTop: 4 }}>
                            EPFO APFC and SSC CGL AAO modules appear here once granted
                        </Text>
                    </View>
                ) : (
                    modules.map((mod: any) => {
                        const colors = MODULE_COLORS[mod.slug] || DEFAULT_COLORS;
                        const iconName = MODULE_ICONS[mod.slug] || 'book';
                        return (
                            <TouchableOpacity
                                key={mod.slug}
                                activeOpacity={0.88}
                                style={{ marginBottom: 16 }}
                                onPress={() => navigation.navigate('PrivateModule', { slug: mod.slug, moduleName: mod.name })}
                            >
                                <LinearGradient
                                    colors={colors}
                                    start={{ x: 0, y: 0 }}
                                    end={{ x: 1, y: 0 }}
                                    style={{ borderRadius: 18, padding: 18, flexDirection: 'row', alignItems: 'center', shadowColor: colors[0], shadowOpacity: 0.4, shadowRadius: 10, shadowOffset: { width: 0, height: 4 }, elevation: 6 }}
                                >
                                    <View style={{ width: 50, height: 50, borderRadius: 14, backgroundColor: 'rgba(255,255,255,0.2)', alignItems: 'center', justifyContent: 'center', marginRight: 14 }}>
                                        <Ionicons name={iconName as any} size={26} color="white" />
                                    </View>
                                    <View style={{ flex: 1 }}>
                                        <Text style={{ color: 'white', fontSize: 15, fontWeight: '800', marginBottom: 2 }} numberOfLines={1}>{mod.name}</Text>
                                        <Text style={{ color: 'rgba(255,255,255,0.8)', fontSize: 12 }} numberOfLines={2}>{mod.description?.slice(0, 70)}…</Text>
                                    </View>
                                    <View style={{ width: 28, height: 28, borderRadius: 14, backgroundColor: 'rgba(255,255,255,0.2)', alignItems: 'center', justifyContent: 'center' }}>
                                        <Ionicons name="chevron-forward" size={16} color="white" />
                                    </View>
                                </LinearGradient>
                            </TouchableOpacity>
                        );
                    })
                )}

                {/* ── Recent Test Attempts ── */}
                <Text style={[styles.sectionTitle, { marginTop: 10, marginBottom: 12 }]}>Recent Test Attempts</Text>

                {attempts.length === 0 ? (
                    <View style={{ backgroundColor: '#f9fafb', borderRadius: 16, padding: 24, alignItems: 'center', marginBottom: 20 }}>
                        <Ionicons name="document-text-outline" size={36} color="#9ca3af" />
                        <Text style={{ color: '#6b7280', fontSize: 14, fontWeight: '600', marginTop: 10 }}>No attempts yet</Text>
                        <Text style={{ color: '#9ca3af', fontSize: 12, marginTop: 4, textAlign: 'center' }}>
                            Start a Mock Test or Previous Year Paper to see your history here
                        </Text>
                        <TouchableOpacity
                            onPress={() => navigation.navigate('HomeTab')}
                            style={{ marginTop: 14, paddingHorizontal: 20, paddingVertical: 9, backgroundColor: COLORS.primary, borderRadius: 10 }}
                        >
                            <Text style={{ color: 'white', fontSize: 13, fontWeight: '700' }}>Browse Tests</Text>
                        </TouchableOpacity>
                    </View>
                ) : (
                    attempts.map((att: any) => {
                        const isCompleted = att.status === 'completed';
                        const statusColor = isCompleted ? '#22c55e' : '#f59e0b';
                        const dateStr = att.ended_at || att.started_at;
                        return (
                            <TouchableOpacity
                                key={att.id}
                                style={[styles.card, { marginBottom: 10, borderLeftWidth: 3, borderLeftColor: statusColor }]}
                                onPress={() => isCompleted && navigation.navigate('TestAnalysis', { attemptId: att.id })}
                                activeOpacity={0.8}
                            >
                                <View style={{ flex: 1 }}>
                                    <Text style={[styles.cardTitle, { marginBottom: 4, fontSize: 14 }]} numberOfLines={1}>{att.test_title || 'Mock Test'}</Text>
                                    <View style={{ flexDirection: 'row', alignItems: 'center', gap: 10, flexWrap: 'wrap' }}>
                                        <View style={{ flexDirection: 'row', alignItems: 'center' }}>
                                            <View style={{ width: 7, height: 7, borderRadius: 4, backgroundColor: statusColor, marginRight: 5 }} />
                                            <Text style={{ fontSize: 11, color: COLORS.textSub, fontWeight: '600', textTransform: 'capitalize' }}>
                                                {isCompleted ? 'Completed' : 'In Progress'}
                                            </Text>
                                        </View>
                                        {dateStr && (
                                            <Text style={{ fontSize: 11, color: COLORS.textSub }}>
                                                {new Date(dateStr).toLocaleDateString('en-IN', { day: 'numeric', month: 'short', year: '2-digit' })}
                                            </Text>
                                        )}
                                    </View>
                                </View>
                                {isCompleted && (
                                    <Ionicons name="analytics-outline" size={20} color={COLORS.textSub} />
                                )}
                            </TouchableOpacity>
                        );
                    })
                )}

            </View>
        </ScrollView>
    );
}
