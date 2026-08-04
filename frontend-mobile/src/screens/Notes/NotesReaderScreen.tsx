import React, { useEffect, useLayoutEffect, useState, useCallback } from 'react';
import { View, Text, StyleSheet, ActivityIndicator, TouchableOpacity, StatusBar, Alert, Platform } from 'react-native';
import { Ionicons } from '@expo/vector-icons';
import Pdf from 'react-native-pdf';
import AsyncStorage from '@react-native-async-storage/async-storage';
import * as FileSystem from 'expo-file-system/legacy';
import * as Sharing from 'expo-sharing';
import { NotesAPI } from '../../services/api';

/**
 * Native in-app PDF reader. Renders the actual PDF (react-native-pdf) exactly as the
 * original — pinch-zoom, page scroll. Supports a distraction-free fullscreen mode the
 * user can enter and leave with one tap, plus a download-to-device action.
 */
export default function NotesReaderScreen({ route, navigation }: any) {
    const { bookId, title } = route.params || {};
    const [token, setToken] = useState<string | null>(null);
    const [page, setPage] = useState(1);
    const [pageCount, setPageCount] = useState(0);
    const [loading, setLoading] = useState(true);
    const [error, setError] = useState<string | null>(null);
    const [fullscreen, setFullscreen] = useState(false);
    const [downloading, setDownloading] = useState(false);

    useEffect(() => {
        AsyncStorage.getItem('token').then(setToken);
    }, []);

    const download = useCallback(async () => {
        if (!token) return;
        setDownloading(true);
        try {
            const target = FileSystem.cacheDirectory + `${bookId}.pdf`;
            const res = await FileSystem.downloadAsync(NotesAPI.fileUrl(bookId), target, {
                headers: { Authorization: `Bearer ${token}` },
            });
            if (res.status !== 200) throw new Error('download failed');
            if (await Sharing.isAvailableAsync()) {
                await Sharing.shareAsync(res.uri, { mimeType: 'application/pdf', dialogTitle: title });
            } else {
                Alert.alert('Downloaded', 'The PDF has been saved to the app cache.');
            }
        } catch {
            Alert.alert('Download failed', 'Please check your connection and try again.');
        } finally {
            setDownloading(false);
        }
    }, [token, bookId, title]);

    // Header: title + download; hidden entirely in fullscreen.
    useLayoutEffect(() => {
        navigation.setOptions({
            headerShown: !fullscreen,
            title: title || 'Study Notes',
            headerRight: () => (
                <TouchableOpacity onPress={download} disabled={downloading} style={{ paddingHorizontal: 8 }}>
                    {downloading
                        ? <ActivityIndicator size="small" color="#f97316" />
                        : <Ionicons name="download-outline" size={24} color="#f97316" />}
                </TouchableOpacity>
            ),
        });
    }, [navigation, fullscreen, title, download, downloading]);

    // Hide the status bar while in fullscreen for an immersive, PDF-like page.
    useEffect(() => {
        StatusBar.setHidden(fullscreen, 'fade');
        return () => StatusBar.setHidden(false, 'fade');
    }, [fullscreen]);

    if (!token) {
        return <View style={styles.center}><ActivityIndicator size="large" color="#f97316" /></View>;
    }

    return (
        <View style={styles.container}>
            <Pdf
                trustAllCerts={false}
                source={{ uri: NotesAPI.fileUrl(bookId), headers: { Authorization: `Bearer ${token}` }, cache: true }}
                onLoadComplete={(n) => { setPageCount(n); setLoading(false); }}
                onPageChanged={(p) => setPage(p)}
                onError={() => { setError('Could not open this book. Please try again.'); setLoading(false); }}
                enablePaging={false}
                horizontal={false}
                spacing={6}
                style={styles.pdf}
            />

            {loading && !error && (
                <View style={styles.overlay} pointerEvents="none">
                    <ActivityIndicator size="large" color="#f97316" />
                    <Text style={styles.loadingText}>Opening…</Text>
                </View>
            )}

            {error && (
                <View style={styles.overlay}>
                    <Ionicons name="alert-circle-outline" size={48} color="#ef4444" />
                    <Text style={styles.errorText}>{error}</Text>
                </View>
            )}

            {/* Page indicator */}
            {!loading && !error && pageCount > 0 && (
                <View style={[styles.pageBadge, fullscreen && styles.pageBadgeFs]} pointerEvents="none">
                    <Text style={styles.pageBadgeText}>{page} / {pageCount}</Text>
                </View>
            )}

            {/* Fullscreen enter / exit — always reachable, floats over the PDF */}
            <TouchableOpacity
                onPress={() => setFullscreen((v) => !v)}
                activeOpacity={0.85}
                style={[styles.fsButton, fullscreen && styles.fsButtonFs]}
            >
                <Ionicons name={fullscreen ? 'contract-outline' : 'expand-outline'} size={22} color="#fff" />
            </TouchableOpacity>
        </View>
    );
}

const styles = StyleSheet.create({
    container: { flex: 1, backgroundColor: '#525659' },
    pdf: { flex: 1, backgroundColor: '#525659' },
    center: { flex: 1, alignItems: 'center', justifyContent: 'center', backgroundColor: '#fff' },
    overlay: { ...StyleSheet.absoluteFillObject, alignItems: 'center', justifyContent: 'center' },
    loadingText: { marginTop: 10, color: '#f3f4f6', fontWeight: '600' },
    errorText: { marginTop: 12, color: '#f3f4f6', fontWeight: '600', paddingHorizontal: 30, textAlign: 'center' },
    pageBadge: { position: 'absolute', top: 10, alignSelf: 'center', backgroundColor: 'rgba(0,0,0,0.55)', paddingHorizontal: 12, paddingVertical: 4, borderRadius: 20 },
    pageBadgeFs: { top: 8 },
    pageBadgeText: { color: '#fff', fontSize: 12, fontWeight: '700' },
    fsButton: { position: 'absolute', bottom: 20, right: 16, width: 48, height: 48, borderRadius: 24, backgroundColor: 'rgba(249,115,22,0.95)', alignItems: 'center', justifyContent: 'center', elevation: 5, shadowColor: '#000', shadowOpacity: 0.3, shadowRadius: 4, shadowOffset: { width: 0, height: 2 } },
    fsButtonFs: { bottom: Platform.OS === 'android' ? 28 : 40 },
});
