import React, { useState } from 'react';
import { NavigationContainer } from '@react-navigation/native';
import { createNativeStackNavigator } from '@react-navigation/native-stack';
import { createBottomTabNavigator } from '@react-navigation/bottom-tabs';
import { View, Text, TextInput, TouchableOpacity, StyleSheet, FlatList, ScrollView, SafeAreaView, KeyboardAvoidingView, Platform, DimensionValue } from 'react-native';
import { Ionicons } from '@expo/vector-icons';

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

// --- AUTH SCREENS ---
const LoginScreen = ({ navigation }: any) => {
  return (
    <SafeAreaView style={styles.authContainer}>
      <KeyboardAvoidingView behavior={Platform.OS === 'ios' ? 'padding' : 'height'} style={styles.authInner}>
        <View style={styles.authHeader}>
          <Text style={styles.authTitle}>Welcome Back</Text>
          <Text style={styles.authSubtitle}>Sign in to continue your preparation</Text>
        </View>
        <View style={styles.formContainer}>
          <TextInput style={styles.input} placeholder="Email" placeholderTextColor="#9ca3af" keyboardType="email-address" autoCapitalize="none" />
          <TextInput style={styles.input} placeholder="Password" placeholderTextColor="#9ca3af" secureTextEntry />
          <TouchableOpacity style={styles.primaryButton} onPress={() => navigation.replace('MainTabs')}>
            <Text style={styles.primaryButtonText}>Login</Text>
          </TouchableOpacity>
        </View>
      </KeyboardAvoidingView>
    </SafeAreaView>
  );
};
const SignupScreen = ({ navigation }: any) => {
  return (
    <SafeAreaView style={styles.authContainer}>
      <KeyboardAvoidingView behavior={Platform.OS === 'ios' ? 'padding' : 'height'} style={styles.authInner}>
        <Text style={styles.authTitle}>Create Account</Text>
        <View style={styles.formContainer}>
          <TextInput style={styles.input} placeholder="Full Name" placeholderTextColor="#9ca3af" />
          <TextInput style={styles.input} placeholder="Email" placeholderTextColor="#9ca3af" keyboardType="email-address" />
          <TextInput style={styles.input} placeholder="Password" placeholderTextColor="#9ca3af" secureTextEntry />
          <TouchableOpacity style={styles.primaryButton} onPress={() => navigation.replace('MainTabs')}><Text style={styles.primaryButtonText}>Sign Up</Text></TouchableOpacity>
        </View>
      </KeyboardAvoidingView>
    </SafeAreaView>
  );
};

// --- MAIN TAB SCREENS ---
const HomeScreen = ({ navigation }: any) => {
  return (
    <ScrollView style={styles.container}>
      <View style={styles.header}>
        <Text style={styles.greeting}>Hello, Student!</Text>
        <Text style={styles.subGreeting}>Let's ace your next exam.</Text>
      </View>
      <View style={styles.contentPad}>
        <Text style={styles.sectionTitle}>Upcoming Exams</Text>
        <ScrollView horizontal showsHorizontalScrollIndicator={false} style={styles.upcomingScroll}>
          <View style={styles.upcomingCard}><Ionicons name="calendar" size={24} color="#f97316" /><View style={{ marginLeft: 12 }}><Text style={styles.upcomingTitle}>RRB NTPC</Text><Text style={styles.upcomingDate}>June 15, 2026</Text></View></View>
        </ScrollView>
        <Text style={styles.sectionTitle}>Popular Test Series</Text>
        <FlatList scrollEnabled={false} data={MOCK_TESTS} keyExtractor={item => item.id} renderItem={({ item }) => <TestCard item={item} onPress={() => navigation.navigate('TestDetail', { test: item })} />} />
      </View>
    </ScrollView>
  );
};

const MyTestsScreen = () => {
  return (
    <ScrollView style={styles.container}>
      <View style={styles.contentPad}>
        <Text style={[styles.sectionTitle, { marginTop: 15 }]}>Enrolled Test Series</Text>
        {ENROLLED_TESTS.map(test => (
          <TouchableOpacity key={test.id} style={styles.card}>
            <View style={{ flex: 1 }}>
              <Text style={styles.cardTitle}>{test.title}</Text>
              <View style={styles.progressBarBg}><View style={[styles.progressBarFill, { width: test.progress as DimensionValue }]} /></View>
              <Text style={styles.metricText}>Progress: {test.progress}</Text>
            </View>
            <Ionicons name="chevron-forward" size={24} color="#9ca3af" />
          </TouchableOpacity>
        ))}
      </View>
    </ScrollView>
  );
};

// --- Testbook-Style Profile Screen ---
const ProfileScreen = ({ navigation }: any) => {
  return (
    <ScrollView style={styles.container}>
      {/* Testbook Style Header */}
      <View style={styles.profileHeaderAlt}>
        <View style={styles.profileHeaderContent}>
          <View style={styles.avatarPlaceholderAlt}>
            <Text style={styles.avatarTextAlt}>S</Text>
          </View>
          <View style={{ flex: 1, marginLeft: 15 }}>
            <Text style={styles.profileNameAlt}>Student Name</Text>
            <Text style={styles.profileEmailAlt}>+91 9876543210</Text>
          </View>
          <TouchableOpacity style={styles.editIconBtn} onPress={() => navigation.navigate('EditProfile')}>
            <Ionicons name="pencil" size={20} color="white" />
          </TouchableOpacity>
        </View>
      </View>

      {/* Top Quick Stats or Banner replacing the Pro Pass */}
      <View style={styles.contentPadAlt}>
        <View style={styles.statsBannerRow}>
          <View style={styles.statsBox}>
            <Text style={styles.statsValue}>14</Text>
            <Text style={styles.statsLabel}>Tests Taken</Text>
          </View>
          <View style={styles.statsBox}>
            <Text style={styles.statsValue}>88%</Text>
            <Text style={styles.statsLabel}>Avg Score</Text>
          </View>
        </View>

        {/* Quick Links Grid */}
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

        {/* List Menu */}
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

        <TouchableOpacity style={styles.logoutButtonAlt} onPress={() => navigation.replace('Login')}>
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
const AttemptHistoryScreen = () => (
  <ScrollView style={styles.container}>
    <View style={styles.contentPadAlt}>
      <View style={styles.card}>
        <View style={styles.flexRowBetween}>
          <Text style={styles.cardTitle}>SSC CGL Full Mock 1</Text>
          <Text style={styles.scoreText}>120/200</Text>
        </View>
        <Text style={styles.metricText}>Attempted on Jan 14, 2026</Text>
        <Text style={styles.metricText}>Percentile: 94.5% - <Text style={{ color: '#10b981', fontWeight: 'bold' }}>Excellent</Text></Text>
      </View>
    </View>
  </ScrollView>
);
const ReferEarnScreen = () => (
  <View style={styles.detailContainer}>
    <Text style={styles.detailTitle}>🎁 Refer & Earn</Text>
    <Text style={[styles.metricText, { marginTop: 15, fontSize: 16, lineHeight: 24 }]}>Refer a friend and both of you get 10% off your next EdTech Pass PRO purchase! Use code S10X9A.</Text>
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
const EditProfileScreen = () => (
  <View style={styles.detailContainer}>
    <Text style={styles.detailTitle}>Edit Profile</Text>
    <TextInput style={[styles.input, { marginTop: 20 }]} placeholder="Full Name" defaultValue="Student Name" />
    <TextInput style={styles.input} placeholder="Phone Number" keyboardType="phone-pad" defaultValue="+91 9876543210" />
    <TextInput style={styles.input} placeholder="Email" defaultValue="student@example.com" />
    <TouchableOpacity style={styles.button}><Text style={styles.buttonText}>Save Changes</Text></TouchableOpacity>
  </View>
);
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
    <Text style={[styles.metricText, { marginTop: 15, fontSize: 16 }]}>For all queries, technical issues, or refund requests, please email us directly at support@edtech.com</Text>
  </View>
);

const TestDetailScreen = ({ route }: any) => {
  const { test } = route.params;
  return (
    <ScrollView style={styles.detailContainer}>
      <Text style={styles.detailTitle}>{test.title}</Text>
      <View style={{ flexDirection: 'row', marginTop: 10, marginBottom: 20 }}><Text style={styles.tag}>{test.tags}</Text></View>
      <View style={{ marginTop: 40 }}>
        <TouchableOpacity style={test.isFree ? styles.button : styles.buttonDisabled}>
          <Text style={styles.buttonText}>{test.isFree ? 'Start Test' : 'Purchase on Website'}</Text>
        </TouchableOpacity>
      </View>
    </ScrollView>
  );
};

// --- NAVIGATION CONFIG ---
const MainTabs = () => {
  return (
    <Tab.Navigator
      screenOptions={({ route }) => ({
        tabBarIcon: ({ focused, color, size }) => {
          let iconName: any = 'home';
          if (route.name === 'HomeTab') iconName = focused ? 'home' : 'home-outline';
          else if (route.name === 'MyTestsTab') iconName = focused ? 'document-text' : 'document-text-outline';
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
      <Tab.Screen name="HomeTab" component={HomeScreen} options={{ title: 'Home', headerShown: false }} />
      <Tab.Screen name="MyTestsTab" component={MyTestsScreen} options={{ title: 'My Tests' }} />
      <Tab.Screen name="ProfileTab" component={ProfileScreen} options={{ title: 'Profile', headerShown: false }} />
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
        {/* Testbook Sub-Screens */}
        <Stack.Screen name="EditProfile" component={EditProfileScreen} options={{ title: 'Edit Profile' }} />
        <Stack.Screen name="SavedQuestions" component={SavedQuestionsScreen} options={{ title: 'Saved Questions' }} />
        <Stack.Screen name="Downloads" component={DownloadsScreen} options={{ title: 'Downloads' }} />
        <Stack.Screen name="AttemptHistory" component={AttemptHistoryScreen} options={{ title: 'Attempt History' }} />
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
});
