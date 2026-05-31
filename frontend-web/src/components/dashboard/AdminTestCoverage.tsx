import { useEffect, useMemo, useState } from 'react';
import { AdminTestSeriesAPI, type CoverageRow, type CoverageResponse } from '../../services/api';

// Admin view of every TestSeries (PYQ + MOCK) with actual vs sanctioned
// question count and a publish toggle. Lets the admin override the loader's
// 100% gate paper-by-paper — useful when a 98/100 paper is fine to ship and
// when a flagged published paper needs to come down fast.

const STATUS_BADGE: Record<CoverageRow['status'], { label: string; cls: string }> = {
    complete:      { label: '100%',        cls: 'bg-green-100 text-green-700 ring-green-200' },
    near_complete: { label: 'near (≥95%)', cls: 'bg-emerald-100 text-emerald-700 ring-emerald-200' },
    partial:       { label: 'partial',     cls: 'bg-amber-100 text-amber-700 ring-amber-200' },
    fragment:      { label: 'fragment',    cls: 'bg-red-100 text-red-700 ring-red-200' },
    no_pattern:    { label: 'no pattern',  cls: 'bg-gray-100 text-gray-600 ring-gray-200' },
};

export const AdminTestCoverage = () => {
    const [data, setData] = useState<CoverageResponse | null>(null);
    const [loading, setLoading] = useState(true);
    const [error, setError] = useState<string | null>(null);
    const [filterType, setFilterType] = useState<'ALL' | 'PYQ' | 'MOCK'>('ALL');
    const [statusFilter, setStatusFilter] = useState<'all' | 'gated' | 'published' | 'incomplete'>('all');
    const [searchQuery, setSearchQuery] = useState('');
    const [savingId, setSavingId] = useState<string | null>(null);

    const load = async () => {
        setLoading(true);
        setError(null);
        try {
            const res = await AdminTestSeriesAPI.getCoverage(
                filterType === 'ALL' ? undefined : filterType
            );
            setData(res.data);
        } catch (e: any) {
            setError(e?.response?.data?.detail || e?.message || 'Failed to load');
        } finally {
            setLoading(false);
        }
    };

    useEffect(() => { load(); }, [filterType]);

    const togglePublish = async (row: CoverageRow) => {
        if (savingId) return;
        // Confirm explicit unpublish — easy to mis-click
        if (row.is_published && !confirm(`Unpublish "${row.title}"? Students will no longer see it.`)) return;
        setSavingId(row.id);
        try {
            await AdminTestSeriesAPI.togglePublish(row.id, !row.is_published);
            // Optimistic local update
            setData(d => d ? {
                ...d,
                summary: {
                    ...d.summary,
                    published: d.summary.published + (row.is_published ? -1 : 1),
                },
                papers: d.papers.map(p => p.id === row.id ? { ...p, is_published: !row.is_published } : p),
            } : d);
        } catch (e: any) {
            alert(e?.response?.data?.detail || 'Toggle failed');
        } finally {
            setSavingId(null);
        }
    };

    const filtered = useMemo(() => {
        if (!data) return [];
        let rows = data.papers;
        if (statusFilter === 'gated') rows = rows.filter(r => !r.is_published);
        if (statusFilter === 'published') rows = rows.filter(r => r.is_published);
        if (statusFilter === 'incomplete') rows = rows.filter(r => r.status !== 'complete');
        if (searchQuery.trim()) {
            const q = searchQuery.trim().toLowerCase();
            rows = rows.filter(r =>
                r.title.toLowerCase().includes(q)
                || (r.category || '').toLowerCase().includes(q)
                || (r.subcategory || '').toLowerCase().includes(q)
                || (r.stage || '').toLowerCase().includes(q)
            );
        }
        return rows;
    }, [data, statusFilter, searchQuery]);

    if (loading) {
        return (
            <div className="p-8 text-center">
                <div className="animate-spin rounded-full h-10 w-10 border-b-2 border-orange-600 mx-auto"></div>
                <p className="mt-3 text-gray-500">Loading coverage…</p>
            </div>
        );
    }

    if (error) {
        return (
            <div className="p-6 text-red-700 bg-red-50 rounded-lg border border-red-200">
                <p className="font-bold mb-1">Failed to load</p>
                <p className="text-sm">{error}</p>
                <button onClick={load} className="mt-3 bg-red-600 hover:bg-red-700 text-white px-4 py-1.5 rounded text-sm font-bold">
                    Retry
                </button>
            </div>
        );
    }

    if (!data) return null;
    const s = data.summary;

    return (
        <div className="p-4 md:p-6 space-y-4">
            <div>
                <h2 className="text-2xl font-black text-gray-900">Test-Series Coverage</h2>
                <p className="text-sm text-gray-500">
                    Each row shows the loaded question count vs the official sanctioned count from the linked exam pattern. Publish-toggle is below.
                </p>
            </div>

            {/* Summary strip */}
            <div className="grid grid-cols-2 md:grid-cols-6 gap-2">
                {[
                    { label: 'Total', val: s.total, cls: 'bg-gray-50 text-gray-700' },
                    { label: 'Published', val: s.published, cls: 'bg-orange-50 text-orange-700' },
                    { label: '100%', val: s.complete, cls: 'bg-green-50 text-green-700' },
                    { label: '≥95%', val: s.near_complete, cls: 'bg-emerald-50 text-emerald-700' },
                    { label: 'Partial', val: s.partial, cls: 'bg-amber-50 text-amber-700' },
                    { label: 'Fragment', val: s.fragment, cls: 'bg-red-50 text-red-700' },
                ].map(c => (
                    <div key={c.label} className={`rounded-lg border border-gray-200 px-3 py-2 ${c.cls}`}>
                        <div className="text-xs font-bold uppercase tracking-wider opacity-70">{c.label}</div>
                        <div className="text-2xl font-black">{c.val}</div>
                    </div>
                ))}
            </div>

            {/* Filter bar */}
            <div className="flex flex-wrap gap-2 items-center bg-white border border-gray-100 rounded-lg p-3 shadow-sm">
                <div className="flex gap-1">
                    {(['ALL', 'PYQ', 'MOCK'] as const).map(t => (
                        <button key={t}
                            onClick={() => setFilterType(t)}
                            className={`px-3 py-1.5 rounded text-xs font-bold uppercase tracking-wider transition-colors ${filterType === t ? 'bg-orange-600 text-white' : 'bg-gray-100 hover:bg-gray-200 text-gray-700'}`}>
                            {t}
                        </button>
                    ))}
                </div>
                <div className="w-px h-6 bg-gray-200" />
                <div className="flex gap-1">
                    {(['all', 'published', 'gated', 'incomplete'] as const).map(t => (
                        <button key={t}
                            onClick={() => setStatusFilter(t)}
                            className={`px-3 py-1.5 rounded text-xs font-bold uppercase tracking-wider transition-colors ${statusFilter === t ? 'bg-gray-900 text-white' : 'bg-gray-100 hover:bg-gray-200 text-gray-700'}`}>
                            {t}
                        </button>
                    ))}
                </div>
                <div className="flex-1 min-w-[200px]">
                    <input type="search" placeholder="Search title / exam / stage…"
                        value={searchQuery} onChange={e => setSearchQuery(e.target.value)}
                        className="w-full px-3 py-1.5 text-sm border border-gray-200 rounded focus:outline-none focus:ring-2 focus:ring-orange-200" />
                </div>
                <button onClick={load} className="text-xs font-bold text-gray-500 hover:text-gray-900 uppercase tracking-wider">
                    Refresh
                </button>
            </div>

            {/* Table */}
            <div className="bg-white border border-gray-100 rounded-lg shadow-sm overflow-hidden">
                <div className="overflow-x-auto">
                    <table className="min-w-full text-sm">
                        <thead className="bg-gray-50 text-xs uppercase tracking-wider text-gray-500">
                            <tr>
                                <th className="text-left px-4 py-3">Paper</th>
                                <th className="text-left px-4 py-3">Type</th>
                                <th className="text-center px-4 py-3 whitespace-nowrap">Coverage</th>
                                <th className="text-center px-4 py-3">Status</th>
                                <th className="text-center px-4 py-3 whitespace-nowrap">Duration</th>
                                <th className="text-center px-4 py-3">Publish</th>
                            </tr>
                        </thead>
                        <tbody className="divide-y divide-gray-100">
                            {filtered.length === 0 && (
                                <tr><td colSpan={6} className="px-4 py-8 text-center text-gray-400">No papers match.</td></tr>
                            )}
                            {filtered.map(r => {
                                const badge = STATUS_BADGE[r.status];
                                const exam = [r.category, r.subcategory, r.stage].filter(Boolean).join(' › ');
                                return (
                                    <tr key={r.id} className={r.is_published ? '' : 'bg-gray-50/40'}>
                                        <td className="px-4 py-3">
                                            <div className="flex items-center gap-2">
                                                <div className="font-bold text-gray-900 leading-tight">{r.title}</div>
                                                <button
                                                    onClick={async () => {
                                                        const nt = prompt('Rename test series:', r.title);
                                                        if (!nt || nt.trim() === '' || nt.trim() === r.title) return;
                                                        setSavingId(r.id);
                                                        try {
                                                            await AdminTestSeriesAPI.patchMeta(r.id, { title: nt.trim() });
                                                            setData(d => d ? {
                                                                ...d,
                                                                papers: d.papers.map(p => p.id === r.id ? { ...p, title: nt.trim() } : p),
                                                            } : d);
                                                        } catch (e: any) {
                                                            alert(e?.response?.data?.detail || 'Rename failed');
                                                        } finally {
                                                            setSavingId(null);
                                                        }
                                                    }}
                                                    disabled={savingId === r.id}
                                                    className="text-[10px] text-gray-400 hover:text-orange-600 px-1.5 py-0.5 rounded border border-transparent hover:border-orange-200 transition-colors disabled:opacity-50"
                                                    title="Rename"
                                                >
                                                    ✎
                                                </button>
                                            </div>
                                            <div className="text-xs text-gray-500 mt-0.5">{exam || '—'}</div>
                                        </td>
                                        <td className="px-4 py-3">
                                            <span className={`text-[10px] font-bold uppercase tracking-wider px-2 py-0.5 rounded ${r.test_type === 'PYQ' ? 'bg-blue-100 text-blue-700' : 'bg-purple-100 text-purple-700'}`}>
                                                {r.test_type}
                                            </span>
                                        </td>
                                        <td className="px-4 py-3 text-center font-mono whitespace-nowrap">
                                            <span className="font-bold">{r.actual}</span>
                                            <span className="text-gray-400"> / </span>
                                            <span className="text-gray-600">{r.sanctioned ?? '?'}</span>
                                            {r.coverage_pct !== null && (
                                                <div className="text-[10px] text-gray-400 mt-0.5">{r.coverage_pct}%</div>
                                            )}
                                        </td>
                                        <td className="px-4 py-3 text-center">
                                            <span className={`text-[10px] font-bold uppercase tracking-wider px-2 py-0.5 rounded ring-1 ${badge.cls}`}>
                                                {badge.label}
                                            </span>
                                        </td>
                                        <td className="px-4 py-3 text-center text-xs text-gray-600 whitespace-nowrap">
                                            {r.total_duration_minutes ? `${r.total_duration_minutes} min` : '—'}
                                            {r.has_sectional_timing && <div className="text-[10px] text-amber-600 font-bold">sectional</div>}
                                        </td>
                                        <td className="px-4 py-3 text-center">
                                            <button
                                                onClick={() => togglePublish(r)}
                                                disabled={savingId === r.id}
                                                className={`relative inline-flex items-center h-6 w-11 rounded-full transition-colors ${r.is_published ? 'bg-orange-600' : 'bg-gray-300'} ${savingId === r.id ? 'opacity-50 cursor-wait' : 'hover:opacity-90'}`}
                                                title={r.is_published ? 'Click to unpublish' : 'Click to publish'}
                                            >
                                                <span className={`inline-block w-4 h-4 bg-white rounded-full shadow transform transition-transform ${r.is_published ? 'translate-x-6' : 'translate-x-1'}`} />
                                            </button>
                                            <div className="text-[10px] text-gray-400 mt-1">
                                                {r.is_published ? 'live' : 'hidden'}
                                            </div>
                                        </td>
                                    </tr>
                                );
                            })}
                        </tbody>
                    </table>
                </div>
            </div>

            <p className="text-xs text-gray-400 text-center">
                Showing {filtered.length} of {data.papers.length} papers. Toggle publish state per paper to override the loader's 100% gate.
            </p>
        </div>
    );
};
