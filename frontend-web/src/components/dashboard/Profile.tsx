import { useState, useEffect } from 'react';
import { UserAPI, AttemptAPI } from '../../services/api';
import { useDispatch } from 'react-redux';
import { logout } from '../../store/slices/authSlice';
import { useNavigate } from 'react-router-dom';

export const Profile = () => {
    const dispatch = useDispatch();
    const navigate = useNavigate();

    const [user, setUser] = useState<any>(null);
    const [attempts, setAttempts] = useState<any[]>([]);
    const [loading, setLoading] = useState(true);
    const [editing, setEditing] = useState(false);
    const [editName, setEditName] = useState('');
    const [editPhone, setEditPhone] = useState('');
    const [saving, setSaving] = useState(false);

    useEffect(() => {
        const fetchProfileData = async () => {
            try {
                const [userRes, attemptsRes] = await Promise.all([
                    UserAPI.getMe(),
                    AttemptAPI.list()
                ]);
                setUser(userRes.data);
                setAttempts(attemptsRes.data);
                setEditName(userRes.data.name || '');
                setEditPhone(userRes.data.phone || '');
            } catch (err) {
                console.error("Failed to load profile data:", err);
            } finally {
                setLoading(false);
            }
        };
        fetchProfileData();
    }, []);

    const handleLogout = () => {
        dispatch(logout());
        navigate('/auth');
    };

    const handleSaveProfile = async () => {
        setSaving(true);
        try {
            const res = await UserAPI.updateMe({ name: editName, phone: editPhone });
            setUser(res.data);
            setEditing(false);
        } catch (err) {
            alert('Failed to update profile.');
            console.error(err);
        } finally {
            setSaving(false);
        }
    };

    if (loading) {
        return (
            <div className="flex justify-center items-center py-20">
                <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-orange-600"></div>
            </div>
        );
    }

    const totalAttempts = attempts.length;
    const completedAttempts = attempts.filter(a => a.status === 'SUBMITTED').length;
    const completionRate = totalAttempts > 0 ? Math.round((completedAttempts / totalAttempts) * 100) : 0;

    return (
        <div className="max-w-4xl mx-auto py-8">
            <div className="bg-white rounded-2xl overflow-hidden border border-gray-100 shadow-sm mb-8">
                <div className="h-32 bg-gradient-to-r from-orange-500 to-red-500 relative">
                    <div className="absolute -bottom-12 left-8">
                        <div className="w-24 h-24 bg-white rounded-full p-1.5 shadow-md">
                            <div className="w-full h-full bg-orange-100 rounded-full flex items-center justify-center border border-orange-200">
                                <span className="text-3xl font-bold text-orange-600">
                                    {(user?.name || 'S').charAt(0).toUpperCase()}
                                </span>
                            </div>
                        </div>
                    </div>
                </div>

                <div className="pt-16 pb-8 px-8 flex flex-col md:flex-row md:items-center justify-between">
                    <div>
                        {editing ? (
                            <div className="space-y-3">
                                <div>
                                    <label className="text-xs font-semibold text-gray-500">Name</label>
                                    <input type="text" value={editName} onChange={e => setEditName(e.target.value)}
                                        className="block w-full border border-gray-300 rounded-lg px-3 py-2 text-sm focus:ring-orange-500 focus:border-orange-500" />
                                </div>
                                <div>
                                    <label className="text-xs font-semibold text-gray-500">Phone</label>
                                    <input type="tel" value={editPhone} onChange={e => setEditPhone(e.target.value)}
                                        className="block w-full border border-gray-300 rounded-lg px-3 py-2 text-sm focus:ring-orange-500 focus:border-orange-500" placeholder="e.g. +91 9876543210" />
                                </div>
                                <div className="flex gap-2">
                                    <button onClick={handleSaveProfile} disabled={saving}
                                        className="bg-orange-600 hover:bg-orange-700 text-white px-4 py-2 rounded-lg text-sm font-bold disabled:opacity-50">
                                        {saving ? 'Saving...' : 'Save Changes'}
                                    </button>
                                    <button onClick={() => { setEditing(false); setEditName(user?.name || ''); setEditPhone(user?.phone || ''); }}
                                        className="bg-gray-200 hover:bg-gray-300 text-gray-700 px-4 py-2 rounded-lg text-sm font-medium">
                                        Cancel
                                    </button>
                                </div>
                            </div>
                        ) : (
                            <>
                                <h2 className="text-2xl font-bold text-gray-900">{user?.name || 'Student'}</h2>
                                <div className="flex flex-wrap items-center mt-2 text-gray-500 text-sm gap-4">
                                    <span className="flex items-center">
                                        <svg className="w-4 h-4 mr-1.5" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M3 8l7.89 5.26a2 2 0 002.22 0L21 8M5 19h14a2 2 0 002-2V7a2 2 0 00-2-2H5a2 2 0 00-2 2v10a2 2 0 002 2z" /></svg>
                                        {user?.email}
                                    </span>
                                    {user?.phone && (
                                        <span className="flex items-center">
                                            <svg className="w-4 h-4 mr-1.5" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M3 5a2 2 0 012-2h3.28a1 1 0 01.948.684l1.498 4.493a1 1 0 01-.502 1.21l-2.257 1.13a11.042 11.042 0 005.516 5.516l1.13-2.257a1 1 0 011.21-.502l4.493 1.498a1 1 0 01.684.949V19a2 2 0 01-2 2h-1C9.716 21 3 14.284 3 6V5z" /></svg>
                                            {user.phone}
                                        </span>
                                    )}
                                </div>
                            </>
                        )}
                    </div>
                    {!editing && (
                        <button onClick={() => setEditing(true)} className="mt-6 md:mt-0 inline-flex items-center px-4 py-2 border border-gray-300 shadow-sm text-sm font-medium rounded-lg text-gray-700 bg-white hover:bg-gray-50 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-orange-500 transition-colors">
                            <svg className="w-4 h-4 mr-2 text-gray-500" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M15.232 5.232l3.536 3.536m-2.036-5.036a2.5 2.5 0 113.536 3.536L6.5 21.036H3v-3.572L16.732 3.732z" /></svg>
                            Edit Profile
                        </button>
                    )}
                </div>
            </div>

            <h3 className="text-xl font-bold text-gray-900 mb-6">Learning Statistics</h3>

            <div className="grid grid-cols-1 md:grid-cols-3 gap-6 mb-8">
                <div className="bg-white rounded-2xl p-6 border border-gray-100 shadow-sm flex items-center">
                    <div className="p-3 rounded-xl bg-blue-50 text-blue-600 mr-4">
                        <svg className="w-8 h-8" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z" /></svg>
                    </div>
                    <div>
                        <p className="text-sm font-semibold text-gray-500">Total Attempts</p>
                        <p className="text-2xl font-black text-gray-900">{totalAttempts}</p>
                    </div>
                </div>
                <div className="bg-white rounded-2xl p-6 border border-gray-100 shadow-sm flex items-center">
                    <div className="p-3 rounded-xl bg-green-50 text-green-600 mr-4">
                        <svg className="w-8 h-8" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z" /></svg>
                    </div>
                    <div>
                        <p className="text-sm font-semibold text-gray-500">Completed</p>
                        <p className="text-2xl font-black text-gray-900">{completedAttempts}</p>
                    </div>
                </div>
                <div className="bg-white rounded-2xl p-6 border border-gray-100 shadow-sm flex items-center">
                    <div className="p-3 rounded-xl bg-orange-50 text-orange-600 mr-4">
                        <svg className="w-8 h-8" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M13 7h8m0 0v8m0-8l-8 8-4-4-6 6" /></svg>
                    </div>
                    <div>
                        <p className="text-sm font-semibold text-gray-500">Completion Rate</p>
                        <p className="text-2xl font-black text-gray-900">{completionRate}%</p>
                    </div>
                </div>
            </div>

            <div className="mt-8 border-t border-gray-200 pt-8 flex justify-center">
                <button onClick={handleLogout}
                    className="inline-flex items-center px-6 py-3 border border-transparent text-base font-medium rounded-xl text-red-700 bg-red-100 hover:bg-red-200 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-red-500 transition-colors">
                    <svg className="w-5 h-5 mr-2" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M17 16l4-4m0 0l-4-4m4 4H7m6 4v1a3 3 0 01-3 3H6a3 3 0 01-3-3V7a3 3 0 013-3h4a3 3 0 013 3v1" /></svg>
                    Sign Out Securely
                </button>
            </div>
        </div>
    );
};
