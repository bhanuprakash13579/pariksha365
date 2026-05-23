import { useCallback, useEffect, useState } from 'react';
import { ArrowLeft, Lock, Sparkles } from 'lucide-react';
import { PrivateModuleAPI } from '../../services/api';

function renderExplanation(text: string) {
    return text.split('\n').map((line, i) => {
        const parts = line.split(/\*\*(.*?)\*\*/g);
        return (
            <span key={i} className="block">
                {parts.map((p, j) => j % 2 === 1 ? <strong key={j}>{p}</strong> : p)}
            </span>
        );
    });
}

type ModuleSummary = {
    slug: string;
    name: string;
    description?: string;
};

type SubjectRow = {
    subject: string;
    question_count: number;
    attempted_count: number;
};

type WeakTopicInfo = {
    subject: string;
    topic?: string;
    topic_code: string;
    accuracy: number;
    total_attempted: number;
};

type Question = {
    id: string;
    question_text: string;
    options: { option_text: string; is_correct?: boolean }[];
    explanation?: string;
    subject: string;
    topic: string;
    topic_code: string;
};

type ActiveQuiz = {
    title: string;                 // shown as subject header ("EPFO · Polity")
    questions: Question[];
    current: number;
    answers: Record<string, number>;
    submitted: boolean;
    scorecard: any | null;
};

const moduleHeader = (m: ModuleSummary | null) =>
    m?.name || 'Private Module';

export const PrivateModuleQuizzes = ({ slug }: { slug: string }) => {
    const [module, setModule] = useState<ModuleSummary | null>(null);
    const [subjects, setSubjects] = useState<SubjectRow[]>([]);
    const [weak, setWeak] = useState<{ questions: Question[]; weak_topics: WeakTopicInfo[] } | null>(null);
    const [loading, setLoading] = useState(true);
    const [active, setActive] = useState<ActiveQuiz | null>(null);

    const fetchHome = useCallback(async () => {
        setLoading(true);
        try {
            const [modRes, weakRes] = await Promise.all([
                PrivateModuleAPI.getModule(slug),
                PrivateModuleAPI.getWeakTopics(slug, 10),
            ]);
            setModule({ slug: modRes.data.slug, name: modRes.data.name, description: modRes.data.description });
            setSubjects(modRes.data.subjects || []);
            setWeak({ questions: weakRes.data.questions || [], weak_topics: weakRes.data.weak_topics || [] });
        } catch (err) {
            console.error('[PrivateModule] failed to load', err);
        } finally {
            setLoading(false);
        }
    }, [slug]);

    useEffect(() => { fetchHome(); }, [fetchHome]);

    const startSubjectQuiz = async (subject: string) => {
        try {
            const res = await PrivateModuleAPI.getQuiz(slug, subject, 10);
            const qs: Question[] = res.data?.questions ?? [];
            if (qs.length === 0) {
                alert('No more fresh questions in this subject today — try another one or tomorrow.');
                return;
            }
            setActive({
                title: `${module?.name ?? 'Module'} · ${subject}`,
                questions: qs,
                current: 0,
                answers: {},
                submitted: false,
                scorecard: null,
            });
        } catch (err) {
            alert('Failed to load questions.');
        }
    };

    const startWeakPractice = () => {
        if (!weak || weak.questions.length === 0) return;
        setActive({
            title: `${module?.name ?? 'Module'} · Weak Topics`,
            questions: weak.questions,
            current: 0,
            answers: {},
            submitted: false,
            scorecard: null,
        });
    };

    const selectAnswer = (qid: string, idx: number) => {
        if (!active || active.submitted) return;
        setActive((prev) => prev ? { ...prev, answers: { ...prev.answers, [qid]: idx } } : prev);
    };

    const submitQuiz = async () => {
        if (!active) return;
        const payload = active.questions.map((q) => ({
            question_id: q.id,
            selected_option_index: active.answers[q.id] !== undefined ? active.answers[q.id] : null,
        }));
        try {
            const res = await PrivateModuleAPI.submitQuiz(slug, payload);
            setActive((prev) => prev ? { ...prev, submitted: true, scorecard: res.data } : prev);
        } catch (err) {
            alert('Failed to submit.');
        }
    };

    const exitQuiz = () => {
        setActive(null);
        fetchHome();
    };

    if (loading) {
        return (
            <div className="flex justify-center items-center py-20">
                <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-orange-600"></div>
            </div>
        );
    }

    if (!module) {
        return (
            <div className="max-w-xl mx-auto py-12 text-center text-gray-500 text-sm">
                This private module is not available for your account.
            </div>
        );
    }

    // ─── Quiz session view (ran inside this same component) ───
    if (active) {
        const q = active.questions[active.current];
        const total = active.questions.length;
        const answered = Object.keys(active.answers).length;

        if (active.submitted && active.scorecard) {
            const sc = active.scorecard;
            return (
                <div className="max-w-2xl mx-auto py-8">
                    <div className="bg-gradient-to-br from-gray-900 via-gray-800 to-gray-900 rounded-2xl text-white p-8 text-center mb-6">
                        <h2 className="text-2xl font-bold mb-2">Session Complete</h2>
                        <p className="text-gray-400 text-sm mb-6">{active.title}</p>
                        <div className="grid grid-cols-3 gap-4 mb-6">
                            <div className="bg-white/10 rounded-xl p-4">
                                <p className="text-2xl font-black text-green-400">{sc.correct}</p>
                                <p className="text-xs text-gray-400 mt-1">Correct</p>
                            </div>
                            <div className="bg-white/10 rounded-xl p-4">
                                <p className="text-2xl font-black text-red-400">{sc.wrong}</p>
                                <p className="text-xs text-gray-400 mt-1">Wrong</p>
                            </div>
                            <div className="bg-white/10 rounded-xl p-4">
                                <p className="text-2xl font-black text-gray-300">{sc.total_questions}</p>
                                <p className="text-xs text-gray-400 mt-1">Total</p>
                            </div>
                        </div>
                        <div className="text-4xl font-black">{Math.round(sc.score_pct ?? 0)}%</div>
                    </div>

                    {/* Per-question review */}
                    <div className="space-y-3 mb-6">
                        {active.questions.map((qq, idx) => {
                            const r = sc.results?.[idx];
                            const correctIdx = r?.correct_option_index;
                            const picked = active.answers[qq.id];
                            return (
                                <div key={qq.id} className="bg-white rounded-xl p-4 border border-gray-100">
                                    <div className="text-sm font-medium text-gray-900 mb-2">
                                        {idx + 1}. {qq.question_text}
                                    </div>
                                    <div className="text-xs text-gray-600 space-y-1 mb-2">
                                        {qq.options.map((o, i) => (
                                            <div key={i}
                                                className={`pl-2 border-l-2 ${i === correctIdx ? 'border-green-500 text-green-700' : i === picked ? 'border-red-400 text-red-700' : 'border-transparent'}`}
                                            >
                                                {String.fromCharCode(65 + i)}. {o.option_text}
                                            </div>
                                        ))}
                                    </div>
                                    {r?.explanation && (
                                        <div className="text-[11px] text-gray-500 bg-gray-50 rounded p-2">{renderExplanation(r.explanation)}</div>
                                    )}
                                </div>
                            );
                        })}
                    </div>

                    <button onClick={exitQuiz}
                        className="w-full bg-orange-600 hover:bg-orange-700 text-white font-bold py-3 rounded-xl shadow-lg">
                        ← Back to {moduleHeader(module)}
                    </button>
                </div>
            );
        }

        return (
            <div className="max-w-2xl mx-auto py-8">
                <div className="flex items-center justify-between mb-6">
                    <button onClick={exitQuiz} className="text-gray-500 hover:text-gray-700 flex items-center text-sm">
                        <ArrowLeft className="w-4 h-4 mr-1" /> Exit
                    </button>
                    <span className="text-sm font-bold text-gray-500 truncate max-w-[60%]">{active.title}</span>
                    <span className="text-sm font-medium text-gray-500">{active.current + 1} / {total}</span>
                </div>
                <div className="w-full bg-gray-200 rounded-full h-1.5 mb-6">
                    <div className="bg-orange-500 h-1.5 rounded-full transition-all"
                         style={{ width: `${((active.current + 1) / total) * 100}%` }}></div>
                </div>
                <div className="bg-white rounded-2xl p-6 border border-gray-100 shadow-sm mb-6">
                    <div className="text-[11px] text-orange-600 font-semibold mb-2 uppercase tracking-wide">
                        {q.subject} · {q.topic}
                    </div>
                    <div className="text-base font-medium text-gray-900 leading-relaxed mb-6">
                        {q.question_text}
                    </div>
                    <div className="space-y-3">
                        {q.options.map((opt, i) => {
                            const picked = active.answers[q.id] === i;
                            return (
                                <button key={i} onClick={() => selectAnswer(q.id, i)}
                                    className={`w-full text-left flex items-center p-4 border rounded-xl transition-all ${picked
                                        ? 'bg-orange-50 border-orange-500 shadow-[0_0_0_1px_rgba(249,115,22,1)]'
                                        : 'bg-white border-gray-200 hover:border-orange-200'
                                        }`}>
                                    <div className={`w-5 h-5 rounded-full border flex-shrink-0 flex items-center justify-center mr-3 ${picked ? 'border-orange-600 bg-orange-600' : 'border-gray-300 bg-white'}`}>
                                        {picked && <div className="w-2 h-2 rounded-full bg-white" />}
                                    </div>
                                    <span className="text-sm">{String.fromCharCode(65 + i)}. {opt.option_text}</span>
                                </button>
                            );
                        })}
                    </div>
                </div>
                <div className="flex gap-3">
                    {active.current > 0 && (
                        <button onClick={() => setActive((p) => p ? { ...p, current: p.current - 1 } : p)}
                            className="flex-1 bg-gray-100 hover:bg-gray-200 text-gray-700 font-bold py-3 rounded-xl">
                            ← Previous
                        </button>
                    )}
                    {active.current < total - 1 ? (
                        <button onClick={() => setActive((p) => p ? { ...p, current: p.current + 1 } : p)}
                            className="flex-[2] bg-orange-600 hover:bg-orange-700 text-white font-bold py-3 rounded-xl shadow-lg shadow-orange-200">
                            Next →
                        </button>
                    ) : (
                        <button onClick={submitQuiz}
                            className="flex-[2] bg-green-600 hover:bg-green-700 text-white font-bold py-3 rounded-xl shadow-lg shadow-green-200">
                            Submit ({answered}/{total} answered)
                        </button>
                    )}
                </div>
            </div>
        );
    }

    // ─── Home (subject grid) ───
    return (
        <div className="max-w-6xl mx-auto py-8">
            <div className="mb-6 flex items-start gap-3">
                <div className="w-12 h-12 rounded-xl bg-orange-100 text-orange-600 flex items-center justify-center flex-shrink-0">
                    <Lock className="w-5 h-5" />
                </div>
                <div className="min-w-0">
                    <h1 className="text-2xl sm:text-3xl font-bold text-gray-900">{module.name}</h1>
                    {module.description && (
                        <p className="text-sm text-gray-500 mt-1 max-w-2xl">{module.description}</p>
                    )}
                    <div className="mt-2 inline-flex items-center gap-2 text-[11px] uppercase tracking-wider text-orange-700 bg-orange-50 px-2 py-1 rounded-full">
                        <Sparkles className="w-3 h-3" /> Isolated practice · suggestions stay within this module
                    </div>
                </div>
            </div>

            {/* Weak-topic banner (module-scoped) */}
            {weak && weak.weak_topics.length > 0 && (
                <div className="mb-10">
                    <div className="flex items-center gap-3 mb-4">
                        <span className="bg-orange-100 text-orange-700 text-xs font-bold px-3 py-1 rounded-full uppercase tracking-wider">
                            Recommended
                        </span>
                        <h2 className="text-xl font-bold text-gray-900">Improve your {module.name} weak areas</h2>
                    </div>
                    <div className="bg-gradient-to-br from-orange-50 to-amber-50 border-2 border-orange-200 rounded-2xl p-6">
                        <div className="flex flex-wrap gap-2 mb-6">
                            {weak.weak_topics.map((wt, idx) => (
                                <div key={idx} className="flex items-center gap-2 bg-white px-4 py-2 rounded-full border border-orange-200 text-sm">
                                    <div className={`w-2 h-2 rounded-full ${wt.accuracy < 40 ? 'bg-red-500' : 'bg-orange-400'}`}></div>
                                    <span className="font-medium text-gray-700">{wt.subject}</span>
                                    {wt.topic && <span className="text-gray-400">→ {wt.topic}</span>}
                                    <span className={`font-bold ${wt.accuracy < 40 ? 'text-red-600' : 'text-orange-600'}`}>
                                        {Math.round(wt.accuracy)}%
                                    </span>
                                </div>
                            ))}
                        </div>
                        <div className="flex items-center justify-between">
                            <div className="text-sm text-gray-500">{weak.questions.length} questions ready</div>
                            <button onClick={startWeakPractice}
                                className="bg-orange-600 hover:bg-orange-700 text-white font-bold px-8 py-3 rounded-xl shadow-lg shadow-orange-200">
                                Start practice →
                            </button>
                        </div>
                    </div>
                </div>
            )}

            {/* Subject grid */}
            <h2 className="text-xl font-bold text-gray-900 mb-2">Practice by subject</h2>
            <p className="text-sm text-gray-500 mb-6">
                Each subject within this module is isolated — a mistake here will surface follow-ups
                from {module.name} only, never from the main quiz pool.
            </p>
            <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-4">
                {subjects.map((s) => {
                    const attemptedPct = s.question_count ? Math.round((s.attempted_count / s.question_count) * 100) : 0;
                    return (
                        <button key={s.subject} onClick={() => startSubjectQuiz(s.subject)}
                            className="group bg-white border border-gray-100 hover:border-orange-200 rounded-2xl p-5 text-left transition-all hover:shadow-md">
                            <h3 className="font-bold text-gray-900 mb-1">{s.subject}</h3>
                            <div className="text-xs text-gray-500 mb-3">
                                {s.question_count} questions · {s.attempted_count} attempted
                            </div>
                            <div className="h-1.5 w-full bg-gray-100 rounded-full overflow-hidden">
                                <div className="h-full bg-orange-400 rounded-full"
                                     style={{ width: `${attemptedPct}%` }}></div>
                            </div>
                            <div className="mt-3 flex items-center gap-1 text-orange-600 text-sm font-semibold opacity-0 group-hover:opacity-100 transition-opacity">
                                Start session →
                            </div>
                        </button>
                    );
                })}
            </div>
        </div>
    );
};
