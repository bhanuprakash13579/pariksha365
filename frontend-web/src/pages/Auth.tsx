import { useState } from 'react';
import { useNavigate, Link } from 'react-router-dom';
import { useDispatch } from 'react-redux';
import { GoogleLogin } from '@react-oauth/google';
import { loginUser, signupUser, googleLogin } from '../store/slices/authSlice';
import { UserAPI } from '../services/api';

export const Auth = () => {
    const [isLogin, setIsLogin] = useState(true);
    const [email, setEmail] = useState('');
    const [password, setPassword] = useState('');
    const [name, setName] = useState('');
    const [error, setError] = useState('');
    const [loading, setLoading] = useState(false);
    const dispatch = useDispatch();
    const navigate = useNavigate();

    const handleNavigationAfterLogin = async (token?: string) => {
        try {
            // Give localStorage a tiny tick to settle, or pass token directly to headers
            if (token) {
                localStorage.setItem('token', token);
            }
            const res = await UserAPI.getMe();
            if (res.data.role?.name?.toLowerCase() === 'admin') {
                navigate('/admin');
            } else if (!res.data.selected_exam_category_id) {
                navigate('/onboarding');
            } else {
                navigate('/dashboard');
            }
        } catch (e) {
            navigate('/dashboard');
        }
    };

    const handleSubmit = async (e: React.FormEvent) => {
        e.preventDefault();
        setError('');
        setLoading(true);
        try {
            if (isLogin) {
                // @ts-ignore
                const resultAction = await dispatch(loginUser({ email, password }));
                if (loginUser.fulfilled.match(resultAction)) {
                    await handleNavigationAfterLogin((resultAction.payload as any).access_token);
                } else {
                    setError((resultAction.payload as any)?.detail || 'Login failed. Please check your credentials.');
                }
            } else {
                // @ts-ignore
                const resultAction = await dispatch(signupUser({ name, email, password }));
                if (signupUser.fulfilled.match(resultAction)) {
                    // Auto-login after signup
                    // @ts-ignore
                    const loginResult = await dispatch(loginUser({ email, password }));
                    if (loginUser.fulfilled.match(loginResult)) {
                        await handleNavigationAfterLogin((loginResult.payload as any).access_token);
                    }
                } else {
                    setError((resultAction.payload as any)?.detail || 'Signup failed. Please try again.');
                }
            }
        } catch (err) {
            setError('An unexpected error occurred.');
        } finally {
            setLoading(false);
        }
    };

    const handleGoogleSuccess = async (credentialResponse: any) => {
        setError('');
        setLoading(true);
        try {
            // @ts-ignore
            const resultAction = await dispatch(googleLogin(credentialResponse.credential));
            if (googleLogin.fulfilled.match(resultAction)) {
                await handleNavigationAfterLogin((resultAction.payload as any).access_token);
            } else {
                setError((resultAction.payload as any)?.detail || 'Google Sign-In failed.');
            }
        } catch (err) {
            setError('An unexpected error occurred during Google Sign-In.');
        } finally {
            setLoading(false);
        }
    };

    return (
        <div className="min-h-screen bg-gray-50 flex">
            {/* Left Desktop Pane - Premium Gradient & Messaging */}
            <div className="hidden lg:flex lg:w-1/2 bg-gradient-to-br from-orange-500 via-orange-600 to-red-600 p-12 text-white justify-center items-center relative overflow-hidden">
                <div
                    className="absolute top-0 left-0 w-full h-full opacity-10 pointer-events-none"
                    style={{ backgroundImage: 'radial-gradient(circle at 20% 30%, white 1px, transparent 1px)', backgroundSize: '24px 24px' }}
                ></div>
                <div className="absolute top-[-10%] left-[-10%] w-96 h-96 bg-white opacity-10 rounded-full blur-3xl pointer-events-none"></div>
                <div className="absolute bottom-[-10%] right-[-10%] w-96 h-96 bg-red-900 opacity-20 rounded-full blur-3xl pointer-events-none"></div>

                <div className="max-w-xl z-10 text-center transform transition-all hover:scale-105 duration-500 ease-out">
                    <h1 className="text-5xl font-extrabold mb-6 tracking-tight drop-shadow-md">Unlock Your Potential</h1>
                    <p className="text-lg opacity-95 leading-relaxed font-medium">
                        Join Pariksha365 to access thousands of high-quality mock tests, personalized analytics, and expertly crafted study materials. Your journey to cracking the exam starts right here.
                    </p>
                    <div className="mt-12 grid grid-cols-2 gap-6 opacity-90">
                        <div className="p-5 bg-white/10 rounded-2xl backdrop-blur-md border border-white/20 shadow-xl">
                            <div className="text-4xl font-bold mb-1">10k+</div>
                            <div className="text-sm font-semibold uppercase tracking-wider">Active Students</div>
                        </div>
                        <div className="p-5 bg-white/10 rounded-2xl backdrop-blur-md border border-white/20 shadow-xl">
                            <div className="text-4xl font-bold mb-1">500+</div>
                            <div className="text-sm font-semibold uppercase tracking-wider">Mock Tests</div>
                        </div>
                    </div>
                </div>
            </div>

            {/* Right Auth Pane */}
            <div className="flex-1 flex flex-col justify-center py-12 px-6 sm:px-12 lg:px-20 xl:px-24 bg-white relative">
                <div className="mx-auto w-full max-w-sm lg:max-w-md">
                    <div className="text-center lg:text-left">
                        <div className="flex justify-center xl:hidden mb-6">
                            <div className="w-36 h-36 rounded-full bg-white shadow-xl ring-4 ring-orange-100 flex items-center justify-center overflow-hidden relative">
                                <img src="/logo_square.png" alt="Pariksha365 Logo" className="absolute top-0 left-0 w-full h-full object-cover object-center mix-blend-multiply drop-shadow-sm transition-transform duration-300 hover:scale-[2.8] scale-[2.7] translate-y-3 transform origin-center" />
                            </div>
                        </div>
                        <h2 className="text-3xl font-extrabold text-gray-900 tracking-tight">
                            {isLogin ? 'Welcome back' : 'Create an account'}
                        </h2>
                        <p className="mt-3 text-sm text-gray-600">
                            {isLogin ? "Don't have an account? " : "Already have an account? "}
                            <button
                                type="button"
                                onClick={() => { setIsLogin(!isLogin); setError(''); }}
                                className="font-bold text-orange-600 hover:text-orange-500 focus:outline-none transition-colors"
                            >
                                {isLogin ? 'Sign up for free' : 'Sign in instead'}
                            </button>
                        </p>
                    </div>

                    <div className="mt-8">
                        {error && (
                            <div className="mb-6 p-4 bg-red-50 border border-red-200 rounded-xl animate-fade-in shadow-sm">
                                <div className="flex">
                                    <div className="flex-shrink-0">
                                        <svg className="h-5 w-5 text-red-500" xmlns="http://www.w3.org/2000/svg" viewBox="0 0 20 20" fill="currentColor">
                                            <path fillRule="evenodd" d="M10 18a8 8 0 100-16 8 8 0 000 16zM8.28 7.22a.75.75 0 00-1.06 1.06L8.94 10l-1.72 1.72a.75.75 0 101.06 1.06L10 11.06l1.72 1.72a.75.75 0 101.06-1.06L11.06 10l1.72-1.72a.75.75 0 00-1.06-1.06L10 8.94 8.28 7.22z" clipRule="evenodd" />
                                        </svg>
                                    </div>
                                    <div className="ml-3">
                                        <p className="text-sm text-red-700 font-medium">{error}</p>
                                    </div>
                                </div>
                            </div>
                        )}

                        <form className="space-y-5" onSubmit={handleSubmit}>
                            {/* Inputs */}
                            {!isLogin && (
                                <div>
                                    <label className="block text-sm font-semibold text-gray-700 mb-1">Full Name</label>
                                    <input id="name" name="name" type="text" value={name} onChange={(e) => setName(e.target.value)} required className="appearance-none block w-full px-4 py-3 border border-gray-300 rounded-xl shadow-sm placeholder-gray-400 focus:outline-none focus:ring-2 focus:ring-orange-500 focus:border-transparent transition-all sm:text-sm" placeholder="John Doe" />
                                </div>
                            )}

                            <div>
                                <label className="block text-sm font-semibold text-gray-700 mb-1">Email address</label>
                                <input id="email" name="email" type="email" value={email} onChange={(e) => setEmail(e.target.value)} required className="appearance-none block w-full px-4 py-3 border border-gray-300 rounded-xl shadow-sm placeholder-gray-400 focus:outline-none focus:ring-2 focus:ring-orange-500 focus:border-transparent transition-all sm:text-sm" placeholder="you@example.com" />
                            </div>

                            <div>
                                <label className="block text-sm font-semibold text-gray-700 mb-1">Password</label>
                                <input id="password" name="password" type="password" value={password} onChange={(e) => setPassword(e.target.value)} required className="appearance-none block w-full px-4 py-3 border border-gray-300 rounded-xl shadow-sm placeholder-gray-400 focus:outline-none focus:ring-2 focus:ring-orange-500 focus:border-transparent transition-all sm:text-sm" placeholder="••••••••" />
                            </div>

                            {isLogin && (
                                <div className="flex items-center justify-between pt-2">
                                    <div className="flex items-center">
                                        <input id="remember-me" name="remember-me" type="checkbox" className="h-4 w-4 text-orange-600 focus:ring-orange-500 border-gray-300 rounded cursor-pointer" />
                                        <label htmlFor="remember-me" className="ml-2 block text-sm text-gray-700 cursor-pointer font-medium">Remember me</label>
                                    </div>

                                    <div className="text-sm">
                                        <Link to="/forgot-password" className="font-bold text-orange-600 hover:text-orange-500 transition-colors">Forgot password?</Link>
                                    </div>
                                </div>
                            )}

                            {!isLogin && (
                                <div className="flex items-start pt-2">
                                    <div className="flex items-center h-5">
                                        <input id="terms" name="terms" type="checkbox" required className="focus:ring-orange-500 h-4 w-4 text-orange-600 border-gray-300 rounded cursor-pointer mt-0.5" />
                                    </div>
                                    <div className="ml-3 text-sm">
                                        <label htmlFor="terms" className="text-gray-600 leading-tight">
                                            I agree to the{' '}
                                            <Link to="/terms" className="font-bold text-orange-600 hover:text-orange-500 transition-colors">Terms of Service</Link>
                                            {' '}and{' '}
                                            <Link to="/privacy" className="font-bold text-orange-600 hover:text-orange-500 transition-colors">Privacy Policy</Link>.
                                        </label>
                                    </div>
                                </div>
                            )}

                            <button
                                type="submit"
                                disabled={loading}
                                className="w-full flex justify-center mt-6 py-3.5 px-4 border border-transparent rounded-xl shadow-[0_4px_14px_0_rgba(249,115,22,0.39)] text-sm font-bold text-white bg-gradient-to-r from-orange-600 to-orange-500 hover:from-orange-700 hover:to-orange-600 hover:shadow-[0_6px_20px_rgba(249,115,22,0.23)] focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-orange-500 disabled:opacity-70 disabled:cursor-not-allowed transform hover:-translate-y-0.5 transition-all duration-200"
                            >
                                {loading ? (
                                    <svg className="animate-spin -ml-1 mr-3 h-5 w-5 text-white" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24"><circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4"></circle><path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path></svg>
                                ) : (isLogin ? 'Sign in to Dashboard' : 'Create Account')}
                            </button>
                        </form>

                        <div className="relative my-8">
                            <div className="absolute inset-0 flex items-center">
                                <div className="w-full border-t border-gray-200" />
                            </div>
                            <div className="relative flex justify-center lg:justify-start lg:pl-4 bg-white">
                                <span className="bg-white px-3 text-sm text-gray-500 font-medium">Or continue with</span>
                            </div>
                        </div>

                        <div className="flex justify-center lg:justify-start transform hover:scale-[1.02] transition-transform w-[250px] lg:w-auto mx-auto lg:mx-0">
                            <GoogleLogin
                                onSuccess={handleGoogleSuccess}
                                onError={() => setError('Google Sign-In was unsuccessful.')}
                                useOneTap
                                shape="rectangular"
                                size="large"
                                text="continue_with"
                            />
                        </div>
                    </div>
                </div>
            </div>
        </div>
    );
};
