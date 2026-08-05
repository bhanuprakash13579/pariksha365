import React, { useEffect, useLayoutEffect, useState, useCallback } from 'react';
import { View, Text, StyleSheet, ActivityIndicator, TouchableOpacity, StatusBar, Alert, Platform } from 'react-native';
import { Ionicons } from '@expo/vector-icons';
import Pdf from 'react-native-pdf';
import AsyncStorage from '@react-native-async-storage/async-storage';
import * as FileSystem from 'expo-file-system/legacy';
import * as Sharing from 'expo-sharing';
import { NotesAPI } from '../../services/api';

/**
 * Native in-app PDF reader. We download the (auth-gated) PDF to a local cache file first,
 * then render that local file with react-native-pdf — this is far more reliable than letting
 * the PDF view fetch a remote URL with auth headers. Renders the actual PDF exactly like the
 * original, with pinch-zoom, one-tap fullscreen, and a download/share action.
 */
export default function NotesReaderScreen({ route, navigation }: any) {
    const { bookId, title } = route.params || {};
    const [localUri, setLocalUri] = useState<string | null>(null);
    const [page, setPage] = useState(1);
    const [pageCount, setPageCount] = useState(0);
    const [loading, setLoading] = useState(true);
    const [error, setError] = useState<string | null>(null);
    const [fullscreen, setFullscreen] = useState(false);
    const [sharing, setSharing] = useState(false);

    // Download the PDF (with auth) to a local file, then render it locally.
    useEffect(() => {
        let cancelled = false;
        (async () => {
            try {
                setLoading(true);
                setError(null);
                const token = await AsyncStorage.getItem('token');
                const target = FileSystem.cacheDirectory + `${bookId}.pdf`;
                const res = await FileSystem.downloadAsync(NotesAPI.fileUrl(bookId), target, {
                    headers: { Authorization: `Bearer ${token}` },
                });
                if (cancelled) return;
                if (res.status !== 200) {
                    setError(res.status === 403 ? 'You do not have access to this book yet.'
                        : res.status === 404 ? 'This book is not available.'
                        : `Could not load (error ${res.status}).`);
                    setLoading(false);
                    return;
                }
                setLocalUri(res.uri);
            } catch (e: any) {
                if (!cancelled) { setError('Could not download this book. Check your connection.'); setLoading(false); }
            }
        })();
        return () => { cancelled = true; };
    }, [bookId]);

    const share = useCallback(async () => {
        if (!localUri) return;
        setSharing(true);
        try {
            if (await Sharing.isAvailableAsync()) {
                await Sharing.shareAsync(localUri, { mimeType: 'application/pdf', dialogTitle: title });
            } else {
                Alert.alert('Saved', 'The PDF is saved in the app storage.');
            }
        } catch { /* user cancelled */ } finally { setSharing(false); }
    }, [localUri, title]);

    useLayoutEffect(() => {
        navigation.setOptions({
            headerShown: !fullscreen,
            title: title || 'Study Notes',
            headerRight: () => (
                <TouchableOpacity onPress={share} disabled={!localUri || sharing} style={{ paddingHorizontal: 8 }}>
                    {sharing ? <ActivityIndicator size="small" color="#f97316" />
                        : <Ionicons name="download-outline" size={24} color={localUri ? '#f97316' : '#d1d5db'} />}
                </TouchableOpacity>
            ),
        });
    }, [navigation, fullscreen, title, share, localUri, sharing]);

    useEffect(() => {
        StatusBar.setHidden(fullscreen, 'fade');
        return () => StatusBar.setHidden(false, 'fade');
    }, [fullscreen]);

    if (error) {
        return (
            <View style={styles.center}>
                <Ionicons name="alert-circle-outline" size={48} color="#ef4444" />
                <Text style={styles.errorText}>{error}</Text>
                <TouchableOpacity style={styles.retry} onPress={() => { setLocalUri(null); setError(null); setLoading(true); navigation.setParams({ _r: Date.now() }); }}>
                    <Text style={styles.retryText}>Retry</Text>
                </TouchableOpacity>
            </View>
        );
    }

    return (
        <View style={styles.container}>
            {localUri && (
                <Pdf
                    source={{ uri: localUri }}
                    onLoadComplete={(n) => { setPageCount(n); setLoading(false); }}
                    onPageChanged={(p) => setPage(p)}
                    onError={() => { setError('This file could not be opened.'); setLoading(false); }}
                    enablePaging={false}
                    spacing={6}
                    style={styles.pdf}
                />
            )}

            {loading && (
                <View style={styles.overlay} pointerEvents="none">
                    <ActivityIndicator size="large" color="#f97316" />
                    <Text style={styles.loadingText}>Opening…</Text>
                </View>
            )}

            {!loading && pageCount > 0 && (
                <View style={styles.pageBadge} pointerEvents="none">
                    <Text style={styles.pageBadgeText}>{page} / {pageCount}</Text>
                </View>
            )}

            {localUri && (
                <TouchableOpacity
                    onPress={() => setFullscreen((v) => !v)}
                    activeOpacity={0.85}
                    style={[styles.fsButton, fullscreen && styles.fsButtonFs]}
                >
                    <Ionicons name={fullscreen ? 'contract-outline' : 'expand-outline'} size={22} color="#fff" />
                </TouchableOpacity>
            )}
        </View>
    );
}

const styles = StyleSheet.create({
    container: { flex: 1, backgroundColor: '#525659' },
    pdf: { flex: 1, backgroundColor: '#525659' },
    center: { flex: 1, alignItems: 'center', justifyContent: 'center', backgroundColor: '#fff', padding: 30 },
    overlay: { ...StyleSheet.absoluteFillObject, alignItems: 'center', justifyContent: 'center' },
    loadingText: { marginTop: 10, color: '#f3f4f6', fontWeight: '600' },
    errorText: { marginTop: 12, color: '#374151', fontWeight: '600', textAlign: 'center' },
    retry: { marginTop: 16, backgroundColor: '#f97316', paddingHorizontal: 22, paddingVertical: 10, borderRadius: 10 },
    retryText: { color: '#fff', fontWeight: '800' },
    pageBadge: { position: 'absolute', top: 10, alignSelf: 'center', backgroundColor: 'rgba(0,0,0,0.55)', paddingHorizontal: 12, paddingVertical: 4, borderRadius: 20 },
    pageBadgeText: { color: '#fff', fontSize: 12, fontWeight: '700' },
    fsButton: { position: 'absolute', bottom: 20, right: 16, width: 48, height: 48, borderRadius: 24, backgroundColor: 'rgba(249,115,22,0.95)', alignItems: 'center', justifyContent: 'center', elevation: 5 },
    fsButtonFs: { bottom: Platform.OS === 'android' ? 28 : 40 },
});
