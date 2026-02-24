import { BrowserRouter as Router, Routes, Route, Navigate } from 'react-router-dom';
import { AdminDashboard } from './pages/AdminDashboard';
import { MockTestInterface } from './pages/MockTestInterface';
import { Auth } from './pages/Auth';
import { StudentDashboard } from './pages/Dashboard';
import { PrivacyPolicy } from './pages/PrivacyPolicy';

function App() {
    return (
        <Router>
            <Routes>
                <Route path="/" element={<Navigate to="/auth" />} />
                <Route path="/auth" element={<Auth />} />
                <Route path="/dashboard" element={<StudentDashboard />} />
                <Route path="/admin" element={<AdminDashboard />} />
                <Route path="/mock-test" element={<MockTestInterface />} />
                <Route path="/privacy" element={<PrivacyPolicy />} />
            </Routes>
        </Router>
    );
}

export default App;
