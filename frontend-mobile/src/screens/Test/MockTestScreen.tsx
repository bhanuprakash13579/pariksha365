import React, { useState, useEffect, useCallback, useRef } from 'react';
import {
    View, Text, ScrollView, TouchableOpacity, Alert, ActivityIndicator,
    Modal, SafeAreaView, Dimensions, BackHandler, Image, AppState
} from 'react-native';
import { Ionicons } from '@expo/vector-icons';
import AsyncStorage from '@react-native-async-storage/async-storage';
import { AttemptAPI, api } from '../../services/api';
import { COLORS } from '../../styles/theme';

const { width: SCREEN_WIDTH } = Dimensions.get('window');

interface QuestionOption { option_text: string; is_correct?: boolean; }
interface Question { id: string; question_text: string; image_url?: string; options: QuestionOption[]; }
interface Section { id: string; name: string; marks_per_question: number; questions: Question[]; }

const TIMER_KEY = 'p365_timer';
const VISITED_KEY = 'p365_visited';

export default function MockTestScreen({ navigation, route }: any) {
    const { testSeriesId, testTitle: initialTitle } = route.params;

    const [sections, setSections] = useState<Section[]>([]);
    const [currentSectionIdx, setCurrentSectionIdx] = useState(0);
    const [currentQuestionIdx, setCurrentQuestionIdx] = useState(0);
    const [answers, setAnswers] = useState<Record<string, number | null>>({});
    const [markedForReview, setMarkedForReview] = useState<Set<string>>(new Set());
    const [visitedQuestions, setVisitedQuestions] = useState<Set<string>>(new Set());
    const [attemptId, setAttemptId] = useState<string | null>(null);
    const [loading, setLoading] = useState(true);
    const [submitting, setSubmitting] = useState(false);
    const [timeLeft, setTimeLeft] = useState(0);
    const [testTitle, setTestTitle] = useState(initialTitle || 'Mock Test');
    const [negMarking, setNegMarking] = useState(0.25);
    const [isPaused, setIsPaused] = useState(false);
    const [showPalette, setShowPalette] = useState(false);
    const [showSubmitModal, setShowSubmitModal] = useState(false);

    const timeLeftRef = useRef(0);
    const timerRef = useRef<ReturnType<typeof setInterval> | null>(null);
    const attemptIdRef = useRef<string | null>(null);

    // -- Timer Helpers --
    const saveTimerState = async (aid: string, startTime: number, total: number) => {
        try { await AsyncStorage.setItem(TIMER_KEY, JSON.stringify({ attemptId: aid, startTime, totalSeconds: total })); } catch { }
    };
    const loadTimerState = async (aid: string) => {
        try {
            const raw = await AsyncStorage.getItem(TIMER_KEY);
            if (!raw) return null;
            const data = JSON.parse(raw);
            return data.attemptId === aid ? data : null;
        } catch { return null; }
    };
    const clearTimerState = async () => {
        try { await AsyncStorage.multiRemove([TIMER_KEY, VISITED_KEY]); } catch { }
    };

    // -- Question Status --
    const getQuestionStatus = useCallback((qId: string): string => {
        const isAnswered = answers[qId] !== undefined && answers[qId] !== null;
        const isMarked = markedForReview.has(qId);
        const isVisited = visitedQuestions.has(qId);
        if (isAnswered && isMarked) return 'answered-marked';
        if (isMarked) return 'marked';
        if (isAnswered) return 'answered';
        if (isVisited) return 'not-answered';
        return 'not-visited';
    }, [answers, markedForReview, visitedQuestions]);

    const getStats = useCallback(() => {
        let answered = 0, notAnswered = 0, marked = 0, notVisited = 0;
        sections.forEach(s => s.questions?.forEach(q => {
            const status = getQuestionStatus(q.id);
            if (status === 'answered' || status === 'answered-marked') answered++;
            else if (status === 'not-answered') notAnswered++;
            if (status === 'marked' || status === 'answered-marked') marked++;
            if (status === 'not-visited') notVisited++;
        }));
        return { answered, notAnswered, marked, notVisited };
    }, [sections, getQuestionStatus]);

    const totalQuestions = sections.reduce((sum, s) => sum + (s.questions?.length || 0), 0);

    const getFlatIndex = (sIdx: number, qIdx: number) => {
        let flat = 0;
        for (let i = 0; i < sIdx; i++) flat += sections[i].questions?.length || 0;
        return flat + qIdx;
    };

    const formatTime = (secs: number) => {
        const h = Math.floor(secs / 3600);
        const m = Math.floor((secs % 3600) / 60);
        const s = secs % 60;
        if (h > 0) return `${h.toString().padStart(2, '0')}:${m.toString().padStart(2, '0')}:${s.toString().padStart(2, '0')}`;
        return `${m.toString().padStart(2, '0')}:${s.toString().padStart(2, '0')}`;
    };

    // STATUS COLORS (React Native style)
    const statusColorMap: Record<string, { bg: string; text: string; border: string }> = {
        'not-visited': { bg: '#e5e7eb', text: '#4b5563', border: '#d1d5db' },
        'not-answered': { bg: '#ef4444', text: '#ffffff', border: '#dc2626' },
        'answered': { bg: '#22c55e', text: '#ffffff', border: '#16a34a' },
        'marked': { bg: '#a855f7', text: '#ffffff', border: '#9333ea' },
        'answered-marked': { bg: '#22c55e', text: '#ffffff', border: '#9333ea' },
    };

    // -- Submit --
    const handleSubmit = useCallback(async (autoSubmit = false) => {
        const aid = attemptIdRef.current;
        if (!aid || submitting) return;
        setSubmitting(true);
        try {
            await AttemptAPI.submit(aid);
            await clearTimerState();
            if (timerRef.current) clearInterval(timerRef.current);
            navigation.replace('PostTestResults', { attemptId: aid });
        } catch (err) {
            console.error("Failed to submit:", err);
            Alert.alert("Submission Failed", "Please try again.");
        } finally {
            setSubmitting(false);
        }
    }, [submitting, navigation]);

    // -- Initialize --
    useEffect(() => {
        const init = async () => {
            try {
                const attemptRes = await AttemptAPI.start(testSeriesId);
                const aid = attemptRes.data.id;
                setAttemptId(aid);
                attemptIdRef.current = aid;

                // Load test data
                const cdnUrl = attemptRes.data.test_series?.cdn_url;
                let testData;
                if (cdnUrl) {
                    try {
                        const cdnRes = await fetch(cdnUrl);
                        testData = await cdnRes.json();
                    } catch {
                        const fallbackRes = await api.get(`/tests/${testSeriesId}`);
                        testData = fallbackRes.data;
                    }
                } else {
                    const testRes = await api.get(`/tests/${testSeriesId}`);
                    testData = testRes.data;
                }

                setTestTitle(testData.title || 'Mock Test');
                setNegMarking(testData.negative_marking || 0.25);
                const durationSecs = (testData.sections?.reduce((sum: number, s: any) => sum + (s.time_limit_minutes || 0), 0) || 60) * 60;
                setSections(testData.sections || []);

                // Restore previous answers
                try {
                    const answersRes = await AttemptAPI.getAnswers(aid);
                    if (answersRes.data?.length > 0) {
                        const restored: Record<string, number | null> = {};
                        const restoredVisited = new Set<string>();
                        answersRes.data.forEach((a: any) => {
                            restored[a.question_id] = a.selected_option_index ?? null;
                            restoredVisited.add(a.question_id);
                        });
                        setAnswers(restored);
                        setVisitedQuestions(prev => new Set([...prev, ...restoredVisited]));
                    }
                } catch { }

                // Timer
                const saved = await loadTimerState(aid);
                if (saved) {
                    const elapsed = (Date.now() - saved.startTime) / 1000;
                    const remaining = Math.max(0, Math.floor(saved.totalSeconds - elapsed));
                    setTimeLeft(remaining);
                    timeLeftRef.current = remaining;
                } else {
                    setTimeLeft(durationSecs);
                    timeLeftRef.current = durationSecs;
                    await saveTimerState(aid, Date.now(), durationSecs);
                }

                // Visited questions from storage
                try {
                    const visitedRaw = await AsyncStorage.getItem(VISITED_KEY);
                    if (visitedRaw) setVisitedQuestions(prev => new Set([...prev, ...JSON.parse(visitedRaw)]));
                } catch { }
            } catch (err) {
                console.error("Failed to load test:", err);
                Alert.alert("Error", "Failed to load test. Please try again.");
                navigation.goBack();
            } finally {
                setLoading(false);
            }
        };
        init();
    }, [testSeriesId]);

    // -- Timer countdown --
    useEffect(() => {
        if (timeLeftRef.current <= 0 || !attemptId || isPaused) return;
        timerRef.current = setInterval(() => {
            timeLeftRef.current -= 1;
            setTimeLeft(timeLeftRef.current);
            if (timeLeftRef.current <= 0) {
                if (timerRef.current) clearInterval(timerRef.current);
                handleSubmit(true);
            }
        }, 1000);
        return () => { if (timerRef.current) clearInterval(timerRef.current); };
    }, [attemptId, isPaused, handleSubmit]);

    // -- Mark question visited --
    useEffect(() => {
        const q = sections[currentSectionIdx]?.questions?.[currentQuestionIdx];
        if (q && !visitedQuestions.has(q.id)) {
            setVisitedQuestions(prev => {
                const next = new Set(prev);
                next.add(q.id);
                AsyncStorage.setItem(VISITED_KEY, JSON.stringify([...next])).catch(() => { });
                return next;
            });
        }
    }, [currentSectionIdx, currentQuestionIdx, sections]);

    // -- Handle back press --
    useEffect(() => {
        const backAction = () => {
            Alert.alert("Leave Test?", "Your progress is saved. You can resume later.", [
                { text: "Cancel", style: "cancel" },
                { text: "Leave", style: "destructive", onPress: () => navigation.goBack() }
            ]);
            return true;
        };
        const backHandler = BackHandler.addEventListener('hardwareBackPress', backAction);
        return () => backHandler.remove();
    }, [navigation]);

    // -- Handle app background (auto-pause) --
    useEffect(() => {
        const subscription = AppState.addEventListener('change', (nextAppState) => {
            if (nextAppState === 'background' && !isPaused && !submitting) {
                setIsPaused(true);
            }
        });
        return () => subscription.remove();
    }, [isPaused, submitting]);

    // -- Select Option + Save --
    const selectOption = async (optionIndex: number) => {
        const q = sections[currentSectionIdx]?.questions?.[currentQuestionIdx];
        if (!q || !attemptId) return;
        setAnswers(prev => ({ ...prev, [q.id]: optionIndex }));
        try {
            await AttemptAPI.saveAnswer(attemptId, {
                question_id: q.id,
                selected_option_index: optionIndex,
            });
        } catch (err) { console.error("Failed to save answer:", err); }
    };

    const clearSelection = () => {
        const q = sections[currentSectionIdx]?.questions?.[currentQuestionIdx];
        if (q) setAnswers(prev => ({ ...prev, [q.id]: null }));
    };

    const toggleMark = () => {
        const q = sections[currentSectionIdx]?.questions?.[currentQuestionIdx];
        if (!q) return;
        setMarkedForReview(prev => {
            const next = new Set(prev);
            if (next.has(q.id)) next.delete(q.id); else next.add(q.id);
            return next;
        });
    };

    const goNext = () => {
        const section = sections[currentSectionIdx];
        if (!section) return;
        if (currentQuestionIdx < (section.questions?.length || 0) - 1) {
            setCurrentQuestionIdx(prev => prev + 1);
        } else if (currentSectionIdx < sections.length - 1) {
            setCurrentSectionIdx(prev => prev + 1);
            setCurrentQuestionIdx(0);
        }
    };

    const goPrev = () => {
        if (currentQuestionIdx === 0 && currentSectionIdx === 0) return;
        if (currentQuestionIdx > 0) {
            setCurrentQuestionIdx(prev => prev - 1);
        } else if (currentSectionIdx > 0) {
            setCurrentSectionIdx(prev => prev - 1);
            const prevSection = sections[currentSectionIdx - 1];
            setCurrentQuestionIdx((prevSection.questions?.length || 1) - 1);
        }
    };

    const jumpToQuestion = (sIdx: number, qIdx: number) => {
        setCurrentSectionIdx(sIdx);
        setCurrentQuestionIdx(qIdx);
        setShowPalette(false);
    };

    // -- Resume from pause --
    const handleResume = () => {
        setIsPaused(false);
    };

    // -- LOADING --
    if (loading) {
        return (
            <View style={{ flex: 1, backgroundColor: '#f3f4f6', justifyContent: 'center', alignItems: 'center' }}>
                <ActivityIndicator size="large" color={COLORS.primary} />
                <Text style={{ color: '#6b7280', marginTop: 12, fontWeight: '500' }}>Loading test...</Text>
            </View>
        );
    }

    const currentSection = sections[currentSectionIdx];
    const currentQuestion = currentSection?.questions?.[currentQuestionIdx];
    const stats = getStats();
    const isTimeLow = timeLeft < 300;

    // =================== RENDER ===================
    return (
        <SafeAreaView style={{ flex: 1, backgroundColor: '#f3f4f6' }}>
            {/* ─── HEADER ─── */}
            <View style={{ backgroundColor: '#1e293b' }}>
                {/* Top bar */}
                <View style={{ flexDirection: 'row', alignItems: 'center', justifyContent: 'space-between', paddingHorizontal: 12, paddingVertical: 10 }}>
                    {/* Left: Back + Title */}
                    <View style={{ flexDirection: 'row', alignItems: 'center', flex: 1 }}>
                        <TouchableOpacity
                            onPress={() => Alert.alert("Leave Test?", "Your progress is saved.", [
                                { text: "Cancel", style: "cancel" },
                                { text: "Leave", style: "destructive", onPress: () => navigation.goBack() }
                            ])}
                            style={{ padding: 6 }}
                        >
                            <Ionicons name="arrow-back" size={20} color="#d1d5db" />
                        </TouchableOpacity>
                        <View style={{ marginLeft: 8, flex: 1 }}>
                            <Text style={{ color: '#fff', fontSize: 13, fontWeight: 'bold' }} numberOfLines={1}>{testTitle}</Text>
                            <Text style={{ color: '#9ca3af', fontSize: 10 }}>
                                {currentSection?.name} • Q{getFlatIndex(currentSectionIdx, currentQuestionIdx) + 1} of {totalQuestions}
                            </Text>
                        </View>
                    </View>

                    {/* Center: Timer */}
                    <View style={{
                        flexDirection: 'row', alignItems: 'center',
                        backgroundColor: isTimeLow ? 'rgba(239,68,68,0.8)' : '#334155',
                        paddingHorizontal: 12, paddingVertical: 6, borderRadius: 8, marginHorizontal: 8,
                    }}>
                        <Ionicons name="time-outline" size={14} color={isTimeLow ? '#fecaca' : '#fff'} />
                        <Text style={{
                            color: isTimeLow ? '#fecaca' : '#fff',
                            fontWeight: '900', fontSize: 15, marginLeft: 4, fontVariant: ['tabular-nums'],
                        }}>
                            {formatTime(timeLeft)}
                        </Text>
                    </View>

                    {/* Right: Palette + Pause */}
                    <View style={{ flexDirection: 'row', alignItems: 'center', gap: 6 }}>
                        <TouchableOpacity
                            onPress={() => setShowPalette(true)}
                            style={{ backgroundColor: '#334155', padding: 8, borderRadius: 8 }}
                        >
                            <Ionicons name="grid-outline" size={18} color="#fff" />
                        </TouchableOpacity>
                        <TouchableOpacity
                            onPress={() => setIsPaused(true)}
                            style={{ backgroundColor: '#334155', padding: 8, borderRadius: 8 }}
                        >
                            <Ionicons name="pause" size={18} color="#fff" />
                        </TouchableOpacity>
                    </View>
                </View>

                {/* Section Tabs */}
                <ScrollView horizontal showsHorizontalScrollIndicator={false} style={{ borderTopWidth: 1, borderTopColor: '#374151' }}>
                    {sections.map((section, idx) => (
                        <TouchableOpacity
                            key={section.id}
                            onPress={() => { setCurrentSectionIdx(idx); setCurrentQuestionIdx(0); }}
                            style={{
                                paddingHorizontal: 16, paddingVertical: 10,
                                borderBottomWidth: 2,
                                borderBottomColor: idx === currentSectionIdx ? COLORS.primary : 'transparent',
                            }}
                        >
                            <Text style={{
                                color: idx === currentSectionIdx ? COLORS.primary : '#9ca3af',
                                fontWeight: 'bold', fontSize: 11, textTransform: 'uppercase', letterSpacing: 0.5,
                            }}>
                                {section.name}
                            </Text>
                        </TouchableOpacity>
                    ))}
                </ScrollView>
            </View>

            {/* ─── QUESTION AREA ─── */}
            <ScrollView style={{ flex: 1 }} contentContainerStyle={{ paddingBottom: 80 }}>
                {currentQuestion && (
                    <>
                        {/* Question meta bar */}
                        <View style={{
                            flexDirection: 'row', justifyContent: 'space-between', alignItems: 'center',
                            paddingHorizontal: 16, paddingVertical: 10, backgroundColor: '#fff', borderBottomWidth: 1, borderBottomColor: '#e5e7eb',
                        }}>
                            <View style={{ flexDirection: 'row', alignItems: 'center' }}>
                                <View style={{ backgroundColor: '#fff7ed', paddingHorizontal: 8, paddingVertical: 4, borderRadius: 8 }}>
                                    <Text style={{ color: '#c2410c', fontWeight: '900', fontSize: 13 }}>
                                        Q.{getFlatIndex(currentSectionIdx, currentQuestionIdx) + 1}
                                    </Text>
                                </View>
                                <Text style={{ color: '#6b7280', fontWeight: '500', fontSize: 12, marginLeft: 8 }}>{currentSection?.name}</Text>
                            </View>
                            <View style={{ flexDirection: 'row', alignItems: 'center', gap: 6 }}>
                                <View style={{ backgroundColor: '#f0fdf4', paddingHorizontal: 6, paddingVertical: 3, borderRadius: 4 }}>
                                    <Text style={{ color: '#16a34a', fontWeight: 'bold', fontSize: 11 }}>+{currentSection?.marks_per_question || 1}</Text>
                                </View>
                                <View style={{ backgroundColor: '#fef2f2', paddingHorizontal: 6, paddingVertical: 3, borderRadius: 4 }}>
                                    <Text style={{ color: '#ef4444', fontWeight: 'bold', fontSize: 11 }}>-{negMarking}</Text>
                                </View>
                            </View>
                        </View>

                        {/* Question body */}
                        <View style={{ backgroundColor: '#fff', paddingHorizontal: 16, paddingVertical: 20 }}>
                            <Text style={{ fontSize: 15, fontWeight: '500', color: '#111827', lineHeight: 24, marginBottom: 16 }}>
                                {currentQuestion.question_text.replace(/\*\*(.*?)\*\*/g, '$1')}
                            </Text>

                            {currentQuestion.image_url ? (
                                <Image
                                    source={{ uri: currentQuestion.image_url }}
                                    style={{ width: '100%', height: 200, borderRadius: 12, marginBottom: 16 }}
                                    resizeMode="contain"
                                />
                            ) : null}

                            {/* Options */}
                            {currentQuestion.options.map((opt, i) => {
                                const isSelected = answers[currentQuestion.id] === i;
                                return (
                                    <TouchableOpacity
                                        key={i}
                                        onPress={() => selectOption(i)}
                                        activeOpacity={0.7}
                                        style={{
                                            flexDirection: 'row', alignItems: 'center',
                                            padding: 14, borderRadius: 12, marginBottom: 10,
                                            borderWidth: 2,
                                            borderColor: isSelected ? COLORS.primary : '#e5e7eb',
                                            backgroundColor: isSelected ? '#fff7ed' : '#fff',
                                        }}
                                    >
                                        <View style={{
                                            width: 22, height: 22, borderRadius: 11,
                                            borderWidth: 2, borderColor: isSelected ? COLORS.primary : '#d1d5db',
                                            backgroundColor: isSelected ? COLORS.primary : '#fff',
                                            alignItems: 'center', justifyContent: 'center', marginRight: 12,
                                        }}>
                                            {isSelected && <View style={{ width: 8, height: 8, borderRadius: 4, backgroundColor: '#fff' }} />}
                                        </View>
                                        <Text style={{ fontSize: 14, fontWeight: isSelected ? '600' : '400', color: isSelected ? '#9a3412' : '#374151', flex: 1 }}>
                                            <Text style={{ fontWeight: 'bold', color: '#9ca3af' }}>{String.fromCharCode(65 + i)}. </Text>
                                            {opt.option_text}
                                        </Text>
                                    </TouchableOpacity>
                                );
                            })}
                        </View>
                    </>
                )}
            </ScrollView>

            {/* ─── BOTTOM BAR ─── */}
            <View style={{
                flexDirection: 'row', paddingHorizontal: 8, paddingVertical: 8, paddingBottom: 20,
                backgroundColor: '#fff', borderTopWidth: 1, borderTopColor: '#e5e7eb',
                shadowColor: '#000', shadowOpacity: 0.08, shadowRadius: 12, shadowOffset: { width: 0, height: -3 }, elevation: 10,
            }}>
                <TouchableOpacity onPress={goPrev} style={{
                    flex: 1, flexDirection: 'row', alignItems: 'center', justifyContent: 'center',
                    paddingVertical: 10, backgroundColor: '#f3f4f6', borderRadius: 10, marginRight: 4,
                    borderWidth: 1, borderColor: '#e5e7eb',
                }}>
                    <Ionicons name="chevron-back" size={16} color="#4b5563" />
                    <Text style={{ color: '#4b5563', fontWeight: 'bold', fontSize: 12, marginLeft: 2 }}>Prev</Text>
                </TouchableOpacity>
                <TouchableOpacity onPress={clearSelection} style={{
                    flex: 1, alignItems: 'center', justifyContent: 'center',
                    paddingVertical: 10, backgroundColor: '#f3f4f6', borderRadius: 10, marginHorizontal: 4,
                    borderWidth: 1, borderColor: '#e5e7eb',
                }}>
                    <Text style={{ color: '#4b5563', fontWeight: 'bold', fontSize: 12 }}>Clear</Text>
                </TouchableOpacity>
                <TouchableOpacity onPress={toggleMark} style={{
                    flex: 1, alignItems: 'center', justifyContent: 'center',
                    paddingVertical: 10, borderRadius: 10, marginHorizontal: 4,
                    backgroundColor: currentQuestion && markedForReview.has(currentQuestion.id) ? '#f3e8ff' : '#faf5ff',
                    borderWidth: 1, borderColor: currentQuestion && markedForReview.has(currentQuestion.id) ? '#c084fc' : '#e9d5ff',
                }}>
                    <Text style={{ color: '#7c3aed', fontWeight: 'bold', fontSize: 12 }}>
                        {currentQuestion && markedForReview.has(currentQuestion.id) ? '★ Mark' : '☆ Mark'}
                    </Text>
                </TouchableOpacity>
                <TouchableOpacity onPress={goNext} style={{
                    flex: 2, flexDirection: 'row', alignItems: 'center', justifyContent: 'center',
                    paddingVertical: 10, backgroundColor: COLORS.primary, borderRadius: 10, marginLeft: 4,
                    shadowColor: COLORS.primary, shadowOpacity: 0.3, shadowRadius: 6, shadowOffset: { width: 0, height: 3 }, elevation: 5,
                }}>
                    <Text style={{ color: '#fff', fontWeight: 'bold', fontSize: 12 }}>Save & Next</Text>
                    <Ionicons name="chevron-forward" size={16} color="#fff" style={{ marginLeft: 2 }} />
                </TouchableOpacity>
            </View>

            {/* ─── QUESTION PALETTE MODAL ─── */}
            <Modal visible={showPalette} animationType="slide" transparent>
                <View style={{ flex: 1, backgroundColor: 'rgba(0,0,0,0.5)', justifyContent: 'flex-end' }}>
                    <View style={{ backgroundColor: '#fff', borderTopLeftRadius: 20, borderTopRightRadius: 20, maxHeight: '75%' }}>
                        {/* Header */}
                        <View style={{ flexDirection: 'row', justifyContent: 'space-between', alignItems: 'center', padding: 16, borderBottomWidth: 1, borderBottomColor: '#e5e7eb' }}>
                            <Text style={{ fontSize: 17, fontWeight: 'bold', color: '#111827' }}>Question Palette</Text>
                            <TouchableOpacity onPress={() => setShowPalette(false)}>
                                <Ionicons name="close" size={24} color="#6b7280" />
                            </TouchableOpacity>
                        </View>

                        {/* Legend */}
                        <View style={{ flexDirection: 'row', flexWrap: 'wrap', padding: 12, gap: 8, backgroundColor: '#f9fafb', borderBottomWidth: 1, borderBottomColor: '#e5e7eb' }}>
                            {[
                                { color: '#22c55e', label: `Answered (${stats.answered})` },
                                { color: '#ef4444', label: `Not Answered (${stats.notAnswered})` },
                                { color: '#a855f7', label: `Marked (${stats.marked})` },
                                { color: '#e5e7eb', label: `Not Visited (${stats.notVisited})`, textColor: '#4b5563' },
                            ].map((item, idx) => (
                                <View key={idx} style={{ flexDirection: 'row', alignItems: 'center', width: '48%' }}>
                                    <View style={{ width: 14, height: 14, borderRadius: 3, backgroundColor: item.color, marginRight: 6 }} />
                                    <Text style={{ fontSize: 10, fontWeight: '600', color: '#6b7280' }}>{item.label}</Text>
                                </View>
                            ))}
                        </View>

                        {/* Grid */}
                        <ScrollView contentContainerStyle={{ padding: 16 }}>
                            {sections.map((sec, sIdx) => (
                                <View key={sec.id} style={{ marginBottom: 16 }}>
                                    <Text style={{ fontSize: 10, fontWeight: 'bold', color: '#9ca3af', textTransform: 'uppercase', letterSpacing: 1, marginBottom: 8 }}>{sec.name}</Text>
                                    <View style={{ flexDirection: 'row', flexWrap: 'wrap', gap: 6 }}>
                                        {sec.questions?.map((q, qIdx) => {
                                            const status = getQuestionStatus(q.id);
                                            const colors = statusColorMap[status];
                                            const isCurrent = sIdx === currentSectionIdx && qIdx === currentQuestionIdx;
                                            return (
                                                <TouchableOpacity
                                                    key={q.id}
                                                    onPress={() => jumpToQuestion(sIdx, qIdx)}
                                                    style={{
                                                        width: 36, height: 36, borderRadius: 6,
                                                        backgroundColor: colors.bg,
                                                        borderWidth: isCurrent ? 2 : 1,
                                                        borderColor: isCurrent ? COLORS.primary : colors.border,
                                                        alignItems: 'center', justifyContent: 'center',
                                                    }}
                                                >
                                                    <Text style={{ color: colors.text, fontWeight: 'bold', fontSize: 11 }}>
                                                        {getFlatIndex(sIdx, qIdx) + 1}
                                                    </Text>
                                                </TouchableOpacity>
                                            );
                                        })}
                                    </View>
                                </View>
                            ))}
                        </ScrollView>

                        {/* Submit */}
                        <View style={{ padding: 16, borderTopWidth: 1, borderTopColor: '#e5e7eb' }}>
                            <TouchableOpacity
                                onPress={() => { setShowPalette(false); setShowSubmitModal(true); }}
                                style={{
                                    backgroundColor: '#dc2626', borderRadius: 12, paddingVertical: 14, alignItems: 'center',
                                }}
                            >
                                <Text style={{ color: '#fff', fontWeight: 'bold', fontSize: 15 }}>Submit Test</Text>
                            </TouchableOpacity>
                        </View>
                    </View>
                </View>
            </Modal>

            {/* ─── SUBMIT CONFIRMATION MODAL ─── */}
            <Modal visible={showSubmitModal} transparent animationType="fade">
                <View style={{ flex: 1, backgroundColor: 'rgba(0,0,0,0.6)', justifyContent: 'center', alignItems: 'center', padding: 20 }}>
                    <View style={{ backgroundColor: '#fff', borderRadius: 20, padding: 24, width: '100%', maxWidth: 350 }}>
                        <Text style={{ fontSize: 20, fontWeight: '800', color: '#111827', textAlign: 'center', marginBottom: 6 }}>Submit Test?</Text>
                        <Text style={{ fontSize: 13, color: '#6b7280', textAlign: 'center', marginBottom: 20 }}>
                            You cannot change answers after submission.
                        </Text>

                        <View style={{ flexDirection: 'row', justifyContent: 'space-between', marginBottom: 20 }}>
                            {[
                                { label: 'Answered', value: stats.answered, color: '#22c55e' },
                                { label: 'Unanswered', value: stats.notAnswered + stats.notVisited, color: '#ef4444' },
                                { label: 'Marked', value: stats.marked, color: '#a855f7' },
                            ].map((item, idx) => (
                                <View key={idx} style={{ alignItems: 'center', flex: 1 }}>
                                    <Text style={{ fontSize: 24, fontWeight: '900', color: item.color }}>{item.value}</Text>
                                    <Text style={{ fontSize: 10, fontWeight: '600', color: '#9ca3af', marginTop: 2 }}>{item.label}</Text>
                                </View>
                            ))}
                        </View>

                        <TouchableOpacity
                            onPress={() => { setShowSubmitModal(false); handleSubmit(); }}
                            disabled={submitting}
                            style={{
                                backgroundColor: '#dc2626', borderRadius: 12, paddingVertical: 14, alignItems: 'center', marginBottom: 10,
                            }}
                        >
                            {submitting ? <ActivityIndicator color="#fff" /> :
                                <Text style={{ color: '#fff', fontWeight: 'bold', fontSize: 15 }}>Confirm Submit</Text>}
                        </TouchableOpacity>
                        <TouchableOpacity
                            onPress={() => setShowSubmitModal(false)}
                            style={{ borderRadius: 12, paddingVertical: 14, alignItems: 'center', backgroundColor: '#f3f4f6' }}
                        >
                            <Text style={{ color: '#374151', fontWeight: '600', fontSize: 14 }}>Go Back</Text>
                        </TouchableOpacity>
                    </View>
                </View>
            </Modal>

            {/* ─── PAUSE OVERLAY ─── */}
            <Modal visible={isPaused} transparent animationType="fade">
                <View style={{ flex: 1, backgroundColor: 'rgba(15,23,42,0.9)', justifyContent: 'center', alignItems: 'center', padding: 20 }}>
                    <View style={{ backgroundColor: '#fff', borderRadius: 20, padding: 28, width: '100%', maxWidth: 340, alignItems: 'center' }}>
                        <View style={{
                            width: 56, height: 56, borderRadius: 28, backgroundColor: '#fff7ed',
                            alignItems: 'center', justifyContent: 'center', marginBottom: 16,
                        }}>
                            <Ionicons name="pause" size={28} color={COLORS.primary} />
                        </View>
                        <Text style={{ fontSize: 22, fontWeight: '900', color: '#111827', marginBottom: 8 }}>Test Paused</Text>
                        <Text style={{ fontSize: 14, color: '#6b7280', marginBottom: 4 }}>
                            Time remaining: <Text style={{ fontWeight: 'bold', color: '#111827' }}>{formatTime(timeLeft)}</Text>
                        </Text>
                        <Text style={{ fontSize: 14, color: '#6b7280', marginBottom: 16 }}>
                            Answered: <Text style={{ fontWeight: 'bold', color: '#111827' }}>{stats.answered}/{totalQuestions}</Text>
                        </Text>

                        <View style={{
                            flexDirection: 'row', alignItems: 'center', backgroundColor: '#f0fdf4',
                            borderWidth: 1, borderColor: '#bbf7d0', borderRadius: 12, padding: 10, marginBottom: 20, width: '100%',
                        }}>
                            <Ionicons name="checkmark-circle" size={16} color="#16a34a" style={{ marginRight: 6 }} />
                            <Text style={{ color: '#166534', fontSize: 11, fontWeight: '500', flex: 1 }}>
                                Progress is saved. You can exit and resume later.
                            </Text>
                        </View>

                        <TouchableOpacity
                            onPress={handleResume}
                            style={{
                                backgroundColor: COLORS.primary, borderRadius: 14, paddingVertical: 14, width: '100%', alignItems: 'center',
                                marginBottom: 10, shadowColor: COLORS.primary, shadowOpacity: 0.3, shadowRadius: 8,
                                shadowOffset: { width: 0, height: 4 }, elevation: 5,
                            }}
                        >
                            <Text style={{ color: '#fff', fontWeight: '800', fontSize: 16 }}>▶ Resume Test</Text>
                        </TouchableOpacity>
                        <TouchableOpacity
                            onPress={() => navigation.goBack()}
                            style={{
                                backgroundColor: '#f3f4f6', borderRadius: 14, paddingVertical: 14, width: '100%', alignItems: 'center',
                                borderWidth: 1, borderColor: '#e5e7eb',
                            }}
                        >
                            <Text style={{ color: '#374151', fontWeight: '600', fontSize: 14 }}>← Exit to Dashboard</Text>
                        </TouchableOpacity>
                    </View>
                </View>
            </Modal>
        </SafeAreaView>
    );
}
