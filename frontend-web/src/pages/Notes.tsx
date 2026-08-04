import { useEffect, useMemo, useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { ConfigAPI, PaymentAPI, type NotesOfferConfig, type NotesFileInfo } from '../services/api';
import { LegalFooter } from '../components/common/LegalFooter';

// Pretty short tags for the exam-family slugs the manifest carries. Kept tiny
// so the badges fit cleanly on a card without overflowing.
const EXAM_LABELS: Record<string, string> = {
    ssc: 'SSC',
    rrb: 'RRB',
    banks: 'Banks',
    state_psc: 'State PSC',
    psu: 'PSU',
};

// Storefront page for the Master Notes Bundle. Everything pricing-related
// (price, UPI handle, contact email) is fetched at runtime from the backend
// /config/notes endpoint so it can be rotated from Railway env vars without
// a SPA redeploy.

const formatINR = (n: number) => `₹${n.toLocaleString('en-IN')}`;

const buildUpiUrl = (cfg: NotesOfferConfig) => {
    const params = new URLSearchParams({
        pa: cfg.upi_id,
        pn: cfg.payee_name,
        am: String(cfg.price_inr),
        cu: 'INR',
        tn: 'Pariksha365 Notes Bundle',
    });
    return `upi://pay?${params.toString()}`;
};

export const Notes = () => {
    const navigate = useNavigate();
    const [cfg, setCfg] = useState<NotesOfferConfig | null>(null);
    const [loading, setLoading] = useState(true);
    const [copied, setCopied] = useState<'upi' | 'email' | null>(null);
    const [hasAccess, setHasAccess] = useState(false);
    const [noteFiles, setNoteFiles] = useState<NotesFileInfo[]>([]);
    const [buyingCashfree, setBuyingCashfree] = useState(false);
    const [openingId, setOpeningId] = useState<string | null>(null);

    // The notes file endpoint is Bearer-gated, so we fetch the PDF through the authenticated
    // axios client and hand the browser a blob URL — for reading online (new tab) or downloading.
    const openNote = async (f: NotesFileInfo, mode: 'read' | 'download') => {
        setOpeningId(f.id + mode);
        try {
            const res = await PaymentAPI.fetchNoteBlob(f.id);
            const blob = new Blob([res.data], { type: 'application/pdf' });
            const url = URL.createObjectURL(blob);
            if (mode === 'read') {
                window.open(url, '_blank', 'noopener,noreferrer');
            } else {
                const a = document.createElement('a');
                a.href = url;
                a.download = f.filename || `${f.id}.pdf`;
                document.body.appendChild(a);
                a.click();
                a.remove();
            }
            setTimeout(() => URL.revokeObjectURL(url), 60000);
        } catch {
            alert('Could not open this book. Please try again.');
        } finally {
            setOpeningId(null);
        }
    };

    useEffect(() => {
        let active = true;
        ConfigAPI.getNotesOffer()
            .then((res) => { if (active) setCfg(res.data); })
            .catch(() => {
                if (active) setCfg({
                    enabled: true,
                    price_inr: 100,
                    upi_id: 'bhanuprakashnaidu13579@okicici',
                    payee_name: 'Pariksha365 Notes',
                    contact_email: 'contact@gsicorp.in',
                    bundle_title: 'Pariksha365 Master Notes Bundle',
                    page_count: 1500,
                    subject_count: 15,
                    materials: [],
                    sample_available: false,
                    sample_title: 'Polity & Constitution — Common Book',
                    sample_pdf_url: null,
                    cashfree_enabled: false,
                });
            })
            .finally(() => { if (active) setLoading(false); });

        // Check if logged-in user already purchased the notes
        if (localStorage.getItem('token')) {
            PaymentAPI.getNotesAccess()
                .then((res) => {
                    if (!active) return;
                    setHasAccess(res.data.has_access);
                    if (res.data.has_access) setNoteFiles(res.data.files);
                })
                .catch(() => {});
        }

        return () => { active = false; };
    }, []);

    const handleBuyCashfree = async () => {
        if (!localStorage.getItem('token')) {
            navigate('/auth');
            return;
        }
        setBuyingCashfree(true);
        try {
            const res = await PaymentAPI.createNotesOrder();
            window.location.href = res.data.checkout_url;
        } catch {
            alert('Could not start payment. Please try again.');
            setBuyingCashfree(false);
        }
    };

    // Group materials by sample-or-not for the storefront. Quant/reasoning/
    // English/vocabulary land in "Premium-only — paid bundle" so it's clear
    // those titles are NOT in the free sample. Polity is the free sample.
    const grouped = useMemo(() => {
        if (!cfg) return { common: [], premium: [] };
        const premiumIds = new Set([
            'arithmetic_ssc_rrb', 'quant_banks',
            'reasoning_ssc_rrb', 'reasoning_banks',
            'english_ssc_rrb', 'english_banks',
            'vocabulary',
        ]);
        const common = cfg.materials.filter(m => !premiumIds.has(m.id));
        const premium = cfg.materials.filter(m => premiumIds.has(m.id));
        return { common, premium };
    }, [cfg]);

    const copy = async (kind: 'upi' | 'email', value: string) => {
        try {
            await navigator.clipboard.writeText(value);
            setCopied(kind);
            setTimeout(() => setCopied(null), 1800);
        } catch { /* ignore */ }
    };

    if (loading || !cfg) {
        return (
            <div className="min-h-screen bg-gray-50 flex items-center justify-center">
                <div className="text-center">
                    <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-orange-600 mx-auto"></div>
                    <p className="mt-4 text-gray-500 font-medium">Loading offer...</p>
                </div>
            </div>
        );
    }

    if (!cfg.enabled) {
        return (
            <div className="min-h-screen bg-gray-50 flex items-center justify-center px-4">
                <div className="max-w-md w-full bg-white rounded-2xl p-10 text-center border border-gray-100 shadow">
                    <h1 className="text-xl font-bold text-gray-900 mb-2">Notes bundle is currently unavailable</h1>
                    <p className="text-gray-500 mb-6">We're refreshing the bundle. Please check back soon.</p>
                    <button onClick={() => navigate('/dashboard')}
                        className="bg-orange-600 hover:bg-orange-700 text-white font-bold py-2.5 px-6 rounded-lg">
                        Back to Dashboard
                    </button>
                </div>
            </div>
        );
    }

    const upiUrl = buildUpiUrl(cfg);

    return (
        <div className="min-h-screen bg-gradient-to-b from-orange-50/40 via-white to-white">
            {/* Top bar */}
            <header className="sticky top-0 z-30 bg-white/90 backdrop-blur border-b border-gray-100">
                <div className="max-w-5xl mx-auto px-4 py-3 flex items-center justify-between">
                    <button onClick={() => navigate(-1)} className="flex items-center gap-2 text-gray-600 hover:text-gray-900 text-sm font-semibold">
                        <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M15 19l-7-7 7-7" /></svg>
                        Back
                    </button>
                    <span className="text-xs font-bold tracking-wider text-orange-600 uppercase">Pariksha365 · Notes</span>
                    <div className="w-10" />
                </div>
            </header>

            <main className="max-w-5xl mx-auto px-4 py-10 md:py-14">
                {/* Hero */}
                <section className="text-center mb-10">
                    <span className="inline-block bg-orange-100 text-orange-700 text-xs font-black uppercase tracking-wider px-3 py-1 rounded-full mb-4">
                        Optional · Student-friendly pricing
                    </span>
                    <h1 className="text-3xl md:text-5xl font-black text-gray-900 leading-tight max-w-3xl mx-auto">
                        {cfg.bundle_title}
                    </h1>
                    <p className="mt-4 text-base md:text-lg text-gray-600 max-w-2xl mx-auto">
                        Hand-curated revision notes covering <span className="font-bold text-gray-900">{cfg.subject_count} subjects</span> across <span className="font-bold text-gray-900">{cfg.page_count.toLocaleString('en-IN')}+ pages</span>. Built from the same syllabus and PYQ patterns this app trains you on — so you revise exactly what shows up.
                    </p>

                    {/* Anchor + price */}
                    <div className="mt-8 inline-flex items-end gap-3">
                        <span className="text-gray-400 line-through text-2xl font-bold">₹499</span>
                        <span className="text-5xl md:text-6xl font-black text-orange-600 tracking-tight">{formatINR(cfg.price_inr)}</span>
                        <span className="text-gray-500 text-sm pb-2">one-time · no subscription</span>
                    </div>
                    <p className="mt-2 text-xs text-gray-400">Lifetime access to the PDF set. Updates included.</p>

                    {/* Free sample — reciprocity nudge. Lets students judge the
                        quality before paying. The sample is intentionally a
                        static-GK book (Polity); quant/reasoning/English are
                        premium-only and never sampled. */}
                    {cfg.sample_available && cfg.sample_pdf_url && (
                        <div className="mt-6 inline-flex flex-col items-center gap-2">
                            <a href={ConfigAPI.notesSampleUrl()}
                                target="_blank" rel="noopener noreferrer"
                                className="inline-flex items-center gap-2 bg-white hover:bg-gray-50 border-2 border-orange-200 text-orange-700 font-bold px-5 py-3 rounded-xl shadow-sm transition-colors">
                                <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 10v6m0 0l-3-3m3 3l3-3M3 17V7a2 2 0 012-2h6l2 2h6a2 2 0 012 2v8a2 2 0 01-2 2H5a2 2 0 01-2-2z" /></svg>
                                Download free sample · {cfg.sample_title.replace(' — Common Book', '')}
                            </a>
                            <span className="text-xs text-gray-400">No signup needed · ~1.5 MB PDF</span>
                        </div>
                    )}
                </section>

                {/* What's inside — real list pulled from the build manifest so
                    students see exactly the named books they're getting. The
                    static cards we used to show were generic — buyers asked
                    for explicit titles before paying. */}
                {cfg.materials.length > 0 && (
                    <section className="mb-12">
                        <h2 className="text-xl md:text-2xl font-black text-gray-900 mb-1">What's inside the bundle</h2>
                        <p className="text-sm text-gray-500 mb-6">
                            {cfg.materials.length} books — the same set the app uses to teach you. Listed by exact title.
                        </p>

                        {grouped.common.length > 0 && (
                            <>
                                <h3 className="text-xs font-black text-gray-500 uppercase tracking-wider mb-3">
                                    Static GK &amp; Awareness <span className="text-orange-600">· free sample available</span>
                                </h3>
                                <div className="grid md:grid-cols-2 gap-3 mb-8">
                                    {grouped.common.map((m) => {
                                        const isSample = m.title.toLowerCase().startsWith('polity') && cfg.sample_available;
                                        return (
                                            <div key={m.id} className={`bg-white rounded-xl p-5 border shadow-sm ${isSample ? 'border-orange-300 ring-1 ring-orange-200' : 'border-gray-100'}`}>
                                                <div className="flex items-start justify-between gap-3 mb-2">
                                                    <h4 className="font-black text-gray-900 leading-tight">{m.title}</h4>
                                                    {isSample && (
                                                        <span className="flex-shrink-0 bg-orange-600 text-white text-[10px] font-black uppercase tracking-wider px-2 py-1 rounded-full">
                                                            Free sample
                                                        </span>
                                                    )}
                                                </div>
                                                {m.subtitle && <p className="text-sm text-gray-500 leading-relaxed mb-3">{m.subtitle}</p>}
                                                <div className="flex flex-wrap gap-1.5">
                                                    {m.exams.map(e => (
                                                        <span key={e} className="text-[10px] font-bold bg-gray-100 text-gray-600 px-2 py-0.5 rounded uppercase tracking-wider">
                                                            {EXAM_LABELS[e] || e}
                                                        </span>
                                                    ))}
                                                </div>
                                            </div>
                                        );
                                    })}
                                </div>
                            </>
                        )}

                        {grouped.premium.length > 0 && (
                            <>
                                <h3 className="text-xs font-black text-gray-500 uppercase tracking-wider mb-3">
                                    Quant · Reasoning · English <span className="text-gray-400">· paid bundle only</span>
                                </h3>
                                <div className="grid md:grid-cols-2 gap-3">
                                    {grouped.premium.map((m) => (
                                        <div key={m.id} className="bg-gradient-to-br from-gray-900 to-slate-800 rounded-xl p-5 text-white shadow-sm">
                                            <div className="flex items-start justify-between gap-3 mb-2">
                                                <h4 className="font-black leading-tight">{m.title}</h4>
                                                <svg className="w-4 h-4 flex-shrink-0 text-amber-400 mt-1" fill="currentColor" viewBox="0 0 20 20"><path fillRule="evenodd" d="M5 9V7a5 5 0 0110 0v2a2 2 0 012 2v5a2 2 0 01-2 2H5a2 2 0 01-2-2v-5a2 2 0 012-2zm8-2v2H7V7a3 3 0 016 0z" clipRule="evenodd" /></svg>
                                            </div>
                                            {m.subtitle && <p className="text-sm text-gray-300 leading-relaxed mb-3">{m.subtitle}</p>}
                                            <div className="flex flex-wrap gap-1.5">
                                                {m.exams.map(e => (
                                                    <span key={e} className="text-[10px] font-bold bg-white/10 text-gray-200 px-2 py-0.5 rounded uppercase tracking-wider">
                                                        {EXAM_LABELS[e] || e}
                                                    </span>
                                                ))}
                                            </div>
                                        </div>
                                    ))}
                                </div>
                            </>
                        )}
                    </section>
                )}

                {/* Payment / Download block */}
                <section className="bg-white rounded-2xl border border-gray-100 shadow-md p-6 md:p-10 mb-10">
                    {hasAccess ? (
                        /* ── Already purchased: show downloads ── */
                        <>
                            <div className="flex items-center gap-3 mb-4">
                                <div className="w-10 h-10 bg-green-100 rounded-full flex items-center justify-center flex-shrink-0">
                                    <svg className="w-5 h-5 text-green-600" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z" /></svg>
                                </div>
                                <div>
                                    <h2 className="text-xl font-black text-gray-900">You own the bundle</h2>
                                    <p className="text-sm text-gray-500">Lifetime access — download any time.</p>
                                </div>
                            </div>
                            {noteFiles.length > 0 ? (
                                <div className="grid sm:grid-cols-2 gap-3 mt-4">
                                    {noteFiles.map((f) => (
                                        <div
                                            key={f.id}
                                            className="flex items-center gap-3 bg-gray-50 border border-gray-200 rounded-xl p-4"
                                        >
                                            <svg className="w-8 h-8 text-orange-500 flex-shrink-0" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path strokeLinecap="round" strokeLinejoin="round" strokeWidth={1.5} d="M7 21h10a2 2 0 002-2V9.414a1 1 0 00-.293-.707l-5.414-5.414A1 1 0 0012.586 3H7a2 2 0 00-2 2v14a2 2 0 002 2z" /></svg>
                                            <div className="flex-1 min-w-0">
                                                <p className="font-bold text-gray-900 text-sm leading-tight truncate">{f.title}</p>
                                                <div className="flex gap-3 mt-1.5">
                                                    <button
                                                        onClick={() => openNote(f, 'read')}
                                                        disabled={openingId === f.id + 'read'}
                                                        className="text-xs font-bold text-orange-600 hover:text-orange-700 disabled:opacity-50"
                                                    >
                                                        {openingId === f.id + 'read' ? 'Opening…' : '📖 Read online'}
                                                    </button>
                                                    <button
                                                        onClick={() => openNote(f, 'download')}
                                                        disabled={openingId === f.id + 'download'}
                                                        className="text-xs font-bold text-gray-600 hover:text-gray-800 disabled:opacity-50"
                                                    >
                                                        {openingId === f.id + 'download' ? 'Preparing…' : '⬇ Download PDF'}
                                                    </button>
                                                </div>
                                            </div>
                                        </div>
                                    ))}
                                </div>
                            ) : (
                                <p className="text-sm text-gray-500 mt-3">PDFs are being prepared. Check back shortly or contact {cfg.contact_email}.</p>
                            )}
                        </>
                    ) : cfg.cashfree_enabled ? (
                        /* ── Cashfree checkout ── */
                        <>
                            <h2 className="text-2xl font-black text-gray-900 mb-2">Get instant access</h2>
                            <p className="text-gray-500 mb-6">
                                Pay {formatINR(cfg.price_inr)} securely via Cashfree (UPI / cards / netbanking). Download starts immediately after payment.
                            </p>
                            <button
                                onClick={handleBuyCashfree}
                                disabled={buyingCashfree}
                                className="w-full bg-orange-600 hover:bg-orange-700 disabled:opacity-60 text-white font-black py-4 rounded-xl transition-colors shadow-lg shadow-orange-500/30 text-lg mb-4"
                            >
                                {buyingCashfree ? 'Opening payment…' : `Pay ${formatINR(cfg.price_inr)} · Get instant access →`}
                            </button>
                            <p className="text-xs text-gray-400 text-center mb-6">
                                Secured by Cashfree · UPI / Debit / Credit / Netbanking · 7-day refund guarantee
                            </p>
                            <div className="border-t border-gray-100 pt-6">
                                <h3 className="text-sm font-bold text-gray-900 mb-2">Refunds &amp; guarantees</h3>
                                <p className="text-sm text-gray-500 leading-relaxed">
                                    Not the right fit? Email us within 7 days and we refund the full {formatINR(cfg.price_inr)}. No forms, no questions.
                                </p>
                            </div>
                        </>
                    ) : (
                        /* ── Manual UPI fallback (used when Cashfree is not yet configured) ── */
                        <>
                            <h2 className="text-2xl font-black text-gray-900 mb-2">How to get the bundle</h2>
                            <p className="text-gray-500 mb-6">
                                Pay {formatINR(cfg.price_inr)} via UPI, then email us the transaction reference. We send the PDFs within 24 hours.
                            </p>
                            <ol className="space-y-5 mb-8">
                                <li className="flex gap-4">
                                    <span className="flex-shrink-0 w-8 h-8 rounded-full bg-orange-600 text-white font-black flex items-center justify-center">1</span>
                                    <div className="flex-1">
                                        <p className="font-bold text-gray-900 mb-1">Pay {formatINR(cfg.price_inr)} to this UPI ID</p>
                                        <div className="flex flex-col sm:flex-row gap-2 sm:items-center">
                                            <code className="bg-gray-100 px-3 py-2 rounded-lg text-sm font-mono text-gray-800 break-all">{cfg.upi_id}</code>
                                            <button onClick={() => copy('upi', cfg.upi_id)}
                                                className="text-xs font-bold bg-orange-100 hover:bg-orange-200 text-orange-700 px-3 py-2 rounded-lg transition-colors">
                                                {copied === 'upi' ? '✓ Copied' : 'Copy UPI ID'}
                                            </button>
                                            <a href={upiUrl} className="text-xs font-bold bg-orange-600 hover:bg-orange-700 text-white px-3 py-2 rounded-lg transition-colors text-center">
                                                Open in UPI app
                                            </a>
                                        </div>
                                    </div>
                                </li>
                                <li className="flex gap-4">
                                    <span className="flex-shrink-0 w-8 h-8 rounded-full bg-orange-600 text-white font-black flex items-center justify-center">2</span>
                                    <div className="flex-1">
                                        <p className="font-bold text-gray-900 mb-1">Email the UPI transaction ID</p>
                                        <div className="flex flex-col sm:flex-row gap-2 sm:items-center">
                                            <code className="bg-gray-100 px-3 py-2 rounded-lg text-sm font-mono text-gray-800 break-all">{cfg.contact_email}</code>
                                            <button onClick={() => copy('email', cfg.contact_email)}
                                                className="text-xs font-bold bg-orange-100 hover:bg-orange-200 text-orange-700 px-3 py-2 rounded-lg transition-colors">
                                                {copied === 'email' ? '✓ Copied' : 'Copy email'}
                                            </button>
                                        </div>
                                    </div>
                                </li>
                                <li className="flex gap-4">
                                    <span className="flex-shrink-0 w-8 h-8 rounded-full bg-orange-600 text-white font-black flex items-center justify-center">3</span>
                                    <div className="flex-1">
                                        <p className="font-bold text-gray-900 mb-1">Receive the PDFs in your inbox within 24 hours</p>
                                    </div>
                                </li>
                            </ol>
                            <div className="border-t border-gray-100 pt-6">
                                <h3 className="text-sm font-bold text-gray-900 mb-2">Refunds &amp; guarantees</h3>
                                <p className="text-sm text-gray-500 leading-relaxed">
                                    Not the right fit? Email us within 7 days and we refund the full {formatINR(cfg.price_inr)}. No forms, no questions.
                                </p>
                            </div>
                        </>
                    )}
                </section>

                {/* Trust strip */}
                <section className="grid md:grid-cols-3 gap-4 mb-12">
                    <div className="bg-white rounded-xl p-4 border border-gray-100 text-center">
                        <p className="text-2xl font-black text-orange-600">7-day</p>
                        <p className="text-xs text-gray-500 font-semibold uppercase tracking-wider">Refund window</p>
                    </div>
                    <div className="bg-white rounded-xl p-4 border border-gray-100 text-center">
                        <p className="text-2xl font-black text-orange-600">{cfg.subject_count}+</p>
                        <p className="text-xs text-gray-500 font-semibold uppercase tracking-wider">Subjects covered</p>
                    </div>
                    <div className="bg-white rounded-xl p-4 border border-gray-100 text-center">
                        <p className="text-2xl font-black text-orange-600">Lifetime</p>
                        <p className="text-xs text-gray-500 font-semibold uppercase tracking-wider">Access &amp; updates</p>
                    </div>
                </section>

                {/* FAQ */}
                <section className="mb-16">
                    <h2 className="text-xl font-black text-gray-900 mb-4">Frequently asked</h2>
                    <div className="space-y-3">
                        {[
                            { q: `Why only ${formatINR(cfg.price_inr)}?`, a: 'We want every serious aspirant to be able to afford it. The marginal cost of distributing a PDF is essentially zero — pricing it at ₹100 keeps it accessible without diluting quality.' },
                            { q: 'Can I keep using the app without buying these notes?', a: 'Yes — 100%. The PYQs, mock tests, daily quizzes and weak-topic engine are free and stay free. The notes bundle is purely optional.' },
                            { q: 'What format are the notes?', a: 'Searchable, printable PDFs organised by subject. You can read them on phone, tablet, laptop, or print them.' },
                            { q: 'Is this an EMI / subscription?', a: 'No. One-time payment, lifetime access, all future updates included.' },
                        ].map((f, i) => (
                            <details key={i} className="bg-white rounded-xl border border-gray-100 p-4 group">
                                <summary className="font-bold text-gray-900 cursor-pointer list-none flex items-center justify-between">
                                    {f.q}
                                    <svg className="w-4 h-4 text-gray-400 group-open:rotate-180 transition-transform" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M19 9l-7 7-7-7" /></svg>
                                </summary>
                                <p className="mt-3 text-sm text-gray-500 leading-relaxed">{f.a}</p>
                            </details>
                        ))}
                    </div>
                </section>

                {/* Footer CTA */}
                {!hasAccess && (
                    <section className="bg-gradient-to-br from-orange-600 to-amber-600 rounded-2xl p-8 md:p-10 text-center text-white shadow-xl">
                        <h2 className="text-2xl md:text-3xl font-black mb-2">Ready to revise smarter?</h2>
                        <p className="text-orange-100 mb-6 max-w-xl mx-auto">
                            {cfg.cashfree_enabled
                                ? `Pay ${formatINR(cfg.price_inr)} — instant access to all PDFs.`
                                : `Pay ${formatINR(cfg.price_inr)} via UPI and get the full bundle within 24 hours.`}
                        </p>
                        <div className="flex flex-col sm:flex-row gap-3 justify-center items-center">
                            {cfg.cashfree_enabled ? (
                                <button
                                    onClick={handleBuyCashfree}
                                    disabled={buyingCashfree}
                                    className="bg-white text-orange-700 font-black px-6 py-3 rounded-xl hover:bg-orange-50 disabled:opacity-60 transition-colors shadow"
                                >
                                    {buyingCashfree ? 'Opening payment…' : `Pay ${formatINR(cfg.price_inr)} →`}
                                </button>
                            ) : (
                                <a href={upiUrl}
                                    className="bg-white text-orange-700 font-black px-6 py-3 rounded-xl hover:bg-orange-50 transition-colors shadow">
                                    Pay {formatINR(cfg.price_inr)} via UPI →
                                </a>
                            )}
                            <a href={`mailto:${cfg.contact_email}?subject=${encodeURIComponent('Pariksha365 Notes Bundle — question')}`}
                                className="bg-orange-700/40 hover:bg-orange-700/60 border border-white/30 text-white font-bold px-6 py-3 rounded-xl transition-colors">
                                Have a question? Email us
                            </a>
                        </div>
                    </section>
                )}
            </main>
            <LegalFooter />
        </div>
    );
};
