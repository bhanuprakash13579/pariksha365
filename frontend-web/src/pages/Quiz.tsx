import { useEffect, useState } from 'react';
import { Lock, ChevronRight } from 'lucide-react';
import { DailyQuizzes } from '../components/dashboard/DailyQuizzes';
import { PrivateModuleQuizzes } from '../components/dashboard/PrivateModuleQuizzes';
import { PrivateModuleAPI } from '../services/api';

type AccessibleModule = { slug: string; name: string; description?: string };

/**
 * Quiz page.
 *
 * Primary view = daily-quiz categories (unchanged).
 *
 * On top, if the signed-in user has been whitelisted for one or more private
 * modules (e.g. the EPFO APFC bank), a card appears for each. Tapping a card
 * swaps the page into that module's own quiz universe — subjects, weak-topic
 * suggestions, attempts, etc. are all scoped to the module so signals never
 * cross into the main pool.
 */
export const Quiz = () => {
    const [privateModules, setPrivateModules] = useState<AccessibleModule[]>([]);
    const [activeSlug, setActiveSlug] = useState<string | null>(null);
    const [checked, setChecked] = useState(false);

    useEffect(() => {
        PrivateModuleAPI.listMine()
            .then((r) => setPrivateModules(r.data?.modules ?? []))
            .catch(() => setPrivateModules([]))
            .finally(() => setChecked(true));
    }, []);

    if (activeSlug) {
        return (
            <div>
                <div className="max-w-6xl mx-auto pt-4 px-4 sm:px-0">
                    <button
                        onClick={() => setActiveSlug(null)}
                        className="text-sm text-gray-500 hover:text-gray-700"
                    >
                        ← Back to Daily Quizzes
                    </button>
                </div>
                <PrivateModuleQuizzes slug={activeSlug} />
            </div>
        );
    }

    return (
        <div>
            {checked && privateModules.length > 0 && (
                <div className="max-w-6xl mx-auto pt-6 px-4 sm:px-0">
                    <div className="flex items-center gap-2 mb-3">
                        <span className="text-[10px] font-bold uppercase tracking-wider text-purple-700 bg-purple-100 px-2 py-0.5 rounded-full">
                            Invite-only
                        </span>
                        <h2 className="text-lg font-bold text-gray-900">Your Private Modules</h2>
                    </div>
                    <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-3">
                        {privateModules.map((m) => (
                            <button
                                key={m.slug}
                                onClick={() => setActiveSlug(m.slug)}
                                className="group text-left bg-gradient-to-br from-indigo-50 to-purple-50 border border-purple-200 hover:border-purple-400 rounded-2xl p-5 transition-all hover:shadow-md"
                            >
                                <div className="flex items-start gap-3">
                                    <div className="w-10 h-10 rounded-xl bg-purple-100 text-purple-600 flex items-center justify-center flex-shrink-0">
                                        <Lock className="w-4 h-4" />
                                    </div>
                                    <div className="min-w-0 flex-1">
                                        <h3 className="font-bold text-gray-900">{m.name}</h3>
                                        {m.description && (
                                            <p className="text-xs text-gray-500 mt-1 line-clamp-2">{m.description}</p>
                                        )}
                                    </div>
                                    <ChevronRight className="w-4 h-4 text-purple-500 mt-1 opacity-70 group-hover:opacity-100" />
                                </div>
                            </button>
                        ))}
                    </div>
                </div>
            )}
            <DailyQuizzes />
        </div>
    );
};
