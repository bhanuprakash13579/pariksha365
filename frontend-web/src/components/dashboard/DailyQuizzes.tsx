import { useState, useEffect } from 'react';
import { Lock, ChevronRight } from 'lucide-react';
import { QuizAPI, PrivateModuleAPI } from '../../services/api';
import { PrivateModuleQuizzes } from './PrivateModuleQuizzes';

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

type AccessibleModule = { slug: string; name: string; description?: string };

export const DailyQuizzes = ({ onQuizComplete }: { onQuizComplete?: () => void }) => {
    const [categories, setCategories] = useState<any[]>([]);
    const [streak, setStreak] = useState<any>(null);
    const [weakQuiz, setWeakQuiz] = useState<any>(null);
    const [loading, setLoading] = useState(true);

    // Private modules (e.g. EPFO APFC) the signed-in email has been whitelisted for.
    // Fetched in parallel with the rest; `privateChecked` gates the card render so
    // we don't flash the "Invite-only" heading for users without access.
    const [privateModules, setPrivateModules] = useState<AccessibleModule[]>([]);
    const [privateChecked, setPrivateChecked] = useState(false);
    const [activePrivateSlug, setActivePrivateSlug] = useState<string | null>(null);

    // Quiz session state
    const [activeQuiz, setActiveQuiz] = useState<any>(null); // { subject, questions, current, answers, submitted, scorecard }

    useEffect(() => {
        // Main quiz data — must never block on the private-module fetch.
        const fetchData = async () => {
            try {
                const [catRes, weakRes] = await Promise.all([
                    QuizAPI.getCategories(),
                    QuizAPI.getWeakTopicQuiz(),
                ]);
                setCategories(catRes.data.categories || []);
                setStreak(catRes.data.streak || null);
                setWeakQuiz(weakRes.data || null);
            } catch (err) {
                console.error("Failed to fetch quiz data:", err);
            } finally {
                setLoading(false);
            }
        };
        fetchData();

        // Private modules — fire-and-forget side fetch. If it 404s or the
        // prod backend hasn't redeployed yet, the main page is unaffected.
        PrivateModuleAPI.listMine()
            .then((r) => setPrivateModules(r.data?.modules || []))
            .catch(() => setPrivateModules([]))
            .finally(() => setPrivateChecked(true));
    }, []);

    // Start a daily quiz for a category
    const startCategoryQuiz = async (subject: string) => {
        try {
            const res = await QuizAPI.getDailyQuiz(subject, 10);
            if (res.data.questions && res.data.questions.length > 0) {
                setActiveQuiz({
                    subject: res.data.subject,
                    questions: res.data.questions,
                    current: 0,
                    answers: {},
                    submitted: false,
                    scorecard: null
                });
            } else {
                alert('No questions available for this category yet.');
            }
        } catch (err) {
            console.error("Failed to start quiz:", err);
            alert('Failed to load quiz questions.');
        }
    };

    // Start weak-topic practice quiz
    const startWeakTopicPractice = async () => {
        if (weakQuiz?.questions && weakQuiz.questions.length > 0) {
            setActiveQuiz({
                subject: 'Weak Topics',
                questions: weakQuiz.questions,
                current: 0,
                answers: {},
                submitted: false,
                scorecard: null
            });
        }
    };

    // Select an answer
    const selectAnswer = (questionId: string, optionIndex: number) => {
        if (!activeQuiz || activeQuiz.submitted) return;
        setActiveQuiz((prev: any) => ({
            ...prev,
            answers: { ...prev.answers, [questionId]: optionIndex }
        }));
    };

    // Submit the quiz
    const submitQuiz = async () => {
        if (!activeQuiz) return;
        const answerPayload = activeQuiz.questions.map((q: any) => ({
            question_id: q.id,
            selected_option_index: activeQuiz.answers[q.id] !== undefined ? activeQuiz.answers[q.id] : null
        }));
        try {
            const res = await QuizAPI.submitQuiz(answerPayload);
            setActiveQuiz((prev: any) => ({
                ...prev,
                submitted: true,
                scorecard: res.data
            }));
            // Notify parent to refresh user stats (points/stars)
            onQuizComplete?.();
        } catch (err) {
            console.error("Failed to submit quiz:", err);
            alert('Failed to submit quiz.');
        }
    };

    // Exit quiz session
    const exitQuiz = () => {
        setActiveQuiz(null);
        // Refresh categories to get updated question counts
        QuizAPI.getCategories().then(res => {
            setCategories(res.data.categories || []);
            setStreak(res.data.streak || null);
        });
    };

    // ───── QUIZ SESSION VIEW ─────
    if (activeQuiz) {
        const q = activeQuiz.questions[activeQuiz.current];
        const totalQ = activeQuiz.questions.length;
        const answeredCount = Object.keys(activeQuiz.answers).length;

        if (activeQuiz.submitted && activeQuiz.scorecard) {
            const sc = activeQuiz.scorecard;
            return (
                <div className="max-w-2xl mx-auto py-8">
                    <div className="bg-gradient-to-br from-gray-900 via-gray-800 to-gray-900 rounded-2xl text-white p-8 text-center mb-6">
                        <h2 className="text-2xl font-bold mb-2">Quiz Complete!</h2>
                        <p className="text-gray-400 text-sm mb-6">{activeQuiz.subject}</p>
                        <div className="grid grid-cols-3 gap-4 mb-6">
                            <div className="bg-white/10 backdrop-blur rounded-xl p-4">
                                <p className="text-2xl font-black text-green-400">{sc.correct}</p>
                                <p className="text-xs text-gray-400 mt-1">Correct</p>
                            </div>
                            <div className="bg-white/10 backdrop-blur rounded-xl p-4">
                                <p className="text-2xl font-black text-red-400">{sc.incorrect}</p>
                                <p className="text-xs text-gray-400 mt-1">Wrong</p>
                            </div>
                            <div className="bg-white/10 backdrop-blur rounded-xl p-4">
                                <p className="text-2xl font-black text-gray-400">{sc.skipped}</p>
                                <p className="text-xs text-gray-400 mt-1">Skipped</p>
                            </div>
                        </div>
                        <div className="text-4xl font-black mb-2">
                            {sc.score_percentage != null ? `${Math.round(sc.score_percentage)}%` : `${sc.correct}/${sc.total}`}
                        </div>
                        {sc.points_earned > 0 && (
                            <div className="inline-block bg-yellow-400/20 text-yellow-300 font-bold px-4 py-1.5 rounded-full border border-yellow-400/30 mb-2">
                                +{sc.points_earned} Points Earned!
                            </div>
                        )}
                        {sc.new_star_unlocked && (
                            <div className="mt-2 mb-4 animate-bounce">
                                <span className="text-3xl">🌟</span>
                                <p className="text-yellow-400 font-black text-lg mt-1 tracking-wide uppercase">New Star Unlocked!</p>
                            </div>
                        )}
                        {sc.nudge && <p className="text-sm text-orange-300 mt-4">{sc.nudge}</p>}
                    </div>

                    {/* Weak topics from scorecard */}
                    {sc.weak_topics && sc.weak_topics.length > 0 && (
                        <div className="bg-orange-50 border border-orange-200 rounded-xl p-4 mb-4">
                            <h4 className="font-bold text-gray-900 mb-2">🎯 Focus Areas</h4>
                            <div className="flex flex-wrap gap-2">
                                {sc.weak_topics.map((wt: any, i: number) => (
                                    <span key={i} className="bg-white px-3 py-1 rounded-full text-sm border border-orange-200">
                                        {wt.subject} → {wt.topic} <span className="font-bold text-orange-600">{Math.round(wt.accuracy)}%</span>
                                    </span>
                                ))}
                            </div>
                        </div>
                    )}

                    <button onClick={exitQuiz}
                        className="w-full bg-orange-600 hover:bg-orange-700 text-white font-bold py-3 rounded-xl transition-colors shadow-lg">
                        ← Back to Categories
                    </button>

                    {/* Review Answers */}
                    <div className="mt-6">
                        <h3 className="font-bold text-gray-900 mb-4">📋 Review Answers</h3>
                        {activeQuiz.questions.map((q: any, idx: number) => {
                            const selectedIdx = activeQuiz.answers[q.id];
                            const correctIdx = q.options?.findIndex((o: any) => o.is_correct);
                            return (
                                <div key={q.id} className="bg-white rounded-xl border border-gray-200 p-4 mb-4 shadow-sm">
                                    <p className="text-sm font-medium text-gray-900 mb-3 leading-relaxed">
                                        <span className="text-gray-400 font-bold mr-1">{idx + 1}.</span>
                                        <span dangerouslySetInnerHTML={{ __html: q.question_text.replace(/\*\*(.*?)\*\*/g, '<b>$1</b>').replace(/\n/g, '<br />') }} />
                                    </p>
                                    <div className="space-y-1.5 mb-3">
                                        {q.options?.map((opt: any, i: number) => {
                                            const isCorrect = opt.is_correct;
                                            const isSelected = selectedIdx === i;
                                            const cls = isCorrect
                                                ? 'bg-green-50 border-green-400 text-green-900'
                                                : isSelected
                                                    ? 'bg-red-50 border-red-400 text-red-900'
                                                    : 'bg-gray-50 border-gray-200 text-gray-700';
                                            return (
                                                <div key={i} className={`flex items-center px-3 py-2 border rounded-lg text-sm ${cls}`}>
                                                    <span className="font-bold mr-2">{String.fromCharCode(65 + i)}.</span>
                                                    <span className="flex-1">{opt.option_text}</span>
                                                    {isCorrect && <span className="ml-2 font-bold text-green-600">✓</span>}
                                                    {isSelected && !isCorrect && <span className="ml-2 font-bold text-red-600">✗</span>}
                                                </div>
                                            );
                                        })}
                                    </div>
                                    {q.explanation && (
                                        <div className="bg-blue-50 border border-blue-200 rounded-lg p-3 text-xs text-blue-900">
                                            💡 {renderExplanation(q.explanation)}
                                        </div>
                                    )}
                                    {q.explanation_svg && (
                                        <div className="mt-3 flex justify-center overflow-x-auto"
                                            dangerouslySetInnerHTML={{ __html: q.explanation_svg }} />
                                    )}
                                </div>
                            );
                        })}
                    </div>
                </div>
            );
        }

        // Active question view
        return (
            <div className="max-w-2xl mx-auto py-8">
                <div className="flex items-center justify-between mb-6">
                    <button onClick={exitQuiz} className="text-gray-500 hover:text-gray-700 flex items-center text-sm">
                        <svg className="w-4 h-4 mr-1" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M10 19l-7-7m0 0l7-7m-7 7h18" /></svg>
                        Exit Quiz
                    </button>
                    <span className="text-sm font-bold text-gray-500">{activeQuiz.subject}</span>
                    <span className="text-sm font-medium text-gray-500">{activeQuiz.current + 1} / {totalQ}</span>
                </div>

                {/* Progress bar */}
                <div className="w-full bg-gray-200 rounded-full h-1.5 mb-6">
                    <div className="bg-orange-500 h-1.5 rounded-full transition-all" style={{ width: `${((activeQuiz.current + 1) / totalQ) * 100}%` }}></div>
                </div>

                {/* Question */}
                <div className="bg-white rounded-2xl p-6 border border-gray-100 shadow-sm mb-6">
                    <div className="text-base font-medium text-gray-900 leading-relaxed mb-6 prose prose-sm max-w-none"
                        dangerouslySetInnerHTML={{ __html: q.question_text.replace(/\*\*(.*?)\*\*/g, '<b>$1</b>').replace(/\n/g, '<br />') }} />
                    {q.diagram_svg && (
                        <div className="mb-6 flex justify-center"
                            dangerouslySetInnerHTML={{ __html: q.diagram_svg }} />
                    )}

                    <div className="space-y-3">
                        {q.options?.map((opt: any, i: number) => (
                            <button key={i}
                                onClick={() => selectAnswer(q.id, i)}
                                className={`w-full text-left flex items-center p-4 border rounded-xl transition-all ${activeQuiz.answers[q.id] === i
                                    ? 'bg-orange-50 border-orange-500 shadow-[0_0_0_1px_rgba(249,115,22,1)]'
                                    : 'bg-white border-gray-200 hover:border-orange-200'
                                    }`}>
                                <div className={`w-5 h-5 rounded-full border flex-shrink-0 flex items-center justify-center mr-3 ${activeQuiz.answers[q.id] === i ? 'border-orange-600 bg-orange-600' : 'border-gray-300 bg-white'
                                    }`}>
                                    {activeQuiz.answers[q.id] === i && <div className="w-2 h-2 rounded-full bg-white"></div>}
                                </div>
                                <span className="text-sm">{String.fromCharCode(65 + i)}. {opt.option_text}</span>
                            </button>
                        ))}
                    </div>
                </div>

                {/* Navigation */}
                <div className="flex gap-3">
                    {activeQuiz.current > 0 && (
                        <button onClick={() => setActiveQuiz((p: any) => ({ ...p, current: p.current - 1 }))}
                            className="flex-1 bg-gray-100 hover:bg-gray-200 text-gray-700 font-bold py-3 rounded-xl transition-colors">
                            ← Previous
                        </button>
                    )}
                    {activeQuiz.current < totalQ - 1 ? (
                        <button onClick={() => setActiveQuiz((p: any) => ({ ...p, current: p.current + 1 }))}
                            className="flex-[2] bg-orange-600 hover:bg-orange-700 text-white font-bold py-3 rounded-xl transition-colors shadow-lg shadow-orange-200">
                            Next →
                        </button>
                    ) : (
                        <button onClick={submitQuiz}
                            className="flex-[2] bg-green-600 hover:bg-green-700 text-white font-bold py-3 rounded-xl transition-colors shadow-lg shadow-green-200">
                            Submit Quiz ({answeredCount}/{totalQ} answered)
                        </button>
                    )}
                </div>
            </div>
        );
    }

    // ───── CATEGORY LIST VIEW ─────
    if (loading) {
        return (
            <div className="flex justify-center items-center py-20">
                <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-orange-600"></div>
            </div>
        );
    }

    // If the user picked a private module, swap the whole view for the module's
    // isolated quiz universe (subject grid, weak-topic banner, session flow).
    if (activePrivateSlug) {
        return (
            <div>
                <div className="max-w-6xl mx-auto pt-4 px-4 sm:px-0">
                    <button
                        onClick={() => { setActivePrivateSlug(null); onQuizComplete?.(); }}
                        className="text-sm text-gray-500 hover:text-gray-700"
                    >
                        ← Back to Daily Quizzes
                    </button>
                </div>
                <PrivateModuleQuizzes slug={activePrivateSlug} />
            </div>
        );
    }

    return (
        <div className="max-w-6xl mx-auto py-8">
            {/* Private Modules (invite-only banks — e.g. EPFO APFC) */}
            {privateChecked && privateModules.length > 0 && (
                <div className="mb-8">
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
                                onClick={() => setActivePrivateSlug(m.slug)}
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

            {/* Streak Banner */}
            {streak && (
                <div className={`mb-8 rounded-2xl p-6 flex items-center justify-between ${streak.at_risk
                    ? 'bg-gradient-to-r from-red-500 to-orange-500 text-white'
                    : streak.current_streak > 0
                        ? 'bg-gradient-to-r from-orange-500 to-amber-400 text-white'
                        : 'bg-gradient-to-r from-gray-100 to-gray-200 text-gray-700'
                    }`}>
                    <div className="flex items-center gap-4">
                        <div className="text-4xl">🔥</div>
                        <div>
                            <h3 className="text-xl font-bold">{streak.nudge}</h3>
                            <div className="flex gap-6 mt-2 text-sm opacity-90">
                                <span>Current: <strong>{streak.current_streak} days</strong></span>
                                <span>Longest: <strong>{streak.longest_streak} days</strong></span>
                            </div>
                        </div>
                    </div>
                    {streak.current_streak > 0 && (
                        <div className="text-5xl font-black opacity-30">{streak.current_streak}</div>
                    )}
                </div>
            )}

            {/* Recommended Weak Topics Quiz */}
            {weakQuiz && weakQuiz.weak_topics && weakQuiz.weak_topics.length > 0 && (
                <div className="mb-10">
                    <div className="flex items-center gap-3 mb-4">
                        <span className="bg-orange-100 text-orange-700 text-xs font-bold px-3 py-1 rounded-full uppercase tracking-wider">Recommended</span>
                        <h2 className="text-2xl font-bold text-gray-900">Improve Your Weak Areas</h2>
                    </div>
                    <div className="bg-gradient-to-br from-orange-50 to-amber-50 border-2 border-orange-200 rounded-2xl p-6 shadow-sm">
                        <div className="flex items-start gap-4 mb-6">
                            <div className="w-14 h-14 rounded-2xl bg-orange-100 flex items-center justify-center flex-shrink-0">
                                <span className="text-2xl">🎯</span>
                            </div>
                            <div>
                                <h3 className="text-lg font-bold text-gray-900">Personalized Weakness Quiz</h3>
                                <p className="text-sm text-gray-600 mt-1">{weakQuiz.message}</p>
                            </div>
                        </div>

                        {/* Weak topic pills */}
                        <div className="flex flex-wrap gap-2 mb-6">
                            {weakQuiz.weak_topics.map((wt: any, idx: number) => (
                                <div key={idx} className="flex items-center gap-2 bg-white px-4 py-2 rounded-full border border-orange-200 text-sm">
                                    <div className={`w-2 h-2 rounded-full ${wt.accuracy < 40 ? 'bg-red-500' : 'bg-orange-400'}`}></div>
                                    <span className="font-medium text-gray-700">{wt.subject}</span>
                                    {wt.topic && wt.topic !== 'General' && (
                                        <span className="text-gray-400">→ {wt.topic}</span>
                                    )}
                                    <span className={`font-bold ${wt.accuracy < 40 ? 'text-red-600' : 'text-orange-600'}`}>
                                        {wt.accuracy}%
                                    </span>
                                </div>
                            ))}
                        </div>

                        <div className="flex items-center justify-between">
                            <div className="text-sm text-gray-500">
                                {weakQuiz.questions?.length || 0} questions ready • {weakQuiz.total_available || 0} total in pool
                            </div>
                            <button onClick={startWeakTopicPractice}
                                className="bg-orange-600 hover:bg-orange-700 text-white font-bold px-8 py-3 rounded-xl transition-all transform hover:scale-105 shadow-lg shadow-orange-200">
                                Start Practice →
                            </button>
                        </div>
                    </div>
                </div>
            )}

            {/* Quiz Categories Grid */}
            <h2 className="text-2xl font-bold text-gray-900 mb-6">Daily Quiz Categories</h2>
            <p className="text-gray-500 mb-6 -mt-4">Choose a subject to practice. 10 random questions daily!</p>

            <div className="grid grid-cols-2 md:grid-cols-3 lg:grid-cols-4 gap-4">
                {categories.map((cat: any, idx: number) => (
                    <button
                        key={idx}
                        onClick={() => cat.has_questions && startCategoryQuiz(cat.key)}
                        className={`group relative overflow-hidden rounded-2xl p-6 text-left transition-all duration-300 hover:scale-[1.03] hover:shadow-xl border ${cat.has_questions
                            ? 'bg-white border-gray-100 hover:border-orange-200 cursor-pointer'
                            : 'bg-gray-50 border-gray-100 opacity-60 cursor-not-allowed'
                            }`}
                        disabled={!cat.has_questions}
                    >
                        <div className="absolute top-0 right-0 w-24 h-24 rounded-full opacity-10 -mr-6 -mt-6 transition-transform group-hover:scale-150"
                            style={{ backgroundColor: cat.color }}></div>

                        <div className="w-12 h-12 rounded-xl flex items-center justify-center mb-4 transition-colors"
                            style={{ backgroundColor: cat.color + '20' }}>
                            <span className="text-2xl" style={{ color: cat.color }}>
                                {_getCategoryEmoji(cat.key)}
                            </span>
                        </div>

                        <h3 className="text-lg font-bold text-gray-900 mb-1">{cat.name}</h3>
                        <p className="text-sm text-gray-500">
                            {cat.question_count > 0 ? `${cat.question_count} questions` : 'Coming soon'}
                        </p>

                        {cat.has_questions && (
                            <div className="mt-4 flex items-center gap-2 text-orange-600 text-sm font-semibold opacity-0 group-hover:opacity-100 transition-opacity">
                                <span>Start Quiz</span>
                                <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 5l7 7-7 7" />
                                </svg>
                            </div>
                        )}
                    </button>
                ))}
            </div>

            {/* Practice-mode CTA when no weak topics yet — still clickable, no mock required */}
            {(!weakQuiz || !weakQuiz.weak_topics || weakQuiz.weak_topics.length === 0) &&
             weakQuiz?.questions && weakQuiz.questions.length > 0 && (
                <div className="mt-10 bg-gradient-to-r from-indigo-50 to-purple-50 rounded-2xl p-6 border border-indigo-100">
                    <div className="flex items-start gap-4 mb-4">
                        <div className="w-14 h-14 rounded-2xl bg-indigo-100 flex items-center justify-center flex-shrink-0">
                            <span className="text-2xl">🚀</span>
                        </div>
                        <div>
                            <h3 className="text-lg font-bold text-gray-900">Quick Practice</h3>
                            <p className="text-sm text-gray-600 mt-1">
                                {weakQuiz.message || "Start practising — we'll auto-learn your weak topics as you go."}
                            </p>
                        </div>
                    </div>
                    <div className="flex items-center justify-between">
                        <div className="text-sm text-gray-500">
                            {weakQuiz.questions.length} questions ready
                        </div>
                        <button onClick={startWeakTopicPractice}
                            className="bg-indigo-600 hover:bg-indigo-700 text-white font-bold px-8 py-3 rounded-xl transition-all transform hover:scale-105 shadow-lg shadow-indigo-200">
                            Start Practice →
                        </button>
                    </div>
                </div>
            )}
        </div>
    );
};

function _getCategoryEmoji(key: string): string {
    const map: Record<string, string> = {
        polity: '⚖️',
        history: '🏛️',
        geography: '🌍',
        economics: '📈',
        general_science: '🔬',
        reasoning: '🧠',
        quantitative_aptitude: '📐',
        english: '📖',
        computer_knowledge: '💻',
        current_affairs: '📰',
        general_knowledge: '🎓',
    };
    return map[key] || '📚';
}
