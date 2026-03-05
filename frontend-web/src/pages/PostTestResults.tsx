import { useState, useEffect } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import { AnalyticsAPI } from '../services/api';

export const PostTestResults = () => {
    const { attemptId } = useParams<{ attemptId: string }>();
    const navigate = useNavigate();
    const [data, setData] = useState<any>(null);
    const [loading, setLoading] = useState(true);
    const [expandedSubjects, setExpandedSubjects] = useState<Set<string>>(new Set());

    const toggleSubject = (subject: string) => {
        setExpandedSubjects(prev => {
            const next = new Set(prev);
            if (next.has(subject)) next.delete(subject); else next.add(subject);
            return next;
        });
    };

    useEffect(() => {
        if (!attemptId) return;
        const fetch = async () => {
            try {
                const res = await AnalyticsAPI.getPostTestResults(attemptId);
                setData(res.data);
            } catch (err) {
                console.error("Failed to fetch results:", err);
            } finally {
                setLoading(false);
            }
        };
        fetch();
    }, [attemptId]);

    if (loading) {
        return (
            <div className="min-h-screen bg-gray-50 flex items-center justify-center">
                <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-orange-600"></div>
            </div>
        );
    }

    if (!data) {
        return (
            <div className="min-h-screen bg-gray-50 flex items-center justify-center">
                <div className="text-center">
                    <h2 className="text-xl font-bold text-gray-900">Results Not Found</h2>
                    <p className="text-gray-500 mt-2">This attempt may not have been submitted yet.</p>
                    <button onClick={() => navigate('/dashboard')} className="mt-4 bg-orange-600 text-white px-6 py-2 rounded-lg">
                        Go to Dashboard
                    </button>
                </div>
            </div>
        );
    }

    return (
        <div className="min-h-screen bg-gray-50">
            {/* Hero Section */}
            <div className="bg-gradient-to-br from-gray-900 via-gray-800 to-gray-900 text-white">
                <div className="max-w-4xl mx-auto px-4 py-10">
                    <button onClick={() => navigate('/dashboard')} className="flex items-center text-gray-400 hover:text-white mb-6 transition-colors">
                        <svg className="w-5 h-5 mr-2" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M10 19l-7-7m0 0l7-7m-7 7h18" />
                        </svg>
                        Back to Dashboard
                    </button>

                    <h1 className="text-2xl font-bold mb-2">{data.test_title}</h1>
                    <p className="text-gray-400 text-sm mb-8">Test Results & Analysis</p>

                    {/* Score Cards */}
                    <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
                        <div className="bg-white/10 backdrop-blur rounded-2xl p-5 text-center">
                            <p className="text-3xl font-black">{data.total_score}</p>
                            <p className="text-xs text-gray-400 mt-1 uppercase tracking-wider">Score</p>
                        </div>
                        <div className="bg-white/10 backdrop-blur rounded-2xl p-5 text-center">
                            <p className="text-3xl font-black">#{data.rank}</p>
                            <p className="text-xs text-gray-400 mt-1 uppercase tracking-wider">Rank</p>
                        </div>
                        <div className="bg-white/10 backdrop-blur rounded-2xl p-5 text-center">
                            <p className="text-3xl font-black">{data.percentile}%</p>
                            <p className="text-xs text-gray-400 mt-1 uppercase tracking-wider">Percentile</p>
                        </div>
                        <div className="bg-white/10 backdrop-blur rounded-2xl p-5 text-center">
                            <p className="text-3xl font-black">{data.accuracy}%</p>
                            <p className="text-xs text-gray-400 mt-1 uppercase tracking-wider">Accuracy</p>
                        </div>
                    </div>

                    {/* Quick Stats */}
                    <div className="flex justify-center gap-8 mt-6 text-sm">
                        <span className="text-green-400">✓ {data.correct_count} Correct</span>
                        <span className="text-red-400">✗ {data.incorrect_count} Wrong</span>
                        <span className="text-gray-400">○ {data.skipped_count} Skipped</span>
                    </div>
                </div>
            </div>

            <div className="max-w-4xl mx-auto px-4 py-8 space-y-8">
                {/* Encouragement */}
                <div className="bg-gradient-to-r from-orange-50 to-amber-50 rounded-2xl p-6 border border-orange-200 text-center">
                    <p className="text-lg font-bold text-gray-900">{data.encouragement}</p>
                </div>

                {/* Psychological Nudges */}
                {data.nudges && data.nudges.length > 0 && (
                    <div className="space-y-3">
                        <h3 className="text-lg font-bold text-gray-900">Smart Insights</h3>
                        {data.nudges.map((nudge: any, idx: number) => {
                            const colors: Record<string, string> = {
                                loss_aversion: 'bg-red-50 border-red-200 text-red-900',
                                social_proof: 'bg-blue-50 border-blue-200 text-blue-900',
                                progress_anchor: 'bg-purple-50 border-purple-200 text-purple-900',
                                specificity_bias: 'bg-orange-50 border-orange-200 text-orange-900',
                            };
                            return (
                                <div key={idx} className={`rounded-xl p-4 border ${colors[nudge.type] || 'bg-gray-50 border-gray-200'}`}>
                                    <span className="text-lg mr-2">{nudge.icon}</span>
                                    <span className="text-sm">{nudge.message}</span>
                                </div>
                            );
                        })}
                    </div>
                )}

                {/* Weak Topics */}
                {data.weak_topics && data.weak_topics.length > 0 && (
                    <div>
                        <h3 className="text-lg font-bold text-gray-900 mb-4">
                            🎯 Areas to Improve
                        </h3>
                        <div className="grid grid-cols-1 md:grid-cols-2 gap-3">
                            {data.weak_topics.map((wt: any, idx: number) => (
                                <div key={idx} className="bg-white rounded-xl p-4 border border-red-100 flex items-center justify-between">
                                    <div>
                                        <p className="text-sm font-bold text-gray-900">{wt.topic}</p>
                                        <p className="text-xs text-gray-500">{wt.subject}</p>
                                    </div>
                                    <div className="text-right">
                                        <span className={`inline-flex px-2 py-0.5 rounded-full text-xs font-bold ${wt.accuracy < 40 ? 'bg-red-100 text-red-700' : 'bg-orange-100 text-orange-700'
                                            }`}>
                                            {Math.round(wt.accuracy)}%
                                        </span>
                                        <p className="text-xs text-gray-400 mt-0.5">
                                            {wt.total_attempted} Qs
                                        </p>
                                    </div>
                                </div>
                            ))}
                        </div>
                        <button
                            onClick={() => navigate('/quiz')}
                            className="mt-4 w-full bg-orange-600 hover:bg-orange-700 text-white font-bold py-3 rounded-xl transition-colors shadow-lg shadow-orange-200"
                        >
                            Practice Weak Areas →
                        </button>
                    </div>
                )}

                {/* Strong Topics */}
                {data.strong_topics && data.strong_topics.length > 0 && (
                    <div>
                        <h3 className="text-lg font-bold text-gray-900 mb-4">💪 Your Strengths</h3>
                        <div className="flex flex-wrap gap-2">
                            {data.strong_topics.map((st: any, idx: number) => (
                                <span key={idx} className="bg-green-50 text-green-800 px-3 py-1.5 rounded-full text-sm font-semibold border border-green-200">
                                    {st.topic} ({Math.round(st.accuracy)}%)
                                </span>
                            ))}
                        </div>
                    </div>
                )}

                {/* Subject + Topic Breakdown */}
                {data.subject_performances && data.subject_performances.length > 0 && (
                    <div>
                        <h3 className="text-lg font-bold text-gray-900 mb-4">Subject & Topic Breakdown</h3>
                        <div className="space-y-3">
                            {data.subject_performances.map((sub: any, idx: number) => {
                                const isExpanded = expandedSubjects.has(sub.subject);
                                const hasTopics = sub.topics && sub.topics.length > 0;
                                return (
                                    <div key={idx} className="bg-white rounded-2xl border border-gray-100 shadow-sm overflow-hidden">
                                        <button
                                            onClick={() => hasTopics && toggleSubject(sub.subject)}
                                            className="w-full px-5 py-4 flex items-center justify-between hover:bg-gray-50 transition-colors"
                                        >
                                            <div className="flex items-center gap-3">
                                                {hasTopics && (
                                                    <svg className={`w-4 h-4 text-gray-400 transition-transform ${isExpanded ? 'rotate-90' : ''}`} fill="none" stroke="currentColor" viewBox="0 0 24 24">
                                                        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 5l7 7-7 7" />
                                                    </svg>
                                                )}
                                                <div className="text-left">
                                                    <h4 className="font-bold text-gray-900">{sub.subject}</h4>
                                                    <p className="text-xs text-gray-500">{sub.correct}/{sub.total_questions} correct</p>
                                                </div>
                                            </div>
                                            <div className="flex items-center gap-4">
                                                <div className="w-24 bg-gray-100 rounded-full h-2 hidden sm:block">
                                                    <div className={`h-2 rounded-full ${sub.accuracy_percentage >= 70 ? 'bg-green-500' : sub.accuracy_percentage >= 40 ? 'bg-orange-500' : 'bg-red-500'
                                                        }`} style={{ width: `${sub.accuracy_percentage}%` }}></div>
                                                </div>
                                                <span className={`text-sm font-bold px-2 py-0.5 rounded-full ${sub.accuracy_percentage >= 70 ? 'bg-green-100 text-green-800' : sub.accuracy_percentage >= 40 ? 'bg-orange-100 text-orange-800' : 'bg-red-100 text-red-800'
                                                    }`}>{Math.round(sub.accuracy_percentage)}%</span>
                                            </div>
                                        </button>

                                        {isExpanded && hasTopics && (
                                            <div className="border-t border-gray-100 bg-gray-50 px-5 py-3">
                                                {sub.topics.map((tp: any, tidx: number) => (
                                                    <div key={tidx} className="flex items-center justify-between py-2">
                                                        <div className="flex items-center gap-2">
                                                            <div className={`w-2 h-2 rounded-full ${tp.accuracy_percentage >= 70 ? 'bg-green-500' : tp.accuracy_percentage >= 40 ? 'bg-orange-500' : 'bg-red-500'
                                                                }`}></div>
                                                            <span className="text-sm text-gray-700">{tp.topic}</span>
                                                            <span className="text-xs text-gray-400">({tp.correct}/{tp.total_questions})</span>
                                                        </div>
                                                        <span className={`text-xs font-bold ${tp.accuracy_percentage >= 70 ? 'text-green-700' : tp.accuracy_percentage >= 40 ? 'text-orange-700' : 'text-red-700'
                                                            }`}>{Math.round(tp.accuracy_percentage)}%</span>
                                                    </div>
                                                ))}
                                            </div>
                                        )}
                                    </div>
                                );
                            })}
                        </div>
                    </div>
                )}
            </div>
        </div>
    );
};
