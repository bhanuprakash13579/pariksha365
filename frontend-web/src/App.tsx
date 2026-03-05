import { BrowserRouter as Router, Routes, Route, Navigate } from 'react-router-dom';
import { GoogleOAuthProvider } from '@react-oauth/google';
import { AdminDashboard } from './pages/AdminDashboard';
import { MockTestInterface } from './pages/MockTestInterface';
import { Auth } from './pages/Auth';
import { Onboarding } from './pages/Onboarding';
import { StudentDashboard } from './pages/Dashboard';
import { PrivacyPolicy } from './pages/PrivacyPolicy';
import { TermsAndConditions } from './pages/TermsAndConditions';
import { ForgotPassword } from './pages/ForgotPassword';
import { Quiz } from './pages/Quiz';
import { PostTestResults } from './pages/PostTestResults';
import { PaymentSuccess, PaymentCancelled } from './pages/PaymentPages';

const GOOGLE_CLIENT_ID = "592393648560-o4ou87jvmv6tj3uura8ls27td06pv0o5.apps.googleusercontent.com";

function App() {
    return (
        <GoogleOAuthProvider clientId={GOOGLE_CLIENT_ID}>
            <Router>
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
                    <Route path="/privacy" element={<PrivacyPolicy />} />
                    <Route path="/terms" element={<TermsAndConditions />} />
                    <Route path="/forgot-password" element={<ForgotPassword />} />
                </Routes>
            </Router>
        </GoogleOAuthProvider>
    );
}

export default App;

