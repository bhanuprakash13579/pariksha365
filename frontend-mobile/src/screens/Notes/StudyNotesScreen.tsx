import React, { useEffect, useState, useCallback } from 'react';
import { View, Text, StyleSheet, FlatList, TouchableOpacity, ActivityIndicator, RefreshControl, Alert, Linking } from 'react-native';
import { Ionicons } from '@expo/vector-icons';
import AsyncStorage from '@react-native-async-storage/async-storage';
import * as FileSystem from 'expo-file-system/legacy';
import * as Sharing from 'expo-sharing';
import { NotesAPI, type NoteFile } from '../../services/api';

/**
 * Study-notes library. Lists the admin-enabled books the student has access to, each with
 * "Read" (opens the native in-app PDF reader) and "Download" (saves the PDF to the device).
 */
export default function StudyNotesScreen({ navigation }: any) {
    const [files, setFiles] = useState<NoteFile[]>([]);
    const [hasAccess, setHasAccess] = useState(true);
    const [loading, setLoading] = useState(true);
    const [refreshing, setRefreshing] = useState(false);
    const [downloadingId, setDownloadingId] = useState<string | null>(null);

    const load = useCallback(async () => {
        try {
            const res = await NotesAPI.getAccess();
            setHasAccess(res.data.has_access);
            setFiles(res.data.files || []);
        } catch {
            setHasAccess(false);
            setFiles([]);
        } finally {
            setLoading(false);
            setRefreshing(false);
        }
    }, []);

    useEffect(() => { load(); }, [load]);

    const download = async (f: NoteFile) => {
        setDownloadingId(f.id);
        try {
            const token = await AsyncStorage.getItem('token');
            const target = FileSystem.cacheDirectory + `${f.id}.pdf`;
            const res = await FileSystem.downloadAsync(NotesAPI.fileUrl(f.id), target, {
                headers: { Authorization: `Bearer ${token}` },
            });
            if (res.status !== 200) throw new Error('failed');
            if (await Sharing.isAvailableAsync()) {
                await Sharing.shareAsync(res.uri, { mimeType: 'application/pdf', dialogTitle: f.title });
            } else {
                Alert.alert('Downloaded', 'Saved to the app storage.');
            }
        } catch {
            Alert.alert('Download failed', 'Please check your connection and try again.');
        } finally {
            setDownloadingId(null);
        }
    };

    if (loading) {
        return <View style={styles.center}><ActivityIndicator size="large" color="#f97316" /></View>;
    }

    if (!hasAccess) {
        return (
            <View style={styles.center}>
                <Ionicons name="lock-closed-outline" size={56} color="#d1d5db" />
                <Text style={styles.emptyTitle}>Notes bundle not unlocked</Text>
                <Text style={styles.emptySub}>Get lifetime access to all study notes to read and download them here.</Text>
                <TouchableOpacity style={styles.cta} onPress={() => Linking.openURL('https://pariksha365.in/notes')}>
                    <Text style={styles.ctaText}>View the notes bundle</Text>
                </TouchableOpacity>
            </View>
        );
    }

    if (files.length === 0) {
        return (
            <View style={styles.center}>
                <Ionicons name="book-outline" size={56} color="#d1d5db" />
                <Text style={styles.emptyTitle}>No notes available yet</Text>
                <Text style={styles.emptySub}>Study notes will appear here once they are published.</Text>
            </View>
        );
    }

    return (
        <FlatList
            data={files}
            keyExtractor={(f) => f.id}
            contentContainerStyle={{ padding: 14 }}
            refreshControl={<RefreshControl refreshing={refreshing} onRefresh={() => { setRefreshing(true); load(); }} tintColor="#f97316" />}
            renderItem={({ item }) => (
                <View style={styles.card}>
                    <View style={styles.iconWrap}>
                        <Ionicons name="document-text" size={26} color="#f97316" />
                    </View>
                    <View style={{ flex: 1, minWidth: 0 }}>
                        <Text style={styles.cardTitle} numberOfLines={2}>{item.title}</Text>
                        <View style={styles.actions}>
                            <TouchableOpacity
                                style={styles.readBtn}
                                onPress={() => navigation.navigate('NotesReader', { bookId: item.id, title: item.title })}
                            >
                                <Ionicons name="book" size={15} color="#fff" />
                                <Text style={styles.readBtnText}>Read</Text>
                            </TouchableOpacity>
                            <TouchableOpacity style={styles.dlBtn} onPress={() => download(item)} disabled={downloadingId === item.id}>
                                {downloadingId === item.id
                                    ? <ActivityIndicator size="small" color="#f97316" />
                                    : <><Ionicons name="download-outline" size={15} color="#f97316" /><Text style={styles.dlBtnText}>Download</Text></>}
                            </TouchableOpacity>
                        </View>
                    </View>
                </View>
            )}
        />
    );
}

const styles = StyleSheet.create({
    center: { flex: 1, alignItems: 'center', justifyContent: 'center', padding: 30, backgroundColor: '#f9fafb' },
    emptyTitle: { marginTop: 14, fontSize: 17, fontWeight: '800', color: '#374151' },
    emptySub: { marginTop: 6, fontSize: 13, color: '#9ca3af', textAlign: 'center' },
    cta: { marginTop: 18, backgroundColor: '#f97316', paddingHorizontal: 20, paddingVertical: 12, borderRadius: 12 },
    ctaText: { color: '#fff', fontWeight: '800' },
    card: { flexDirection: 'row', gap: 12, backgroundColor: '#fff', borderRadius: 14, borderWidth: 1, borderColor: '#f3f4f6', padding: 14, marginBottom: 10, alignItems: 'center' },
    iconWrap: { width: 46, height: 46, borderRadius: 10, backgroundColor: '#fff7ed', alignItems: 'center', justifyContent: 'center' },
    cardTitle: { fontSize: 14, fontWeight: '800', color: '#1f2937' },
    actions: { flexDirection: 'row', gap: 10, marginTop: 10 },
    readBtn: { flexDirection: 'row', alignItems: 'center', gap: 5, backgroundColor: '#f97316', paddingHorizontal: 14, paddingVertical: 8, borderRadius: 10 },
    readBtnText: { color: '#fff', fontWeight: '800', fontSize: 13 },
    dlBtn: { flexDirection: 'row', alignItems: 'center', gap: 5, backgroundColor: '#fff7ed', borderWidth: 1, borderColor: '#fed7aa', paddingHorizontal: 14, paddingVertical: 8, borderRadius: 10 },
    dlBtnText: { color: '#ea580c', fontWeight: '800', fontSize: 13 },
});
