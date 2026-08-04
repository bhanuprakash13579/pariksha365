import { useEffect, useState } from 'react';
import { AdminNotesAPI, type AdminNoteRow } from '../../services/api';

/**
 * Admin control for the study-notes catalogue. Every built/uploaded book appears here;
 * students (app + web) can only read/download a book once the admin enables it.
 */
export function AdminNotesManager() {
    const [notes, setNotes] = useState<AdminNoteRow[]>([]);
    const [loading, setLoading] = useState(true);
    const [error, setError] = useState<string | null>(null);
    const [busy, setBusy] = useState<string | null>(null);

    const load = async () => {
        setLoading(true);
        setError(null);
        try {
            const res = await AdminNotesAPI.list();
            setNotes(res.data.notes);
        } catch {
            setError('Could not load notes. Are you signed in as admin?');
        } finally {
            setLoading(false);
        }
    };

    useEffect(() => { load(); }, []);

    const toggle = async (n: AdminNoteRow) => {
        setBusy(n.slug);
        // optimistic
        setNotes(prev => prev.map(x => x.slug === n.slug ? { ...x, is_enabled: !x.is_enabled } : x));
        try {
            await AdminNotesAPI.setVisibility(n.slug, !n.is_enabled);
        } catch {
            // revert on failure
            setNotes(prev => prev.map(x => x.slug === n.slug ? { ...x, is_enabled: n.is_enabled } : x));
            setError(`Failed to update "${n.title}".`);
        } finally {
            setBusy(null);
        }
    };

    const enabledCount = notes.filter(n => n.is_enabled).length;

    return (
        <div className="max-w-3xl">
            <div className="flex items-center justify-between mb-4">
                <div>
                    <h2 className="text-xl font-bold text-gray-800 dark:text-gray-100">Study Notes</h2>
                    <p className="text-sm text-gray-500 dark:text-gray-400">
                        Turn a book ON to make it readable/downloadable for students in the app and on the web.
                    </p>
                </div>
                <button onClick={load} className="text-sm font-semibold px-3 py-2 rounded-lg border border-gray-300 dark:border-gray-600 hover:border-orange-400 text-gray-600 dark:text-gray-300">
                    ↻ Refresh
                </button>
            </div>

            {error && <div className="mb-3 text-sm text-red-600 bg-red-50 dark:bg-red-900/20 rounded-lg px-3 py-2">{error}</div>}

            <div className="mb-3 text-sm font-semibold text-gray-600 dark:text-gray-300">
                {enabledCount} of {notes.length} enabled
            </div>

            {loading ? (
                <p className="text-gray-400">Loading…</p>
            ) : (
                <div className="space-y-2">
                    {notes.map(n => (
                        <div key={n.slug} className="flex items-center justify-between bg-white dark:bg-gray-800 border border-gray-200 dark:border-gray-700 rounded-xl px-4 py-3">
                            <div className="min-w-0">
                                <p className="font-semibold text-gray-800 dark:text-gray-100 truncate">{n.title}</p>
                                <p className="text-xs text-gray-400">
                                    <span className="font-mono">{n.slug}</span>
                                    <span className="ml-2 uppercase tracking-wide">{n.source}</span>
                                </p>
                            </div>
                            <button
                                onClick={() => toggle(n)}
                                disabled={busy === n.slug}
                                aria-pressed={n.is_enabled}
                                className={`relative inline-flex h-7 w-12 shrink-0 items-center rounded-full transition-colors ${n.is_enabled ? 'bg-green-500' : 'bg-gray-300 dark:bg-gray-600'} ${busy === n.slug ? 'opacity-60' : ''}`}
                                title={n.is_enabled ? 'Enabled — click to disable' : 'Disabled — click to enable'}
                            >
                                <span className={`inline-block h-5 w-5 transform rounded-full bg-white shadow transition-transform ${n.is_enabled ? 'translate-x-6' : 'translate-x-1'}`} />
                            </button>
                        </div>
                    ))}
                    {notes.length === 0 && <p className="text-gray-400">No notes found. Build the study-notes PDFs and redeploy.</p>}
                </div>
            )}
        </div>
    );
}
