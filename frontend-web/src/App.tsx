import { lazy, Suspense } from 'react';
import { BrowserRouter as Router, Routes, Route, Navigate } from 'react-router-dom';
import { GoogleOAuthProvider } from '@react-oauth/google';
import { Auth } from './pages/Auth';
import { Onboarding } from './pages/Onboarding';

// Code-split everything past the auth screen. The student bundle no longer
// ships the admin dashboard (884-line quiz manager + analytics), the mock-test
// interface, the marketing/legal pages, or the payment screens. Each route
// downloads only when visited, so the auth → dashboard cold-start handshake is
// dramatically smaller. The Suspense fallback uses the same loading spinner
// the inner pages already use, so there is no visible regression.
const AdminDashboard = lazy(() =>
    import('./pages/AdminDashboard').then(m => ({ default: m.AdminDashboard }))
);
const MockTestInterface = lazy(() =>
    import('./pages/MockTestInterface').then(m => ({ default: m.MockTestInterface }))
);
const StudentDashboard = lazy(() =>
    import('./pages/Dashboard').then(m => ({ default: m.StudentDashboard }))
);
const PrivacyPolicy = lazy(() =>
    import('./pages/PrivacyPolicy').then(m => ({ default: m.PrivacyPolicy }))
);
const TermsAndConditions = lazy(() =>
    import('./pages/TermsAndConditions').then(m => ({ default: m.TermsAndConditions }))
);
const ForgotPassword = lazy(() =>
    import('./pages/ForgotPassword').then(m => ({ default: m.ForgotPassword }))
);
const Quiz = lazy(() =>
    import('./pages/Quiz').then(m => ({ default: m.Quiz }))
);
const PostTestResults = lazy(() =>
    import('./pages/PostTestResults').then(m => ({ default: m.PostTestResults }))
);
const PaymentSuccess = lazy(() =>
    import('./pages/PaymentPages').then(m => ({ default: m.PaymentSuccess }))
);
const PaymentCancelled = lazy(() =>
    import('./pages/PaymentPages').then(m => ({ default: m.PaymentCancelled }))
);
const CashfreeReturn = lazy(() =>
    import('./pages/PaymentPages').then(m => ({ default: m.CashfreeReturn }))
);
const Notes = lazy(() =>
    import('./pages/Notes').then(m => ({ default: m.Notes }))
);

const GOOGLE_CLIENT_ID = "592393648560-o4ou87jvmv6tj3uura8ls27td06pv0o5.apps.googleusercontent.com";

const RouteFallback = () => (
    <div className="min-h-screen bg-gray-100 flex items-center justify-center">
        <div className="text-center">
            <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-orange-600 mx-auto"></div>
            <p className="mt-4 text-gray-500 font-medium">Loading...</p>
        </div>
    </div>
);

function App() {
    return (
        <GoogleOAuthProvider clientId={GOOGLE_CLIENT_ID}>
            <Router>
                <Suspense fallback={<RouteFallback />}>
                    <Routes>
                        <Route path="/" element={<Navigate to="/auth" />} />
                        <Route path="/auth" element={<Auth />} />
                        <Route path="/onboarding" element={<Onboarding />} />
                        <Route path="/dashboard" element={<StudentDashboard />} />
                        <Route path="/admin" element={<AdminDashboard />} />
                        <Route path="/mock-test/:testId" element={<MockTestInterface />} />
                        <Route path="/mock-test" element={<MockTestInterface />} />
                        <Route path="/quiz" element={<Quiz />} />
                        <Route path="/results/:attemptId" element={<PostTestResults />} />
                        <Route path="/payment-success" element={<PaymentSuccess />} />
                        <Route path="/payment-cancelled" element={<PaymentCancelled />} />
                        <Route path="/payment/return" element={<CashfreeReturn />} />
                        <Route path="/notes" element={<Notes />} />
                        <Route path="/privacy" element={<PrivacyPolicy />} />
                        <Route path="/terms" element={<TermsAndConditions />} />
                        <Route path="/forgot-password" element={<ForgotPassword />} />
                    </Routes>
                </Suspense>
            </Router>
        </GoogleOAuthProvider>
    );
}

export default App;

