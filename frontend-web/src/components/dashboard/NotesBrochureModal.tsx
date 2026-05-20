import { useEffect, useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { ConfigAPI, type NotesOfferConfig } from '../../services/api';

// Soft "have you seen the notes bundle?" modal that fires once per browser
// session. The pattern matches what Notion / Duolingo / Apple do — a single
// non-blocking promo with a clear dismiss, never re-shown without user
// action. We deliberately do NOT block the dashboard until dismiss; the
// student can ignore the modal and keep working.
//
// Storage:
//   sessionStorage key NOTES_PROMPT_KEY → "shown" once it's been displayed.
//   localStorage key   NOTES_DISMISS_KEY → "dismissed" if the user opted out.
//                                           Cleared after 14 days so they get
//                                           one more reminder, never spammed.

const NOTES_PROMPT_KEY = 'p365_notes_prompt_session';
const NOTES_DISMISS_KEY = 'p365_notes_dismissed_at';
const DISMISS_COOLDOWN_DAYS = 14;

export const NotesBrochureModal = () => {
    const navigate = useNavigate();
    const [open, setOpen] = useState(false);
    const [cfg, setCfg] = useState<NotesOfferConfig | null>(null);

    useEffect(() => {
        // Already shown this session? Stay quiet.
        if (sessionStorage.getItem(NOTES_PROMPT_KEY)) return;

        // User dismissed recently? Respect the cooldown.
        const dismissedRaw = localStorage.getItem(NOTES_DISMISS_KEY);
        if (dismissedRaw) {
            const dismissedAt = Number(dismissedRaw);
            const elapsedDays = (Date.now() - dismissedAt) / (1000 * 60 * 60 * 24);
            if (elapsedDays < DISMISS_COOLDOWN_DAYS) return;
        }

        // Fetch the config; only show modal if the offer is enabled. Tiny
        // delay so the dashboard's own data lands first — modal popping over
        // an empty grey screen looks jarring.
        let active = true;
        const t = setTimeout(() => {
            ConfigAPI.getNotesOffer()
                .then((res) => {
                    if (!active || !res.data?.enabled) return;
                    setCfg(res.data);
                    setOpen(true);
                    sessionStorage.setItem(NOTES_PROMPT_KEY, 'shown');
                })
                .catch(() => { /* silent — never block the dashboard for a promo */ });
        }, 1200);

        return () => { active = false; clearTimeout(t); };
    }, []);

    const close = (markDismissed: boolean) => {
        setOpen(false);
        if (markDismissed) {
            localStorage.setItem(NOTES_DISMISS_KEY, String(Date.now()));
        }
    };

    const goToNotes = () => {
        // Don't mark as "dismissed" — they engaged with the offer.
        setOpen(false);
        navigate('/notes');
    };

    if (!open || !cfg) return null;

    return (
        <div
            className="fixed inset-0 z-[60] bg-black/40 backdrop-blur-sm flex items-end sm:items-center justify-center p-4 animate-fade-in"
            onClick={() => close(false)}
        >
            <div
                className="bg-white rounded-2xl max-w-md w-full shadow-2xl overflow-hidden animate-slide-up-bro"
                onClick={(e) => e.stopPropagation()}
            >
                {/* Banner */}
                <div className="bg-gradient-to-br from-orange-500 to-amber-600 p-6 text-white relative">
                    <button
                        onClick={() => close(false)}
                        aria-label="Close"
                        className="absolute top-3 right-3 w-8 h-8 rounded-full bg-white/20 hover:bg-white/30 flex items-center justify-center transition-colors"
                    >
                        <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2.5} d="M6 18L18 6M6 6l12 12" /></svg>
                    </button>
                    <div className="text-[11px] font-black uppercase tracking-[0.2em] text-orange-100 mb-2">
                        Optional · For students who want notes
                    </div>
                    <h2 className="text-2xl font-black leading-tight mb-1">
                        Revise smarter — full notes for ₹{cfg.price_inr}
                    </h2>
                    <p className="text-orange-50 text-sm">
                        {cfg.subject_count}+ subjects, {cfg.page_count.toLocaleString('en-IN')}+ pages of curated notes — the same syllabus this app trains you on.
                    </p>
                </div>

                {/* Body */}
                <div className="p-6">
                    <ul className="space-y-2.5 mb-5">
                        {[
                            'Hand-written examiner-mindset summaries',
                            'PYQ-style worked examples + trap cards',
                            cfg.sample_available
                                ? 'Free sample available — judge before you buy'
                                : 'Lifetime access · all future updates included',
                            '7-day money-back, no questions asked',
                        ].map((t, i) => (
                            <li key={i} className="flex items-start gap-2 text-sm text-gray-700">
                                <svg className="w-4 h-4 text-green-600 flex-shrink-0 mt-0.5" fill="currentColor" viewBox="0 0 20 20"><path fillRule="evenodd" d="M10 18a8 8 0 100-16 8 8 0 000 16zm3.707-9.293a1 1 0 00-1.414-1.414L9 10.586 7.707 9.293a1 1 0 00-1.414 1.414l2 2a1 1 0 001.414 0l4-4z" clipRule="evenodd" /></svg>
                                <span>{t}</span>
                            </li>
                        ))}
                    </ul>

                    <div className="flex flex-col gap-2">
                        <button
                            onClick={goToNotes}
                            className="w-full bg-orange-600 hover:bg-orange-700 text-white font-black py-3 rounded-xl transition-colors shadow-md shadow-orange-500/30"
                        >
                            See what's inside →
                        </button>
                        <button
                            onClick={() => close(true)}
                            className="w-full bg-transparent text-gray-500 hover:text-gray-700 font-semibold py-2 text-sm transition-colors"
                        >
                            Maybe later
                        </button>
                    </div>
                    <p className="mt-3 text-[11px] text-gray-400 text-center leading-relaxed">
                        Pariksha365's PYQs, mock tests &amp; daily quizzes stay free forever. The notes bundle is purely optional.
                    </p>
                </div>
            </div>

            <style>{`
                @keyframes fade-in { from { opacity: 0; } to { opacity: 1; } }
                .animate-fade-in { animation: fade-in 0.25s ease-out; }
                @keyframes slide-up-bro { from { transform: translateY(40px); opacity: 0; } to { transform: translateY(0); opacity: 1; } }
                .animate-slide-up-bro { animation: slide-up-bro 0.35s ease-out; }
            `}</style>
        </div>
    );
};
