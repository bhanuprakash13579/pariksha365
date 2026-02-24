import React, { useState, useEffect } from 'react';
import { NavigationContainer } from '@react-navigation/native';
import { createNativeStackNavigator } from '@react-navigation/native-stack';
import { createBottomTabNavigator } from '@react-navigation/bottom-tabs';
import { View, Text, TextInput, TouchableOpacity, StyleSheet, FlatList, ScrollView, SafeAreaView, KeyboardAvoidingView, Platform, DimensionValue, Dimensions, Modal, Image, Alert, ActivityIndicator } from 'react-native';
import { Ionicons } from '@expo/vector-icons';
import { BarChart, LineChart, ProgressChart } from 'react-native-chart-kit';
import { TabView, SceneMap, TabBar } from 'react-native-tab-view';
import * as AppleAuthentication from 'expo-apple-authentication';
import * as Google from 'expo-auth-session/providers/google';
import * as WebBrowser from 'expo-web-browser';
import axios from 'axios';
import AsyncStorage from '@react-native-async-storage/async-storage';

WebBrowser.maybeCompleteAuthSession();

// --- API SERVICE ---
const API_BASE_URL = 'https://pariksha365-backend-production.up.railway.app/api/v1';

const api = axios.create({ baseURL: API_BASE_URL, headers: { 'Content-Type': 'application/json' } });

api.interceptors.request.use(async (config) => {
  const token = await AsyncStorage.getItem('token');
  if (token && config.headers) { config.headers.Authorization = `Bearer ${token}`; }
  return config;
});

const AuthAPI = {
  login: (email: string, password: string) => api.post('/auth/login', { email, password }),
  signup: (name: string, email: string, password: string) => api.post('/auth/signup', { name, email, password }),
};
const UserAPI = {
  getMe: () => api.get('/users/me'),
  updateMe: (data: { name?: string; phone?: string }) => api.put('/users/me', data),
  changePassword: (old_password: string, new_password: string) => api.put('/users/me/password', { old_password, new_password }),
};
const TestAPI = {
  list: (category?: string) => api.get('/tests', { params: category ? { category } : {} }),
  getById: (id: string) => api.get(`/tests/${id}`),
};
const AttemptAPI = {
  list: () => api.get('/attempts'),
  start: (test_series_id: string) => api.post('/attempts/start', { test_series_id }),
  saveAnswer: (attemptId: string, data: any) => api.post(`/attempts/${attemptId}/answers`, data),
  submit: (attemptId: string) => api.post(`/attempts/${attemptId}/submit`),
};

// Replace with your actual IDs when generating for Web and Android
const GOOGLE_IOS_CLIENT_ID = "592393648560-0csjsd0dvukv94qg05np14rj1v3o9gg2.apps.googleusercontent.com";
const GOOGLE_WEB_CLIENT_ID = "592393648560-o4ou87jvmv6tj3uura8ls27td06pv0o5.apps.googleusercontent.com";
const GOOGLE_ANDROID_CLIENT_ID = "592393648560-rpddhav13tiikcpgki71kvlegmi3s91c.apps.googleusercontent.com";

const { width } = Dimensions.get('window');
const Stack = createNativeStackNavigator();
const Tab = createBottomTabNavigator();

// --- MOCK DATA ---
const MOCK_TESTS = [
  { id: '1', title: 'SSC CGL Tier 1 Full Mock', tags: 'Mock Test / English', price: '₹149', isFree: false, questions: 100, mins: 60, validity: 365 },
  { id: '2', title: 'SBI PO Prelims Mini Test', tags: 'Mini Test / English', price: 'Free', isFree: true, questions: 30, mins: 20, validity: 30 },
  { id: '3', title: 'UPSC CSAT Complete Prep', tags: 'Subject Wise / Hindi', price: '₹299', isFree: false, questions: 80, mins: 120, validity: 180 },
];
const ENROLLED_TESTS = [
  { id: '1', title: 'SSC CGL Tier 1 Full Mock', progress: '30%', lastAttempted: '2 days ago' },
  { id: '2', title: 'SBI PO Prelims Mini Test', progress: '100%', lastAttempted: 'Completed' },
];

const SERIES_TESTS = [
  { id: 't1', title: 'Mock Test 1: Full Syllabus', questions: 100, mins: 60, type: 'Full Mock', isFree: true, isLocked: false },
  { id: 't2', title: 'Mock Test 2: Full Syllabus', questions: 100, mins: 60, type: 'Full Mock', isFree: false, isLocked: true },
  { id: 't3', title: 'Mock Test 3: Full Syllabus', questions: 100, mins: 60, type: 'Full Mock', isFree: false, isLocked: true },
  { id: 't4', title: 'Sectional: Quant 1', questions: 25, mins: 15, type: 'Sectional', isFree: false, isLocked: true },
  { id: 't5', title: 'Sectional: English 1', questions: 25, mins: 15, type: 'Sectional', isFree: false, isLocked: true },
];

const CHART_CONFIG = {
  backgroundGradientFrom: "#ffffff",
  backgroundGradientTo: "#ffffff",
  color: (opacity = 1) => `rgba(249, 115, 22, ${opacity})`,
  strokeWidth: 2,
  barPercentage: 0.5,
  useShadowColorFromDataset: false
};

// --- REUSABLE COMPONENTS ---
const TestCard = ({ item, onPress }: any) => (
  <TouchableOpacity style={styles.card} onPress={onPress}>
    <View style={{ flex: 1, marginRight: 10 }}>
      <Text style={styles.cardTitle}>{item.title}</Text>
      <Text style={styles.tag}>{item.tags}</Text>
      <View style={styles.metricsRow}>
        <Text style={styles.metricText}><Ionicons name="time-outline" size={12} /> {item.mins} Mins</Text>
        <Text style={styles.metricText}><Ionicons name="document-text-outline" size={12} /> {item.questions} Qs</Text>
      </View>
    </View>
    <View style={{ alignItems: 'flex-end' }}>
      <View style={[styles.priceTag, item.isFree && styles.freeTag]}>
        <Text style={[styles.priceTagText, item.isFree && styles.freeTagText]}>{item.isFree ? 'Free' : 'Paid'}</Text>
      </View>
      <Text style={styles.price}>{item.price}</Text>
    </View>
  </TouchableOpacity>
);

// --- GUEST PAYWALL MODAL ---
const GuestPaywallModal = ({ visible, onClose, navigation }: { visible: boolean, onClose: () => void, navigation: any }) => (
  <Modal visible={visible} animationType="slide" transparent={true}>
    <View style={styles.modalOverlay}>
      <View style={styles.modalContent}>
        <View style={styles.modalHeader}>
          <Text style={styles.modalTitle}>Sign In Required</Text>
          <TouchableOpacity onPress={onClose}><Ionicons name="close" size={28} color="#9ca3af" /></TouchableOpacity>
        </View>
        <Ionicons name="person-circle-outline" size={64} color="#f97316" style={{ alignSelf: 'center', marginVertical: 20 }} />
        <Text style={styles.modalTextCenter}>You are currently browsing as a Guest.</Text>
        <Text style={[styles.modalTextCenter, { marginTop: 10, fontWeight: 'bold' }]}>To save your progress, bookmark questions, or start an actual test, please create a free account.</Text>
        <TouchableOpacity style={[styles.button, { marginTop: 30 }]} onPress={() => { onClose(); navigation.replace('Signup'); }}>
          <Text style={styles.buttonText}>Create Free Account</Text>
        </TouchableOpacity>
      </View>
    </View>
  </Modal>
);


import LoginScreen from './src/screens/Auth/LoginScreen';
import SignupScreen from './src/screens/Auth/SignupScreen';
import HomeScreen from './src/screens/Main/HomeScreen';
import CourseDetailScreen from './src/screens/Course/CourseDetailScreen';
import CategoryScreen from './src/screens/Course/CategoryScreen';

// --- AUTH AND HOME SCREENS EXTRACTED TO src/screens ---

import MyLearningScreen from './src/screens/Main/MyLearningScreen';
import AnalyticsScreen from './src/screens/Main/AnalyticsScreen';
import DailyQuizScreen from './src/screens/Main/DailyQuizScreen';

// --- Testbook-Style Profile Screen ---
const ProfileScreen = ({ navigation, route }: any) => {
  const isGuest = route.params?.isGuest || false;
  const [user, setUser] = useState<any>(null);
  const [attempts, setAttempts] = useState<any[]>([]);
  const [loadingProfile, setLoadingProfile] = useState(!isGuest);

  useEffect(() => {
    if (isGuest) return;
    const fetchData = async () => {
      try {
        const userRes = await UserAPI.getMe();
        setUser(userRes.data);
        const attemptsRes = await AttemptAPI.list();
        setAttempts(attemptsRes.data);
      } catch { /* silently fall back */ }
      finally { setLoadingProfile(false); }
    };
    fetchData();
  }, [isGuest]);

  const handleLogout = async () => {
    await AsyncStorage.removeItem('token');
    navigation.replace('Login');
  };

  if (isGuest) {
    return (
      <View style={[styles.container, { justifyContent: 'center', alignItems: 'center', padding: 20 }]}>
        <Ionicons name="person-circle-outline" size={80} color="#d1d5db" />
        <Text style={[styles.authTitle, { marginTop: 20 }]}>Guest Profile</Text>
        <Text style={[styles.modalTextCenter, { marginVertical: 15 }]}>You are currently not signed in. Accounts are required to track history and save questions.</Text>
        <TouchableOpacity style={[styles.button, { width: '100%', marginTop: 20 }]} onPress={() => navigation.replace('Signup')}>
          <Text style={styles.buttonText}>Sign Up Now</Text>
        </TouchableOpacity>
        <TouchableOpacity style={{ marginTop: 20, alignItems: 'center' }} onPress={() => navigation.replace('Login')}>
          <Text style={{ color: '#4b5563', fontSize: 16 }}>Already have an account? <Text style={{ color: '#f97316', fontWeight: 'bold' }}>Log In</Text></Text>
        </TouchableOpacity>
      </View>
    );
  }

  if (loadingProfile) {
    return <View style={[styles.container, { justifyContent: 'center', alignItems: 'center' }]}><ActivityIndicator size="large" color="#f97316" /></View>;
  }

  const avgScore = attempts.length > 0 ? Math.round(attempts.filter(a => a.status === 'SUBMITTED').length / attempts.length * 100) : 0;

  return (
    <ScrollView style={styles.container}>
      <View style={styles.profileHeaderAlt}>
        <View style={styles.profileHeaderContent}>
          <View style={styles.avatarPlaceholderAlt}>
            <Text style={styles.avatarTextAlt}>{(user?.name || 'S').charAt(0).toUpperCase()}</Text>
          </View>
          <View style={{ flex: 1, marginLeft: 15 }}>
            <Text style={styles.profileNameAlt}>{user?.name || 'Student'}</Text>
            <Text style={styles.profileEmailAlt}>{user?.email || user?.phone || ''}</Text>
          </View>
          <TouchableOpacity style={styles.editIconBtn} onPress={() => navigation.navigate('EditProfile', { user })}>
            <Ionicons name="pencil" size={20} color="white" />
          </TouchableOpacity>
        </View>
      </View>

      <View style={styles.contentPadAlt}>
        <View style={styles.statsBannerRow}>
          <View style={styles.statsBox}>
            <Text style={styles.statsValue}>{attempts.length}</Text>
            <Text style={styles.statsLabel}>Tests Taken</Text>
          </View>
          <View style={styles.statsBox}>
            <Text style={styles.statsValue}>{avgScore}%</Text>
            <Text style={styles.statsLabel}>Completion</Text>
          </View>
        </View>

        <View style={styles.quickGrid}>
          <TouchableOpacity style={styles.quickGridItem} onPress={() => navigation.navigate('SavedQuestions')}>
            <Ionicons name="bookmark" size={24} color="#f97316" />
            <Text style={styles.quickGridText}>Saved</Text>
          </TouchableOpacity>
          <TouchableOpacity style={styles.quickGridItem} onPress={() => navigation.navigate('Downloads')}>
            <Ionicons name="download" size={24} color="#f97316" />
            <Text style={styles.quickGridText}>Offline</Text>
          </TouchableOpacity>
          <TouchableOpacity style={styles.quickGridItem} onPress={() => navigation.navigate('AttemptHistory')}>
            <Ionicons name="stats-chart" size={24} color="#f97316" />
            <Text style={styles.quickGridText}>History</Text>
          </TouchableOpacity>
          <TouchableOpacity style={styles.quickGridItem} onPress={() => navigation.navigate('ReferEarn')}>
            <Ionicons name="share-social" size={24} color="#f97316" />
            <Text style={styles.quickGridText}>Refer</Text>
          </TouchableOpacity>
        </View>

        <View style={styles.settingsGroup}>
          <Text style={styles.settingsGroupTitle}>Account & Settings</Text>
          <TouchableOpacity style={styles.settingItem} onPress={() => navigation.navigate('ChangeExam')}>
            <View style={styles.settingItemLeft}><Ionicons name="aperture" size={20} color="#6b7280" style={styles.iconSpaced} /><Text style={styles.settingText}>Change Exam Goal</Text></View>
            <Ionicons name="chevron-forward" size={20} color="#9ca3af" />
          </TouchableOpacity>
          <TouchableOpacity style={styles.settingItem} onPress={() => navigation.navigate('PaymentHistory')}>
            <View style={styles.settingItemLeft}><Ionicons name="receipt" size={20} color="#6b7280" style={styles.iconSpaced} /><Text style={styles.settingText}>My Transactions</Text></View>
            <Ionicons name="chevron-forward" size={20} color="#9ca3af" />
          </TouchableOpacity>
          <TouchableOpacity style={styles.settingItem} onPress={() => navigation.navigate('AppLanguage')}>
            <View style={styles.settingItemLeft}><Ionicons name="language" size={20} color="#6b7280" style={styles.iconSpaced} /><Text style={styles.settingText}>App Language</Text></View>
            <Ionicons name="chevron-forward" size={20} color="#9ca3af" />
          </TouchableOpacity>
          <TouchableOpacity style={styles.settingItem} onPress={() => navigation.navigate('Notifications')}>
            <View style={styles.settingItemLeft}><Ionicons name="notifications" size={20} color="#6b7280" style={styles.iconSpaced} /><Text style={styles.settingText}>Notifications</Text></View>
            <Ionicons name="chevron-forward" size={20} color="#9ca3af" />
          </TouchableOpacity>
          <TouchableOpacity style={styles.settingItem} onPress={() => navigation.navigate('HelpSupport')}>
            <View style={styles.settingItemLeft}><Ionicons name="help-buoy" size={20} color="#6b7280" style={styles.iconSpaced} /><Text style={styles.settingText}>Help & Support</Text></View>
            <Ionicons name="chevron-forward" size={20} color="#9ca3af" />
          </TouchableOpacity>
        </View>

        <TouchableOpacity style={styles.logoutButtonAlt} onPress={handleLogout}>
          <Ionicons name="power" size={20} color="#ef4444" style={{ marginRight: 8 }} />
          <Text style={styles.logoutText}>Log Out</Text>
        </TouchableOpacity>
      </View>
    </ScrollView>
  );
};

// --- Testbook Profile Sub-Screens ---
const SavedQuestionsScreen = () => (
  <View style={styles.detailContainer}>
    <View style={styles.emptyState}>
      <Ionicons name="bookmark-outline" size={64} color="#d1d5db" />
      <Text style={styles.emptyText}>No saved questions yet.</Text>
      <Text style={styles.emptySubText}>Bookmark questions during a test to review them here.</Text>
    </View>
  </View>
);
const DownloadsScreen = () => (
  <View style={styles.detailContainer}>
    <View style={styles.emptyState}>
      <Ionicons name="download-outline" size={64} color="#d1d5db" />
      <Text style={styles.emptyText}>No offline downloads.</Text>
      <Text style={styles.emptySubText}>Download test papers or notes to view without internet.</Text>
    </View>
  </View>
);
const AttemptHistoryScreen = ({ navigation }: any) => {
  const [attempts, setAttempts] = useState<any[]>([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const fetchAttempts = async () => {
      try {
        const res = await AttemptAPI.list();
        setAttempts(res.data);
      } catch { /* silent */ }
      finally { setLoading(false); }
    };
    fetchAttempts();
  }, []);

  if (loading) return <View style={[styles.container, { justifyContent: 'center', alignItems: 'center' }]}><ActivityIndicator size="large" color="#f97316" /></View>;

  if (attempts.length === 0) {
    return (
      <View style={styles.detailContainer}>
        <View style={styles.emptyState}>
          <Ionicons name="time-outline" size={64} color="#d1d5db" />
          <Text style={styles.emptyText}>No attempts yet.</Text>
          <Text style={styles.emptySubText}>Start a test to see your attempt history here.</Text>
        </View>
      </View>
    );
  }

  return (
    <ScrollView style={styles.container}>
      <View style={styles.contentPadAlt}>
        {attempts.map((attempt: any) => (
          <TouchableOpacity key={attempt.id} style={styles.card} onPress={() => navigation.navigate('TestAnalysis')}>
            <View style={styles.flexRowBetween}>
              <View>
                <Text style={styles.cardTitle}>Test Attempt</Text>
                <Text style={styles.metricText}>{attempt.status} • {new Date(attempt.started_at).toLocaleDateString()}</Text>
              </View>
              <Text style={[styles.priceTagText, { color: attempt.status === 'SUBMITTED' ? '#15803d' : '#f97316' }]}>{attempt.status}</Text>
            </View>
          </TouchableOpacity>
        ))}
      </View>
    </ScrollView>
  );
};

const TestAnalysisScreen = () => {
  return (
    <ScrollView style={styles.container}>
      <View style={styles.analysisHeader}>
        <View style={{ alignItems: 'center' }}>
          <ProgressChart
            data={{ labels: ["Percentile"], data: [0.94] }}
            width={width - 40}
            height={150}
            strokeWidth={16}
            radius={50}
            chartConfig={{ ...CHART_CONFIG, color: (opacity = 1) => `rgba(16, 185, 129, ${opacity})` }}
            hideLegend={true}
            style={{}}
          />
          <View style={{ position: 'absolute', top: 55, alignItems: 'center' }}>
            <Text style={{ fontSize: 24, fontWeight: 'bold', color: '#10b981' }}>94.5</Text>
            <Text style={{ fontSize: 10, color: '#6b7280' }}>%ile</Text>
          </View>
        </View>

        <View style={styles.statsBannerRow}>
          <View style={styles.statsBox}>
            <Text style={[styles.statsValue, { fontSize: 18, color: '#111827' }]}>1,402<Text style={{ fontSize: 10, color: '#9ca3af' }}>/10k</Text></Text>
            <Text style={styles.statsLabel}>Rank</Text>
          </View>
          <View style={styles.statsBox}>
            <Text style={[styles.statsValue, { fontSize: 18, color: '#111827' }]}>120<Text style={{ fontSize: 10, color: '#9ca3af' }}>/200</Text></Text>
            <Text style={styles.statsLabel}>Score</Text>
          </View>
          <View style={styles.statsBox}>
            <Text style={[styles.statsValue, { fontSize: 18, color: '#111827' }]}>88%</Text>
            <Text style={styles.statsLabel}>Accuracy</Text>
          </View>
        </View>
      </View>

      <View style={styles.contentPadAlt}>
        <Text style={styles.sectionTitle}>Section-wise Score</Text>
        <View style={styles.chartWrapper}>
          <BarChart
            data={{
              labels: ["Quant", "Reason", "Eng", "GK"],
              datasets: [{ data: [45, 40, 25, 10] }]
            }}
            width={width - 64}
            height={220}
            yAxisLabel=""
            yAxisSuffix=""
            chartConfig={CHART_CONFIG}
            verticalLabelRotation={0}
            style={{ borderRadius: 16 }}
            flatColor={true}
            withInnerLines={false}
          />
        </View>

        <Text style={[styles.sectionTitle, { marginTop: 20 }]}>Strong & Weak Areas</Text>
        <View style={{ flexDirection: 'row', gap: 10 }}>
          <View style={[styles.analysisCard, { borderColor: '#bbf7d0', backgroundColor: '#f0fdf4' }]}>
            <Text style={[styles.cardTitle, { color: '#166534', marginBottom: 10 }]}>Strengths</Text>
            <Text style={styles.tag}>Profit & Loss</Text>
            <Text style={styles.tag}>Syllogism</Text>
          </View>
          <View style={[styles.analysisCard, { borderColor: '#fecaca', backgroundColor: '#fef2f2' }]}>
            <Text style={[styles.cardTitle, { color: '#991b1b', marginBottom: 10 }]}>Weaknesses</Text>
            <Text style={[styles.tag, { color: '#991b1b' }]}>Current Affairs</Text>
            <Text style={[styles.tag, { color: '#991b1b' }]}>Vocabulary</Text>
          </View>
        </View>

        <TouchableOpacity style={[styles.button, { marginTop: 30, marginBottom: 40 }]}>
          <Text style={styles.buttonText}>Review All Answers</Text>
        </TouchableOpacity>
      </View>
    </ScrollView>
  );
};

const SeriesTrendScreen = ({ route }: any) => {
  const { test } = route.params;
  return (
    <ScrollView style={styles.container}>
      <View style={styles.analysisHeader}>
        <Text style={styles.detailTitle}>{test.title}</Text>
        <Text style={{ color: '#6b7280', marginTop: 5 }}>Performance Trajectory</Text>
      </View>

      <View style={styles.contentPadAlt}>
        <Text style={styles.sectionTitle}>Score Progression</Text>
        <View style={styles.chartWrapper}>
          <LineChart
            data={{
              labels: ["M1", "M2", "M3", "M4", "M5"],
              datasets: [{ data: [80, 95, 88, 110, 120] }]
            }}
            width={width - 64}
            height={220}
            chartConfig={CHART_CONFIG}
            bezier
            style={{ borderRadius: 16 }}
            withShadow={false}
            withHorizontalLines={true}
            withVerticalLines={false}
          />
        </View>

        <View style={styles.infoBox}>
          <Text style={{ fontWeight: 'bold', color: '#166534' }}>Projected Result: Clear Cut-off</Text>
          <Text style={[styles.infoText, { marginTop: 5 }]}>Based on your recent upward trend, you are projected to score ~135 in the actual exam, comfortably clearing the 130 cut-off mark.</Text>
        </View>
      </View>
    </ScrollView>
  );
};
const ReferEarnScreen = () => (
  <View style={styles.detailContainer}>
    <Text style={styles.detailTitle}>🎁 Refer & Earn</Text>
    <Text style={[styles.metricText, { marginTop: 15, fontSize: 16, lineHeight: 24 }]}>Refer a friend and both of you get 10% off your next Pariksha365 Pass PRO purchase! Use code S10X9A.</Text>
  </View>
);
const ChangeExamScreen = () => (
  <View style={styles.detailContainer}>
    <Text style={styles.detailTitle}>Select Your Goal</Text>
    {['SSC Exams', 'Banking Exams', 'UPSC Prelims', 'Teaching (CTET)'].map(exam => (
      <TouchableOpacity key={exam} style={[styles.card, { marginTop: 15 }]}>
        <Text style={styles.cardTitle}>{exam}</Text>
        <Ionicons name="chevron-forward" size={20} color="#9ca3af" />
      </TouchableOpacity>
    ))}
  </View>
);
const AppLanguageScreen = () => (
  <View style={styles.detailContainer}>
    <Text style={styles.detailTitle}>Choose Language</Text>
    {['English', 'हिन्दी (Hindi)'].map(lang => (
      <TouchableOpacity key={lang} style={[styles.card, { marginTop: 15 }]}>
        <Text style={styles.cardTitle}>{lang}</Text>
      </TouchableOpacity>
    ))}
  </View>
);
const EditProfileScreen = ({ route }: any) => {
  const userData = route?.params?.user;
  const [name, setName] = useState(userData?.name || '');
  const [phone, setPhone] = useState(userData?.phone || '');
  const [email] = useState(userData?.email || '');
  const [saving, setSaving] = useState(false);

  const handleSave = async () => {
    setSaving(true);
    try {
      await UserAPI.updateMe({ name, phone });
      Alert.alert('Success', 'Profile updated successfully!');
    } catch (err: any) {
      Alert.alert('Error', err.response?.data?.detail || 'Could not update profile.');
    } finally { setSaving(false); }
  };

  return (
    <View style={styles.detailContainer}>
      <Text style={styles.detailTitle}>Edit Profile</Text>
      <TextInput style={[styles.input, { marginTop: 20 }]} placeholder="Full Name" value={name} onChangeText={setName} />
      <TextInput style={styles.input} placeholder="Phone Number" keyboardType="phone-pad" value={phone} onChangeText={setPhone} />
      <TextInput style={[styles.input, { color: '#9ca3af' }]} placeholder="Email" value={email} editable={false} />
      <TouchableOpacity style={saving ? styles.buttonDisabled : styles.button} onPress={handleSave} disabled={saving}>
        {saving ? <ActivityIndicator color="#fff" /> : <Text style={styles.buttonText}>Save Changes</Text>}
      </TouchableOpacity>
    </View>
  );
};
const PaymentHistoryScreen = () => (
  <ScrollView style={styles.container}>
    <View style={styles.contentPadAlt}>
      <View style={[styles.card, { marginTop: 10 }]}>
        <View>
          <Text style={styles.cardTitle}>SSC CGL Full Mock</Text>
          <Text style={styles.metricText}>Feb 15, 2026</Text>
        </View>
        <Text style={[styles.priceTagText, { color: '#15803d' }]}>SUCCESS (₹149)</Text>
      </View>
    </View>
  </ScrollView>
);
const NotificationsScreen = () => (
  <View style={styles.detailContainer}>
    <View style={styles.infoBox}>
      <Text style={styles.infoText}>You have an upcoming exam (RRB NTPC) in 12 days. Complete your mocks!</Text>
    </View>
  </View>
);
const HelpSupportScreen = () => (
  <View style={styles.detailContainer}>
    <Text style={styles.detailTitle}>Help Desk</Text>
    <Text style={[styles.metricText, { marginTop: 15, fontSize: 16 }]}>For all queries, technical issues, or refund requests, please email us directly at support@pariksha365.in</Text>
  </View>
);

// --- Deep Series Details & Netflix Reader Bypass ---
const WebUnlockModal = ({ visible, onClose, testTitle }: { visible: boolean, onClose: () => void, testTitle: string }) => (
  <Modal visible={visible} animationType="slide" transparent={true}>
    <View style={styles.modalOverlay}>
      <View style={styles.modalContent}>
        <View style={styles.modalHeader}>
          <Text style={styles.modalTitle}>Premium Content</Text>
          <TouchableOpacity onPress={onClose}><Ionicons name="close" size={28} color="#9ca3af" /></TouchableOpacity>
        </View>
        <Ionicons name="lock-closed" size={64} color="#f97316" style={{ alignSelf: 'center', marginVertical: 20 }} />
        <Text style={styles.modalTextCenter}>This is a premium test locked under the Pariksha365 platform policies.</Text>
        <Text style={[styles.modalTextCenter, { marginTop: 10, fontWeight: 'bold' }]}>To take this test, please purchase the complete Test Series on our official website.</Text>
        <TouchableOpacity style={[styles.button, { marginTop: 30 }]} onPress={onClose}>
          <Text style={styles.buttonText}>Okay, I understand</Text>
        </TouchableOpacity>
      </View>
    </View>
  </Modal>
);

const TestDetailScreen = ({ route, navigation }: any) => {
  const { test, isGuest } = route.params;
  const [index, setIndex] = useState(0);
  const [modalVisible, setModalVisible] = useState(false);
  const [guestModal, setGuestModal] = useState(false);
  const [routes] = useState([
    { key: 'overview', title: 'Overview' },
    { key: 'tests', title: 'Content' },
  ]);

  const handleTestTap = (item: any) => {
    if (item.isLocked) { setModalVisible(true); }
    else if (isGuest) { setGuestModal(true); }
    else { /* Navigate to Test Engine Screen */ }
  };

  const OverviewRoute = () => (
    <ScrollView style={styles.contentPadAlt}>
      <View style={styles.infoBox}>
        <Text style={[styles.detailTitle, { fontSize: 20, marginBottom: 10 }]}>Syllabus Covered</Text>
        <Text style={styles.metricText}>• Quantitative Aptitude (Algebra, Geometry)</Text>
        <Text style={styles.metricText}>• Logical Reasoning (Puzzles, Syllogism)</Text>
        <Text style={styles.metricText}>• English Language (Comprehension, Grammar)</Text>
        <Text style={styles.metricText}>• General Awareness (History, Constitution, Physics)</Text>
      </View>
      <View style={[styles.card, { marginTop: 15 }]}>
        <Text style={styles.cardTitle}>Total Tests</Text>
        <Text style={styles.scoreText}>140+</Text>
      </View>
    </ScrollView>
  );

  const TestsRoute = () => (
    <ScrollView style={styles.contentPadAlt}>
      <Text style={[styles.sectionTitle, { marginTop: 10 }]}>Full Mock Tests</Text>
      {SERIES_TESTS.filter(t => t.type === 'Full Mock').map(item => (
        <TouchableOpacity key={item.id} style={styles.card} onPress={() => handleTestTap(item)}>
          <View style={{ flexDirection: 'row', alignItems: 'center', flex: 1 }}>
            <View style={[styles.iconBox, item.isLocked && styles.iconBoxLocked]}>
              <Ionicons name={item.isLocked ? "lock-closed" : "play"} size={20} color={item.isLocked ? "#9ca3af" : "#f97316"} />
            </View>
            <View style={{ flex: 1, marginLeft: 15 }}>
              <Text style={[styles.cardTitle, item.isLocked && { color: '#9ca3af' }]}>{item.title}</Text>
              <View style={styles.metricsRow}>
                <Text style={styles.metricText}>{item.questions} Qs</Text>
                <Text style={styles.metricText}>{item.mins} Mins</Text>
              </View>
            </View>
            {item.isFree && <View style={styles.freeTag}><Text style={styles.freeTagText}>FREE</Text></View>}
          </View>
        </TouchableOpacity>
      ))}

      <Text style={[styles.sectionTitle, { marginTop: 20 }]}>Sectional Tests</Text>
      {SERIES_TESTS.filter(t => t.type === 'Sectional').map(item => (
        <TouchableOpacity key={item.id} style={styles.card} onPress={() => handleTestTap(item)}>
          <View style={{ flexDirection: 'row', alignItems: 'center', flex: 1 }}>
            <View style={[styles.iconBox, item.isLocked && styles.iconBoxLocked]}>
              <Ionicons name={item.isLocked ? "lock-closed" : "play"} size={20} color={item.isLocked ? "#9ca3af" : "#f97316"} />
            </View>
            <View style={{ flex: 1, marginLeft: 15 }}>
              <Text style={[styles.cardTitle, item.isLocked && { color: '#9ca3af' }]}>{item.title}</Text>
              <View style={styles.metricsRow}>
                <Text style={styles.metricText}>{item.questions} Qs</Text>
                <Text style={styles.metricText}>{item.mins} Mins</Text>
              </View>
            </View>
          </View>
        </TouchableOpacity>
      ))}
    </ScrollView>
  );

  return (
    <View style={styles.container}>
      {/* Test Series Header Block */}
      <View style={styles.seriesHeader}>
        <Text style={styles.seriesTitle}>{test.title}</Text>
        <Text style={{ color: '#6b7280', marginTop: 8 }}>{test.tags}</Text>
      </View>

      {/* Deep Tab Navigation */}
      <TabView
        navigationState={{ index, routes }}
        renderScene={SceneMap({ overview: OverviewRoute, tests: TestsRoute })}
        onIndexChange={setIndex}
        initialLayout={{ width }}
        renderTabBar={props => (
          <TabBar {...props} indicatorStyle={{ backgroundColor: '#f97316' }} style={{ backgroundColor: '#ffffff', elevation: 0 }} activeColor="#f97316" inactiveColor="#6b7280" />
        )}
      />
      <WebUnlockModal visible={modalVisible} onClose={() => setModalVisible(false)} testTitle={""} />
      <GuestPaywallModal visible={guestModal} onClose={() => setGuestModal(false)} navigation={navigation} />
    </View>
  );
};

// --- NAVIGATION CONFIG ---
const MainTabs = ({ route }: any) => {
  const isGuest = route.params?.isGuest || false;
  return (
    <Tab.Navigator
      screenOptions={({ route }) => ({
        tabBarIcon: ({ focused, color, size }) => {
          let iconName: any = 'home';
          if (route.name === 'HomeTab') iconName = focused ? 'home' : 'home-outline';
          else if (route.name === 'DailyQuizTab') iconName = focused ? 'flash' : 'flash-outline';
          else if (route.name === 'MyLearningTab') iconName = focused ? 'book' : 'book-outline';
          else if (route.name === 'AnalyticsTab') iconName = focused ? 'stats-chart' : 'stats-chart-outline';
          else if (route.name === 'ProfileTab') iconName = focused ? 'person' : 'person-outline';
          return <Ionicons name={iconName} size={size} color={color} />;
        },
        tabBarActiveTintColor: '#f97316',
        tabBarInactiveTintColor: 'gray',
        headerShown: true,
        headerStyle: { backgroundColor: '#ffffff', elevation: 0, shadowOpacity: 0 },
        headerTitleStyle: { fontWeight: 'bold' }
      })}
    >
      <Tab.Screen name="HomeTab" component={HomeScreen} initialParams={{ isGuest }} options={{ title: 'Home', headerShown: false }} />
      <Tab.Screen name="DailyQuizTab" component={DailyQuizScreen} options={{ title: 'Daily Quizzes' }} />
      <Tab.Screen name="MyLearningTab" component={MyLearningScreen} options={{ title: 'My Learning' }} />
      <Tab.Screen name="AnalyticsTab" component={AnalyticsScreen} options={{ title: 'Analytics' }} />
      <Tab.Screen name="ProfileTab" component={ProfileScreen} initialParams={{ isGuest }} options={{ title: 'Profile', headerShown: false }} />
    </Tab.Navigator>
  );
};

export default function App() {
  return (
    <NavigationContainer>
      <Stack.Navigator initialRouteName="Login">
        <Stack.Screen name="Login" component={LoginScreen} options={{ headerShown: false }} />
        <Stack.Screen name="Signup" component={SignupScreen} options={{ headerShown: false }} />
        <Stack.Screen name="MainTabs" component={MainTabs} options={{ headerShown: false }} />
        <Stack.Screen name="TestDetail" component={TestDetailScreen} options={{ title: 'Overview' }} />
        <Stack.Screen name="CourseDetail" component={CourseDetailScreen} options={{ title: 'Course Details' }} />
        <Stack.Screen name="Category" component={CategoryScreen} options={{ headerShown: false }} />
        {/* Testbook Sub-Screens */}
        <Stack.Screen name="EditProfile" component={EditProfileScreen} options={{ title: 'Edit Profile' }} />
        <Stack.Screen name="SavedQuestions" component={SavedQuestionsScreen} options={{ title: 'Saved Questions' }} />
        <Stack.Screen name="Downloads" component={DownloadsScreen} options={{ title: 'Downloads' }} />
        <Stack.Screen name="AttemptHistory" component={AttemptHistoryScreen} options={{ title: 'Attempt History' }} />
        <Stack.Screen name="TestAnalysis" component={TestAnalysisScreen} options={{ title: 'Detailed Analysis' }} />
        <Stack.Screen name="SeriesTrend" component={SeriesTrendScreen} options={{ title: 'Series Progress' }} />
        <Stack.Screen name="ReferEarn" component={ReferEarnScreen} options={{ title: 'Refer & Earn' }} />
        <Stack.Screen name="ChangeExam" component={ChangeExamScreen} options={{ title: 'Change Goal' }} />
        <Stack.Screen name="PaymentHistory" component={PaymentHistoryScreen} options={{ title: 'Payment History' }} />
        <Stack.Screen name="AppLanguage" component={AppLanguageScreen} options={{ title: 'Language' }} />
        <Stack.Screen name="Notifications" component={NotificationsScreen} options={{ title: 'Notifications' }} />
        <Stack.Screen name="HelpSupport" component={HelpSupportScreen} options={{ title: 'Help & Support' }} />
      </Stack.Navigator>
    </NavigationContainer>
  );
}

// --- STYLES ---
const styles = StyleSheet.create({
  container: { flex: 1, backgroundColor: '#f9fafb' },
  contentPad: { padding: 16 },
  contentPadAlt: { padding: 16, paddingTop: 10 },
  flexRowBetween: { flexDirection: 'row', justifyContent: 'space-between', alignItems: 'center' },

  // Auth
  authContainer: { flex: 1, backgroundColor: '#ffffff' },
  authInner: { flex: 1, padding: 24, justifyContent: 'center' },
  authHeader: { marginBottom: 40 },
  authTitle: { fontSize: 32, fontWeight: 'bold', color: '#111827', marginBottom: 8 },
  authSubtitle: { fontSize: 16, color: '#6b7280' },
  formContainer: { marginBottom: 32 },
  input: { backgroundColor: '#f3f4f6', borderRadius: 12, padding: 16, marginBottom: 16, fontSize: 16, color: '#1f2937', borderWidth: 1, borderColor: '#e5e7eb' },
  primaryButton: { backgroundColor: '#f97316', borderRadius: 12, padding: 16, alignItems: 'center', shadowColor: '#f97316', shadowOffset: { width: 0, height: 4 }, shadowOpacity: 0.3, shadowRadius: 8, elevation: 5 },
  primaryButtonText: { color: '#ffffff', fontSize: 18, fontWeight: 'bold' },
  dividerRow: { flexDirection: 'row', alignItems: 'center', marginVertical: 25 },
  divider: { flex: 1, height: 1, backgroundColor: '#e5e7eb' },
  dividerText: { color: '#9ca3af', paddingHorizontal: 10, fontWeight: 'bold' },
  socialButton: { flexDirection: 'row', alignItems: 'center', justifyContent: 'center', backgroundColor: '#ffffff', borderWidth: 1, borderColor: '#e5e7eb', borderRadius: 12, padding: 14, marginBottom: 15 },
  socialButtonText: { fontSize: 16, fontWeight: 'bold', color: '#374151', marginLeft: 10 },

  // Home Header
  header: { padding: 20, paddingTop: 60, backgroundColor: '#f97316', paddingBottom: 30, borderBottomLeftRadius: 24, borderBottomRightRadius: 24 },
  greeting: { fontSize: 24, fontWeight: 'bold', color: 'white' },
  subGreeting: { fontSize: 15, color: '#ffedd5', marginTop: 4 },
  sectionTitle: { fontSize: 18, fontWeight: 'bold', marginBottom: 12, color: '#111827' },
  upcomingScroll: { marginBottom: 15 },
  upcomingCard: { backgroundColor: '#fff7ed', borderWidth: 1, borderColor: '#fed7aa', padding: 16, borderRadius: 12, flexDirection: 'row', alignItems: 'center', marginRight: 12, width: 220 },
  upcomingTitle: { fontSize: 15, fontWeight: 'bold', color: '#1f2937' },
  upcomingDate: { fontSize: 13, color: '#ea580c', marginTop: 4 },

  // Cards
  card: { backgroundColor: 'white', marginBottom: 15, padding: 16, borderRadius: 16, flexDirection: 'row', justifyContent: 'space-between', alignItems: 'center', elevation: 2, shadowColor: '#000', shadowOpacity: 0.1, shadowRadius: 5 },
  cardTitle: { fontSize: 16, fontWeight: 'bold', color: '#1f2937' },
  tag: { color: '#6b7280', fontSize: 13, marginTop: 4 },
  metricsRow: { flexDirection: 'row', marginTop: 8 },
  metricText: { color: '#6b7280', fontSize: 12, marginRight: 12, marginTop: 4 },
  priceTag: { backgroundColor: '#fee2e2', paddingHorizontal: 8, paddingVertical: 4, borderRadius: 6, marginBottom: 8 },
  priceTagText: { color: '#b91c1c', fontSize: 10, fontWeight: 'bold', textTransform: 'uppercase' },
  freeTag: { backgroundColor: '#dcfce7' },
  freeTagText: { color: '#15803d' },
  price: { fontSize: 18, fontWeight: 'bold', color: '#1f2937' },
  progressBarBg: { height: 6, backgroundColor: '#f3f4f6', borderRadius: 3, marginTop: 8, width: '100%' },
  progressBarFill: { height: 6, backgroundColor: '#10b981', borderRadius: 3 },
  scoreText: { fontSize: 18, fontWeight: 'bold', color: '#f97316' },

  // Testbook Profile specific
  profileHeaderAlt: { backgroundColor: '#111827', padding: 24, paddingTop: 60, borderBottomLeftRadius: 24, borderBottomRightRadius: 24 },
  profileHeaderContent: { flexDirection: 'row', alignItems: 'center' },
  avatarPlaceholderAlt: { width: 70, height: 70, borderRadius: 35, backgroundColor: '#f97316', alignItems: 'center', justifyContent: 'center' },
  avatarTextAlt: { color: 'white', fontSize: 28, fontWeight: 'bold' },
  profileNameAlt: { fontSize: 20, fontWeight: 'bold', color: '#ffffff' },
  profileEmailAlt: { fontSize: 14, color: '#9ca3af', marginTop: 4 },
  badgePro: { backgroundColor: '#374151', paddingHorizontal: 8, paddingVertical: 4, borderRadius: 4, marginTop: 8, alignSelf: 'flex-start' },
  badgeProText: { color: '#fb923c', fontSize: 10, fontWeight: 'bold' },
  editIconBtn: { backgroundColor: 'rgba(255,255,255,0.2)', padding: 10, borderRadius: 20 },

  statsBannerRow: { flexDirection: 'row', justifyContent: 'space-between', marginBottom: 20, marginTop: 10, gap: 12 },
  statsBox: { flex: 1, backgroundColor: '#ffffff', padding: 16, borderRadius: 16, alignItems: 'center', justifyContent: 'center', elevation: 1, shadowColor: '#000', shadowOpacity: 0.05, shadowRadius: 3, borderWidth: 1, borderColor: '#f3f4f6' },
  statsValue: { fontSize: 24, fontWeight: 'bold', color: '#f97316' },
  statsLabel: { fontSize: 12, color: '#6b7280', marginTop: 4, fontWeight: '500' },

  quickGrid: { flexDirection: 'row', justifyContent: 'space-between', backgroundColor: '#ffffff', padding: 20, borderRadius: 16, marginBottom: 20, elevation: 1, shadowColor: '#000', shadowOpacity: 0.05, shadowRadius: 3 },
  quickGridItem: { alignItems: 'center' },
  quickGridText: { fontSize: 12, color: '#4b5563', marginTop: 8, fontWeight: '500' },

  settingsGroup: { backgroundColor: '#ffffff', borderRadius: 16, marginBottom: 24, paddingVertical: 8, elevation: 1, shadowColor: '#000', shadowOpacity: 0.05, shadowRadius: 3 },
  settingsGroupTitle: { fontSize: 14, fontWeight: 'bold', color: '#9ca3af', paddingHorizontal: 16, paddingVertical: 12, textTransform: 'uppercase', letterSpacing: 0.5 },
  settingItem: { flexDirection: 'row', justifyContent: 'space-between', alignItems: 'center', padding: 16, borderTopWidth: 1, borderTopColor: '#f3f4f6' },
  settingItemLeft: { flexDirection: 'row', alignItems: 'center' },
  iconSpaced: { marginRight: 12 },
  settingText: { fontSize: 16, color: '#374151', fontWeight: '500' },

  logoutButtonAlt: { flexDirection: 'row', alignItems: 'center', justifyContent: 'center', padding: 16, backgroundColor: '#ffffff', borderRadius: 16, borderWidth: 1, borderColor: '#fecaca', marginBottom: 40 },
  logoutText: { color: '#ef4444', fontSize: 16, fontWeight: 'bold' },

  // Detail Screen
  detailContainer: { flex: 1, padding: 20, backgroundColor: 'white' },
  detailTitle: { fontSize: 24, fontWeight: 'bold', color: '#111827' },
  infoBox: { marginTop: 20, padding: 15, backgroundColor: '#f0fdf4', borderRadius: 8, borderWidth: 1, borderColor: '#bbf7d0' },
  infoText: { color: '#166534', fontSize: 14, lineHeight: 20 },
  button: { backgroundColor: '#f97316', padding: 16, borderRadius: 12, alignItems: 'center' },
  buttonDisabled: { backgroundColor: '#9ca3af', padding: 16, borderRadius: 12, alignItems: 'center' },
  buttonText: { color: 'white', fontWeight: 'bold', fontSize: 16 },

  // Empty State (Downloads, Bookmarks)
  emptyState: { flex: 1, alignItems: 'center', justifyContent: 'center', paddingTop: 60 },
  emptyText: { fontSize: 18, fontWeight: 'bold', color: '#4b5563', marginTop: 16 },
  emptySubText: { fontSize: 14, color: '#9ca3af', textAlign: 'center', marginTop: 8, paddingHorizontal: 40 },

  // Advanced Analysis
  analysisHeader: { backgroundColor: '#ffffff', padding: 20, paddingTop: 30, borderBottomWidth: 1, borderBottomColor: '#f3f4f6' },
  chartWrapper: { backgroundColor: '#ffffff', padding: 16, borderRadius: 16, alignItems: 'center', elevation: 1, shadowColor: '#000', shadowOpacity: 0.05, shadowRadius: 3, borderWidth: 1, borderColor: '#f3f4f6' },
  analysisCard: { flex: 1, padding: 16, borderRadius: 16, borderWidth: 1 },

  // Deep Series & Catgories
  categoryBadge: { paddingHorizontal: 20, paddingVertical: 10, backgroundColor: '#f3f4f6', borderRadius: 20, marginRight: 10, borderWidth: 1, borderColor: '#e5e7eb' },
  categoryBadgeText: { fontWeight: 'bold', color: '#4b5563' },
  seriesHeader: { backgroundColor: '#ffffff', padding: 20, paddingTop: 20, borderBottomWidth: 1, borderBottomColor: '#f3f4f6' },
  seriesTitle: { fontSize: 22, fontWeight: 'bold', color: '#111827' },
  iconBox: { width: 40, height: 40, borderRadius: 20, backgroundColor: '#fff7ed', alignItems: 'center', justifyContent: 'center' },
  iconBoxLocked: { backgroundColor: '#f3f4f6' },

  // Modals
  modalOverlay: { flex: 1, backgroundColor: 'rgba(0,0,0,0.5)', justifyContent: 'flex-end' },
  modalContent: { backgroundColor: '#ffffff', borderTopLeftRadius: 24, borderTopRightRadius: 24, padding: 24, paddingBottom: 40 },
  modalHeader: { flexDirection: 'row', justifyContent: 'space-between', alignItems: 'center' },
  modalTitle: { fontSize: 20, fontWeight: 'bold', color: '#111827' },
  modalTextCenter: { fontSize: 16, color: '#4b5563', textAlign: 'center', lineHeight: 24 }
});
