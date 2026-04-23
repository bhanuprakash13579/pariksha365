import { useCallback, useEffect, useState } from 'react';
import {
    Lock, Mail, Plus, Trash2, AlertCircle, CheckCircle, Shield, Users,
} from 'lucide-react';
import { PrivateModuleAPI } from '../../services/api';

type ModuleRow = {
    id: string;
    slug: string;
    name: string;
    description?: string;
    is_active: boolean;
    question_count: number;
    granted_count: number;
};

type AccessRow = {
    id: string;
    email: string;
    note?: string;
    granted_at?: string;
};

export const AdminPrivateModuleManager = () => {
    const [modules, setModules] = useState<ModuleRow[]>([]);
    const [selectedSlug, setSelectedSlug] = useState<string | null>(null);
    const [access, setAccess] = useState<AccessRow[]>([]);
    const [loading, setLoading] = useState(false);
    const [accessLoading, setAccessLoading] = useState(false);
    const [email, setEmail] = useState('');
    const [note, setNote] = useState('');
    const [toast, setToast] = useState<{ type: 'success' | 'error'; message: string } | null>(null);

    useEffect(() => {
        if (!toast) return;
        const t = setTimeout(() => setToast(null), 3500);
        return () => clearTimeout(t);
    }, [toast]);

    const fetchModules = useCallback(async () => {
        setLoading(true);
        try {
            const res = await PrivateModuleAPI.adminListModules();
            const rows: ModuleRow[] = res.data?.modules ?? [];
            setModules(rows);
            if (rows.length > 0 && !selectedSlug) {
                setSelectedSlug(rows[0].slug);
            }
        } catch (err: any) {
            setToast({ type: 'error', message: 'Failed to load private modules.' });
        } finally {
            setLoading(false);
        }
    }, [selectedSlug]);

    const fetchAccess = useCallback(async (slug: string) => {
        setAccessLoading(true);
        try {
            const res = await PrivateModuleAPI.adminListAccess(slug);
            setAccess(res.data?.access ?? []);
        } catch (err) {
            setToast({ type: 'error', message: 'Failed to load whitelist.' });
        } finally {
            setAccessLoading(false);
        }
    }, []);

    useEffect(() => { fetchModules(); }, [fetchModules]);

    useEffect(() => {
        if (selectedSlug) fetchAccess(selectedSlug);
    }, [selectedSlug, fetchAccess]);

    const grant = async () => {
        const cleaned = email.trim().toLowerCase();
        if (!cleaned || !cleaned.includes('@')) {
            setToast({ type: 'error', message: 'Enter a valid email address.' });
            return;
        }
        if (!selectedSlug) return;
        try {
            const res = await PrivateModuleAPI.adminGrantAccess(selectedSlug, cleaned, note.trim() || undefined);
            const status = res.data?.status;
            if (status === 'already_granted') {
                setToast({ type: 'success', message: `${cleaned} already had access.` });
            } else {
                setToast({ type: 'success', message: `Access granted to ${cleaned}.` });
            }
            setEmail('');
            setNote('');
            fetchAccess(selectedSlug);
            fetchModules();
        } catch (err: any) {
            const detail = err?.response?.data?.detail || 'Failed to grant access.';
            setToast({ type: 'error', message: detail });
        }
    };

    const revoke = async (row: AccessRow) => {
        if (!selectedSlug) return;
        if (!confirm(`Revoke access for ${row.email}?\nThey will no longer see this module.`)) return;
        try {
            await PrivateModuleAPI.adminRevokeAccess(selectedSlug, row.id);
            setToast({ type: 'success', message: `Revoked ${row.email}.` });
            fetchAccess(selectedSlug);
            fetchModules();
        } catch (err) {
            setToast({ type: 'error', message: 'Failed to revoke access.' });
        }
    };

    const selectedModule = modules.find((m) => m.slug === selectedSlug);

    return (
        <div className="relative max-w-5xl">
            {toast && (
                <div
                    className={`fixed top-4 right-4 z-50 flex items-center gap-2 px-4 py-3 rounded-lg shadow-lg text-sm font-medium ${toast.type === 'success' ? 'bg-green-600 text-white' : 'bg-red-600 text-white'}`}
                >
                    {toast.type === 'success' ? <CheckCircle className="w-4 h-4" /> : <AlertCircle className="w-4 h-4" />}
                    {toast.message}
                </div>
            )}

            <div className="flex flex-col gap-1 mb-6">
                <h1 className="text-2xl sm:text-3xl font-semibold text-gray-800 dark:text-white flex items-center gap-2">
                    <Lock className="w-6 h-6 text-orange-600" /> Private Modules
                </h1>
                <p className="text-sm text-gray-500 dark:text-gray-400">
                    Whitelist Gmail addresses per private question bank. A user sees a private
                    module only if their login email is on that module&apos;s list.
                </p>
            </div>

            {loading ? (
                <div className="text-gray-400 text-sm">Loading modules…</div>
            ) : modules.length === 0 ? (
                <div className="p-8 bg-yellow-50 dark:bg-gray-800 rounded-lg border border-yellow-200 dark:border-gray-700 text-sm text-gray-600 dark:text-gray-300">
                    No private modules exist yet. Run the seed script (<code className="bg-gray-100 dark:bg-gray-700 px-1 py-0.5 rounded">python3 backend/scripts/seed_epfo_module.py</code>) to create the EPFO APFC module.
                </div>
            ) : (
                <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
                    {/* Module list */}
                    <div className="lg:col-span-1 bg-white dark:bg-gray-800 rounded-lg shadow-sm border border-gray-100 dark:border-gray-700 p-4">
                        <h2 className="text-sm font-semibold text-gray-500 uppercase mb-3 tracking-wide">Modules</h2>
                        <div className="space-y-2">
                            {modules.map((m) => (
                                <button
                                    key={m.id}
                                    onClick={() => setSelectedSlug(m.slug)}
                                    className={`w-full text-left px-3 py-2 rounded-lg border transition-colors ${m.slug === selectedSlug
                                        ? 'bg-orange-50 border-orange-300 text-orange-700 dark:bg-gray-700'
                                        : 'bg-white dark:bg-gray-800 border-gray-200 dark:border-gray-700 hover:bg-gray-50 dark:hover:bg-gray-700 text-gray-700 dark:text-gray-200'
                                        }`}
                                >
                                    <div className="font-semibold text-sm truncate">{m.name}</div>
                                    <div className="flex items-center gap-3 text-xs mt-1 opacity-80">
                                        <span>{m.question_count} Qs</span>
                                        <span>•</span>
                                        <span className="flex items-center gap-1">
                                            <Users className="w-3 h-3" /> {m.granted_count}
                                        </span>
                                    </div>
                                </button>
                            ))}
                        </div>
                    </div>

                    {/* Access manager */}
                    <div className="lg:col-span-2 bg-white dark:bg-gray-800 rounded-lg shadow-sm border border-gray-100 dark:border-gray-700 p-5">
                        {selectedModule ? (
                            <>
                                <div className="flex items-start justify-between gap-3 mb-4">
                                    <div>
                                        <h2 className="font-semibold text-gray-800 dark:text-white">{selectedModule.name}</h2>
                                        {selectedModule.description && (
                                            <p className="text-xs text-gray-500 dark:text-gray-400 mt-1 max-w-xl">
                                                {selectedModule.description}
                                            </p>
                                        )}
                                    </div>
                                    <span className="text-xs bg-orange-100 text-orange-700 px-2 py-1 rounded-full font-bold whitespace-nowrap">
                                        {selectedModule.question_count} questions
                                    </span>
                                </div>

                                <div className="bg-gray-50 dark:bg-gray-900 rounded-lg p-4 mb-5 border border-gray-100 dark:border-gray-700">
                                    <h3 className="text-xs font-semibold text-gray-500 uppercase tracking-wide mb-2 flex items-center gap-2">
                                        <Shield className="w-3.5 h-3.5" /> Grant Access
                                    </h3>
                                    <div className="flex flex-col sm:flex-row gap-2">
                                        <div className="flex-1 relative">
                                            <Mail className="w-4 h-4 text-gray-400 absolute left-3 top-1/2 -translate-y-1/2" />
                                            <input
                                                type="email"
                                                value={email}
                                                onChange={(e) => setEmail(e.target.value)}
                                                placeholder="user@example.com"
                                                className="w-full pl-9 pr-3 py-2 text-sm border border-gray-200 dark:border-gray-700 rounded-lg bg-white dark:bg-gray-800 text-gray-800 dark:text-white focus:outline-none focus:border-orange-400"
                                            />
                                        </div>
                                        <input
                                            type="text"
                                            value={note}
                                            onChange={(e) => setNote(e.target.value)}
                                            placeholder="Note (optional)"
                                            className="flex-1 px-3 py-2 text-sm border border-gray-200 dark:border-gray-700 rounded-lg bg-white dark:bg-gray-800 text-gray-800 dark:text-white focus:outline-none focus:border-orange-400"
                                        />
                                        <button
                                            onClick={grant}
                                            className="inline-flex items-center justify-center gap-1 px-4 py-2 bg-orange-500 hover:bg-orange-600 text-white rounded-lg text-sm font-semibold"
                                        >
                                            <Plus className="w-4 h-4" /> Add
                                        </button>
                                    </div>
                                </div>

                                <h3 className="text-xs font-semibold text-gray-500 uppercase tracking-wide mb-3">
                                    Whitelisted emails ({access.length})
                                </h3>
                                {accessLoading ? (
                                    <div className="text-gray-400 text-sm">Loading…</div>
                                ) : access.length === 0 ? (
                                    <div className="text-sm text-gray-500 italic">
                                        No emails whitelisted yet. Questions from this module are hidden from every user.
                                    </div>
                                ) : (
                                    <div className="divide-y dark:divide-gray-700 border border-gray-100 dark:border-gray-700 rounded-lg overflow-hidden">
                                        {access.map((row) => (
                                            <div
                                                key={row.id}
                                                className="flex items-center justify-between px-3 py-2 bg-white dark:bg-gray-800"
                                            >
                                                <div className="min-w-0 flex-1">
                                                    <div className="text-sm font-medium text-gray-800 dark:text-white truncate">
                                                        {row.email}
                                                    </div>
                                                    {row.note && (
                                                        <div className="text-xs text-gray-500 dark:text-gray-400 truncate">{row.note}</div>
                                                    )}
                                                    {row.granted_at && (
                                                        <div className="text-[10px] text-gray-400 uppercase tracking-wide mt-0.5">
                                                            Granted {new Date(row.granted_at).toLocaleString()}
                                                        </div>
                                                    )}
                                                </div>
                                                <button
                                                    onClick={() => revoke(row)}
                                                    className="p-2 rounded-lg text-red-500 hover:bg-red-50 dark:hover:bg-gray-700"
                                                    title="Revoke access"
                                                >
                                                    <Trash2 className="w-4 h-4" />
                                                </button>
                                            </div>
                                        ))}
                                    </div>
                                )}
                            </>
                        ) : (
                            <div className="text-sm text-gray-500">Select a module to manage access.</div>
                        )}
                    </div>
                </div>
            )}
        </div>
    );
};
