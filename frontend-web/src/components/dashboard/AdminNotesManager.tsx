import { useEffect, useState } from 'react';
import { AdminNotesAPI, type AdminNoteRow, type NotesGrantedUser } from '../../services/api';

/**
 * Admin control for the study-notes catalogue. Every built/uploaded book appears here;
 * students (app + web) can only read/download a book once the admin enables it.
 */
export function AdminNotesManager() {
    const [notes, setNotes] = useState<AdminNoteRow[]>([]);
    const [loading, setLoading] = useState(true);
    const [error, setError] = useState<string | null>(null);
    const [busy, setBusy] = useState<string | null>(null);
    const [grantEmail, setGrantEmail] = useState('');
    const [granting, setGranting] = useState(false);
    const [grantMsg, setGrantMsg] = useState<string | null>(null);
    const [granted, setGranted] = useState<NotesGrantedUser[]>([]);

    const loadGranted = async () => {
        try { setGranted((await AdminNotesAPI.listGranted()).data.users); } catch { /* ignore */ }
    };

    const grant = async () => {
        const email = grantEmail.trim();
        if (!email) return;
        setGranting(true);
        setGrantMsg(null);
        try {
            const res = await AdminNotesAPI.grantAccess(email);
            setGrantMsg(res.data.status === 'already_has_access'
                ? `${res.data.email} already has access.`
                : `✓ Access granted to ${res.data.email} (no watermark).`);
            setGrantEmail('');
            loadGranted();
        } catch (e: any) {
            setGrantMsg(e?.response?.data?.detail || 'Could not grant access. Check the email.');
        } finally {
            setGranting(false);
        }
    };

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

    useEffect(() => { load(); loadGranted(); }, []);

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

            {/* Grant free access to a specific user (no payment → no watermark) */}
            <div className="mb-6 bg-orange-50 dark:bg-gray-800 border border-orange-200 dark:border-gray-700 rounded-xl p-4">
                <p className="font-bold text-gray-800 dark:text-gray-100 mb-1">Give a user free access</p>
                <p className="text-xs text-gray-500 dark:text-gray-400 mb-3">Grants lifetime access to all notes without payment. These accounts get clean, un-watermarked PDFs.</p>
                <div className="flex flex-wrap gap-2">
                    <input
                        type="email"
                        value={grantEmail}
                        onChange={(e) => setGrantEmail(e.target.value)}
                        onKeyDown={(e) => { if (e.key === 'Enter') grant(); }}
                        placeholder="user@email.com"
                        className="flex-1 min-w-[220px] border border-gray-300 dark:border-gray-600 dark:bg-gray-900 rounded-lg px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-orange-400"
                    />
                    <button
                        onClick={grant}
                        disabled={granting || !grantEmail.trim()}
                        className="px-4 py-2 rounded-lg text-sm font-bold bg-orange-500 text-white hover:bg-orange-600 disabled:opacity-50"
                    >
                        {granting ? 'Granting…' : 'Grant access'}
                    </button>
                </div>
                {grantMsg && <p className="text-xs mt-2 font-semibold text-gray-700 dark:text-gray-300">{grantMsg}</p>}
                {granted.length > 0 && (
                    <div className="mt-3 text-xs text-gray-600 dark:text-gray-400">
                        <span className="font-semibold">{granted.length}</span> user{granted.length === 1 ? '' : 's'} with access
                        <span className="ml-1">({granted.filter(g => g.type === 'granted').length} free · {granted.filter(g => g.type === 'paid').length} paid)</span>
                    </div>
                )}
            </div>

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
