import React, { useState, useEffect } from 'react';
import { View, Text, ScrollView, TouchableOpacity, ActivityIndicator, SafeAreaView, Dimensions } from 'react-native';
import { Ionicons, MaterialCommunityIcons } from '@expo/vector-icons';
import { LinearGradient } from 'expo-linear-gradient';
import { CategoryAPI, UserAPI } from '../../services/api';
import { getCategoryAsset } from '../../utils/categoryAssets';
import { COLORS } from '../../styles/theme';

const { width } = Dimensions.get('window');

export default function OnboardingScreen({ navigation, route }: any) {
    const isChangeExam = route.params?.isChangeExam || false;
    const [categories, setCategories] = useState<any[]>([]);
    const [selectedId, setSelectedId] = useState<string | null>(null);
    const [loading, setLoading] = useState(true);
    const [saving, setSaving] = useState(false);

    useEffect(() => {
        const fetchCategories = async () => {
            try {
                const res = await CategoryAPI.list();
                setCategories(res.data || []);
            } catch (error) {
                console.error("Failed to fetch categories:", error);
            } finally {
                setLoading(false);
            }
        };
        fetchCategories();
    }, []);

    const handleSave = async () => {
        if (!selectedId) return;
        setSaving(true);
        try {
            await UserAPI.updateExamPreference(selectedId);
            if (isChangeExam) {
                navigation.goBack();
            } else {
                navigation.replace('MainTabs', { isGuest: false });
            }
        } catch (error) {
            console.error("Failed to save preference:", error);
            setSaving(false);
        }
    };

    if (loading) {
        return (
            <View style={{ flex: 1, backgroundColor: '#f9fafb', justifyContent: 'center', alignItems: 'center' }}>
                <ActivityIndicator size="large" color={COLORS.primary} />
            </View>
        );
    }

    return (
        <SafeAreaView style={{ flex: 1, backgroundColor: '#f9fafb' }}>
            <ScrollView contentContainerStyle={{ padding: 20, paddingBottom: 120 }}>
                {/* Header */}
                <View style={{ alignItems: 'center', marginTop: 20, marginBottom: 30 }}>
                    <View style={{
                        width: 70, height: 70, borderRadius: 35,
                        backgroundColor: '#fff7ed', alignItems: 'center', justifyContent: 'center',
                        marginBottom: 16, borderWidth: 1, borderColor: '#fed7aa',
                        shadowColor: COLORS.primary, shadowOpacity: 0.2, shadowRadius: 10, shadowOffset: { width: 0, height: 4 }, elevation: 5
                    }}>
                        <Text style={{ fontSize: 32 }}>🎯</Text>
                    </View>
                    <Text style={{ fontSize: 28, fontWeight: '800', color: '#111827', textAlign: 'center', letterSpacing: -0.5 }}>
                        {isChangeExam ? 'Change Your Exam Goal' : 'What are you preparing for?'}
                    </Text>
                    <Text style={{ fontSize: 15, color: '#6b7280', textAlign: 'center', marginTop: 8, lineHeight: 22, paddingHorizontal: 20 }}>
                        {isChangeExam
                            ? 'Select a different exam to personalize your study experience.'
                            : "Select your primary exam target. We'll personalize your entire study experience."}
                    </Text>
                </View>

                {/* Category Grid */}
                <View style={{ flexDirection: 'row', flexWrap: 'wrap', justifyContent: 'space-between' }}>
                    {categories.map((category) => {
                        const isSelected = selectedId === category.id;
                        const asset = getCategoryAsset(category.name);
                        return (
                            <TouchableOpacity
                                key={category.id}
                                onPress={() => setSelectedId(category.id)}
                                activeOpacity={0.8}
                                style={{ width: '48%', marginBottom: 12 }}
                            >
                                <View style={{
                                    borderRadius: 16, padding: 16, height: 100,
                                    justifyContent: 'space-between',
                                    backgroundColor: isSelected ? '#fff7ed' : '#ffffff',
                                    borderWidth: 2,
                                    borderColor: isSelected ? COLORS.primary : '#e5e7eb',
                                    shadowColor: isSelected ? COLORS.primary : '#000',
                                    shadowOpacity: isSelected ? 0.15 : 0.05,
                                    shadowRadius: isSelected ? 8 : 3,
                                    shadowOffset: { width: 0, height: 2 },
                                    elevation: isSelected ? 4 : 1,
                                }}>
                                    <View style={{ flexDirection: 'row', alignItems: 'center', justifyContent: 'space-between' }}>
                                        <View style={{
                                            width: 36, height: 36, borderRadius: 10,
                                            backgroundColor: isSelected ? COLORS.primary : '#f3f4f6',
                                            alignItems: 'center', justifyContent: 'center'
                                        }}>
                                            {asset.iconFamily === 'MaterialCommunityIcons' ? (
                                                <MaterialCommunityIcons name={asset.iconName as any} size={18} color={isSelected ? '#fff' : asset.iconColor} />
                                            ) : (
                                                <Ionicons name={asset.iconName as any} size={18} color={isSelected ? '#fff' : asset.iconColor} />
                                            )}
                                        </View>
                                        {isSelected && (
                                            <View style={{
                                                width: 22, height: 22, borderRadius: 11,
                                                backgroundColor: COLORS.primary, alignItems: 'center', justifyContent: 'center'
                                            }}>
                                                <Ionicons name="checkmark" size={14} color="#fff" />
                                            </View>
                                        )}
                                    </View>
                                    <Text style={{
                                        fontSize: 14, fontWeight: '700',
                                        color: isSelected ? '#9a3412' : '#111827',
                                        lineHeight: 18,
                                    }} numberOfLines={2}>
                                        {category.name}
                                    </Text>
                                </View>
                            </TouchableOpacity>
                        );
                    })}
                </View>
            </ScrollView>

            {/* Sticky Bottom Button */}
            <View style={{
                position: 'absolute', bottom: 0, left: 0, right: 0,
                backgroundColor: '#ffffff', paddingHorizontal: 20, paddingVertical: 16,
                paddingBottom: 34,
                borderTopWidth: 1, borderTopColor: '#f3f4f6',
                shadowColor: '#000', shadowOpacity: 0.08, shadowRadius: 10, shadowOffset: { width: 0, height: -3 }, elevation: 10,
            }}>
                <TouchableOpacity
                    onPress={handleSave}
                    disabled={!selectedId || saving}
                    activeOpacity={0.8}
                    style={{
                        backgroundColor: !selectedId || saving ? '#d1d5db' : '#111827',
                        borderRadius: 14, paddingVertical: 16, alignItems: 'center',
                        shadowColor: '#000', shadowOpacity: !selectedId ? 0 : 0.2,
                        shadowRadius: 8, shadowOffset: { width: 0, height: 4 }, elevation: 5,
                    }}
                >
                    {saving ? (
                        <ActivityIndicator color="#fff" />
                    ) : (
                        <Text style={{ color: '#ffffff', fontSize: 17, fontWeight: '700', letterSpacing: 0.3 }}>
                            {isChangeExam ? 'Update Exam Goal' : 'Continue to Dashboard'}
                        </Text>
                    )}
                </TouchableOpacity>
            </View>
        </SafeAreaView>
    );
}
