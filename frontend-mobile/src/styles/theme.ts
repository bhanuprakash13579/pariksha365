import { StyleSheet } from 'react-native';

export const COLORS = {
    primary: '#f97316',
    primaryDisabled: '#9ca3af',
    background: '#f9fafb',
    card: '#ffffff',
    text: '#111827',
    textSub: '#6b7280',
    border: '#e5e7eb',
    success: '#10b981',
    error: '#ef4444',
    black: '#000000',
};

export const styles = StyleSheet.create({
    container: { flex: 1, backgroundColor: COLORS.background },
    contentPad: { padding: 16 },
    contentPadAlt: { padding: 16, paddingTop: 10 },
    flexRowBetween: { flexDirection: 'row', justifyContent: 'space-between', alignItems: 'center' },

    // Auth Screens
    authContainer: { flex: 1, backgroundColor: COLORS.card },
    authInner: { flex: 1, padding: 24, justifyContent: 'center' },
    authHeader: { marginBottom: 40 },
    authTitle: { fontSize: 32, fontWeight: 'bold', color: COLORS.text, marginBottom: 8 },
    authSubtitle: { fontSize: 16, color: COLORS.textSub },
    formContainer: { marginBottom: 32 },
    input: { backgroundColor: '#f3f4f6', borderRadius: 12, padding: 16, marginBottom: 16, fontSize: 16, color: '#1f2937', borderWidth: 1, borderColor: COLORS.border },
    primaryButton: { backgroundColor: COLORS.primary, borderRadius: 12, padding: 16, alignItems: 'center', shadowColor: COLORS.primary, shadowOffset: { width: 0, height: 4 }, shadowOpacity: 0.3, shadowRadius: 8, elevation: 5 },
    buttonDisabled: { backgroundColor: COLORS.primaryDisabled, borderRadius: 12, padding: 16, alignItems: 'center' },
    primaryButtonText: { color: COLORS.card, fontSize: 18, fontWeight: 'bold' },
    dividerRow: { flexDirection: 'row', alignItems: 'center', marginVertical: 25 },
    divider: { flex: 1, height: 1, backgroundColor: COLORS.border },
    dividerText: { color: '#9ca3af', paddingHorizontal: 10, fontWeight: 'bold' },
    socialButton: { flexDirection: 'row', alignItems: 'center', justifyContent: 'center', backgroundColor: COLORS.card, borderWidth: 1, borderColor: COLORS.border, borderRadius: 12, padding: 14, marginBottom: 15 },
    socialButtonText: { fontSize: 16, fontWeight: 'bold', color: '#374151', marginLeft: 10 },

    // Home Header (Premium UI)
    header: { padding: 20, paddingTop: 60, backgroundColor: COLORS.primary, paddingBottom: 30, borderBottomLeftRadius: 24, borderBottomRightRadius: 24 },
    greeting: { fontSize: 24, fontWeight: 'bold', color: 'white' },
    subGreeting: { fontSize: 15, color: '#ffedd5', marginTop: 4 },
    sectionTitle: { fontSize: 18, fontWeight: 'bold', marginBottom: 12, color: COLORS.text },

    // Cards
    card: { backgroundColor: COLORS.card, marginBottom: 15, padding: 16, borderRadius: 16, flexDirection: 'row', justifyContent: 'space-between', alignItems: 'center', elevation: 2, shadowColor: COLORS.black, shadowOpacity: 0.1, shadowRadius: 5 },
    cardTitle: { fontSize: 16, fontWeight: 'bold', color: '#1f2937' },
    tag: { color: COLORS.textSub, fontSize: 13, marginTop: 4 },
    metricsRow: { flexDirection: 'row', marginTop: 8 },
    metricText: { color: COLORS.textSub, fontSize: 12, marginRight: 12, marginTop: 4 },
    priceTag: { backgroundColor: '#fee2e2', paddingHorizontal: 8, paddingVertical: 4, borderRadius: 6, marginBottom: 8 },
    priceTagText: { color: '#b91c1c', fontSize: 10, fontWeight: 'bold', textTransform: 'uppercase' },
    freeTag: { backgroundColor: '#dcfce7', paddingHorizontal: 8, paddingVertical: 4, borderRadius: 6 },
    freeTagText: { color: '#15803d', fontWeight: 'bold', fontSize: 12 },
    price: { fontSize: 18, fontWeight: 'bold', color: '#1f2937' },

    // Course Detail Premium
    courseHeader: { backgroundColor: COLORS.card, padding: 20, paddingTop: 20, borderBottomWidth: 1, borderBottomColor: '#f3f4f6' },
    courseTitle: { fontSize: 24, fontWeight: 'bold', color: COLORS.text, marginBottom: 8 },
    courseDesc: { fontSize: 14, color: COLORS.textSub, lineHeight: 20 },
    iconBox: { width: 40, height: 40, borderRadius: 20, backgroundColor: '#fff7ed', alignItems: 'center', justifyContent: 'center' },
    iconBoxLocked: { backgroundColor: '#f3f4f6' },

    // Modals
    modalOverlay: { flex: 1, backgroundColor: 'rgba(0,0,0,0.5)', justifyContent: 'flex-end' },
    modalContent: { backgroundColor: COLORS.card, borderTopLeftRadius: 24, borderTopRightRadius: 24, padding: 24, paddingBottom: 40 },
    modalHeader: { flexDirection: 'row', justifyContent: 'space-between', alignItems: 'center', marginBottom: 15 },
    modalTitle: { fontSize: 22, fontWeight: 'bold', color: COLORS.text },
    modalTextCenter: { fontSize: 16, color: '#4b5563', textAlign: 'center', lineHeight: 24, marginBottom: 20 }
});
