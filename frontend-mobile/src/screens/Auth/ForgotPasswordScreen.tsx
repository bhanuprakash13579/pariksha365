import React, { useState } from 'react';
import { View, Text, TextInput, TouchableOpacity, Alert, SafeAreaView, KeyboardAvoidingView, Platform, ActivityIndicator, ScrollView } from 'react-native';
import { Ionicons } from '@expo/vector-icons';
import { api } from '../../services/api';
import { COLORS } from '../../styles/theme';

export default function ForgotPasswordScreen({ navigation }: any) {
    const [step, setStep] = useState<'request' | 'reset' | 'done'>('request');
    const [email, setEmail] = useState('');
    const [token, setToken] = useState('');
    const [newPassword, setNewPassword] = useState('');
    const [confirmPassword, setConfirmPassword] = useState('');
    const [message, setMessage] = useState('');
    const [error, setError] = useState('');
    const [loading, setLoading] = useState(false);

    const handleRequestReset = async () => {
        if (!email) { Alert.alert('Error', 'Please enter your email address.'); return; }
        setError('');
        setLoading(true);
        try {
            const response = await api.post('/auth/forgot-password', { email });
            setMessage(response.data.message);
            setStep('reset');
        } catch (err: any) {
            setError(err.response?.data?.detail || 'Failed to request password reset.');
        } finally {
            setLoading(false);
        }
    };

    const handleResetPassword = async () => {
        if (!token || !newPassword || !confirmPassword) {
            Alert.alert('Error', 'Please fill all fields.');
            return;
        }
        if (newPassword !== confirmPassword) {
            setError('Passwords do not match.');
            return;
        }
        setError('');
        setLoading(true);
        try {
            const response = await api.post('/auth/reset-password', { token, new_password: newPassword });
            setMessage(response.data.message);
            setStep('done');
        } catch (err: any) {
            setError(err.response?.data?.detail || 'Failed to reset password. Token may be invalid or expired.');
        } finally {
            setLoading(false);
        }
    };

    return (
        <SafeAreaView style={{ flex: 1, backgroundColor: '#ffffff' }}>
            <KeyboardAvoidingView behavior={Platform.OS === 'ios' ? 'padding' : 'height'} style={{ flex: 1 }}>
                <ScrollView contentContainerStyle={{ flexGrow: 1, padding: 24 }}>
                    {/* Back Button */}
                    <TouchableOpacity
                        onPress={() => navigation.goBack()}
                        style={{ flexDirection: 'row', alignItems: 'center', marginBottom: 30 }}
                    >
                        <Ionicons name="arrow-back" size={22} color="#374151" />
                        <Text style={{ color: '#374151', fontSize: 16, marginLeft: 8, fontWeight: '500' }}>Back</Text>
                    </TouchableOpacity>

                    {/* Header */}
                    <View style={{ alignItems: 'center', marginBottom: 30 }}>
                        <View style={{
                            width: 64, height: 64, borderRadius: 32,
                            backgroundColor: step === 'done' ? '#dcfce7' : '#fff7ed',
                            alignItems: 'center', justifyContent: 'center', marginBottom: 16,
                            borderWidth: 1, borderColor: step === 'done' ? '#bbf7d0' : '#fed7aa'
                        }}>
                            <Ionicons
                                name={step === 'done' ? 'checkmark-circle' : 'lock-closed'}
                                size={32}
                                color={step === 'done' ? '#16a34a' : COLORS.primary}
                            />
                        </View>
                        <Text style={{ fontSize: 26, fontWeight: '800', color: '#111827', textAlign: 'center' }}>
                            {step === 'done' ? 'Password Reset!' : 'Forgot Password'}
                        </Text>
                        <Text style={{ fontSize: 14, color: '#6b7280', textAlign: 'center', marginTop: 8, lineHeight: 20 }}>
                            {step === 'request' && "Enter your email and we'll send you a reset token."}
                            {step === 'reset' && "Enter the reset token and your new password."}
                            {step === 'done' && "Your password has been successfully changed."}
                        </Text>
                    </View>

                    {/* Error Banner */}
                    {error ? (
                        <View style={{
                            backgroundColor: '#fef2f2', borderWidth: 1, borderColor: '#fecaca',
                            borderRadius: 12, padding: 12, marginBottom: 16, flexDirection: 'row', alignItems: 'center'
                        }}>
                            <Ionicons name="alert-circle" size={18} color="#dc2626" style={{ marginRight: 8 }} />
                            <Text style={{ color: '#b91c1c', fontSize: 13, flex: 1 }}>{error}</Text>
                        </View>
                    ) : null}

                    {/* Success Banner */}
                    {message && step !== 'request' && step !== 'done' ? (
                        <View style={{
                            backgroundColor: '#f0fdf4', borderWidth: 1, borderColor: '#bbf7d0',
                            borderRadius: 12, padding: 12, marginBottom: 16, flexDirection: 'row', alignItems: 'center'
                        }}>
                            <Ionicons name="checkmark-circle" size={18} color="#16a34a" style={{ marginRight: 8 }} />
                            <Text style={{ color: '#166534', fontSize: 13, flex: 1 }}>{message}</Text>
                        </View>
                    ) : null}

                    {/* Step 1: Request Reset */}
                    {step === 'request' && (
                        <View>
                            <Text style={{ fontSize: 13, fontWeight: '600', color: '#374151', marginBottom: 6 }}>Email Address</Text>
                            <TextInput
                                style={{
                                    backgroundColor: '#f3f4f6', borderRadius: 12, padding: 16, fontSize: 16,
                                    color: '#1f2937', borderWidth: 1, borderColor: '#e5e7eb', marginBottom: 20,
                                }}
                                placeholder="you@example.com"
                                placeholderTextColor="#9ca3af"
                                keyboardType="email-address"
                                autoCapitalize="none"
                                value={email}
                                onChangeText={setEmail}
                            />
                            <TouchableOpacity
                                onPress={handleRequestReset}
                                disabled={loading}
                                style={{
                                    backgroundColor: loading ? '#d1d5db' : COLORS.primary,
                                    borderRadius: 12, padding: 16, alignItems: 'center',
                                    shadowColor: COLORS.primary, shadowOpacity: 0.3, shadowRadius: 8,
                                    shadowOffset: { width: 0, height: 4 }, elevation: 5,
                                }}
                            >
                                {loading ? <ActivityIndicator color="#fff" /> :
                                    <Text style={{ color: '#fff', fontSize: 16, fontWeight: 'bold' }}>Send Reset Token</Text>}
                            </TouchableOpacity>
                        </View>
                    )}

                    {/* Step 2: Enter Token + New Password */}
                    {step === 'reset' && (
                        <View>
                            <Text style={{ fontSize: 13, fontWeight: '600', color: '#374151', marginBottom: 6 }}>Reset Token</Text>
                            <TextInput
                                style={{
                                    backgroundColor: '#f3f4f6', borderRadius: 12, padding: 16, fontSize: 16,
                                    color: '#1f2937', borderWidth: 1, borderColor: '#e5e7eb', marginBottom: 16,
                                }}
                                placeholder="Paste the token from the message above"
                                placeholderTextColor="#9ca3af"
                                value={token}
                                onChangeText={setToken}
                            />
                            <Text style={{ fontSize: 13, fontWeight: '600', color: '#374151', marginBottom: 6 }}>New Password</Text>
                            <TextInput
                                style={{
                                    backgroundColor: '#f3f4f6', borderRadius: 12, padding: 16, fontSize: 16,
                                    color: '#1f2937', borderWidth: 1, borderColor: '#e5e7eb', marginBottom: 16,
                                }}
                                placeholder="Enter new password"
                                placeholderTextColor="#9ca3af"
                                secureTextEntry
                                value={newPassword}
                                onChangeText={setNewPassword}
                            />
                            <Text style={{ fontSize: 13, fontWeight: '600', color: '#374151', marginBottom: 6 }}>Confirm Password</Text>
                            <TextInput
                                style={{
                                    backgroundColor: '#f3f4f6', borderRadius: 12, padding: 16, fontSize: 16,
                                    color: '#1f2937', borderWidth: 1, borderColor: '#e5e7eb', marginBottom: 20,
                                }}
                                placeholder="Confirm new password"
                                placeholderTextColor="#9ca3af"
                                secureTextEntry
                                value={confirmPassword}
                                onChangeText={setConfirmPassword}
                            />
                            <TouchableOpacity
                                onPress={handleResetPassword}
                                disabled={loading}
                                style={{
                                    backgroundColor: loading ? '#d1d5db' : COLORS.primary,
                                    borderRadius: 12, padding: 16, alignItems: 'center',
                                    shadowColor: COLORS.primary, shadowOpacity: 0.3, shadowRadius: 8,
                                    shadowOffset: { width: 0, height: 4 }, elevation: 5,
                                }}
                            >
                                {loading ? <ActivityIndicator color="#fff" /> :
                                    <Text style={{ color: '#fff', fontSize: 16, fontWeight: 'bold' }}>Reset Password</Text>}
                            </TouchableOpacity>
                        </View>
                    )}

                    {/* Step 3: Done */}
                    {step === 'done' && (
                        <View style={{ alignItems: 'center' }}>
                            <TouchableOpacity
                                onPress={() => navigation.navigate('Login')}
                                style={{
                                    backgroundColor: COLORS.primary, borderRadius: 12,
                                    paddingVertical: 16, paddingHorizontal: 40, alignItems: 'center',
                                    marginTop: 20,
                                }}
                            >
                                <Text style={{ color: '#fff', fontSize: 16, fontWeight: 'bold' }}>Go to Sign In</Text>
                            </TouchableOpacity>
                        </View>
                    )}

                    {/* Footer link */}
                    {step !== 'done' && (
                        <TouchableOpacity onPress={() => navigation.navigate('Login')} style={{ marginTop: 30, alignItems: 'center' }}>
                            <Text style={{ color: '#4b5563', fontSize: 14 }}>
                                Remember your password? <Text style={{ color: COLORS.primary, fontWeight: 'bold' }}>Sign in</Text>
                            </Text>
                        </TouchableOpacity>
                    )}
                </ScrollView>
            </KeyboardAvoidingView>
        </SafeAreaView>
    );
}
