import { useState, useEffect, useCallback, useRef } from 'react';
import { Plus, Trash2, Edit, Search, ChevronLeft, ChevronRight, Save, X, AlertCircle, CheckCircle, Upload, BookOpen, ChevronDown, ChevronUp, Code, ArrowUp, ArrowDown, AlertTriangle } from 'lucide-react';
import { QuizAPI } from '../../services/api';
import { SmartTopicSelector } from '../common/SmartTopicSelector';

const OPTION_LABELS = ['A', 'B', 'C', 'D', 'E', 'F'];

export const AdminQuizPoolManager = () => {
    const [subTab, setSubTab] = useState<'questions' | 'bulk' | 'taxonomy'>('questions');
    const [toast, setToast] = useState<{ type: 'success' | 'error' | 'warning'; message: string } | null>(null);
    const [topicCodes, setTopicCodes] = useState<any[]>([]);
    const [validCodesSet, setValidCodesSet] = useState<Set<string>>(new Set());

    useEffect(() => { if (toast) { const t = setTimeout(() => setToast(null), 4000); return () => clearTimeout(t); } }, [toast]);

    const fetchTopicCodes = useCallback(() => {
        QuizAPI.adminGetTopicCodes().then(r => {
            const codes = r.data || [];
            setTopicCodes(codes);
            setValidCodesSet(new Set(codes.map((c: any) => c.code)));
        }).catch(() => { });
    }, []);

    useEffect(() => {
        fetchTopicCodes();
    }, [fetchTopicCodes]);

    return (
        <div className="relative">
            {toast && (
                <div className={`fixed top-4 right-4 z-50 flex items-center gap-2 px-4 py-3 rounded-lg shadow-lg text-sm font-medium
                    ${toast.type === 'success' ? 'bg-green-600 text-white' : toast.type === 'warning' ? 'bg-amber-500 text-white' : 'bg-red-600 text-white'}`}>
                    {toast.type === 'success' ? <CheckCircle className="w-4 h-4" /> : <AlertCircle className="w-4 h-4" />}
                    {toast.message}
                </div>
            )}

            <div className="flex gap-1 mb-6 bg-gray-100 dark:bg-gray-800 rounded-xl p-1 w-fit">
                {([
                    { key: 'questions', label: 'Questions', icon: Search },
                    { key: 'bulk', label: 'Bulk Upload', icon: Upload },
                    { key: 'taxonomy', label: 'Taxonomy', icon: BookOpen },
                ] as const).map(tab => (
                    <button key={tab.key} onClick={() => setSubTab(tab.key)}
                        className={`flex items-center gap-2 px-4 py-2 rounded-lg text-sm font-medium transition-colors ${subTab === tab.key ? 'bg-white dark:bg-gray-700 text-orange-600 shadow-sm' : 'text-gray-500 hover:text-gray-700'
                            }`}>
                        <tab.icon className="w-4 h-4" /> {tab.label}
                    </button>
                ))}
            </div>

            <div className={subTab === 'questions' ? 'block' : 'hidden'}>
                <QuestionsTab setToast={setToast} topicCodes={topicCodes} validCodesSet={validCodesSet} />
            </div>
            <div className={subTab === 'bulk' ? 'block' : 'hidden'}>
                <BulkUploadTab setToast={setToast} topicCodes={topicCodes} validCodesSet={validCodesSet} />
            </div>
            <div className={subTab === 'taxonomy' ? 'block' : 'hidden'}>
                <TaxonomyTab setToast={setToast} onTaxonomyChange={fetchTopicCodes} />
            </div>
        </div>
    );
};


// ─── QUESTIONS TAB ───

const QuestionsTab = ({ setToast, topicCodes, validCodesSet }: { setToast: any; topicCodes: any[]; validCodesSet: Set<string> }) => {
    const [questions, setQuestions] = useState<any[]>([]);
    const [total, setTotal] = useState(0);
    const [page, setPage] = useState(1);
    const [totalPages, setTotalPages] = useState(1);
    const [loading, setLoading] = useState(true);
    const [filters, setFilters] = useState({ subject: '', topic: '', search: '' });
    const [availableSubjects, setAvailableSubjects] = useState<string[]>([]);
    const [availableTopics, setAvailableTopics] = useState<string[]>([]);
    const [showEditor, setShowEditor] = useState(false);
    const [editingQuestion, setEditingQuestion] = useState<any>(null);
    const [form, setForm] = useState(_emptyForm());
    const [saving, setSaving] = useState(false);

    const fetchQuestions = useCallback(async () => {
        setLoading(true);
        try {
            const params: any = { page, per_page: 20 };
            if (filters.subject) params.subject = filters.subject;
            if (filters.topic) params.topic = filters.topic;
            if (filters.search) params.search = filters.search;
            const res = await QuizAPI.adminListQuestions(params);
            setQuestions(res.data.questions || []);
            setTotal(res.data.total || 0);
            setTotalPages(res.data.total_pages || 1);
            setAvailableSubjects(res.data.filters?.subjects || []);
            setAvailableTopics(res.data.filters?.topics || []);
        } catch { console.error('Failed to fetch'); }
        finally { setLoading(false); }
    }, [page, filters]);

    useEffect(() => { fetchQuestions(); }, [fetchQuestions]);

    const openNew = () => { setEditingQuestion(null); setForm(_emptyForm()); setShowEditor(true); };
    const openEdit = (q: any) => {
        setEditingQuestion(q);
        setForm({
            question_text: q.question_text || '', subject: q.subject || '', topic: q.topic || '',
            topic_code: q.topic_code || '', explanation: q.explanation || '', difficulty: q.difficulty || 'MEDIUM',
            image_url: q.image_url || '',
            options: (q.options || []).map((o: any) => ({ option_text: o.option_text || '', is_correct: !!o.is_correct }))
        });
        setShowEditor(true);
    };

    const handleSave = async () => {
        if (!form.question_text.trim() || !form.subject.trim()) { setToast({ type: 'error', message: 'Question text and subject are required.' }); return; }
        if (!form.options.some((o: any) => o.is_correct)) { setToast({ type: 'error', message: 'Mark at least one correct option.' }); return; }
        setSaving(true);
        try {
            if (editingQuestion) { await QuizAPI.adminUpdateQuestion(editingQuestion.id, form); setToast({ type: 'success', message: 'Updated!' }); }
            else { await QuizAPI.adminCreateQuestion(form); setToast({ type: 'success', message: 'Created!' }); }
            setShowEditor(false); fetchQuestions();
        } catch { setToast({ type: 'error', message: 'Failed to save.' }); }
        finally { setSaving(false); }
    };

    const handleDelete = async (id: string) => {
        if (!confirm('Delete this question permanently?')) return;
        try { await QuizAPI.adminDeleteQuestion(id); setToast({ type: 'success', message: 'Deleted.' }); fetchQuestions(); }
        catch { setToast({ type: 'error', message: 'Failed.' }); }
    };

    return (
        <>
            <div className="flex items-center justify-between mb-6">
                <div><h1 className="text-2xl font-bold text-gray-900 dark:text-white">Quiz Pool</h1><p className="text-sm text-gray-500 mt-1">{total} questions</p></div>
                <button onClick={openNew} className="flex items-center gap-2 bg-orange-600 hover:bg-orange-700 text-white font-bold px-4 py-2.5 rounded-lg"><Plus className="w-4 h-4" /> Add Question</button>
            </div>

            <div className="flex gap-3 mb-6 flex-wrap">
                <div className="relative flex-1 min-w-[200px]">
                    <Search className="absolute left-3 top-1/2 -translate-y-1/2 w-4 h-4 text-gray-400" />
                    <input type="text" placeholder="Search questions..." value={filters.search}
                        onChange={e => { setFilters(prev => ({ ...prev, search: e.target.value })); setPage(1); }}
                        className="w-full pl-10 pr-4 py-2.5 border border-gray-200 rounded-lg text-sm focus:ring-2 focus:ring-orange-500 dark:bg-gray-800 dark:border-gray-700 dark:text-white" />
                </div>
                <select value={filters.subject} onChange={e => { setFilters(prev => ({ ...prev, subject: e.target.value })); setPage(1); }}
                    className="px-4 py-2.5 border border-gray-200 rounded-lg text-sm bg-white dark:bg-gray-800 dark:border-gray-700 dark:text-white">
                    <option value="">All Subjects</option>
                    {availableSubjects.map(s => <option key={s} value={s}>{s}</option>)}
                </select>
                <select value={filters.topic} onChange={e => { setFilters(prev => ({ ...prev, topic: e.target.value })); setPage(1); }}
                    className="px-4 py-2.5 border border-gray-200 rounded-lg text-sm bg-white dark:bg-gray-800 dark:border-gray-700 dark:text-white">
                    <option value="">All Topics</option>
                    {availableTopics.map(t => <option key={t} value={t}>{t}</option>)}
                </select>
            </div>

            {loading ? <div className="text-center py-10 text-gray-400">Loading...</div> :
                questions.length === 0 ? <div className="text-center py-16 bg-white dark:bg-gray-800 rounded-2xl border"><p className="text-gray-400">No questions found.</p></div> :
                    <div className="space-y-3">
                        {questions.map(q => (
                            <div key={q.id} className="bg-white dark:bg-gray-800 rounded-xl border border-gray-100 dark:border-gray-700 p-4 hover:shadow-md transition-shadow">
                                <div className="flex items-start justify-between gap-4">
                                    <div className="flex-1 min-w-0">
                                        <p className="text-sm font-medium text-gray-900 dark:text-white mb-1 line-clamp-2">{q.question_text}</p>
                                        <div className="flex gap-2 flex-wrap mt-2">
                                            <span className="px-2 py-0.5 bg-blue-100 text-blue-700 rounded text-xs font-semibold">{q.subject}</span>
                                            {q.topic && <span className="px-2 py-0.5 bg-purple-100 text-purple-700 rounded text-xs font-semibold">{q.topic}</span>}
                                            {q.topic_code && <span className="px-2 py-0.5 bg-gray-100 text-gray-600 dark:bg-gray-700 dark:text-gray-300 rounded text-xs font-mono font-bold">{q.topic_code}</span>}
                                            <span className={`px-2 py-0.5 rounded text-xs font-semibold ${q.difficulty === 'EASY' ? 'bg-green-100 text-green-700' : q.difficulty === 'HARD' ? 'bg-red-100 text-red-700' : 'bg-orange-100 text-orange-700'}`}>{q.difficulty}</span>
                                        </div>
                                    </div>
                                    <div className="flex gap-1">
                                        <button onClick={() => openEdit(q)} className="p-2 hover:bg-gray-100 dark:hover:bg-gray-700 rounded-lg"><Edit className="w-4 h-4 text-gray-500" /></button>
                                        <button onClick={() => handleDelete(q.id)} className="p-2 hover:bg-red-50 rounded-lg"><Trash2 className="w-4 h-4 text-red-500" /></button>
                                    </div>
                                </div>
                            </div>
                        ))}
                    </div>}

            {totalPages > 1 && (
                <div className="flex items-center justify-center gap-3 mt-6">
                    <button disabled={page <= 1} onClick={() => setPage(p => p - 1)} className="px-3 py-2 border rounded-lg text-sm disabled:opacity-40 hover:bg-gray-50"><ChevronLeft className="w-4 h-4" /></button>
                    <span className="text-sm text-gray-500">Page {page} of {totalPages}</span>
                    <button disabled={page >= totalPages} onClick={() => setPage(p => p + 1)} className="px-3 py-2 border rounded-lg text-sm disabled:opacity-40 hover:bg-gray-50"><ChevronRight className="w-4 h-4" /></button>
                </div>
            )}

            {showEditor && <QuestionEditor form={form} setForm={setForm} editing={!!editingQuestion} saving={saving}
                onSave={handleSave} onClose={() => setShowEditor(false)} subjects={availableSubjects} topics={availableTopics} topicCodes={topicCodes} validCodesSet={validCodesSet} />}
        </>
    );
};


// ─── BULK UPLOAD TAB (with validation + arrow navigation) ───

const BulkUploadTab = ({ setToast, topicCodes, validCodesSet }: { setToast: any; topicCodes: any[]; validCodesSet: Set<string> }) => {
    const [jsonText, setJsonText] = useState('');
    const [parsed, setParsed] = useState<any[] | null>(null);
    const [parseError, setParseError] = useState('');
    const [uploading, setUploading] = useState(false);
    const [result, setResult] = useState<any>(null);
    const [invalidIndices, setInvalidIndices] = useState<number[]>([]);
    const [currentInvalidIdx, setCurrentInvalidIdx] = useState(0);

    // Track indices that need images (valid or invalid)
    const [imageIndices, setImageIndices] = useState<number[]>([]);
    const [currentImageIdx, setCurrentImageIdx] = useState(0);

    const itemRefs = useRef<Record<number, HTMLDivElement | null>>({});

    // Full UI Editor State
    const [bulkEditingIdx, setBulkEditingIdx] = useState<number | null>(null);
    const [bulkEditForm, setBulkEditForm] = useState<any>(_emptyForm());

    const openBulkEditor = (idx: number) => {
        setBulkEditingIdx(idx);
        const qObj = { ...parsed![idx] };
        setBulkEditForm({
            question_text: qObj.question_text || '', subject: qObj.subject || '', topic: qObj.topic || '',
            topic_code: qObj.topic_code || '', explanation: qObj.explanation || '', difficulty: qObj.difficulty || 'MEDIUM',
            image_url: qObj.image_url || '',
            options: (qObj.options || []).map((o: any) => ({ option_text: o.option_text || '', is_correct: !!o.is_correct }))
        });
    };

    const handleSaveBulkEdit = () => {
        if (bulkEditingIdx === null || !parsed) return;

        const qForms = bulkEditForm;
        const isStructInvalid = !qForms.question_text || !qForms.options || Object.keys(qForms.options).length < 2 || !qForms.options.some((o: any) => o.is_correct);

        const updatedQuestion = {
            ...parsed[bulkEditingIdx],
            ...qForms,
            _structInvalid: isStructInvalid,
            _hasImage: !!qForms.image_url && qForms.image_url !== 'null'
        };

        const updatedParsed = [...parsed];
        updatedParsed[bulkEditingIdx] = updatedQuestion;
        setParsed(updatedParsed);

        const newInvalids: number[] = [];
        const newImages: number[] = [];

        updatedParsed.forEach((q, i) => {
            if (q._structInvalid || !q.topic_code || !validCodesSet.has(q.topic_code)) {
                newInvalids.push(i);
            }
            if (q._hasImage) {
                newImages.push(i);
            }
        });

        setInvalidIndices(newInvalids);
        setImageIndices(newImages);
        setBulkEditingIdx(null);

        if (newInvalids.length === 0) {
            setToast({ type: 'success', message: 'All errors fixed! Ready to upload.' });
        }
    };

    const processJson = (textToParse: string) => {
        try {
            // Strip markdown code block wrappers if present
            let cleanText = textToParse.trim();
            if (cleanText.startsWith('```')) {
                const firstNewline = cleanText.indexOf('\n');
                if (firstNewline !== -1) cleanText = cleanText.slice(firstNewline + 1);
                if (cleanText.endsWith('```')) cleanText = cleanText.slice(0, -3);
            }

            const rawData = JSON.parse(cleanText);
            if (!Array.isArray(rawData)) { setParseError('JSON must be an array.'); setParsed(null); return; }
            if (rawData.length === 0) { setParseError('Array is empty.'); setParsed(null); return; }

            let data: any[] = [];
            if (rawData[0] && Array.isArray(rawData[0].questions)) {
                rawData.forEach((section: any) => {
                    if (Array.isArray(section.questions)) {
                        data = [...data, ...section.questions];
                    }
                });
            } else {
                data = rawData;
            }

            if (data.length === 0) { setParseError('No questions found in array.'); setParsed(null); return; }
            setParseError('');

            const invalids: number[] = [];
            const withImages: number[] = [];

            data.forEach((q, i) => {
                const isStructInvalid = !q.question_text || !q.options || Object.keys(q.options).length < 2;
                q._structInvalid = isStructInvalid;
                q._hasImage = !!q.image_url && q.image_url !== 'null';

                if (isStructInvalid || !q.topic_code || !validCodesSet.has(q.topic_code)) {
                    invalids.push(i);
                }
                if (q._hasImage) {
                    withImages.push(i);
                }
            });
            setInvalidIndices(invalids);
            setImageIndices(withImages);
            setCurrentInvalidIdx(0);
            setCurrentImageIdx(0);
            setParsed(data);

            if (invalids.length > 0) {
                setToast({ type: 'warning', message: `${invalids.length} question(s) have errors. Fix them before uploading.` });
            }
        } catch (e: any) { setParseError(`Invalid JSON: ${e.message}`); setParsed(null); }
    };

    const handleParse = () => processJson(jsonText);

    const handleUpload = async () => {
        if (!parsed) return;
        if (invalidIndices.length > 0) {
            setToast({ type: 'error', message: `Fix ${invalidIndices.length} invalid question(s) before uploading.` });
            return;
        }
        setUploading(true);
        try {
            const res = await QuizAPI.adminBulkUpload(parsed);
            setResult(res.data);
            setToast({ type: 'success', message: `${res.data.created} questions uploaded!` });
            setParsed(null); setJsonText(''); setInvalidIndices([]);
        } catch { setToast({ type: 'error', message: 'Upload failed.' }); }
        finally { setUploading(false); }
    };

    const handleFileUpload = (e: React.ChangeEvent<HTMLInputElement>) => {
        const file = e.target.files?.[0];
        if (!file) return;
        const reader = new FileReader();
        reader.onload = (ev) => {
            const text = ev.target?.result as string;
            setJsonText(text);
            processJson(text); // Auto-parse immediately after file upload
        };
        reader.readAsText(file);
    };

    const fixQuestionCode = (questionIdx: number, newCode: string) => {
        if (!parsed) return;
        const updated = [...parsed];
        updated[questionIdx] = { ...updated[questionIdx], topic_code: newCode };

        // Also auto-fill subject and topic from the code
        const match = topicCodes.find((tc: any) => tc.code === newCode);
        if (match) {
            updated[questionIdx].subject = match.subject;
            updated[questionIdx].topic = match.topic;
        }

        setParsed(updated);

        // Recalculate invalids
        const newInvalids = updated.map((q, i) => (q._structInvalid || !q.topic_code || !validCodesSet.has(q.topic_code)) ? i : -1).filter(i => i >= 0);
        setInvalidIndices(newInvalids);
        if (newInvalids.length === 0) {
            setToast({ type: 'success', message: 'All errors fixed! Ready to upload.' });
        }
    };

    const navigateInvalid = (direction: 'next' | 'prev') => {
        if (invalidIndices.length === 0) return;
        let newIdx = currentInvalidIdx;
        if (direction === 'next') {
            newIdx = (currentInvalidIdx + 1) % invalidIndices.length;
        } else {
            newIdx = (currentInvalidIdx - 1 + invalidIndices.length) % invalidIndices.length;
        }
        setCurrentInvalidIdx(newIdx);
        const targetQuestionIdx = invalidIndices[newIdx];
        itemRefs.current[targetQuestionIdx]?.scrollIntoView({ behavior: 'smooth', block: 'center' });
    };

    const navigateImages = (direction: 'next' | 'prev') => {
        if (imageIndices.length === 0) return;
        let newIdx = currentImageIdx;
        if (direction === 'next') {
            newIdx = (currentImageIdx + 1) % imageIndices.length;
        } else {
            newIdx = (currentImageIdx - 1 + imageIndices.length) % imageIndices.length;
        }
        setCurrentImageIdx(newIdx);
        const targetQuestionIdx = imageIndices[newIdx];
        itemRefs.current[targetQuestionIdx]?.scrollIntoView({ behavior: 'smooth', block: 'center' });
    };

    const SAMPLE = `[
  {
    "question_text": "Which article deals with Fundamental Duties?",
    "subject": "Polity",
    "topic": "Fundamental Duties",
    "topic_code": "POL_FD",
    "difficulty": "MEDIUM",
    "explanation": "Article 51A lists 11 Fundamental Duties.",
    "options": [
      {"option_text": "Article 51A", "is_correct": true},
      {"option_text": "Article 19", "is_correct": false},
      {"option_text": "Article 21", "is_correct": false},
      {"option_text": "Article 32", "is_correct": false}
    ]
  }
]`;

    return (
        <div className="max-w-4xl">
            <h1 className="text-2xl font-bold text-gray-900 dark:text-white mb-2">Bulk Upload</h1>
            <p className="text-sm text-gray-500 mb-1">Paste JSON or upload .json file. Each question <strong>must have a valid <code className="bg-gray-100 px-1 rounded">topic_code</code></strong>.</p>
            <p className="text-xs text-orange-600 mb-6">Invalid codes are highlighted in red. Use ↑↓ arrows to navigate to flagged questions and fix them.</p>

            <div className="flex items-center gap-4 mb-4">
                <label className="flex items-center gap-2 px-4 py-2.5 bg-gray-100 hover:bg-gray-200 rounded-lg cursor-pointer text-sm font-medium text-gray-700">
                    <Upload className="w-4 h-4" /> Upload .json file
                    <input type="file" accept=".json" onChange={handleFileUpload} className="hidden" />
                </label>
                <button onClick={() => setJsonText(SAMPLE)} className="text-sm text-orange-600 hover:text-orange-700 font-medium">Paste sample</button>
            </div>

            {!parsed ? (
                <>
                    <textarea rows={12} value={jsonText} onChange={e => setJsonText(e.target.value)}
                        className="w-full px-4 py-3 border border-gray-200 rounded-xl text-sm font-mono resize-y focus:ring-2 focus:ring-orange-500 dark:bg-gray-900 dark:border-gray-700 dark:text-white"
                        placeholder="Paste JSON array here..." />

                    {parseError && <p className="text-sm mt-2 flex items-center gap-1 text-red-500"><AlertCircle className="w-4 h-4" /> {parseError}</p>}

                    <div className="flex gap-3 mt-4">
                        <button onClick={handleParse} disabled={!jsonText.trim()}
                            className="px-5 py-2.5 bg-gray-800 hover:bg-gray-900 text-white rounded-lg text-sm font-bold disabled:opacity-40">Preview & Validate</button>
                    </div>
                </>
            ) : (
                <div className="flex gap-3 mt-2 mb-4">
                    <button onClick={() => { setParsed(null); setInvalidIndices([]); setJsonText(''); setResult(null); }}
                        className="px-4 py-2 border hover:bg-gray-50 dark:hover:bg-gray-800 text-gray-700 dark:text-gray-300 rounded-lg text-sm font-bold">Clear & Start Over</button>
                    {parsed && invalidIndices.length === 0 && (
                        <button onClick={handleUpload} disabled={uploading}
                            className="flex items-center gap-2 px-5 py-2.5 bg-green-600 hover:bg-green-700 text-white rounded-lg text-sm font-bold disabled:opacity-50">
                            <Upload className="w-4 h-4" /> {uploading ? 'Uploading...' : `Upload ${parsed.length} Questions`}
                        </button>
                    )}
                </div>
            )}

            {/* ─── Validation Navigator Bar ─── */}
            {parsed && invalidIndices.length > 0 && (
                <div className="mt-4 flex items-center gap-3 bg-red-50 dark:bg-red-900/20 border border-red-200 dark:border-red-800 rounded-xl px-4 py-3">
                    <AlertTriangle className="w-5 h-5 text-red-500 flex-shrink-0" />
                    <span className="text-sm font-semibold text-red-700 dark:text-red-400 flex-1">
                        {invalidIndices.length} question{invalidIndices.length > 1 ? 's' : ''} have errors
                        {invalidIndices.length > 0 && ` — viewing ${currentInvalidIdx + 1} of ${invalidIndices.length}`}
                    </span>
                    <div className="flex items-center gap-1">
                        <button onClick={() => navigateInvalid('prev')} title="Previous invalid"
                            className="p-2 bg-red-100 hover:bg-red-200 rounded-lg transition-colors">
                            <ArrowUp className="w-4 h-4 text-red-600" />
                        </button>
                        <button onClick={() => navigateInvalid('next')} title="Next invalid"
                            className="p-2 bg-red-100 hover:bg-red-200 rounded-lg transition-colors">
                            <ArrowDown className="w-4 h-4 text-red-600" />
                        </button>
                    </div>
                    <button onClick={handleUpload} disabled className="px-3 py-1.5 bg-gray-300 text-gray-500 rounded-lg text-xs font-bold cursor-not-allowed">
                        Fix all to upload
                    </button>
                </div>
            )}

            {parsed && invalidIndices.length === 0 && (
                <div className="mt-4 flex items-center gap-2 bg-green-50 dark:bg-green-900/20 border border-green-200 rounded-xl px-4 py-3">
                    <CheckCircle className="w-5 h-5 text-green-500" />
                    <span className="text-sm font-semibold text-green-700">All {parsed.length} questions are valid ✓</span>
                </div>
            )}

            {/* ─── Image Navigator Bar ─── */}
            {parsed && imageIndices.length > 0 && (
                <div className="mt-3 flex items-center gap-3 bg-blue-50 dark:bg-blue-900/20 border border-blue-200 dark:border-blue-800 rounded-xl px-4 py-3">
                    <span className="text-xl flex-shrink-0">🖼️</span>
                    <span className="text-sm font-semibold text-blue-700 dark:text-blue-400 flex-1">
                        {imageIndices.length} question{imageIndices.length > 1 ? 's' : ''} have images
                        {imageIndices.length > 0 && ` — viewing ${currentImageIdx + 1} of ${imageIndices.length}`}
                    </span>
                    <div className="flex items-center gap-1">
                        <button onClick={() => navigateImages('prev')} title="Previous image"
                            className="p-2 bg-blue-100 hover:bg-blue-200 rounded-lg transition-colors">
                            <ArrowUp className="w-4 h-4 text-blue-600" />
                        </button>
                        <button onClick={() => navigateImages('next')} title="Next image"
                            className="p-2 bg-blue-100 hover:bg-blue-200 rounded-lg transition-colors">
                            <ArrowDown className="w-4 h-4 text-blue-600" />
                        </button>
                    </div>
                </div>
            )}

            {/* ─── Preview with inline fix ─── */}
            {parsed && (
                <div className="mt-6 bg-white dark:bg-gray-800 rounded-xl border p-4">
                    <h3 className="text-sm font-bold text-gray-700 dark:text-gray-300 mb-3">
                        Preview ({parsed.length} questions • <span className="text-green-600">{parsed.length - invalidIndices.length} valid</span>
                        {invalidIndices.length > 0 && <> • <span className="text-red-500">{invalidIndices.length} need fixing</span></>}
                        {imageIndices.length > 0 && <> • <span className="text-blue-600">{imageIndices.length} need images</span></>})
                    </h3>
                    <div className="max-h-[500px] overflow-y-auto space-y-1">
                        {parsed.map((q, i) => {
                            const isInvalid = invalidIndices.includes(i);
                            const hasImage = imageIndices.includes(i);
                            const isCurrentNav = (isInvalid && invalidIndices[currentInvalidIdx] === i) || (hasImage && imageIndices[currentImageIdx] === i && invalidIndices.length === 0);
                            return (
                                <div key={i}
                                    ref={el => { itemRefs.current[i] = el; }}
                                    className={`rounded-lg p-3 transition-all ${isCurrentNav ? 'bg-orange-100 dark:bg-orange-900/40 border-2 border-orange-400 shadow-md ring-2 ring-orange-300' :
                                        isInvalid ? 'bg-red-50 dark:bg-red-900/20 border border-red-200' :
                                            hasImage ? 'bg-blue-50 dark:bg-blue-900/20 border border-blue-200' : 'border border-gray-50 dark:border-gray-700 hover:bg-gray-50 dark:hover:bg-gray-700'
                                        }`}>
                                    <div className="flex items-center gap-3">
                                        <span className={`font-bold text-xs w-6 ${isInvalid ? 'text-red-500' : 'text-gray-400'}`}>{i + 1}.</span>
                                        <span className="flex-1 text-sm truncate text-gray-700 dark:text-gray-300">{q.question_text}</span>

                                        {isInvalid && q._structInvalid ? (
                                            <span className="px-2 py-0.5 bg-red-100 text-red-700 rounded text-xs font-mono font-bold flex-shrink-0">Missing fields</span>
                                        ) : isInvalid ? (
                                            <div className="flex items-center gap-2 flex-shrink-0">
                                                <SmartTopicSelector
                                                    value={q.topic_code || ''}
                                                    onChange={(code) => fixQuestionCode(i, code)}
                                                    topicCodes={topicCodes}
                                                    hasError={!q.topic_code || !validCodesSet.has(q.topic_code)}
                                                    validCodesSet={validCodesSet}
                                                />
                                                <AlertTriangle className="w-4 h-4 text-red-500 flex-shrink-0" />
                                            </div>
                                        ) : (
                                            <span className="px-2 py-0.5 bg-green-100 text-green-700 rounded text-xs font-mono font-bold flex-shrink-0">{q.topic_code} ✓</span>
                                        )}
                                        {q._hasImage && <span className="px-2 py-0.5 bg-blue-100 text-blue-700 rounded text-xs font-bold flex-shrink-0 flex items-center gap-1">🖼️ Has Image Link</span>}
                                        <span className="text-xs text-gray-400 flex-shrink-0">{q.options?.length || 0} opts</span>
                                    </div>
                                    {isInvalid && (
                                        <div className="ml-9 mt-2">
                                            <div className="flex items-start justify-between gap-4">
                                                <div className="text-xs text-red-500">
                                                    {q._structInvalid ? (
                                                        <span className="font-bold">Error: Question missing text or correctly marked options.</span>
                                                    ) : (
                                                        <>Current JSON mappings: subject="{q.subject}", topic="{q.topic}"{q.topic_code && <>, code=<span className="font-mono font-bold">"{q.topic_code}"</span></>}
                                                            {q._hasImage && <><br /><span className="text-blue-600 font-medium">Note: Requires Image Upload later: "{q.image_url}"</span></>}</>
                                                    )}
                                                </div>
                                            </div>
                                        </div>
                                    )}
                                    <div className="ml-9 mt-2">
                                        <button onClick={() => openBulkEditor(i)} className="px-2.5 py-1 text-xs font-bold bg-white dark:bg-gray-800 border border-gray-200 dark:border-gray-700 shadow-sm rounded hover:bg-gray-50 dark:hover:bg-gray-700 text-gray-700 dark:text-gray-300">✏️ Open UI Editor</button>
                                    </div>
                                </div>
                            );
                        })}
                    </div>
                </div>
            )}

            {result && (
                <div className="mt-6 bg-green-50 dark:bg-green-900/20 rounded-xl border border-green-200 p-4">
                    <h3 className="text-sm font-bold text-green-700 mb-2 flex items-center gap-2"><CheckCircle className="w-4 h-4" /> Upload Complete</h3>
                    <p className="text-sm text-green-600">Created: <b>{result.created}</b> | Auto-normalized: <b>{result.normalized || 0}</b></p>
                    {result.missing_topic_codes?.length > 0 && (
                        <div className="mt-2">
                            <p className="text-xs text-orange-600 font-semibold">Unmatched tags (add topic_code to taxonomy):</p>
                            {result.missing_topic_codes.map((t: string, i: number) => (
                                <span key={i} className="inline-block px-2 py-0.5 bg-orange-100 text-orange-700 rounded text-xs mr-1 mt-1">{t}</span>
                            ))}
                        </div>
                    )}
                </div>
            )}
            {bulkEditingIdx !== null && (
                <QuestionEditor
                    form={bulkEditForm}
                    setForm={setBulkEditForm}
                    editing={true}
                    saving={false}
                    onSave={handleSaveBulkEdit}
                    onClose={() => setBulkEditingIdx(null)}
                    topicCodes={topicCodes}
                    validCodesSet={validCodesSet}
                />
            )}
        </div>
    );
};


// ─── TAXONOMY TAB ───

const TaxonomyTab = ({ setToast, onTaxonomyChange }: { setToast: any; onTaxonomyChange: () => void }) => {
    const [taxonomy, setTaxonomy] = useState<any[]>([]);
    const [loading, setLoading] = useState(true);
    const [expanded, setExpanded] = useState<Record<string, boolean>>({});
    const [showAdd, setShowAdd] = useState(false);
    const [addForm, setAddForm] = useState({ subject: '', topic: '', topic_code: '', aliases: '' });
    const [saving, setSaving] = useState(false);
    const [searchCode, setSearchCode] = useState('');

    const fetchTaxonomy = useCallback(async () => {
        setLoading(true);
        try { const res = await QuizAPI.adminGetTaxonomy(); setTaxonomy(res.data || []); }
        catch { console.error('Failed'); }
        finally { setLoading(false); }
    }, []);

    useEffect(() => { fetchTaxonomy(); }, [fetchTaxonomy]);

    const toggle = (s: string) => setExpanded(p => ({ ...p, [s]: !p[s] }));

    const handleSeed = async () => {
        if (!confirm('Seed default 239-code taxonomy? (Only works if empty)')) return;
        try { const res = await QuizAPI.adminSeedTaxonomy(); setToast({ type: 'success', message: `Seeded ${res.data.created || 0} entries.` }); fetchTaxonomy(); onTaxonomyChange(); }
        catch { setToast({ type: 'error', message: 'Failed.' }); }
    };

    const handleAdd = async () => {
        if (!addForm.subject.trim() || !addForm.topic.trim() || !addForm.topic_code.trim()) {
            setToast({ type: 'error', message: 'Subject, topic, and topic_code are all required.' }); return;
        }
        setSaving(true);
        try {
            const aliases = addForm.aliases.split(',').map(a => a.trim()).filter(Boolean);
            await QuizAPI.adminCreateTaxonomy({ subject: addForm.subject, topic: addForm.topic, topic_code: addForm.topic_code.toUpperCase(), aliases });
            setToast({ type: 'success', message: 'Entry added!' });
            setAddForm({ subject: '', topic: '', topic_code: '', aliases: '' });
            setShowAdd(false); fetchTaxonomy(); onTaxonomyChange();
        } catch { setToast({ type: 'error', message: 'Failed. Duplicate code?' }); }
        finally { setSaving(false); }
    };

    const handleDelete = async (id: string) => {
        if (!confirm('Delete this taxonomy entry?')) return;
        try { await QuizAPI.adminDeleteTaxonomy(id); setToast({ type: 'success', message: 'Deleted.' }); fetchTaxonomy(); onTaxonomyChange(); }
        catch { setToast({ type: 'error', message: 'Failed.' }); }
    };

    const totalTopics = taxonomy.reduce((sum, s) => sum + (s.topics?.length || 0), 0);

    // Filter taxonomy by search
    const filteredTaxonomy = searchCode.trim()
        ? taxonomy.map(subj => ({
            ...subj,
            topics: subj.topics?.filter((t: any) =>
                t.topic_code?.toLowerCase().includes(searchCode.toLowerCase()) ||
                t.topic?.toLowerCase().includes(searchCode.toLowerCase()) ||
                t.aliases?.some((a: string) => a.toLowerCase().includes(searchCode.toLowerCase()))
            ) || []
        })).filter(subj => subj.topics.length > 0)
        : taxonomy;

    return (
        <div className="max-w-3xl">
            <div className="flex items-center justify-between mb-6">
                <div>
                    <h1 className="text-2xl font-bold text-gray-900 dark:text-white">Taxonomy Manager</h1>
                    <p className="text-sm text-gray-500 mt-1">{taxonomy.length} subjects, {totalTopics} topic codes</p>
                </div>
                <div className="flex gap-2">
                    <button onClick={handleSeed} className="px-3 py-2 bg-gray-100 hover:bg-gray-200 rounded-lg text-sm font-medium text-gray-700">Seed Defaults</button>
                    <button onClick={() => setShowAdd(true)} className="flex items-center gap-2 bg-orange-600 hover:bg-orange-700 text-white font-bold px-4 py-2 rounded-lg text-sm"><Plus className="w-4 h-4" /> Add Entry</button>
                </div>
            </div>

            {/* Search codes */}
            <div className="relative mb-4">
                <Search className="absolute left-3 top-1/2 -translate-y-1/2 w-4 h-4 text-gray-400" />
                <input type="text" placeholder="Search codes, topics, or aliases..." value={searchCode}
                    onChange={e => setSearchCode(e.target.value)}
                    className="w-full pl-10 pr-4 py-2.5 border border-gray-200 rounded-lg text-sm focus:ring-2 focus:ring-orange-500 dark:bg-gray-800 dark:border-gray-700 dark:text-white" />
            </div>

            {showAdd && (
                <div className="bg-white dark:bg-gray-800 rounded-xl border p-4 mb-4">
                    <div className="grid grid-cols-2 gap-3 mb-2">
                        <input type="text" placeholder="Subject (e.g. Polity)" value={addForm.subject}
                            onChange={e => setAddForm(p => ({ ...p, subject: e.target.value }))}
                            className="px-3 py-2 border rounded-lg text-sm dark:bg-gray-900 dark:border-gray-700 dark:text-white" />
                        <input type="text" placeholder="Display Name (e.g. Fundamental Rights)" value={addForm.topic}
                            onChange={e => setAddForm(p => ({ ...p, topic: e.target.value }))}
                            className="px-3 py-2 border rounded-lg text-sm dark:bg-gray-900 dark:border-gray-700 dark:text-white" />
                    </div>
                    <div className="grid grid-cols-2 gap-3">
                        <input type="text" placeholder="Topic Code (e.g. POL_FR)" value={addForm.topic_code}
                            onChange={e => setAddForm(p => ({ ...p, topic_code: e.target.value.toUpperCase() }))}
                            className="px-3 py-2 border rounded-lg text-sm font-mono dark:bg-gray-900 dark:border-gray-700 dark:text-white" />
                        <input type="text" placeholder="Aliases (comma-separated)" value={addForm.aliases}
                            onChange={e => setAddForm(p => ({ ...p, aliases: e.target.value }))}
                            className="px-3 py-2 border rounded-lg text-sm dark:bg-gray-900 dark:border-gray-700 dark:text-white" />
                    </div>
                    <div className="flex gap-2 mt-3">
                        <button onClick={handleAdd} disabled={saving} className="px-4 py-2 bg-orange-600 text-white rounded-lg text-sm font-bold disabled:opacity-50">{saving ? 'Saving...' : 'Add'}</button>
                        <button onClick={() => setShowAdd(false)} className="px-4 py-2 bg-gray-100 text-gray-700 rounded-lg text-sm">Cancel</button>
                    </div>
                </div>
            )}

            {loading ? <div className="text-center py-10 text-gray-400">Loading...</div> :
                filteredTaxonomy.length === 0 ? (
                    <div className="text-center py-16 bg-white dark:bg-gray-800 rounded-2xl border">
                        <p className="text-gray-400 mb-4">{taxonomy.length === 0 ? 'No taxonomy entries. Click "Seed Defaults" to initialize 239 topic codes.' : 'No results match your search.'}</p>
                    </div>
                ) : (
                    <div className="space-y-2">
                        {filteredTaxonomy.map(subj => (
                            <div key={subj.subject} className="bg-white dark:bg-gray-800 rounded-xl border overflow-hidden">
                                <button onClick={() => toggle(subj.subject)}
                                    className="w-full flex items-center justify-between px-4 py-3 hover:bg-gray-50 dark:hover:bg-gray-700 transition-colors">
                                    <div className="flex items-center gap-3">
                                        <span className="text-sm font-bold text-gray-900 dark:text-white">{subj.subject}</span>
                                        <span className="text-xs text-gray-400">{subj.topics?.length} codes</span>
                                    </div>
                                    {expanded[subj.subject] ? <ChevronUp className="w-4 h-4 text-gray-400" /> : <ChevronDown className="w-4 h-4 text-gray-400" />}
                                </button>
                                {expanded[subj.subject] && (
                                    <div className="border-t px-4 py-2 space-y-1">
                                        {subj.topics?.map((t: any) => (
                                            <div key={t.id} className="flex items-center justify-between py-1.5 group">
                                                <div className="flex-1">
                                                    <div className="flex items-center gap-2">
                                                        <span className="px-1.5 py-0.5 bg-gray-100 dark:bg-gray-700 text-gray-600 dark:text-gray-300 rounded text-[11px] font-mono font-bold">{t.topic_code}</span>
                                                        <span className="text-sm font-medium text-gray-700 dark:text-gray-300">{t.topic}</span>
                                                    </div>
                                                    {t.aliases?.length > 0 && (
                                                        <div className="flex gap-1 flex-wrap mt-0.5 ml-14">
                                                            {t.aliases.map((a: string, i: number) => (
                                                                <span key={i} className="px-1.5 py-0.5 bg-gray-50 dark:bg-gray-700 text-gray-400 rounded text-[10px]">{a}</span>
                                                            ))}
                                                        </div>
                                                    )}
                                                </div>
                                                <button onClick={() => handleDelete(t.id)}
                                                    className="opacity-0 group-hover:opacity-100 p-1 hover:bg-red-50 rounded transition-opacity">
                                                    <Trash2 className="w-3 h-3 text-red-400" />
                                                </button>
                                            </div>
                                        ))}
                                    </div>
                                )}
                            </div>
                        ))}
                    </div>
                )}
        </div>
    );
};


// ─── QUESTION EDITOR MODAL ───

const QuestionEditor = ({ form, setForm, editing, saving, onSave, onClose, topicCodes, validCodesSet }: any) => {
    const setCorrect = (idx: number) => {
        const opts = form.options.map((o: any, i: number) => ({ ...o, is_correct: i === idx }));
        setForm((p: any) => ({ ...p, options: opts }));
    };
    const addOption = () => { if (form.options.length < 6) setForm((p: any) => ({ ...p, options: [...p.options, { option_text: '', is_correct: false }] })); };
    const removeOption = (idx: number) => { if (form.options.length > 2) setForm((p: any) => ({ ...p, options: p.options.filter((_: any, i: number) => i !== idx) })); };

    const handleCodeChange = (code: string) => {
        const match = topicCodes.find((tc: any) => tc.code === code);
        if (match) {
            setForm((p: any) => ({ ...p, topic_code: code, subject: match.subject, topic: match.topic }));
        } else {
            setForm((p: any) => ({ ...p, topic_code: code }));
        }
    };

    return (
        <div className="fixed inset-0 z-50 bg-black/50 flex items-center justify-center p-4" onClick={onClose}>
            <div className="bg-white dark:bg-gray-800 rounded-2xl shadow-2xl max-w-2xl w-full max-h-[90vh] overflow-y-auto" onClick={(e: any) => e.stopPropagation()}>
                <div className="flex items-center justify-between p-5 border-b dark:border-gray-700">
                    <h2 className="text-lg font-bold">{editing ? 'Edit Question' : 'New Question'}</h2>
                    <button onClick={onClose} className="p-1 hover:bg-gray-100 rounded-lg"><X className="w-5 h-5 text-gray-500" /></button>
                </div>
                <div className="p-5 space-y-5">
                    <div>
                        <label className="block text-sm font-semibold text-gray-700 dark:text-gray-300 mb-1">Question *</label>
                        <textarea rows={3} value={form.question_text} onChange={(e: any) => setForm((p: any) => ({ ...p, question_text: e.target.value }))}
                            className="w-full px-3 py-2 border rounded-lg text-sm focus:ring-2 focus:ring-orange-500 dark:bg-gray-900 dark:border-gray-700 dark:text-white" />
                    </div>

                    <div className="bg-orange-50 dark:bg-orange-900/20 rounded-xl p-4 border border-orange-200 dark:border-orange-800">
                        <label className="flex items-center gap-2 text-sm font-bold text-orange-700 dark:text-orange-400 mb-2"><Code className="w-4 h-4" /> Topic Code *</label>
                        <SmartTopicSelector
                            value={form.topic_code || ''}
                            onChange={(code) => handleCodeChange(code)}
                            topicCodes={topicCodes}
                            hasError={!form.topic_code || !validCodesSet?.has(form.topic_code)}
                            validCodesSet={validCodesSet || new Set()}
                        />
                        <p className="text-xs text-orange-500 mt-1">This code links quiz questions to mock test weak areas. Auto-fills Subject & Topic.</p>
                    </div>

                    <div>
                        <label className="block text-sm font-semibold mb-1">Image URL (Optional)</label>
                        <input type="text" value={form.image_url} onChange={(e: any) => setForm((p: any) => ({ ...p, image_url: e.target.value }))}
                            className="w-full px-3 py-2 border rounded-lg text-sm bg-white dark:bg-gray-900 dark:border-gray-700 dark:text-white" placeholder="https://..." />
                        <p className="text-xs text-gray-400 mt-1">Leave blank if no image is needed.</p>
                    </div>

                    <div className="grid grid-cols-2 gap-4">
                        <div>
                            <label className="block text-sm font-semibold mb-1">Subject</label>
                            <input type="text" value={form.subject} readOnly
                                className="w-full px-3 py-2 border rounded-lg text-sm bg-gray-50 dark:bg-gray-900 dark:border-gray-700 dark:text-white cursor-not-allowed" />
                        </div>
                        <div>
                            <label className="block text-sm font-semibold mb-1">Topic</label>
                            <input type="text" value={form.topic} readOnly
                                className="w-full px-3 py-2 border rounded-lg text-sm bg-gray-50 dark:bg-gray-900 dark:border-gray-700 dark:text-white cursor-not-allowed" />
                        </div>
                    </div>

                    <div>
                        <label className="block text-sm font-semibold mb-1">Difficulty</label>
                        <div className="flex gap-2">
                            {['EASY', 'MEDIUM', 'HARD'].map(d => (
                                <button key={d} onClick={() => setForm((p: any) => ({ ...p, difficulty: d }))}
                                    className={`px-4 py-1.5 rounded-lg text-xs font-bold border ${form.difficulty === d
                                        ? d === 'EASY' ? 'bg-green-500 text-white border-green-500' : d === 'HARD' ? 'bg-red-500 text-white border-red-500' : 'bg-orange-500 text-white border-orange-500'
                                        : 'bg-gray-50 text-gray-600 border-gray-200 hover:bg-gray-100'}`}>{d}</button>
                            ))}
                        </div>
                    </div>
                    <div>
                        <label className="block text-sm font-semibold mb-2">Options <span className="text-gray-400 font-normal">(click ● to mark correct)</span></label>
                        <div className="space-y-2">
                            {form.options.map((opt: any, i: number) => (
                                <div key={i} className="flex items-center gap-2">
                                    <button onClick={() => setCorrect(i)} className={`w-7 h-7 rounded-full border-2 flex items-center justify-center flex-shrink-0
                                        ${opt.is_correct ? 'border-green-500 bg-green-500' : 'border-gray-300 hover:border-green-300'}`}>
                                        {opt.is_correct && <span className="text-white text-xs font-bold">✓</span>}
                                    </button>
                                    <span className="text-xs font-bold text-gray-400 w-5">{OPTION_LABELS[i]}.</span>
                                    <input type="text" value={opt.option_text}
                                        onChange={(e: any) => { const opts = [...form.options]; opts[i] = { ...opts[i], option_text: e.target.value }; setForm((p: any) => ({ ...p, options: opts })); }}
                                        className="flex-1 px-3 py-2 border rounded-lg text-sm dark:bg-gray-900 dark:border-gray-700 dark:text-white" placeholder={`Option ${OPTION_LABELS[i]}`} />
                                    {form.options.length > 2 && <button onClick={() => removeOption(i)} className="p-1 hover:bg-red-50 rounded"><X className="w-4 h-4 text-red-400" /></button>}
                                </div>
                            ))}
                        </div>
                        {form.options.length < 6 && <button onClick={addOption} className="mt-2 text-orange-600 text-sm font-medium flex items-center gap-1"><Plus className="w-3 h-3" /> Add Option</button>}
                    </div>
                    <div>
                        <label className="block text-sm font-semibold mb-1">Explanation (Optional)</label>
                        <textarea rows={2} value={form.explanation} onChange={(e: any) => setForm((p: any) => ({ ...p, explanation: e.target.value }))}
                            className="w-full px-3 py-2 border rounded-lg text-sm dark:bg-gray-900 dark:border-gray-700 dark:text-white" placeholder="Why is the answer correct?" />
                    </div>
                </div>
                <div className="flex justify-end gap-3 p-5 border-t dark:border-gray-700">
                    <button onClick={onClose} className="px-4 py-2.5 bg-gray-100 hover:bg-gray-200 text-gray-700 rounded-lg text-sm font-medium">Cancel</button>
                    <button onClick={onSave} disabled={saving} className="flex items-center gap-2 px-5 py-2.5 bg-orange-600 hover:bg-orange-700 text-white rounded-lg text-sm font-bold disabled:opacity-50">
                        <Save className="w-4 h-4" /> {saving ? 'Saving...' : editing ? 'Update' : 'Create'}
                    </button>
                </div>
            </div >
        </div >
    );
};


function _emptyForm() {
    return {
        question_text: '', subject: '', topic: '', topic_code: '', explanation: '', difficulty: 'MEDIUM', image_url: '',
        options: [{ option_text: '', is_correct: true }, { option_text: '', is_correct: false }, { option_text: '', is_correct: false }, { option_text: '', is_correct: false }],
    };
}
