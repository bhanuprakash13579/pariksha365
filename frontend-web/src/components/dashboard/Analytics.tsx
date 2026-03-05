import { useState, useEffect } from 'react';
import { AnalyticsAPI } from '../../services/api';

export const Analytics = () => {
    const [hierarchy, setHierarchy] = useState<any[]>([]);
    const [selectedCategory, setSelectedCategory] = useState<string | null>(null);
    const [selectedCourse, setSelectedCourse] = useState<string | null>(null);
    const [selectedScope, setSelectedScope] = useState<string>('overall');
    const [analyticsData, setAnalyticsData] = useState<any>(null);
    const [loading, setLoading] = useState(true);
    const [expandedSubjects, setExpandedSubjects] = useState<Set<string>>(new Set());

    const toggleSubject = (subject: string) => {
        setExpandedSubjects(prev => {
            const next = new Set(prev);
            if (next.has(subject)) next.delete(subject);
            else next.add(subject);
            return next;
        });
    };

    // Initial Fetch for Hierarchy
    useEffect(() => {
        const fetchHierarchy = async () => {
            try {
                const res = await AnalyticsAPI.getHierarchy();
                if (res.data && res.data.length > 0) {
                    setHierarchy(res.data);
                    setSelectedCategory(res.data[0].category_name);
                    if (res.data[0].courses.length > 0) {
                        setSelectedCourse(res.data[0].courses[0].course_id);
                    }
                } else {
                    setLoading(false);
                }
            } catch (err) {
                console.error("Failed to fetch analytics hierarchy:", err);
                setLoading(false);
            }
        };
        fetchHierarchy();
    }, []);

    // Change Course -> Reset Scope
    useEffect(() => {
        setSelectedScope('overall');
    }, [selectedCourse]);

    // Fetch Analytics Data when Course or Scope changes
    useEffect(() => {
        if (!selectedCourse) return;

        const fetchAnalytics = async () => {
            setLoading(true);
            try {
                let res;
                if (selectedScope === 'overall') {
                    res = await AnalyticsAPI.getCourseOverallAnalytics(selectedCourse);
                } else {
                    res = await AnalyticsAPI.getSpecificTestAnalytics(selectedCourse, selectedScope);
                }
                setAnalyticsData(res.data);
            } catch (err) {
                console.error("Failed to fetch analytics data:", err);
                setAnalyticsData(null);
            } finally {
                setLoading(false);
            }
        };
        fetchAnalytics();
    }, [selectedCourse, selectedScope]);

    if (loading && hierarchy.length === 0) {
        return (
            <div className="flex justify-center items-center py-20">
                <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-orange-600"></div>
            </div>
        );
    }

    if (hierarchy.length === 0) {
        return (
            <div className="max-w-4xl mx-auto py-8">
                <div className="bg-white rounded-2xl p-12 text-center border border-gray-100 shadow-sm flex flex-col items-center">
                    <svg className="w-20 h-20 text-gray-300 mb-6" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path strokeLinecap="round" strokeLinejoin="round" strokeWidth={1} d="M16 8v8m-4-5v5m-4-2v2m-2 4h12a2 2 0 002-2V6a2 2 0 00-2-2H6a2 2 0 00-2 2v12a2 2 0 002 2z" /></svg>
                    <h3 className="text-xl font-bold text-gray-900 mb-2">No Analytics Available</h3>
                    <p className="text-gray-500 max-w-sm">You need to enroll in a course and attempt a test to see your performance analytics here.</p>
                </div>
            </div>
        );
    }

    const currentCategoryObj = hierarchy.find(c => c.category_name === selectedCategory);
    const courses = currentCategoryObj ? currentCategoryObj.courses : [];
    const hasData = analyticsData?.subject_performances && analyticsData.subject_performances.length > 0;

    return (
        <div className="max-w-6xl mx-auto py-8">
            <h2 className="text-3xl font-bold text-gray-900 mb-8">Intelligent Analytics</h2>

            {/* TIER 1: Categories */}
            <div className="border-b border-gray-200 mb-6">
                <nav className="-mb-px flex space-x-8" aria-label="Tabs">
                    {hierarchy.map((cat, idx) => (
                        <button
                            key={idx}
                            onClick={() => {
                                setSelectedCategory(cat.category_name);
                                if (cat.courses.length > 0) setSelectedCourse(cat.courses[0].course_id);
                            }}
                            className={`whitespace-nowrap py-4 px-1 border-b-2 font-medium text-sm transition-colors ${selectedCategory === cat.category_name
                                ? 'border-orange-500 text-orange-600'
                                : 'border-transparent text-gray-500 hover:text-gray-700 hover:border-gray-300'
                                }`}
                        >
                            {cat.category_name}
                        </button>
                    ))}
                </nav>
            </div>

            {/* TIER 2: Courses */}
            {courses.length > 0 && (
                <div className="flex overflow-x-auto pb-4 mb-6 space-x-3 hide-scrollbar">
                    {courses.map((course: any) => (
                        <button key={course.course_id} onClick={() => setSelectedCourse(course.course_id)}
                            className={`whitespace-nowrap px-5 py-2.5 rounded-full text-sm font-semibold transition-colors ${course.course_id === selectedCourse
                                ? 'bg-orange-600 text-white shadow-md'
                                : 'bg-gray-100 text-gray-600 hover:bg-gray-200'
                                }`}>
                            {course.title.length > 30 ? course.title.substring(0, 30) + '...' : course.title}
                        </button>
                    ))}
                </div>
            )}

            {loading && hierarchy.length > 0 ? (
                <div className="flex justify-center items-center py-20">
                    <div className="animate-spin rounded-full h-10 w-10 border-b-2 border-orange-600"></div>
                </div>
            ) : analyticsData ? (
                <>
                    {/* Scope Selector */}
                    <div className="bg-white p-4 rounded-xl border border-gray-200 shadow-sm mb-8 flex flex-col md:flex-row md:items-center justify-between">
                        <div>
                            <h3 className="text-lg font-bold text-gray-900">Analysis Scope</h3>
                            <p className="text-sm text-gray-500">Select what data to visualize</p>
                        </div>
                        <div className="mt-4 md:mt-0 relative">
                            <select value={selectedScope} onChange={(e) => setSelectedScope(e.target.value)}
                                className="block w-full md:w-80 pl-4 pr-10 py-3 text-base border-gray-300 focus:outline-none focus:ring-orange-500 focus:border-orange-500 sm:text-sm rounded-lg bg-gray-50 border border-gray-200 appearance-none font-medium">
                                <option value="overall">Overall Course Analytics</option>
                                {analyticsData.available_tests && analyticsData.available_tests.map((t: any) => (
                                    <option key={t.course_id} value={t.course_id}>Test: {t.title}</option>
                                ))}
                                {selectedScope !== 'overall' && !analyticsData.available_tests && (
                                    <option value={selectedScope}>Test: {analyticsData.test_title || 'Current Test'}</option>
                                )}
                            </select>
                            <div className="pointer-events-none absolute inset-y-0 right-0 flex items-center px-4 text-gray-500">
                                <svg className="h-4 w-4" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M19 9l-7 7-7-7" /></svg>
                            </div>
                        </div>
                    </div>

                    {/* Insights Panel */}
                    {analyticsData.insights && analyticsData.insights.length > 0 && (
                        <div className="mb-8 space-y-4">
                            {analyticsData.insights.map((insight: string, idx: number) => {
                                const isAlert = insight.includes('Focus Alert') || insight.includes('Targeted Alert');
                                return (
                                    <div key={idx} className={`border rounded-2xl p-5 flex items-start sm:items-center ${isAlert ? 'bg-orange-50 border-orange-200' : 'bg-green-50 border-green-200'}`}>
                                        <div className={`p-2 rounded-full mr-4 flex-shrink-0 mt-1 sm:mt-0 ${isAlert ? 'bg-orange-100 text-orange-600' : 'bg-green-100 text-green-600'}`}>
                                            {isAlert ? (
                                                <svg className="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M13 16h-1v-4h-1m1-4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z" /></svg>
                                            ) : (
                                                <svg className="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z" /></svg>
                                            )}
                                        </div>
                                        <p className={`text-sm sm:text-base ${isAlert ? 'text-orange-900' : 'text-green-900'}`}>
                                            {insight.split(/('.*?')/).map((part, i) =>
                                                part.startsWith("'") && part.endsWith("'")
                                                    ? <strong key={i} className="font-bold">{part.replace(/'/g, '')}</strong>
                                                    : part
                                            )}
                                        </p>
                                    </div>
                                );
                            })}
                        </div>
                    )}

                    {hasData ? (
                        <div className="grid grid-cols-1 lg:grid-cols-3 gap-8 mb-8">
                            {/* CSS Bar Chart */}
                            <div className="bg-white rounded-2xl p-6 border border-gray-100 shadow-sm lg:col-span-2 relative">
                                <div className="flex justify-between items-center mb-6">
                                    <h3 className="text-lg font-bold text-gray-900">Subject Accuracy Overview</h3>
                                    <div className="flex items-center text-xs font-semibold text-gray-500 bg-gray-50 px-3 py-1 rounded-full border border-gray-200">
                                        <div className="w-4 border-t-2 border-dashed border-indigo-400 mr-2"></div>
                                        Target: Top 10% (85%)
                                    </div>
                                </div>

                                <div className="flex h-64 items-end space-x-2 sm:space-x-6 relative">
                                    {/* Ghost Competitor Line */}
                                    <div className="absolute w-full border-t-2 border-dashed border-indigo-300 z-10 flex items-center justify-end pointer-events-none" style={{ bottom: '85%' }}>
                                    </div>

                                    {analyticsData.subject_performances.map((sub: any, idx: number) => (
                                        <div key={idx} className="flex-1 flex flex-col justify-end items-center group relative z-20">
                                            <div className="text-xs font-bold text-gray-600 mb-2 opacity-0 group-hover:opacity-100 transition-opacity bg-white px-2 py-1 rounded shadow-sm border border-gray-100">
                                                {Math.round(sub.accuracy_percentage)}%
                                            </div>
                                            <div
                                                className={`w-full rounded-t-lg transition-colors relative ${sub.accuracy_percentage >= 85
                                                    ? 'bg-gradient-to-t from-indigo-600 to-indigo-400'
                                                    : sub.accuracy_percentage >= 70
                                                        ? 'bg-gradient-to-t from-green-500 to-green-400'
                                                        : sub.accuracy_percentage >= 40
                                                            ? 'bg-gradient-to-t from-orange-500 to-orange-400'
                                                            : 'bg-gradient-to-t from-red-500 to-red-400'
                                                    }`}
                                                style={{ height: `${Math.max(sub.accuracy_percentage, 5)}%` }}
                                            ></div>
                                            <div className="mt-4 text-xs font-bold text-gray-600 truncate w-full text-center px-1" title={sub.subject}>
                                                {sub.subject.length > 8 ? sub.subject.substring(0, 7) + '..' : sub.subject}
                                            </div>
                                        </div>
                                    ))}
                                </div>
                            </div>

                            {/* Hero Metrics */}
                            <div className="grid grid-cols-1 gap-6">
                                {selectedScope === 'overall' ? (
                                    <>
                                        <div className="bg-gradient-to-br from-indigo-900 to-indigo-700 rounded-2xl p-6 shadow-md flex flex-col justify-center relative overflow-hidden text-white">
                                            <div className="absolute top-0 right-0 -mt-4 -mr-4 w-24 h-24 bg-white opacity-10 rounded-full blur-xl"></div>
                                            <span className="text-sm font-semibold text-indigo-200 uppercase tracking-wider relative z-10">Relative Percentile</span>
                                            <div className="mt-2 text-5xl font-black relative z-10">
                                                {analyticsData.course_percentile}%<span className="text-2xl text-indigo-300 font-bold ml-1">ile</span>
                                            </div>
                                        </div>
                                        <div className="bg-white rounded-2xl p-6 border border-gray-100 shadow-sm flex flex-col justify-center">
                                            <span className="text-sm font-semibold text-gray-500 uppercase tracking-wider">Overall Accuracy</span>
                                            <div className="mt-2 text-4xl font-black text-gray-900">{analyticsData.overall_accuracy}%</div>
                                        </div>
                                    </>
                                ) : (
                                    <>
                                        <div className="bg-gradient-to-br from-orange-600 to-orange-400 rounded-2xl p-6 shadow-md flex flex-col justify-center relative overflow-hidden text-white">
                                            <div className="absolute top-0 right-0 -mt-4 -mr-4 w-24 h-24 bg-white opacity-10 rounded-full blur-xl"></div>
                                            <span className="text-sm font-semibold text-orange-100 uppercase tracking-wider relative z-10">Test Rank</span>
                                            <div className="mt-2 text-5xl font-black relative z-10">#{analyticsData.rank}</div>
                                        </div>
                                        <div className="bg-white rounded-2xl p-6 border border-gray-100 shadow-sm flex flex-col justify-center">
                                            <span className="text-sm font-semibold text-gray-500 uppercase tracking-wider">Percentile</span>
                                            <div className="mt-2 text-4xl font-black text-gray-900">{analyticsData.percentile}%</div>
                                        </div>
                                        <div className="bg-white rounded-2xl p-6 border border-gray-100 shadow-sm flex flex-col justify-center">
                                            <span className="text-sm font-semibold text-gray-500 uppercase tracking-wider">Test Score</span>
                                            <div className="mt-2 text-3xl font-black text-gray-900">{analyticsData.total_score}</div>
                                        </div>
                                    </>
                                )}
                            </div>
                        </div>
                    ) : (
                        <div className="bg-white rounded-2xl p-12 text-center border border-gray-100 shadow-sm mt-4">
                            <svg className="w-16 h-16 text-gray-300 mx-auto mb-4" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path strokeLinecap="round" strokeLinejoin="round" strokeWidth={1} d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z" /></svg>
                            <h3 className="text-lg font-medium text-gray-900">No data available yet</h3>
                            <p className="mt-1 text-gray-500">Take a test in this series to unlock your performance analytics!</p>
                        </div>
                    )}

                    {/* Detailed Subject + Topic Breakdown */}
                    {hasData && (
                        <>
                            <h3 className="text-xl font-bold text-gray-900 mb-4 mt-8">Subject & Topic Breakdown</h3>
                            <div className="space-y-3">
                                {analyticsData.subject_performances.map((sub: any, idx: number) => {
                                    const isExpanded = expandedSubjects.has(sub.subject);
                                    const hasTopics = sub.topics && sub.topics.length > 0;
                                    return (
                                        <div key={idx} className="bg-white rounded-2xl border border-gray-100 shadow-sm overflow-hidden">
                                            {/* Subject row */}
                                            <button
                                                onClick={() => hasTopics && toggleSubject(sub.subject)}
                                                className="w-full px-6 py-5 flex items-center justify-between hover:bg-gray-50 transition-colors"
                                            >
                                                <div className="flex items-center gap-4">
                                                    {hasTopics && (
                                                        <svg className={`w-5 h-5 text-gray-400 transition-transform ${isExpanded ? 'rotate-90' : ''}`} fill="none" stroke="currentColor" viewBox="0 0 24 24">
                                                            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 5l7 7-7 7" />
                                                        </svg>
                                                    )}
                                                    <div className="text-left">
                                                        <h4 className="text-base font-bold text-gray-900">{sub.subject}</h4>
                                                        <p className="text-xs text-gray-500 mt-0.5">
                                                            {sub.correct}/{sub.total_questions} correct • {sub.skipped} skipped
                                                        </p>
                                                    </div>
                                                </div>
                                                <div className="flex items-center gap-6">
                                                    <div className="w-32 bg-gray-100 rounded-full h-2.5 hidden sm:block">
                                                        <div
                                                            className={`h-2.5 rounded-full transition-all ${sub.accuracy_percentage >= 70 ? 'bg-green-500'
                                                                : sub.accuracy_percentage >= 40 ? 'bg-orange-500'
                                                                    : 'bg-red-500'
                                                                }`}
                                                            style={{ width: `${sub.accuracy_percentage}%` }}
                                                        ></div>
                                                    </div>
                                                    <span className={`inline-flex items-center px-3 py-1 rounded-full text-sm font-bold ${sub.accuracy_percentage >= 70 ? 'bg-green-100 text-green-800'
                                                        : sub.accuracy_percentage >= 40 ? 'bg-orange-100 text-orange-800'
                                                            : 'bg-red-100 text-red-800'
                                                        }`}>
                                                        {Math.round(sub.accuracy_percentage)}%
                                                    </span>
                                                </div>
                                            </button>

                                            {/* Topic drilldown */}
                                            {isExpanded && hasTopics && (
                                                <div className="border-t border-gray-100 bg-gray-50 px-6 py-4">
                                                    <div className="space-y-3">
                                                        {sub.topics.map((tp: any, tidx: number) => (
                                                            <div key={tidx} className="flex items-center justify-between py-2">
                                                                <div className="flex items-center gap-3">
                                                                    <div className={`w-2 h-2 rounded-full ${tp.accuracy_percentage >= 70 ? 'bg-green-500'
                                                                        : tp.accuracy_percentage >= 40 ? 'bg-orange-500'
                                                                            : 'bg-red-500'
                                                                        }`}></div>
                                                                    <span className="text-sm font-medium text-gray-700">{tp.topic}</span>
                                                                    <span className="text-xs text-gray-400">
                                                                        ({tp.correct}/{tp.total_questions})
                                                                    </span>
                                                                </div>
                                                                <div className="flex items-center gap-4">
                                                                    <div className="w-20 bg-gray-200 rounded-full h-1.5">
                                                                        <div
                                                                            className={`h-1.5 rounded-full ${tp.accuracy_percentage >= 70 ? 'bg-green-500'
                                                                                : tp.accuracy_percentage >= 40 ? 'bg-orange-500'
                                                                                    : 'bg-red-500'
                                                                                }`}
                                                                            style={{ width: `${tp.accuracy_percentage}%` }}
                                                                        ></div>
                                                                    </div>
                                                                    <span className={`text-xs font-bold min-w-[40px] text-right ${tp.accuracy_percentage >= 70 ? 'text-green-700'
                                                                        : tp.accuracy_percentage >= 40 ? 'text-orange-700'
                                                                            : 'text-red-700'
                                                                        }`}>
                                                                        {Math.round(tp.accuracy_percentage)}%
                                                                    </span>
                                                                    {tp.accuracy_percentage < 60 && (
                                                                        <span className="text-xs bg-red-100 text-red-700 px-2 py-0.5 rounded font-semibold">
                                                                            Weak
                                                                        </span>
                                                                    )}
                                                                </div>
                                                            </div>
                                                        ))}
                                                    </div>
                                                </div>
                                            )}
                                        </div>
                                    );
                                })}
                            </div>
                        </>
                    )}
                </>
            ) : null}
        </div>
    );
};
