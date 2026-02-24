import React from 'react';
import { View, TouchableOpacity, TextInput } from 'react-native';
import { Ionicons } from '@expo/vector-icons';
import { styles, COLORS } from '../styles/theme';

export default function GlobalHeader({ onOpenDrawer, onSearch }: any) {
    return (
        <View style={styles.tbHeaderContainer}>
            <TouchableOpacity style={styles.tbHeaderLeftBtn} onPress={onOpenDrawer}>
                <Ionicons name="menu" size={24} color={COLORS.white} />
            </TouchableOpacity>

            <View style={styles.tbSearchContainer}>
                <Ionicons name="search" size={18} color={COLORS.iconColor} />
                <TextInput
                    style={styles.tbSearchText}
                    placeholder="Search exams, tests and more"
                    placeholderTextColor={COLORS.iconColor}
                    onChangeText={onSearch}
                />
            </View>

            <TouchableOpacity style={styles.tbHeaderRightBtn}>
                <Ionicons name="notifications-outline" size={22} color={COLORS.white} />
            </TouchableOpacity>
        </View>
    );
}
