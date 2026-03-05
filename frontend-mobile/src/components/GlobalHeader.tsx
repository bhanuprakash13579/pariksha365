import React, { useState, useEffect } from 'react';
import { View, TouchableOpacity, TextInput, Image, Modal, Text, ScrollView, Platform, Keyboard } from 'react-native';
import { Ionicons } from '@expo/vector-icons';
import { styles, COLORS } from '../styles/theme';
import { SearchAPI } from '../services/api';

export default function GlobalHeader({ onOpenDrawer, onSearch }: any) {
    const [searchQuery, setSearchQuery] = useState('');
    const [searchResults, setSearchResults] = useState<{ categories: any[], courses: any[], tests: any[] }>({ categories: [], courses: [], tests: [] });
    const [isSearching, setIsSearching] = useState(false);
    const [showResults, setShowResults] = useState(false);

    useEffect(() => {
        const delayDebounceFn = setTimeout(async () => {
            if (searchQuery.trim().length >= 2) {
                setIsSearching(true);
                setShowResults(true);
                try {
                    const res = await SearchAPI.globalSearch(searchQuery);
                    setSearchResults(res.data);
                } catch (err) {
                    console.error("Search failed", err);
                } finally {
                    setIsSearching(false);
                }
            } else {
                setSearchResults({ categories: [], courses: [], tests: [] });
                setShowResults(false);
            }
        }, 300);

        return () => clearTimeout(delayDebounceFn);
    }, [searchQuery]);
    return (
        <View style={styles.tbHeaderContainer}>
            <TouchableOpacity style={styles.tbHeaderLeftBtn} onPress={onOpenDrawer}>
                <Ionicons name="menu" size={28} color={COLORS.iconColor} />
            </TouchableOpacity>

            <View style={styles.tbSearchContainer}>
                <Ionicons name="search" size={18} color={COLORS.iconColor} />
                <TextInput
                    style={styles.tbSearchText}
                    placeholder="Search exams, tests and more"
                    placeholderTextColor={COLORS.iconColor}
                    value={searchQuery}
                    onChangeText={setSearchQuery}
                    onFocus={() => searchQuery.trim().length >= 2 && setShowResults(true)}
                />
            </View>

            <TouchableOpacity style={styles.tbHeaderRightBtn}>
                <Ionicons name="notifications-outline" size={22} color={COLORS.white} />
            </TouchableOpacity>

            <Modal visible={showResults} transparent={true} animationType="fade" onRequestClose={() => setShowResults(false)}>
                <TouchableOpacity style={{ flex: 1, backgroundColor: 'rgba(0,0,0,0.1)' }} activeOpacity={1} onPress={() => { setShowResults(false); Keyboard.dismiss(); }}>
                    <View style={{ backgroundColor: 'white', marginTop: Platform.OS === 'ios' ? 105 : 75, marginHorizontal: 20, borderRadius: 12, maxHeight: '60%', shadowColor: '#000', shadowOffset: { width: 0, height: 4 }, shadowOpacity: 0.1, shadowRadius: 10, elevation: 5, overflow: 'hidden' }}>

                        {isSearching ? (
                            <View style={{ padding: 20, alignItems: 'center' }}><Text style={{ color: '#6b7280' }}>Searching...</Text></View>
                        ) : (
                            <ScrollView keyboardShouldPersistTaps="handled">
                                {searchResults.categories.length > 0 && (
                                    <View style={{ borderBottomWidth: 1, borderBottomColor: '#f3f4f6' }}>
                                        <Text style={{ fontSize: 12, fontWeight: 'bold', color: '#9ca3af', textTransform: 'uppercase', paddingHorizontal: 15, paddingTop: 10, paddingBottom: 5 }}>Categories</Text>
                                        {searchResults.categories.map(cat => (
                                            <TouchableOpacity key={cat.id} style={{ paddingHorizontal: 15, paddingVertical: 12 }} onPress={() => setShowResults(false)}>
                                                <Text style={{ color: '#374151', fontSize: 14, fontWeight: '500' }}>{cat.name}</Text>
                                            </TouchableOpacity>
                                        ))}
                                    </View>
                                )}

                                {searchResults.courses.length > 0 && (
                                    <View style={{ borderBottomWidth: 1, borderBottomColor: '#f3f4f6' }}>
                                        <Text style={{ fontSize: 12, fontWeight: 'bold', color: '#9ca3af', textTransform: 'uppercase', paddingHorizontal: 15, paddingTop: 10, paddingBottom: 5 }}>Courses</Text>
                                        {searchResults.courses.map(course => (
                                            <TouchableOpacity key={course.id} style={{ paddingHorizontal: 15, paddingVertical: 12 }} onPress={() => setShowResults(false)}>
                                                <Text style={{ color: '#374151', fontSize: 14, fontWeight: '500' }}>{course.title}</Text>
                                            </TouchableOpacity>
                                        ))}
                                    </View>
                                )}

                                {searchResults.tests.length > 0 && (
                                    <View>
                                        <Text style={{ fontSize: 12, fontWeight: 'bold', color: '#9ca3af', textTransform: 'uppercase', paddingHorizontal: 15, paddingTop: 10, paddingBottom: 5 }}>Test Series</Text>
                                        {searchResults.tests.map(test => (
                                            <TouchableOpacity key={test.id} style={{ paddingHorizontal: 15, paddingVertical: 12 }} onPress={() => setShowResults(false)}>
                                                <Text style={{ color: '#374151', fontSize: 14, fontWeight: '500' }}>{test.title}</Text>
                                            </TouchableOpacity>
                                        ))}
                                    </View>
                                )}

                                {searchResults.categories.length === 0 && searchResults.courses.length === 0 && searchResults.tests.length === 0 && (
                                    <View style={{ padding: 20, alignItems: 'center' }}><Text style={{ color: '#6b7280' }}>No results found for "{searchQuery}"</Text></View>
                                )}
                            </ScrollView>
                        )}
                    </View>
                </TouchableOpacity>
            </Modal>
        </View>
    );
}
