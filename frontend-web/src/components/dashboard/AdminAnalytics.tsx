import React, { useEffect, useState } from 'react';
import { api } from '../../services/api';
import { TrendingUp, Users, FileText, AlertTriangle, Award, Activity, BarChart2, Zap } from 'lucide-react';

interface OverviewData {
    totals: { total_users: number; total_tests: number; total_attempts: number; completed_attempts: number };
    top_tests: { title: string; category: string; attempt_count: number; completion_rate: number; avg_score: number }[];
    category_popularity: { category: string; attempt_count: number; test_count: number; unique_students: number }[];
    weekly_trend: { day: string; attempt_count: number }[];
    coverage: { category: string; test_count: number }[];
    top_users: { name: string; email: string; attempt_count: number; avg_accuracy: number }[];
    health: { overall_completion_rate: number; overall_avg_accuracy: number; avg_percentile: number };
}

const StatCard = ({ icon, label, value, sub, color }: { icon: React.ReactNode; label: string; value: string | number; sub?: string; color: string }) => (
    <div className={`bg-white border border-gray-100 rounded-xl p-5 shadow-sm flex gap-4 items-center`}>
        <div className={`w-11 h-11 rounded-xl flex items-center justify-center ${color}`}>{icon}</div>
        <div>
            <div className="text-2xl font-black text-gray-900">{value ?? '—'}</div>
            <div className="text-xs font-semibold text-gray-500">{label}</div>
            {sub && <div className="text-[11px] text-gray-400">{sub}</div>}
        </div>
    </div>
);

// Simple CSS-only horizontal bar chart
const HBar = ({ label, value, max, sub, color }: { label: string; value: number; max: number; sub?: string; color: string }) => (
    <div className="mb-3">
        <div className="flex justify-between mb-1">
            <span className="text-sm font-semibold text-gray-700 truncate max-w-[60%]">{label}</span>
            <span className="text-sm font-bold text-gray-900">{value.toLocaleString()}</span>
        </div>
        <div className="w-full bg-gray-100 rounded-full h-2">
            <div className={`h-2 rounded-full ${color} transition-all duration-700`} style={{ width: `${max > 0 ? (value / max) * 100 : 0}%` }} />
        </div>
        {sub && <p className="text-[11px] text-gray-400 mt-0.5">{sub}</p>}
    </div>
);

export const AdminAnalytics: React.FC = () => {
    const [data, setData] = useState<OverviewData | null>(null);
    const [loading, setLoading] = useState(true);

    useEffect(() => {
        api.get('/admin/analytics/overview')
            .then((r: { data: OverviewData }) => setData(r.data))
            .catch(() => { })
            .finally(() => setLoading(false));
    }, []);

    if (loading) return (
        <div className="grid grid-cols-4 gap-4 animate-pulse">
            {Array.from({ length: 8 }).map((_, i) => (
                <div key={i} className="bg-gray-100 rounded-xl h-24" />
            ))}
        </div>
    );

    if (!data) return (
        <div className="bg-red-50 border border-red-200 rounded-xl p-8 text-center">
            <AlertTriangle className="w-8 h-8 text-red-400 mx-auto mb-2" />
            <p className="text-red-700 font-semibold">Analytics unavailable — check backend connection.</p>
        </div>
    );

    const { totals, top_tests, category_popularity, weekly_trend, coverage, top_users, health } = data;
    const maxAttempts = Math.max(...(category_popularity.map(c => c.attempt_count) || [1]), 1);
    const maxTestAttempts = Math.max(...(top_tests.map(t => t.attempt_count) || [1]), 1);
    const CATEGORY_COLORS: Record<string, string> = {
        Railway: 'bg-amber-400', SSC: 'bg-orange-400', Bank: 'bg-blue-400',
        UPSC: 'bg-purple-400', Defence: 'bg-red-400', Police: 'bg-indigo-400',
        Judicial: 'bg-violet-400', ESIC: 'bg-teal-400', PSUs: 'bg-slate-400',
        PSCs: 'bg-green-400', 'Post-Office': 'bg-yellow-400',
    };

    // Compute content gap alerts
    const highDemandLowSupply = category_popularity
        .filter(c => c.attempt_count > 0)
        .map(c => ({ ...c, tests: coverage.find(x => x.category === c.category)?.test_count ?? 0 }))
        .filter(c => c.tests < 5)
        .sort((a, b) => b.attempt_count - a.attempt_count);

    // Weekly chart
    const maxTrendCount = Math.max(...(weekly_trend.map(d => d.attempt_count) || [1]), 1);

    const completionPct = totals.total_attempts > 0
        ? Math.round((totals.completed_attempts / totals.total_attempts) * 100)
        : 0;

    return (
        <div className="space-y-8">
            {/* Header */}
            <div className="flex items-center justify-between">
                <div>
                    <h2 className="text-2xl font-black text-gray-900 flex items-center gap-2">
                        <BarChart2 className="w-6 h-6 text-indigo-500" /> Admin Intelligence
                    </h2>
                    <p className="text-sm text-gray-400 mt-0.5">Cached · refreshes every 5 min · zero performance cost</p>
                </div>
            </div>

            {/* Platform Totals */}
            <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
                <StatCard icon={<Users className="w-5 h-5 text-blue-600" />} label="Total Students" value={totals.total_users?.toLocaleString()} color="bg-blue-50" />
                <StatCard icon={<FileText className="w-5 h-5 text-orange-600" />} label="Published Tests" value={totals.total_tests?.toLocaleString()} color="bg-orange-50" />
                <StatCard icon={<Activity className="w-5 h-5 text-green-600" />} label="Total Attempts" value={totals.total_attempts?.toLocaleString()} color="bg-green-50" />
                <StatCard icon={<Award className="w-5 h-5 text-purple-600" />} label="Completion Rate" value={`${completionPct}%`} sub={`${totals.completed_attempts?.toLocaleString()} submitted`} color="bg-purple-50" />
            </div>

            {/* Health Bar */}
            <div className="bg-gradient-to-r from-indigo-50 to-purple-50 border border-indigo-100 rounded-xl p-5 grid grid-cols-3 gap-6">
                {[
                    { label: 'Completion Rate', value: health.overall_completion_rate, suffix: '%', color: 'blue' },
                    { label: 'Avg Accuracy', value: health.overall_avg_accuracy, suffix: '%', color: 'green' },
                    { label: 'Avg Percentile', value: health.avg_percentile, suffix: 'th', color: 'purple' },
                ].map((h, i) => (
                    <div key={i} className="text-center">
                        <div className={`text-3xl font-black text-${h.color}-600`}>{h.value ?? '—'}{h.suffix}</div>
                        <div className="text-xs text-gray-500 mt-1">{h.label}</div>
                    </div>
                ))}
            </div>

            <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
                {/* Category Popularity */}
                <div className="bg-white border border-gray-100 rounded-xl p-5 shadow-sm">
                    <h3 className="font-bold text-gray-800 mb-4 flex items-center gap-2">
                        <TrendingUp className="w-4 h-4 text-orange-500" /> Category Popularity
                        <span className="ml-auto text-xs text-gray-400 font-normal">by attempt count</span>
                    </h3>
                    {category_popularity.length === 0
                        ? <p className="text-gray-400 text-sm text-center py-6">No attempt data yet</p>
                        : category_popularity.map(c => (
                            <HBar key={c.category} label={c.category || 'Uncategorised'}
                                value={c.attempt_count} max={maxAttempts}
                                sub={`${c.test_count} tests · ${c.unique_students} students`}
                                color={CATEGORY_COLORS[c.category] || 'bg-gray-400'} />
                        ))}
                </div>

                {/* Top Tests Leaderboard */}
                <div className="bg-white border border-gray-100 rounded-xl p-5 shadow-sm">
                    <h3 className="font-bold text-gray-800 mb-4 flex items-center gap-2">
                        <Zap className="w-4 h-4 text-yellow-500" /> Top Attempted Tests
                    </h3>
                    {top_tests.length === 0
                        ? <p className="text-gray-400 text-sm text-center py-6">No tests attempted yet</p>
                        : top_tests.map((t, i) => (
                            <div key={i} className="mb-3">
                                <div className="flex items-center justify-between mb-1">
                                    <div className="flex items-center gap-2 min-w-0">
                                        <span className="text-xs font-black text-gray-300 w-5 shrink-0">#{i + 1}</span>
                                        <span className="text-sm font-semibold text-gray-800 truncate">{t.title}</span>
                                    </div>
                                    <span className="text-xs font-bold text-gray-700 shrink-0 ml-2">{t.attempt_count} attempts</span>
                                </div>
                                <div className="flex items-center gap-2">
                                    <div className="flex-1 bg-gray-100 rounded-full h-1.5">
                                        <div className="h-1.5 rounded-full bg-gradient-to-r from-yellow-400 to-orange-500 transition-all duration-700"
                                            style={{ width: `${(t.attempt_count / maxTestAttempts) * 100}%` }} />
                                    </div>
                                    <span className="text-[10px] text-gray-400 shrink-0">{t.completion_rate ?? 0}% done</span>
                                </div>
                            </div>
                        ))}
                </div>

                {/* Content Gap Alerts */}
                <div className="bg-white border border-gray-100 rounded-xl p-5 shadow-sm">
                    <h3 className="font-bold text-gray-800 mb-1 flex items-center gap-2">
                        <AlertTriangle className="w-4 h-4 text-amber-500" /> Content Gaps
                    </h3>
                    <p className="text-xs text-gray-400 mb-4">High-demand categories with &lt;5 published tests — prioritise these!</p>
                    {highDemandLowSupply.length === 0 ? (
                        <div className="text-center py-6">
                            <div className="text-2xl mb-1">✅</div>
                            <p className="text-green-600 font-semibold text-sm">All active categories well stocked!</p>
                        </div>
                    ) : highDemandLowSupply.map((c, i) => (
                        <div key={i} className="flex items-center justify-between py-2.5 border-b border-gray-50 last:border-0">
                            <div>
                                <span className="font-bold text-gray-800 text-sm">{c.category}</span>
                                <p className="text-xs text-amber-600">{c.attempt_count} attempts but only {c.tests} tests</p>
                            </div>
                            <span className="bg-amber-100 text-amber-700 text-xs font-bold px-2.5 py-1 rounded-full">Add more!</span>
                        </div>
                    ))}
                </div>

                {/* Top Students */}
                <div className="bg-white border border-gray-100 rounded-xl p-5 shadow-sm">
                    <h3 className="font-bold text-gray-800 mb-4 flex items-center gap-2">
                        <Award className="w-4 h-4 text-purple-500" /> Most Active Students
                    </h3>
                    {top_users.length === 0 ? (
                        <p className="text-gray-400 text-sm text-center py-6">No student activity yet</p>
                    ) : top_users.map((u, i) => (
                        <div key={i} className="flex items-center gap-3 py-2.5 border-b border-gray-50 last:border-0">
                            <div className="w-8 h-8 rounded-full bg-gradient-to-br from-indigo-400 to-purple-600 flex items-center justify-center text-white text-xs font-black shrink-0">
                                {u.name?.charAt(0)?.toUpperCase() || '?'}
                            </div>
                            <div className="flex-1 min-w-0">
                                <p className="text-sm font-semibold text-gray-800 truncate">{u.name}</p>
                                <p className="text-xs text-gray-400 truncate">{u.email}</p>
                            </div>
                            <div className="text-right shrink-0">
                                <p className="text-sm font-black text-gray-800">{u.attempt_count}</p>
                                <p className="text-[10px] text-gray-400">{u.avg_accuracy ?? 0}% acc.</p>
                            </div>
                        </div>
                    ))}
                </div>
            </div>

            {/* Weekly Trend Mini Chart */}
            <div className="bg-white border border-gray-100 rounded-xl p-5 shadow-sm">
                <h3 className="font-bold text-gray-800 mb-4 flex items-center gap-2">
                    <Activity className="w-4 h-4 text-green-500" /> Last 14 Days — Attempt Activity
                </h3>
                {weekly_trend.length === 0 ? (
                    <p className="text-gray-400 text-sm text-center py-4">No data yet</p>
                ) : (
                    <div className="flex items-end gap-1 h-24">
                        {weekly_trend.map((d, i) => (
                            <div key={i} className="flex-1 flex flex-col items-center gap-1 group">
                                <div className="relative w-full">
                                    <div
                                        className="bg-indigo-400 group-hover:bg-indigo-600 rounded-t transition-all duration-300 w-full"
                                        style={{ height: `${Math.max(4, (d.attempt_count / maxTrendCount) * 80)}px` }}
                                        title={`${d.day}: ${d.attempt_count} attempts`}
                                    />
                                </div>
                                <span className="text-[9px] text-gray-400 rotate-45 origin-left whitespace-nowrap">
                                    {d.day?.slice(5)}
                                </span>
                            </div>
                        ))}
                    </div>
                )}
            </div>
        </div>
    );
};
