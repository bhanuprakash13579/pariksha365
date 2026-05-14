import { useEffect, useMemo, useState } from 'react';
import { QuizAPI } from '../../services/api';

// Admin surface for managing the Current Affairs pool. CA Qs live in the same
// quiz_questions table as static-GK but with is_current_affair=true and
// per-Q event_date / valid_until / last_reviewed_at metadata.
//
// Workflow:
//   1. Add Q via "+ Add CA" (paste stem, options, mark correct, set event_date)
//   2. Browse → status filter (active/expired/unreviewed/all)
//   3. Edit inline — fix typos, refresh dates, toggle publish
//   4. "Mark reviewed" extends the freshness window (admin glanced and confirmed)
//   5. Delete when truly stale (e.g. event got nullified/disputed)

type CAStatus = 'active' | 'expired' | 'unreviewed' | 'all';

interface CARow {
    id: string;
    question_text: string;
    options: { option_text: string; is_correct: boolean }[];
    explanation?: string;
    subject: string;
    topic?: string;
    topic_code?: string;
    difficulty: string;
    is_current_affair: boolean;
    event_date: string | null;
    valid_until: string | null;
    last_reviewed_at: string | null;
    is_published: boolean;
}

interface CAResponse {
    questions: CARow[];
    total: number;
    page: number;
    per_page: number;
    total_pages: number;
    summary: { all: number; active: number; expired: number; unreviewed: number };
}

const blankRow = (): Partial<CARow> => ({
    question_text: '',
    options: [
        { option_text: '', is_correct: true },
        { option_text: '', is_correct: false },
        { option_text: '', is_correct: false },
        { option_text: '', is_correct: false },
    ],
    explanation: '',
    subject: 'General Awareness',
    topic: 'Current Affairs',
    topic_code: 'GA_CURRENT_AFFAIRS',
    difficulty: 'MEDIUM',
    event_date: null,
    valid_until: null,
    is_published: true,
});

const STATUS_BADGE: Record<string, { label: string; cls: string }> = {
    active: { label: 'Active', cls: 'bg-green-100 text-green-700 ring-green-200' },
    expired: { label: 'Expired', cls: 'bg-red-100 text-red-700 ring-red-200' },
    unreviewed: { label: 'Stale', cls: 'bg-amber-100 text-amber-700 ring-amber-200' },
    unpublished: { label: 'Hidden', cls: 'bg-gray-200 text-gray-600 ring-gray-300' },
};

function statusOf(r: CARow): keyof typeof STATUS_BADGE {
    if (!r.is_published) return 'unpublished';
    const today = new Date().toISOString().slice(0, 10);
    if (r.valid_until && r.valid_until < today) return 'expired';
    const thirtyDaysAgo = new Date(Date.now() - 30 * 86400000).toISOString();
    if (!r.last_reviewed_at || r.last_reviewed_at < thirtyDaysAgo) return 'unreviewed';
    return 'active';
}

export const AdminCurrentAffairs = () => {
    const [data, setData] = useState<CAResponse | null>(null);
    const [loading, setLoading] = useState(true);
    const [error, setError] = useState<string | null>(null);
    const [statusFilter, setStatusFilter] = useState<CAStatus>('all');
    const [searchQuery, setSearchQuery] = useState('');
    const [savingId, setSavingId] = useState<string | null>(null);
    const [editing, setEditing] = useState<Partial<CARow> | null>(null);
    const [showCreate, setShowCreate] = useState(false);

    const load = async () => {
        setLoading(true);
        setError(null);
        try {
            const res = await QuizAPI.adminListCA({ status: statusFilter, search: searchQuery || undefined });
            setData(res.data);
        } catch (e: any) {
            setError(e?.response?.data?.detail || e?.message || 'Failed to load');
        } finally {
            setLoading(false);
        }
    };

    useEffect(() => { load(); /* eslint-disable-next-line react-hooks/exhaustive-deps */ }, [statusFilter]);

    const onCreate = async (row: Partial<CARow>) => {
        if (!row.question_text || !row.options || row.options.filter(o => o.option_text.trim()).length < 2) {
            alert('Need a question stem and at least 2 non-empty options.');
            return;
        }
        setSavingId('NEW');
        try {
            await QuizAPI.adminCreateCA(row);
            setShowCreate(false);
            await load();
        } catch (e: any) {
            alert(e?.response?.data?.detail || 'Create failed');
        } finally {
            setSavingId(null);
        }
    };

    const onSave = async (row: Partial<CARow>) => {
        if (!row.id) return;
        setSavingId(row.id);
        try {
            await QuizAPI.adminUpdateCA(row.id, row);
            setEditing(null);
            await load();
        } catch (e: any) {
            alert(e?.response?.data?.detail || 'Save failed');
        } finally {
            setSavingId(null);
        }
    };

    const onMarkReviewed = async (id: string) => {
        setSavingId(id);
        try {
            await QuizAPI.adminMarkCAReviewed(id);
            await load();
        } catch (e: any) {
            alert(e?.response?.data?.detail || 'Failed');
        } finally {
            setSavingId(null);
        }
    };

    const onDelete = async (row: CARow) => {
        if (!confirm(`Delete this CA question? "${row.question_text.slice(0, 80)}..."`)) return;
        setSavingId(row.id);
        try {
            await QuizAPI.adminDeleteCA(row.id);
            await load();
        } catch (e: any) {
            alert(e?.response?.data?.detail || 'Delete failed');
        } finally {
            setSavingId(null);
        }
    };

    const filtered = useMemo(() => {
        if (!data) return [];
        if (!searchQuery.trim()) return data.questions;
        const q = searchQuery.trim().toLowerCase();
        return data.questions.filter(r =>
            r.question_text.toLowerCase().includes(q)
            || (r.explanation || '').toLowerCase().includes(q)
            || (r.topic || '').toLowerCase().includes(q)
        );
    }, [data, searchQuery]);

    if (loading && !data) {
        return <div className="p-8 text-center text-gray-500">Loading current-affairs pool…</div>;
    }
    if (error) {
        return (
            <div className="p-6 text-red-700 bg-red-50 rounded-lg border border-red-200">
                <p className="font-bold mb-1">Failed to load</p><p className="text-sm">{error}</p>
                <button onClick={load} className="mt-3 bg-red-600 hover:bg-red-700 text-white px-4 py-1.5 rounded text-sm font-bold">Retry</button>
            </div>
        );
    }
    if (!data) return null;

    return (
        <div className="p-4 md:p-6 space-y-4">
            <div className="flex items-start justify-between gap-3">
                <div>
                    <h2 className="text-2xl font-black text-gray-900">Current Affairs Manager</h2>
                    <p className="text-sm text-gray-500">
                        Manage time-bound CA questions. <b>Active</b> = published &amp; in window. <b>Stale</b> = not reviewed in 30+ days.
                        Mocks pull from the active pool; daily quiz uses these too.
                    </p>
                </div>
                <button onClick={() => setShowCreate(true)}
                    className="flex-shrink-0 bg-orange-600 hover:bg-orange-700 text-white font-bold px-4 py-2 rounded-lg shadow-sm">
                    + Add CA
                </button>
            </div>

            {/* Summary strip */}
            <div className="grid grid-cols-2 md:grid-cols-4 gap-2">
                {[
                    { key: 'all', label: 'Total', val: data.summary.all, cls: 'bg-gray-50 text-gray-700' },
                    { key: 'active', label: 'Active', val: data.summary.active, cls: 'bg-green-50 text-green-700' },
                    { key: 'unreviewed', label: 'Stale', val: data.summary.unreviewed, cls: 'bg-amber-50 text-amber-700' },
                    { key: 'expired', label: 'Expired', val: data.summary.expired, cls: 'bg-red-50 text-red-700' },
                ].map(c => (
                    <button key={c.key}
                        onClick={() => setStatusFilter(c.key as CAStatus)}
                        className={`rounded-lg border px-3 py-2 transition-colors text-left ${c.cls} ${statusFilter === c.key ? 'border-orange-400 ring-1 ring-orange-200' : 'border-gray-200 hover:border-gray-300'}`}>
                        <div className="text-xs font-bold uppercase tracking-wider opacity-70">{c.label}</div>
                        <div className="text-2xl font-black">{c.val}</div>
                    </button>
                ))}
            </div>

            {/* Search */}
            <div className="flex gap-2 items-center">
                <input type="search" value={searchQuery} onChange={e => setSearchQuery(e.target.value)}
                    onKeyDown={e => { if (e.key === 'Enter') load(); }}
                    placeholder="Search stem, topic, explanation…"
                    className="flex-1 px-3 py-2 text-sm border border-gray-200 rounded focus:outline-none focus:ring-2 focus:ring-orange-200" />
                <button onClick={load} className="text-xs font-bold text-gray-700 hover:text-gray-900 uppercase tracking-wider px-3 py-2 bg-gray-100 hover:bg-gray-200 rounded">
                    Search
                </button>
            </div>

            {/* Table */}
            <div className="bg-white border border-gray-100 rounded-lg shadow-sm overflow-hidden">
                <div className="overflow-x-auto">
                    <table className="min-w-full text-sm">
                        <thead className="bg-gray-50 text-xs uppercase tracking-wider text-gray-500">
                            <tr>
                                <th className="text-left px-4 py-3 w-2/5">Question</th>
                                <th className="text-left px-4 py-3">Topic</th>
                                <th className="text-center px-4 py-3 whitespace-nowrap">Event Date</th>
                                <th className="text-center px-4 py-3 whitespace-nowrap">Valid Until</th>
                                <th className="text-center px-4 py-3">Status</th>
                                <th className="text-center px-4 py-3">Actions</th>
                            </tr>
                        </thead>
                        <tbody className="divide-y divide-gray-100">
                            {filtered.length === 0 && (
                                <tr><td colSpan={6} className="px-4 py-8 text-center text-gray-400">
                                    No CA questions match. Add one to get started.
                                </td></tr>
                            )}
                            {filtered.map(r => {
                                const s = statusOf(r);
                                const badge = STATUS_BADGE[s];
                                return (
                                    <tr key={r.id}>
                                        <td className="px-4 py-3">
                                            <div className="font-medium text-gray-900">{r.question_text}</div>
                                            <div className="text-xs text-gray-500 mt-0.5">
                                                {r.options.map((o, i) => (
                                                    <span key={i} className={`mr-3 ${o.is_correct ? 'text-green-700 font-bold' : 'text-gray-500'}`}>
                                                        {String.fromCharCode(65 + i)}. {o.option_text || '(empty)'}
                                                    </span>
                                                ))}
                                            </div>
                                        </td>
                                        <td className="px-4 py-3 text-xs">{r.topic || '—'}</td>
                                        <td className="px-4 py-3 text-center text-xs whitespace-nowrap">{r.event_date || '—'}</td>
                                        <td className="px-4 py-3 text-center text-xs whitespace-nowrap">{r.valid_until || '—'}</td>
                                        <td className="px-4 py-3 text-center">
                                            <span className={`text-[10px] font-bold uppercase tracking-wider px-2 py-0.5 rounded ring-1 ${badge.cls}`}>
                                                {badge.label}
                                            </span>
                                        </td>
                                        <td className="px-4 py-3 text-center whitespace-nowrap">
                                            <button onClick={() => setEditing(r)}
                                                disabled={savingId === r.id}
                                                className="text-xs font-bold text-blue-600 hover:text-blue-800 mr-3">Edit</button>
                                            <button onClick={() => onMarkReviewed(r.id)}
                                                disabled={savingId === r.id}
                                                className="text-xs font-bold text-emerald-600 hover:text-emerald-800 mr-3">Mark reviewed</button>
                                            <button onClick={() => onDelete(r)}
                                                disabled={savingId === r.id}
                                                className="text-xs font-bold text-red-600 hover:text-red-800">Delete</button>
                                        </td>
                                    </tr>
                                );
                            })}
                        </tbody>
                    </table>
                </div>
            </div>

            {/* Edit / create modal */}
            {(editing || showCreate) && (
                <CAEditModal
                    initial={editing || blankRow()}
                    isCreate={showCreate}
                    saving={savingId === (editing?.id || 'NEW')}
                    onSave={(row) => editing ? onSave(row) : onCreate(row)}
                    onClose={() => { setEditing(null); setShowCreate(false); }}
                />
            )}
        </div>
    );
};


// ─── Edit modal ──────────────────────────────────────────────────────────────

const CAEditModal = ({ initial, isCreate, saving, onSave, onClose }: {
    initial: Partial<CARow>;
    isCreate: boolean;
    saving: boolean;
    onSave: (row: Partial<CARow>) => void;
    onClose: () => void;
}) => {
    const [row, setRow] = useState<Partial<CARow>>(initial);

    const setOpt = (i: number, key: 'option_text' | 'is_correct', value: any) => {
        const opts = [...(row.options || [])];
        opts[i] = { ...opts[i], [key]: value };
        // If toggling is_correct=true, untoggle others
        if (key === 'is_correct' && value === true) {
            opts.forEach((o, j) => { if (j !== i) o.is_correct = false; });
        }
        setRow({ ...row, options: opts });
    };

    return (
        <div className="fixed inset-0 z-50 bg-black/50 flex items-center justify-center p-4" onClick={onClose}>
            <div onClick={e => e.stopPropagation()}
                className="bg-white rounded-2xl shadow-2xl max-w-2xl w-full max-h-[90vh] overflow-y-auto">
                <div className="p-6 border-b border-gray-100 flex items-center justify-between">
                    <h3 className="text-xl font-black text-gray-900">{isCreate ? 'Add Current Affair' : 'Edit Current Affair'}</h3>
                    <button onClick={onClose} className="text-gray-400 hover:text-gray-700 text-2xl leading-none">×</button>
                </div>
                <div className="p-6 space-y-4">
                    <div>
                        <label className="block text-xs font-bold text-gray-700 uppercase tracking-wider mb-1">Question stem</label>
                        <textarea rows={3} value={row.question_text || ''}
                            onChange={e => setRow({ ...row, question_text: e.target.value })}
                            className="w-full px-3 py-2 border border-gray-200 rounded text-sm focus:outline-none focus:ring-2 focus:ring-orange-200"
                            placeholder="Who has been appointed as the new Chief Election Commissioner of India in February 2025?" />
                    </div>

                    <div>
                        <label className="block text-xs font-bold text-gray-700 uppercase tracking-wider mb-1">Options (mark exactly one as correct)</label>
                        {(row.options || []).map((o, i) => (
                            <div key={i} className="flex items-center gap-2 mb-2">
                                <input type="radio" name="correct" checked={o.is_correct}
                                    onChange={() => setOpt(i, 'is_correct', true)}
                                    className="w-4 h-4 text-orange-600" />
                                <span className="text-xs font-bold text-gray-500 w-5">{String.fromCharCode(65 + i)}.</span>
                                <input type="text" value={o.option_text}
                                    onChange={e => setOpt(i, 'option_text', e.target.value)}
                                    className="flex-1 px-2 py-1 border border-gray-200 rounded text-sm focus:outline-none focus:ring-1 focus:ring-orange-200"
                                    placeholder={`Option ${String.fromCharCode(65 + i)}`} />
                            </div>
                        ))}
                    </div>

                    <div className="grid grid-cols-2 gap-3">
                        <div>
                            <label className="block text-xs font-bold text-gray-700 uppercase tracking-wider mb-1">Event Date</label>
                            <input type="date" value={row.event_date || ''}
                                onChange={e => setRow({ ...row, event_date: e.target.value || null })}
                                className="w-full px-2 py-1.5 border border-gray-200 rounded text-sm" />
                        </div>
                        <div>
                            <label className="block text-xs font-bold text-gray-700 uppercase tracking-wider mb-1">Valid Until</label>
                            <input type="date" value={row.valid_until || ''}
                                onChange={e => setRow({ ...row, valid_until: e.target.value || null })}
                                className="w-full px-2 py-1.5 border border-gray-200 rounded text-sm" />
                        </div>
                    </div>

                    <div className="grid grid-cols-3 gap-3">
                        <div>
                            <label className="block text-xs font-bold text-gray-700 uppercase tracking-wider mb-1">Topic</label>
                            <input type="text" value={row.topic || ''}
                                onChange={e => setRow({ ...row, topic: e.target.value })}
                                className="w-full px-2 py-1.5 border border-gray-200 rounded text-sm" />
                        </div>
                        <div>
                            <label className="block text-xs font-bold text-gray-700 uppercase tracking-wider mb-1">Difficulty</label>
                            <select value={row.difficulty || 'MEDIUM'}
                                onChange={e => setRow({ ...row, difficulty: e.target.value })}
                                className="w-full px-2 py-1.5 border border-gray-200 rounded text-sm">
                                <option value="EASY">Easy</option>
                                <option value="MEDIUM">Medium</option>
                                <option value="HARD">Hard</option>
                            </select>
                        </div>
                        <div className="flex items-end">
                            <label className="flex items-center gap-2 text-sm">
                                <input type="checkbox" checked={row.is_published !== false}
                                    onChange={e => setRow({ ...row, is_published: e.target.checked })}
                                    className="w-4 h-4 text-orange-600" />
                                Published
                            </label>
                        </div>
                    </div>

                    <div>
                        <label className="block text-xs font-bold text-gray-700 uppercase tracking-wider mb-1">Explanation</label>
                        <textarea rows={3} value={row.explanation || ''}
                            onChange={e => setRow({ ...row, explanation: e.target.value })}
                            className="w-full px-3 py-2 border border-gray-200 rounded text-sm focus:outline-none focus:ring-2 focus:ring-orange-200"
                            placeholder="Brief context + source. E.g. 'Gyanesh Kumar took charge as CEC in February 2025, replacing Rajiv Kumar.'" />
                    </div>
                </div>
                <div className="p-6 border-t border-gray-100 flex justify-end gap-2">
                    <button onClick={onClose}
                        className="px-4 py-2 text-sm font-bold text-gray-600 hover:text-gray-900">Cancel</button>
                    <button onClick={() => onSave(row)}
                        disabled={saving}
                        className="px-5 py-2 bg-orange-600 hover:bg-orange-700 text-white font-bold text-sm rounded-lg disabled:opacity-50">
                        {saving ? 'Saving…' : (isCreate ? 'Create' : 'Save')}
                    </button>
                </div>
            </div>
        </div>
    );
};
