import React, { useEffect, useState } from 'react';
import { View, Text, TouchableOpacity, Modal } from 'react-native';
import { Ionicons } from '@expo/vector-icons';
import { styles, COLORS } from '../styles/theme';
import { UserAPI } from '../services/api';
import AsyncStorage from '@react-native-async-storage/async-storage';
import { useNavigation } from '@react-navigation/native';

export default function ProfileDrawer({ visible, onClose, isGuest }: any) {
    const navigation = useNavigation<any>();
    const [user, setUser] = useState<any>(null);

    useEffect(() => {
        if (!isGuest && visible) {
            UserAPI.getMe().then(res => setUser(res.data)).catch(() => { });
        }
    }, [visible, isGuest]);

    const handleLogout = async () => {
        await AsyncStorage.removeItem('token');
        onClose();
        navigation.replace('Login');
    };

    return (
        <Modal visible={visible} animationType="fade" transparent={true} onRequestClose={onClose}>
            <View style={styles.drawerOverlay}>
                <View style={styles.drawerContent}>
                    <View style={styles.drawerProfileSection}>
                        <View style={{ width: 60, height: 60, borderRadius: 16, backgroundColor: COLORS.white, alignItems: 'center', justifyContent: 'center' }}>
                            <Text style={{ fontSize: 24, fontWeight: 'bold', color: COLORS.drawerBg }}>
                                {isGuest ? 'G' : (user?.name || 'S').charAt(0).toUpperCase()}
                            </Text>
                        </View>
                        <Text style={styles.drawerName}>{isGuest ? 'Guest User' : (user?.name || 'Student')}</Text>
                        <Text style={styles.drawerPhone}>{isGuest ? 'Login to save progress' : (user?.email || user?.phone || '')}</Text>
                        <TouchableOpacity onPress={() => { onClose(); navigation.navigate('ProfileTab'); }}>
                            <Text style={{ color: '#60a5fa', marginTop: 10, fontWeight: 'bold' }}>View Profile</Text>
                        </TouchableOpacity>
                    </View>

                    <View style={styles.drawerMenu}>
                        <TouchableOpacity style={styles.drawerMenuItem} onPress={onClose}>
                            <Ionicons name="home" size={22} color={COLORS.iconColor} />
                            <Text style={styles.drawerMenuText}>Home</Text>
                        </TouchableOpacity>
                        <TouchableOpacity style={styles.drawerMenuItem}>
                            <Ionicons name="ticket" size={22} color={COLORS.iconColor} />
                            <Text style={styles.drawerMenuText}>Pass Pro MAX</Text>
                        </TouchableOpacity>
                        <TouchableOpacity style={styles.drawerMenuItem}>
                            <Ionicons name="book" size={22} color={COLORS.iconColor} />
                            <Text style={styles.drawerMenuText}>Study Notes</Text>
                            <View style={{ backgroundColor: '#fdba74', paddingHorizontal: 6, paddingVertical: 2, borderRadius: 4, marginLeft: 10 }}>
                                <Text style={{ fontSize: 10, fontWeight: 'bold', color: '#9a3412' }}>NEW</Text>
                            </View>
                        </TouchableOpacity>
                        <TouchableOpacity style={styles.drawerMenuItem} onPress={() => { onClose(); navigation.navigate('Downloads'); }}>
                            <Ionicons name="download-outline" size={22} color={COLORS.iconColor} />
                            <Text style={styles.drawerMenuText}>Downloaded Materials</Text>
                        </TouchableOpacity>

                        <View style={{ flex: 1 }} />

                        {!isGuest && (
                            <TouchableOpacity style={styles.drawerMenuItem} onPress={handleLogout}>
                                <Ionicons name="log-out-outline" size={24} color="#ef4444" />
                                <Text style={[styles.drawerMenuText, { color: '#ef4444' }]}>Log Out</Text>
                            </TouchableOpacity>
                        )}
                    </View>
                </View>

                {/* Clickable overlay right side to close drawer */}
                <TouchableOpacity style={{ flex: 1 }} onPress={onClose} activeOpacity={1} />
            </View>
        </Modal>
    );
}
