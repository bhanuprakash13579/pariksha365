import { useState } from 'react';
import { api } from '../services/api';

export const ForgotPassword = () => {
    const [step, setStep] = useState<'request' | 'reset' | 'done'>('request');
    const [email, setEmail] = useState('');
    const [token, setToken] = useState('');
    const [newPassword, setNewPassword] = useState('');
    const [confirmPassword, setConfirmPassword] = useState('');
    const [message, setMessage] = useState('');
    const [error, setError] = useState('');
    const [loading, setLoading] = useState(false);

    const handleRequestReset = async (e: React.FormEvent) => {
        e.preventDefault();
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

    const handleResetPassword = async (e: React.FormEvent) => {
        e.preventDefault();
        setError('');
        if (newPassword !== confirmPassword) {
            setError('Passwords do not match.');
            return;
        }
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
        <div className="min-h-screen bg-gray-50 flex flex-col justify-center py-12 sm:px-6 lg:px-8">
            <div className="sm:mx-auto sm:w-full sm:max-w-md">
                <h2 className="mt-6 text-center text-3xl font-extrabold text-gray-900">
                    {step === 'done' ? 'Password Reset!' : 'Forgot Password'}
                </h2>
                <p className="mt-2 text-center text-sm text-gray-600">
                    {step === 'request' && "Enter your email and we'll send you a reset token."}
                    {step === 'reset' && "Enter the reset token and your new password."}
                    {step === 'done' && "Your password has been successfully changed."}
                </p>
            </div>

            <div className="mt-8 sm:mx-auto sm:w-full sm:max-w-md">
                <div className="bg-white py-8 px-4 shadow sm:rounded-lg sm:px-10 border border-gray-100">

                    {error && (
                        <div className="mb-4 p-3 bg-red-50 border border-red-200 rounded-md">
                            <p className="text-sm text-red-600">{error}</p>
                        </div>
                    )}

                    {message && step !== 'request' && (
                        <div className="mb-4 p-3 bg-green-50 border border-green-200 rounded-md">
                            <p className="text-sm text-green-600">{message}</p>
                        </div>
                    )}

                    {step === 'request' && (
                        <form className="space-y-6" onSubmit={handleRequestReset}>
                            <div>
                                <label className="block text-sm font-medium text-gray-700">Email address</label>
                                <div className="mt-1">
                                    <input type="email" value={email} onChange={(e) => setEmail(e.target.value)} required className="appearance-none block w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm placeholder-gray-400 focus:outline-none focus:ring-orange-500 focus:border-orange-500 sm:text-sm" />
                                </div>
                            </div>
                            <button type="submit" disabled={loading} className="w-full flex justify-center py-2 px-4 border border-transparent rounded-md shadow-sm text-sm font-medium text-white bg-orange-600 hover:bg-orange-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-orange-500 disabled:opacity-50">
                                {loading ? 'Sending...' : 'Send Reset Token'}
                            </button>
                        </form>
                    )}

                    {step === 'reset' && (
                        <form className="space-y-6" onSubmit={handleResetPassword}>
                            <div>
                                <label className="block text-sm font-medium text-gray-700">Reset Token</label>
                                <div className="mt-1">
                                    <input type="text" value={token} onChange={(e) => setToken(e.target.value)} required placeholder="Paste the token from the message above" className="appearance-none block w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm placeholder-gray-400 focus:outline-none focus:ring-orange-500 focus:border-orange-500 sm:text-sm" />
                                </div>
                            </div>
                            <div>
                                <label className="block text-sm font-medium text-gray-700">New Password</label>
                                <div className="mt-1">
                                    <input type="password" value={newPassword} onChange={(e) => setNewPassword(e.target.value)} required className="appearance-none block w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm placeholder-gray-400 focus:outline-none focus:ring-orange-500 focus:border-orange-500 sm:text-sm" />
                                </div>
                            </div>
                            <div>
                                <label className="block text-sm font-medium text-gray-700">Confirm New Password</label>
                                <div className="mt-1">
                                    <input type="password" value={confirmPassword} onChange={(e) => setConfirmPassword(e.target.value)} required className="appearance-none block w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm placeholder-gray-400 focus:outline-none focus:ring-orange-500 focus:border-orange-500 sm:text-sm" />
                                </div>
                            </div>
                            <button type="submit" disabled={loading} className="w-full flex justify-center py-2 px-4 border border-transparent rounded-md shadow-sm text-sm font-medium text-white bg-orange-600 hover:bg-orange-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-orange-500 disabled:opacity-50">
                                {loading ? 'Resetting...' : 'Reset Password'}
                            </button>
                        </form>
                    )}

                    {step === 'done' && (
                        <div className="text-center">
                            <div className="text-green-500 text-5xl mb-4">✓</div>
                            <a href="/auth" className="font-medium text-orange-600 hover:text-orange-500">
                                Go back to Sign In
                            </a>
                        </div>
                    )}

                    {step !== 'done' && (
                        <p className="mt-6 text-center text-sm text-gray-600">
                            Remember your password?{' '}
                            <a href="/auth" className="font-medium text-orange-600 hover:text-orange-500">Sign in</a>
                        </p>
                    )}
                </div>
            </div>
        </div>
    );
};
