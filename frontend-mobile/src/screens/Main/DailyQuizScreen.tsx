import React, { useState, useEffect } from 'react';
import { View, Text, ScrollView, TouchableOpacity, ActivityIndicator, TextInput } from 'react-native';
import { Ionicons } from '@expo/vector-icons';
import AsyncStorage from '@react-native-async-storage/async-storage';
import { styles, COLORS } from '../../styles/theme';
import { QuizAPI, PrivateModuleAPI } from '../../services/api';

export default function DailyQuizScreen({ navigation }: any) {
    const [categories, setCategories] = useState<any[]>([]);
    const [streak, setStreak] = useState<any>(null);
    const [weakQuiz, setWeakQuiz] = useState<any>(null);
    const [privateModules, setPrivateModules] = useState<any[]>([]);
    const [loading, setLoading] = useState(true);
    // Configurable quiz size & time (default 10 questions / 5 minutes). Fully free-form
    // (any count >=1, any time >=1). Raw string state so typing never snaps mid-keystroke;
    // clamped only when editing ends. Persisted in AsyncStorage so the chosen values stay.
    const [quizCount, setQuizCount] = useState(10);
    const [quizMinutes, setQuizMinutes] = useState(5);
    const [quizCountStr, setQuizCountStr] = useState('10');
    const [quizMinutesStr, setQuizMinutesStr] = useState('5');

    // Difficulty mode — 'auto' = balanced 30/30/40; 'custom' = exact per-difficulty counts.
    const [quizMode, setQuizMode] = useState<'auto' | 'custom'>('auto');
    const [diff, setDiff] = useState<{ EASY: number; MEDIUM: number; HARD: number }>({ EASY: 0, MEDIUM: 0, HARD: 0 });
    const [settingsOpen, setSettingsOpen] = useState(false);
    // Formula-practice mode: draw only formula-application questions (QA_FML_* bank). Persisted.
    const [formulaMode, setFormulaMode] = useState(false);
    const toggleFormula = () => setFormulaMode((prev) => { const next = !prev; AsyncStorage.setItem('quizFormula', next ? '1' : '0').catch(() => { }); return next; });
    const diffTotal = diff.EASY + diff.MEDIUM + diff.HARD;
    const useCustomDiff = quizMode === 'custom' && diffTotal > 0;
    const persistDiff = (next: { EASY: number; MEDIUM: number; HARD: number }) => {
        setDiff(next); AsyncStorage.setItem('quizDiff', JSON.stringify(next)).catch(() => { });
    };
    const setMode = (m: 'auto' | 'custom') => { setQuizMode(m); AsyncStorage.setItem('quizMode', m).catch(() => { }); };
    const toggleDiff = (level: 'EASY' | 'MEDIUM' | 'HARD') => persistDiff({ ...diff, [level]: diff[level] > 0 ? 0 : 5 });
    const setDiffCount = (level: 'EASY' | 'MEDIUM' | 'HARD', t: string) => {
        const n = parseInt(t, 10);
        persistDiff({ ...diff, [level]: isNaN(n) ? 0 : Math.max(0, Math.min(100, n)) });
    };

    useEffect(() => {
        AsyncStorage.multiGet(['quizCount', 'quizMinutes', 'quizMode', 'quizDiff', 'quizFormula']).then(([[, c], [, m], [, mode], [, d], [, f]]) => {
            const cn = parseInt(c || '', 10);
            const mn = parseInt(m || '', 10);
            if (!isNaN(cn) && cn > 0) { setQuizCount(cn); setQuizCountStr(String(cn)); }
            if (!isNaN(mn) && mn > 0) { setQuizMinutes(mn); setQuizMinutesStr(String(mn)); }
            if (mode === 'custom') setQuizMode('custom');
            if (d) { try { const p = JSON.parse(d); setDiff({ EASY: Number(p.EASY) || 0, MEDIUM: Number(p.MEDIUM) || 0, HARD: Number(p.HARD) || 0 }); } catch { } }
            if (f === '1') setFormulaMode(true);
        }).catch(() => { });
    }, []);

    const commitCount = (t: string) => {
        const n = parseInt(t, 10);
        const v = isNaN(n) ? 10 : Math.max(1, Math.min(100, n));
        setQuizCount(v); setQuizCountStr(String(v));
        AsyncStorage.setItem('quizCount', String(v)).catch(() => { });
    };
    const commitMinutes = (t: string) => {
        const n = parseInt(t, 10);
        const v = isNaN(n) ? 5 : Math.max(1, Math.min(180, n));
        setQuizMinutes(v); setQuizMinutesStr(String(v));
        AsyncStorage.setItem('quizMinutes', String(v)).catch(() => { });
    };

    useEffect(() => {
        const fetchData = async () => {
            try {
                const [catRes, weakRes, privateRes] = await Promise.all([
                    QuizAPI.getCategories(),
                    QuizAPI.getWeakTopicQuiz(10),
                    PrivateModuleAPI.listMine().catch(() => ({ data: { modules: [] } })),
                ]);
                setCategories(catRes.data.categories || []);
                setStreak(catRes.data.streak || null);
                setWeakQuiz(weakRes.data || null);
                setPrivateModules(privateRes.data?.modules || []);
            } catch (err) {
                console.error("Failed to fetch quiz data:", err);
            } finally {
                setLoading(false);
            }
        };
        fetchData();
    }, []);

    const getCategoryEmoji = (key: string): string => {
        const map: Record<string, string> = {
            polity: '⚖️', history: '🏛️', geography: '🌍', economics: '📈',
            general_science: '🔬', reasoning: '🧠', quantitative_aptitude: '📐',
            english: '📖', vocabulary: '🔤', computer_knowledge: '💻', current_affairs: '📰',
            general_knowledge: '🎓', physics: '⚡', chemistry: '🧪',
            biology: '🌿', science_technology: '🚀',
        };
        return map[key] || '📚';
    };

    if (loading) {
        return (
            <View style={{ flex: 1, justifyContent: 'center', alignItems: 'center', backgroundColor: '#f9fafb' }}>
                <ActivityIndicator size="large" color={COLORS.primary} />
            </View>
        );
    }

    const hasWeakTopics = (weakQuiz?.weak_topics?.length ?? 0) > 0;

    return (
        <ScrollView style={styles.container}>
            <View style={styles.contentPadAlt}>

                {/* Streak Banner */}
                {streak && (
                    <View style={[styles.card, {
                        backgroundColor: streak.at_risk ? '#ef4444' : streak.current_streak > 0 ? '#f97316' : '#111827',
                        flexDirection: 'row', alignItems: 'center', marginTop: 0
                    }]}>
                        <View style={{
                            width: 50, height: 50, borderRadius: 25,
                            backgroundColor: 'rgba(255,255,255,0.2)',
                            alignItems: 'center', justifyContent: 'center'
                        }}>
                            <Ionicons name="flame" size={28} color="#fff" />
                        </View>
                        <View style={{ flex: 1, marginLeft: 15 }}>
                            <Text style={{ color: '#fff', fontSize: 16, fontWeight: 'bold' }}>{streak.nudge}</Text>
                            <View style={{ flexDirection: 'row', marginTop: 6 }}>
                                <Text style={{ color: 'rgba(255,255,255,0.8)', fontSize: 12 }}>
                                    Current: {streak.current_streak} days
                                </Text>
                                <Text style={{ color: 'rgba(255,255,255,0.8)', fontSize: 12, marginLeft: 15 }}>
                                    Longest: {streak.longest_streak} days
                                </Text>
                            </View>
                        </View>
                    </View>
                )}

                {/* ── PATHWAY 1: Strengthen Weak Topics ── */}
                <TouchableOpacity
                    activeOpacity={hasWeakTopics ? 0.75 : 1}
                    onPress={() => {
                        if (!hasWeakTopics) return;
                        navigation.navigate('QuizSession', {
                            subject: null,
                            title: 'Strengthen Weak Topics',
                            weakTopicMode: true,
                        });
                    }}
                    style={{
                        borderRadius: 16, padding: 16, marginBottom: 20,
                        borderWidth: 1.5,
                        borderColor: hasWeakTopics ? '#fed7aa' : '#e5e7eb',
                        backgroundColor: hasWeakTopics ? '#fff7ed' : '#f9fafb',
                        shadowColor: hasWeakTopics ? '#f97316' : '#000',
                        shadowOpacity: hasWeakTopics ? 0.1 : 0.04,
                        shadowRadius: 6, shadowOffset: { width: 0, height: 2 }, elevation: 2,
                    }}
                >
                    <View style={{ flexDirection: 'row', alignItems: 'center', marginBottom: hasWeakTopics ? 12 : 0 }}>
                        <View style={{
                            width: 44, height: 44, borderRadius: 12,
                            backgroundColor: hasWeakTopics ? '#ffedd5' : '#f3f4f6',
                            alignItems: 'center', justifyContent: 'center', marginRight: 12,
                        }}>
                            <Text style={{ fontSize: 22 }}>🎯</Text>
                        </View>
                        <View style={{ flex: 1 }}>
                            <Text style={{ fontSize: 16, fontWeight: '700', color: hasWeakTopics ? '#111827' : '#9ca3af' }}>
                                Strengthen Weak Topics
                            </Text>
                            <Text style={{ fontSize: 12, color: '#6b7280', marginTop: 2 }}>
                                {hasWeakTopics
                                    ? `${weakQuiz.weak_topics.length} weak area${weakQuiz.weak_topics.length > 1 ? 's' : ''} identified · Tap to start`
                                    : 'Answer a few quizzes to reveal your weak areas'}
                            </Text>
                        </View>
                        <Ionicons
                            name="chevron-forward" size={20}
                            color={hasWeakTopics ? '#f97316' : '#d1d5db'}
                        />
                    </View>

                    {hasWeakTopics && (
                        <View style={{ flexDirection: 'row', flexWrap: 'wrap' }}>
                            {weakQuiz.weak_topics.slice(0, 4).map((wt: any, idx: number) => (
                                <View key={idx} style={{
                                    flexDirection: 'row', alignItems: 'center',
                                    backgroundColor: '#fff', paddingHorizontal: 10, paddingVertical: 5,
                                    borderRadius: 16, borderWidth: 1, borderColor: '#fed7aa',
                                    marginRight: 6, marginBottom: 6,
                                }}>
                                    <View style={{
                                        width: 6, height: 6, borderRadius: 3,
                                        backgroundColor: wt.accuracy < 40 ? '#ef4444' : '#f97316',
                                        marginRight: 5
                                    }} />
                                    <Text style={{ fontSize: 11, fontWeight: '600', color: '#374151' }}>{wt.subject}</Text>
                                    <Text style={{
                                        fontSize: 11, fontWeight: 'bold', marginLeft: 4,
                                        color: wt.accuracy < 40 ? '#dc2626' : '#ea580c'
                                    }}>{wt.accuracy}%</Text>
                                </View>
                            ))}
                        </View>
                    )}
                </TouchableOpacity>

                {/* ── PATHWAY 2: Revise Weak Areas ── */}
                <TouchableOpacity
                    onPress={() => navigation.navigate('QuizSession', {
                        title: 'Revise Weak Areas',
                        wrongPracticeMode: true,
                        limit: 20,
                    })}
                    activeOpacity={0.8}
                    style={{
                        borderRadius: 16, padding: 16, marginBottom: 20,
                        backgroundColor: '#fef2f2', borderWidth: 1.5, borderColor: '#fecaca',
                        flexDirection: 'row', alignItems: 'center',
                        shadowColor: '#dc2626', shadowOpacity: 0.08,
                        shadowRadius: 6, shadowOffset: { width: 0, height: 2 }, elevation: 2,
                    }}
                >
                    <View style={{
                        width: 44, height: 44, borderRadius: 12,
                        backgroundColor: '#fee2e2', alignItems: 'center', justifyContent: 'center', marginRight: 12,
                    }}>
                        <Text style={{ fontSize: 22 }}>📋</Text>
                    </View>
                    <View style={{ flex: 1 }}>
                        <Text style={{ fontSize: 16, fontWeight: '700', color: '#111827' }}>Revise Weak Areas</Text>
                        <Text style={{ fontSize: 12, color: '#6b7280', marginTop: 2 }}>
                            Wrong answers · skipped · bookmarked questions
                        </Text>
                    </View>
                    <Ionicons name="chevron-forward" size={20} color="#dc2626" />
                </TouchableOpacity>

                {/* ── PATHWAY 3: Cover More Ground ── */}
                <Text style={[styles.sectionTitle, { marginBottom: 4 }]}>📚 Cover More Ground</Text>
                <Text style={{ color: '#6b7280', fontSize: 13, marginBottom: 12 }}>
                    Pick a subject — {useCustomDiff
                        ? [diff.EASY && `${diff.EASY} Easy`, diff.MEDIUM && `${diff.MEDIUM} Medium`, diff.HARD && `${diff.HARD} Hard`].filter(Boolean).join(' · ')
                        : `${quizCount} questions`} ({quizMinutes} min) spread across topics.
                </Text>

                {/* Quiz Settings — collapsible: difficulty mix + counts + time. Persisted. */}
                <View style={{ marginBottom: 16 }}>
                    <TouchableOpacity
                        onPress={() => setSettingsOpen((o) => !o)}
                        activeOpacity={0.8}
                        style={{ flexDirection: 'row', alignItems: 'center', justifyContent: 'space-between', backgroundColor: '#fff', borderRadius: 14, borderWidth: 1, borderColor: '#f3f4f6', paddingHorizontal: 14, paddingVertical: 13 }}>
                        <Text style={{ fontWeight: 'bold', color: '#1f2937', fontSize: 14 }}>⚙️  Quiz Settings</Text>
                        <Text style={{ color: '#9ca3af', fontSize: 12, fontWeight: '600' }}>
                            {formulaMode ? <Text style={{ color: '#ea580c' }}>📐 Formula · </Text> : ''}{useCustomDiff ? `${diffTotal} Q · custom` : `${quizCount} Q · balanced`} · {quizMinutes}m  {settingsOpen ? '▲' : '▼'}
                        </Text>
                    </TouchableOpacity>

                    {settingsOpen && (
                        <View style={{ marginTop: 8, backgroundColor: '#fff', borderRadius: 14, borderWidth: 1, borderColor: '#f3f4f6', padding: 14 }}>
                            {/* Mode toggle */}
                            <View style={{ flexDirection: 'row', gap: 8, marginBottom: 14 }}>
                                {(['auto', 'custom'] as const).map((m) => (
                                    <TouchableOpacity key={m} onPress={() => setMode(m)}
                                        style={{ paddingHorizontal: 14, paddingVertical: 8, borderRadius: 10, borderWidth: 1, borderColor: quizMode === m ? '#f97316' : '#e5e7eb', backgroundColor: quizMode === m ? '#f97316' : '#fff' }}>
                                        <Text style={{ fontSize: 13, fontWeight: 'bold', color: quizMode === m ? '#fff' : '#6b7280' }}>{m === 'auto' ? 'Auto-balanced' : 'Choose difficulty'}</Text>
                                    </TouchableOpacity>
                                ))}
                            </View>

                            {quizMode === 'auto' ? (
                                <View>
                                    <Text style={{ fontSize: 11, fontWeight: 'bold', color: '#9ca3af', marginBottom: 4 }}>QUESTIONS</Text>
                                    <TextInput keyboardType="number-pad" value={quizCountStr}
                                        onChangeText={setQuizCountStr} onEndEditing={(e) => commitCount(e.nativeEvent.text)} onBlur={() => commitCount(quizCountStr)}
                                        style={{ width: 80, borderWidth: 1, borderColor: '#e5e7eb', borderRadius: 10, paddingHorizontal: 12, paddingVertical: 8, fontSize: 15, fontWeight: '600', color: '#1f2937' }} />
                                    <Text style={{ fontSize: 11, color: '#9ca3af', marginTop: 8 }}>Auto-balanced to 30% easy · 30% medium · 40% hard.</Text>
                                </View>
                            ) : (
                                <View>
                                    <Text style={{ fontSize: 11, fontWeight: 'bold', color: '#9ca3af', marginBottom: 8 }}>TICK THE LEVELS YOU WANT & SET HOW MANY OF EACH</Text>
                                    {(['EASY', 'MEDIUM', 'HARD'] as const).map((level) => {
                                        const on = diff[level] > 0;
                                        const label = level.charAt(0) + level.slice(1).toLowerCase();
                                        return (
                                            <View key={level} style={{ flexDirection: 'row', alignItems: 'center', gap: 10, marginBottom: 10 }}>
                                                <TouchableOpacity onPress={() => toggleDiff(level)} style={{ flexDirection: 'row', alignItems: 'center', gap: 8, width: 130 }}>
                                                    <View style={{ width: 22, height: 22, borderRadius: 6, borderWidth: 2, borderColor: on ? '#f97316' : '#d1d5db', backgroundColor: on ? '#f97316' : '#fff', alignItems: 'center', justifyContent: 'center' }}>
                                                        {on && <Ionicons name="checkmark" size={15} color="#fff" />}
                                                    </View>
                                                    <Text style={{ fontSize: 14, fontWeight: '600', color: on ? '#1f2937' : '#9ca3af' }}>{label}</Text>
                                                </TouchableOpacity>
                                                <TextInput keyboardType="number-pad" editable={on}
                                                    value={on ? String(diff[level]) : ''} placeholder="0" placeholderTextColor="#d1d5db"
                                                    onChangeText={(t) => setDiffCount(level, t)}
                                                    style={{ width: 70, borderWidth: 1, borderColor: '#e5e7eb', borderRadius: 10, paddingHorizontal: 12, paddingVertical: 8, fontSize: 15, fontWeight: '600', color: on ? '#1f2937' : '#d1d5db', backgroundColor: on ? '#fff' : '#f9fafb' }} />
                                                <Text style={{ fontSize: 12, color: '#9ca3af' }}>questions</Text>
                                            </View>
                                        );
                                    })}
                                    <Text style={{ fontSize: 14, fontWeight: 'bold', color: diffTotal === 0 ? '#ef4444' : '#374151', marginTop: 4 }}>
                                        {diffTotal === 0 ? 'Select at least one level to start' : `Total: ${diffTotal} question${diffTotal === 1 ? '' : 's'}`}
                                    </Text>
                                </View>
                            )}

                            {/* Formula-practice mode — both modes; draws only formula-application questions (Quant) */}
                            <View style={{ marginTop: 14, paddingTop: 12, borderTopWidth: 1, borderTopColor: '#f3f4f6' }}>
                                <TouchableOpacity onPress={toggleFormula} style={{ flexDirection: 'row', alignItems: 'center', gap: 8 }}>
                                    <View style={{ width: 22, height: 22, borderRadius: 6, borderWidth: 2, borderColor: formulaMode ? '#f97316' : '#d1d5db', backgroundColor: formulaMode ? '#f97316' : '#fff', alignItems: 'center', justifyContent: 'center' }}>
                                        {formulaMode && <Ionicons name="checkmark" size={15} color="#fff" />}
                                    </View>
                                    <Text style={{ fontSize: 14, fontWeight: 'bold', color: '#1f2937' }}>📐 Formula-based questions only</Text>
                                </TouchableOpacity>
                                <Text style={{ fontSize: 11, color: '#9ca3af', marginTop: 6 }}>Practise direct formula-application questions so you never lose the easy marks. Available for Quantitative Aptitude.</Text>
                            </View>

                            {/* Time — both modes */}
                            <View style={{ marginTop: 14, paddingTop: 12, borderTopWidth: 1, borderTopColor: '#f3f4f6' }}>
                                <Text style={{ fontSize: 11, fontWeight: 'bold', color: '#9ca3af', marginBottom: 4 }}>TIME (MIN)</Text>
                                <TextInput keyboardType="number-pad" value={quizMinutesStr}
                                    onChangeText={setQuizMinutesStr} onEndEditing={(e) => commitMinutes(e.nativeEvent.text)} onBlur={() => commitMinutes(quizMinutesStr)}
                                    style={{ width: 80, borderWidth: 1, borderColor: '#e5e7eb', borderRadius: 10, paddingHorizontal: 12, paddingVertical: 8, fontSize: 15, fontWeight: '600', color: '#1f2937' }} />
                            </View>

                            <TouchableOpacity
                                onPress={() => { setMode('auto'); commitCount('10'); commitMinutes('5'); persistDiff({ EASY: 0, MEDIUM: 0, HARD: 0 }); setFormulaMode(false); AsyncStorage.setItem('quizFormula', '0').catch(() => { }); }}
                                style={{ marginTop: 14, alignSelf: 'flex-start', paddingHorizontal: 12, paddingVertical: 9, borderRadius: 10, borderWidth: 1, borderColor: '#e5e7eb', backgroundColor: '#fff' }}>
                                <Text style={{ fontSize: 12, fontWeight: 'bold', color: '#6b7280' }}>Reset to default</Text>
                            </TouchableOpacity>
                        </View>
                    )}
                </View>

                <View style={{ flexDirection: 'row', flexWrap: 'wrap', gap: 12 }}>
                    {categories.map((cat: any, idx: number) => (
                        <TouchableOpacity
                            key={idx}
                            disabled={!cat.has_questions}
                            onPress={() => navigation.navigate('QuizSession', { subject: cat.key, title: cat.name, limit: quizCount, durationSecs: quizMinutes * 60, diffCounts: useCustomDiff ? diff : undefined, formula: formulaMode })}
                            activeOpacity={0.75}
                            style={{
                                width: '47%',
                                backgroundColor: cat.has_questions ? '#fff' : '#f3f4f6',
                                borderRadius: 16, padding: 16,
                                borderWidth: 1, borderColor: '#f3f4f6',
                                opacity: cat.has_questions ? 1 : 0.5,
                                shadowColor: '#000', shadowOpacity: 0.05,
                                shadowRadius: 4, shadowOffset: { width: 0, height: 1 }, elevation: 1,
                            }}
                        >
                            <Text style={{ fontSize: 28, marginBottom: 8 }}>{getCategoryEmoji(cat.key)}</Text>
                            <Text style={{ fontSize: 15, fontWeight: 'bold', color: '#1f2937' }}>{cat.name}</Text>
                            <Text style={{ fontSize: 12, color: '#9ca3af', marginTop: 2 }}>
                                {cat.question_count > 0 ? `${cat.question_count} questions` : 'Coming soon'}
                            </Text>
                        </TouchableOpacity>
                    ))}
                </View>

                {/* Private Modules */}
                {privateModules.length > 0 && (
                    <View style={{ marginTop: 24 }}>
                        <Text style={[styles.sectionTitle, { marginBottom: 4 }]}>🔐 Special Practice</Text>
                        <Text style={{ color: '#6b7280', fontSize: 13, marginBottom: 12 }}>
                            Exclusive question banks you have been granted access to.
                        </Text>
                        {privateModules.map((mod: any, idx: number) => (
                            <TouchableOpacity
                                key={idx}
                                onPress={() => navigation.navigate('PrivateModule', { slug: mod.slug, moduleName: mod.name })}
                                activeOpacity={0.85}
                                style={{
                                    backgroundColor: '#111827', borderRadius: 16, padding: 16, marginBottom: 10,
                                    flexDirection: 'row', alignItems: 'center',
                                    shadowColor: '#000', shadowOpacity: 0.12, shadowRadius: 8,
                                    shadowOffset: { width: 0, height: 3 }, elevation: 4,
                                }}
                            >
                                <View style={{ backgroundColor: '#f97316', borderRadius: 10, padding: 8, marginRight: 12 }}>
                                    <Ionicons name="briefcase" size={20} color="#fff" />
                                </View>
                                <View style={{ flex: 1 }}>
                                    <Text style={{ fontSize: 15, fontWeight: '700', color: '#fff' }}>{mod.name}</Text>
                                    {mod.description ? (
                                        <Text style={{ fontSize: 12, color: '#9ca3af', marginTop: 2 }} numberOfLines={1}>
                                            {mod.description}
                                        </Text>
                                    ) : null}
                                </View>
                                <Ionicons name="chevron-forward" size={18} color="#9ca3af" />
                            </TouchableOpacity>
                        ))}
                    </View>
                )}

                <View style={{ height: 20 }} />
            </View>
        </ScrollView>
    );
}
