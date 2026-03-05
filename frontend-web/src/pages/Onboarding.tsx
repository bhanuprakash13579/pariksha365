import { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import { CategoryAPI, UserAPI } from '../services/api';

export const Onboarding = () => {
    const [categories, setCategories] = useState<any[]>([]);
    const [selectedId, setSelectedId] = useState<string | null>(null);
    const [loading, setLoading] = useState(true);
    const [saving, setSaving] = useState(false);
    const navigate = useNavigate();

    useEffect(() => {
        const fetchCategories = async () => {
            try {
                const res = await CategoryAPI.list();
                setCategories(res.data || []);
            } catch (error) {
                console.error("Failed to fetch categories:", error);
            } finally {
                setLoading(false);
            }
        };
        fetchCategories();
    }, []);

    const handleSave = async () => {
        if (!selectedId) return;
        setSaving(true);
        try {
            await UserAPI.updateExamPreference(selectedId);
            // After saving, route them straight into their personalized dashboard
            navigate('/dashboard', { replace: true });
        } catch (error) {
            console.error("Failed to save preference:", error);
            setSaving(false);
        }
    };

    if (loading) {
        return (
            <div className="min-h-screen bg-gray-50 flex items-center justify-center">
                <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-orange-500"></div>
            </div>
        );
    }

    return (
        <div className="min-h-screen bg-gray-50 flex flex-col justify-center py-12 px-6 lg:px-8">
            <div className="sm:mx-auto sm:w-full sm:max-w-xl text-center">
                <div className="w-20 h-20 bg-orange-100 rounded-full flex items-center justify-center mx-auto mb-6 shadow-sm border border-orange-200">
                    <span className="text-4xl text-orange-600">🎯</span>
                </div>
                <h2 className="text-4xl font-extrabold text-gray-900 tracking-tight mb-3">
                    What are you preparing for?
                </h2>
                <p className="text-lg text-gray-600 font-medium">
                    Select your primary exam target. We'll personalize your entire study experience.
                </p>
            </div>

            <div className="mt-12 sm:mx-auto sm:w-full sm:max-w-2xl">
                <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
                    {categories.map((category) => (
                        <div
                            key={category.id}
                            onClick={() => setSelectedId(category.id)}
                            className={`cursor-pointer rounded-2xl p-6 border-2 transition-all duration-200 flex items-center shadow-sm ${selectedId === category.id
                                    ? 'border-orange-500 bg-orange-50 transform scale-[1.02] shadow-orange-100'
                                    : 'border-gray-200 bg-white hover:border-orange-300 hover:bg-orange-50/50'
                                }`}
                        >
                            <div className={`w-12 h-12 rounded-xl flex items-center justify-center shrink-0 mr-4 ${selectedId === category.id ? 'bg-orange-500 text-white' : 'bg-gray-100 text-gray-500'
                                }`}>
                                <svg className="w-6 h-6" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 6.253v13m0-13C10.832 5.477 9.246 5 7.5 5S4.168 5.477 3 6.253v13C4.168 18.477 5.754 18 7.5 18s3.332.477 4.5 1.253m0-13C13.168 5.477 14.754 5 16.5 5c1.747 0 3.332.477 4.5 1.253v13C19.832 18.477 18.247 18 16.5 18c-1.746 0-3.332.477-4.5 1.253" />
                                </svg>
                            </div>
                            <div className="flex-1">
                                <h3 className={`text-lg font-bold ${selectedId === category.id ? 'text-orange-900' : 'text-gray-900'}`}>
                                    {category.name}
                                </h3>
                                <p className={`text-sm mt-1 line-clamp-2 ${selectedId === category.id ? 'text-orange-700' : 'text-gray-500'}`}>
                                    {category.description || `Mock tests, PYQs, and study material for ${category.name}`}
                                </p>
                            </div>

                            {selectedId === category.id && (
                                <div className="ml-4 shrink-0">
                                    <div className="w-6 h-6 bg-orange-500 rounded-full flex items-center justify-center text-white">
                                        <svg className="w-4 h-4" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                                            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={3} d="M5 13l4 4L19 7" />
                                        </svg>
                                    </div>
                                </div>
                            )}
                        </div>
                    ))}
                </div>

                <div className="mt-10 flex justify-center">
                    <button
                        onClick={handleSave}
                        disabled={!selectedId || saving}
                        className={`w-full sm:w-auto px-12 py-4 rounded-xl text-lg font-bold shadow-lg transition-all duration-200 ${!selectedId || saving
                                ? 'bg-gray-300 text-gray-500 cursor-not-allowed'
                                : 'bg-gray-900 text-white hover:bg-black hover:shadow-xl transform hover:-translate-y-1'
                            }`}
                    >
                        {saving ? 'Personalizing Dashboard...' : 'Continue to Dashboard'}
                    </button>
                </div>
            </div>
        </div>
    );
};
