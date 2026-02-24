import React, { useState } from 'react';
import { View, Text, TextInput, TouchableOpacity, Alert, Platform, KeyboardAvoidingView, SafeAreaView, ActivityIndicator } from 'react-native';
import { Ionicons } from '@expo/vector-icons';
import * as Google from 'expo-auth-session/providers/google';
import * as AppleAuthentication from 'expo-apple-authentication';
import AsyncStorage from '@react-native-async-storage/async-storage';
import { AuthAPI } from '../../services/api';
import { styles } from '../../styles/theme';

const GOOGLE_IOS_CLIENT_ID = "592393648560-0csjsd0dvukv94qg05np14rj1v3o9gg2.apps.googleusercontent.com";
const GOOGLE_WEB_CLIENT_ID = "592393648560-70fdb8qfubom1sllvmb29ststk1h1k0v.apps.googleusercontent.com";
const GOOGLE_ANDROID_CLIENT_ID = "592393648560-tk26aam18hnsd38dskfkt64td6l23ebv.apps.googleusercontent.com";

export default function SignupScreen({ navigation }: any) {
    const [name, setName] = useState('');
    const [email, setEmail] = useState('');
    const [password, setPassword] = useState('');
    const [loading, setLoading] = useState(false);
    const [request, response, promptAsync] = Google.useAuthRequest({
        iosClientId: GOOGLE_IOS_CLIENT_ID,
        webClientId: GOOGLE_WEB_CLIENT_ID,
        androidClientId: GOOGLE_ANDROID_CLIENT_ID,
    });

    React.useEffect(() => {
        if (response?.type === 'success') {
            navigation.replace('MainTabs', { isGuest: false });
        }
    }, [response]);

    const handleAppleAuth = async () => {
        try {
            await AppleAuthentication.signInAsync({
                requestedScopes: [
                    AppleAuthentication.AppleAuthenticationScope.FULL_NAME,
                    AppleAuthentication.AppleAuthenticationScope.EMAIL,
                ],
            });
            navigation.replace('MainTabs', { isGuest: false });
        } catch (e: any) {
            if (e.code !== 'ERR_REQUEST_CANCELED') Alert.alert('Authentication Failed', 'Apple Sign in failed.');
        }
    };

    const handleGoogleAuth = () => { promptAsync(); };

    const handleSignup = async () => {
        if (!name || !email || !password) { Alert.alert('Error', 'Please fill all fields.'); return; }
        setLoading(true);
        try {
            await AuthAPI.signup(name, email, password);
            const loginRes = await AuthAPI.login(email, password);
            await AsyncStorage.setItem('token', loginRes.data.access_token);
            navigation.replace('MainTabs', { isGuest: false });
        } catch (err: any) {
            Alert.alert('Signup Failed', err.response?.data?.detail || 'Could not create account.');
        } finally { setLoading(false); }
    };

    return (
        <SafeAreaView style={styles.authContainer}>
            <KeyboardAvoidingView behavior={Platform.OS === 'ios' ? 'padding' : 'height'} style={styles.authInner}>
                <Text style={styles.authTitle}>Create Account</Text>
                <Text style={[styles.authSubtitle, { marginBottom: 20 }]}>Start your preparation journey today</Text>
                <View style={styles.formContainer}>
                    <TextInput style={styles.input} placeholder="Full Name" placeholderTextColor="#9ca3af" value={name} onChangeText={setName} />
                    <TextInput style={styles.input} placeholder="Email" placeholderTextColor="#9ca3af" keyboardType="email-address" autoCapitalize="none" value={email} onChangeText={setEmail} />
                    <TextInput style={styles.input} placeholder="Password" placeholderTextColor="#9ca3af" secureTextEntry value={password} onChangeText={setPassword} />
                    <TouchableOpacity style={loading ? styles.buttonDisabled : styles.primaryButton} onPress={handleSignup} disabled={loading}>
                        {loading ? <ActivityIndicator color="#fff" /> : <Text style={styles.primaryButtonText}>Sign Up</Text>}
                    </TouchableOpacity>

                    <View style={styles.dividerRow}>
                        <View style={styles.divider} /><Text style={styles.dividerText}>OR</Text><View style={styles.divider} />
                    </View>

                    {Platform.OS === 'ios' && (
                        <AppleAuthentication.AppleAuthenticationButton
                            buttonType={AppleAuthentication.AppleAuthenticationButtonType.SIGN_UP}
                            buttonStyle={AppleAuthentication.AppleAuthenticationButtonStyle.BLACK}
                            cornerRadius={12}
                            style={{ width: '100%', height: 50, marginBottom: 15 }}
                            onPress={handleAppleAuth}
                        />
                    )}

                    <TouchableOpacity style={styles.socialButton} onPress={handleGoogleAuth}>
                        <Ionicons name="logo-google" size={24} color="#db4437" />
                        <Text style={styles.socialButtonText}>Sign up with Google</Text>
                    </TouchableOpacity>

                    <TouchableOpacity style={{ marginTop: 20, alignItems: 'center' }} onPress={() => navigation.navigate('Login')}>
                        <Text style={{ color: '#4b5563', fontSize: 14 }}>Already have an account? <Text style={{ color: '#f97316', fontWeight: 'bold' }}>Log In</Text></Text>
                    </TouchableOpacity>
                </View>
            </KeyboardAvoidingView>
        </SafeAreaView>
    );
}
