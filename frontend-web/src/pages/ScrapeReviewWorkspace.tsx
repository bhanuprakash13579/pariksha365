import React, { useState, useRef, useMemo, useCallback } from 'react';
import { Document, Page, pdfjs } from 'react-pdf';

import ReactQuill from 'react-quill-new';
import 'react-image-crop/dist/ReactCrop.css';
import 'react-quill-new/dist/quill.snow.css';
import { api, QuizAPI } from '../services/api';
import { X, Image as ImageIcon, Save, SplitSquareHorizontal, Sparkles, Download, AlertTriangle, ArrowUp, ArrowDown, CheckCircle, Code } from 'lucide-react';
import { SmartTopicSelector } from '../components/common/SmartTopicSelector';

// Setup pdf.js worker
pdfjs.GlobalWorkerOptions.workerSrc = `//unpkg.com/pdfjs-dist@${pdfjs.version}/build/pdf.worker.min.mjs`;

const API_BASE = import.meta.env.VITE_API_URL?.replace('/api/v1', '') || 'http://localhost:8000';

interface OptionData {
    option_text: string;
    is_correct: boolean;
}

interface QuestionData {
    id?: string;
    _ui_id?: string;
    question_text: string;
    image_url: string | null;
    explanation: string;
    difficulty: 'EASY' | 'MEDIUM' | 'HARD';
    subject: string;
    topic: string;
    topic_code: string;
    options: OptionData[];
}

interface SectionData {
    id?: string;
    title: string;
    questions: QuestionData[];
}

interface ScrapeReviewWorkspaceProps {
    draftToEdit?: any;
    onClearDraft?: () => void;
    refreshDrafts?: () => void;
}

export const ScrapeReviewWorkspace: React.FC<ScrapeReviewWorkspaceProps> = ({ draftToEdit, onClearDraft, refreshDrafts }) => {
    const [file, setFile] = useState<File | null>(null);
    const [numPages, setNumPages] = useState<number>(0);
    const [pageNumber, setPageNumber] = useState(1);

    // Generate strict UUID to isolate Cloudinary resources to this specific test
    const generateUUID = () => {
        if (typeof crypto !== 'undefined' && crypto.randomUUID) return crypto.randomUUID();
        return 'xxxxxxxx-xxxx-4xxx-yxxx-xxxxxxxxxxxx'.replace(/[xy]/g, (c) => {
            const r = Math.random() * 16 | 0, v = c === 'x' ? r : (r & 0x3 | 0x8);
            return v.toString(16);
        });
    };
    const [draftId] = useState<string>(draftToEdit?.id || generateUUID());

    // Topic codes from DB for validation
    const [topicCodes, setTopicCodes] = useState<any[]>([]);
    const [validCodesSet, setValidCodesSet] = useState<Set<string>>(new Set());
    const [currentIssueIdx, setCurrentIssueIdx] = useState(0);
    const questionRefs = useRef<Record<string, HTMLDivElement | null>>({});

    React.useEffect(() => {
        QuizAPI.adminGetTopicCodes().then(r => {
            const codes = r.data || [];
            setTopicCodes(codes);
            setValidCodesSet(new Set(codes.map((c: any) => c.code)));
        }).catch(() => { });
    }, []);

    // ── Validation: find ALL issues across ALL sections ──
    type ValidationIssue = { sectionIdx: number; questionIdx: number; type: 'code' | 'image'; label: string };

    // Quill Refs for custom image handler
    const quillRefs = useRef<{ [key: string]: ReactQuill | null }>({});

    const imageHandler = (editorId: string) => {
        const input = document.createElement('input');
        input.setAttribute('type', 'file');
        input.setAttribute('accept', 'image/*');
        input.click();

        input.onchange = async () => {
            if (input.files && input.files[0]) {
                const file = input.files[0];
                const formData = new FormData();
                formData.append('file', file);
                formData.append('test_id', draftId); // Link strict UUID to Cloudinary folder

                try {
                    // Upload to backend
                    const res = await api.post('/admin/upload-image', formData, {
                        headers: { 'Content-Type': 'multipart/form-data' }
                    });

                    const url = res.data.url;

                    // Insert at cursor position
                    const quill = quillRefs.current[editorId]?.getEditor();
                    if (quill) {
                        const range = quill.getSelection(true);
                        quill.insertEmbed(range.index, 'image', url);
                    }
                } catch (e) {
                    console.error('Image upload failed', e);
                    alert("Failed to upload image inline.");
                }
            }
        };
    };

    // Memoize the Quill modules so it doesn't re-render and lose focus constantly
    const getQuillModules = useMemo(() => {
        return (editorId: string) => ({
            toolbar: {
                container: [
                    [{ 'header': [1, 2, false] }],
                    ['bold', 'italic', 'underline', 'strike', 'blockquote'],
                    [{ 'list': 'ordered' }, { 'list': 'bullet' }],
                    ['link', 'image'],
                    ['clean']
                ],
                handlers: {
                    image: () => imageHandler(editorId)
                }
            }
        });
    }, []);

    // Categories
    const [dbCategories, setDbCategories] = useState<any[]>([]);
    const [selectedCategory, setSelectedCategory] = useState('');
    const [selectedSubCategory, setSelectedSubCategory] = useState('');

    // Inline Creation Modals
    const [showAddCategoryModal, setShowAddCategoryModal] = useState(false);
    const [showAddSubCategoryModal, setShowAddSubCategoryModal] = useState(false);
    const [newCategoryName, setNewCategoryName] = useState('');
    const [newSubCategoryName, setNewSubCategoryName] = useState('');

    React.useEffect(() => {
        api.get('/categories').then(res => setDbCategories(res.data)).catch(console.error);
    }, []);

    React.useEffect(() => {
        if (draftToEdit) {
            setTestTitle(draftToEdit.title);
            if (draftToEdit.category && dbCategories.length > 0) {
                const parts = draftToEdit.category.split(' - ');
                const mainName = parts[0];
                const subName = parts[1];
                const mainCat = dbCategories.find(c => c.name === mainName);
                if (mainCat) {
                    setSelectedCategory(mainCat.id);
                    if (subName) {
                        const subCat = mainCat.subcategories?.find((s: any) => s.name === subName);
                        if (subCat) setSelectedSubCategory(subCat.id);
                    }
                }
            }

            const loadedSections = draftToEdit.sections || [];
            if (loadedSections.length > 0) {
                const mappedSections = loadedSections.map((sec: any) => ({
                    id: sec.id,
                    title: sec.name || sec.title || "General Section",
                    questions: sec.questions.map((q: any) => ({
                        id: q.id,
                        _ui_id: q._ui_id || q.id || Math.random().toString(36).substring(7),
                        question_text: q.question_text,
                        image_url: q.image_url,
                        explanation: q.explanation || '',
                        difficulty: q.difficulty || 'MEDIUM',
                        subject: q.subject || '',
                        topic: q.topic || '',
                        topic_code: q.topic_code || '',
                        options: q.options.map((o: any) => ({
                            id: o.id,
                            option_text: o.option_text,
                            is_correct: o.is_correct
                        }))
                    }))
                }));
                setSections(mappedSections);
                setInputMode('json');
            }
        }
    }, [draftToEdit, dbCategories]);

    const handleAddCategory = async () => {
        if (!newCategoryName.trim()) return;
        try {
            const res = await api.post('/categories/', { name: newCategoryName.trim() });
            setDbCategories(prev => [...prev, res.data]);
            setSelectedCategory(res.data.id);
            setNewCategoryName('');
            setShowAddCategoryModal(false);
        } catch (err) {
            console.error("Failed to add category", err);
            alert("Failed to create category. See console.");
        }
    };

    const handleAddSubCategory = async () => {
        if (!newSubCategoryName.trim() || !selectedCategory) return;
        try {
            const res = await api.post('/categories/subcategories', {
                name: newSubCategoryName.trim(),
                category_id: selectedCategory
            });
            const updatedCategories = dbCategories.map(cat => {
                if (cat.id === selectedCategory) {
                    return { ...cat, subcategories: [...(cat.subcategories || []), res.data] };
                }
                return cat;
            });
            setDbCategories(updatedCategories);
            setSelectedSubCategory(res.data.id);
            setNewSubCategoryName('');
            setShowAddSubCategoryModal(false);
        } catch (err) {
            console.error("Failed to add subcategory", err);
            alert("Failed to create subcategory. See console.");
        }
    };

    // New Text Paste Mode
    const [inputMode, setInputMode] = useState<'pdf' | 'text' | 'json'>('pdf');
    const [rawText, setRawText] = useState('');
    const [jsonFileCount, setJsonFileCount] = useState<number>(0);

    // Scraper Results
    const [sections, setSections] = useState<SectionData[]>([
        { title: "General Section", questions: [] }
    ]);
    const [activeSectionIndex, setActiveSectionIndex] = useState(0);

    const activeQuestions = sections[activeSectionIndex]?.questions || [];

    const [loading, setLoading] = useState(false);
    const [aiClassify, setAiClassify] = useState(true);
    const [aiModel, setAiModel] = useState('pymupdf'); // Set fast text scanner as default

    // Publish Target
    const [testTitle, setTestTitle] = useState('Scraped Exam Paper');

    const handleDownloadCurrent = () => {
        if (!sections.some(s => s.questions.length > 0)) return alert("No questions to download!");
        const dataStr = "data:text/json;charset=utf-8," + encodeURIComponent(JSON.stringify(sections, null, 2));
        const downloadAnchorNode = document.createElement('a');
        downloadAnchorNode.setAttribute("href", dataStr);
        downloadAnchorNode.setAttribute("download", `${testTitle.replace(/\s+/g, '_')}_export.json`);
        document.body.appendChild(downloadAnchorNode);
        downloadAnchorNode.click();
        downloadAnchorNode.remove();
    };

    const handleFileChange = (e: React.ChangeEvent<HTMLInputElement>) => {
        if (e.target.files && e.target.files[0]) {
            setFile(e.target.files[0]);
        }
    };

    const handleJsonUpload = async (e: React.ChangeEvent<HTMLInputElement>) => {
        let files = Array.from(e.target.files || []);
        if (files.length === 0) return;

        // Force alphanumeric sort by filename to ensure sequential question ordering
        files.sort((a, b) => a.name.localeCompare(b.name, undefined, { numeric: true, sensitivity: 'base' }));

        setLoading(true);
        setJsonFileCount(files.length);

        try {
            // Helper to convert raw ChatGPT strings into basic HTML for Quill
            const formatForQuill = (text: string | null | undefined) => {
                if (!text) return "";
                return text
                    .replace(/\n/g, '<br/>')
                    .replace(/\*\*(.*?)\*\*/g, '<b>$1</b>');
            };

            // Pre-process all text fields
            const processQuestions = (questions: any[]) => {
                return questions.map(q => {
                    // Regex explanation:
                    // ^\s*      = start of string, optional whitespace
                    // (?:       = non-capturing group for the prefix
                    //   Q(?:uestion)?\s*\d+  = "Q1", "Question 1", "Q 1"
                    //   |       = OR
                    //   \d+     = just a number "1"
                    // )
                    // [\.\)\:-]+ = followed by one or more dots, parens, colons, hyphens
                    // \s*       = optional trailing whitespace
                    const stripRegex = /^\s*(?:Q(?:uestion)?\s*\d+|\d+)[\.\)\:-]+\s*/i;

                    let qText = q.question_text || "";
                    if (typeof qText === 'string') {
                        // Strip the hardcoded number and then apply Quill formatting
                        const strippedText = qText.replace(stripRegex, '');
                        qText = formatForQuill(strippedText);
                    }

                    return {
                        ...q,
                        _ui_id: Math.random().toString(36).substring(7),
                        question_text: qText,
                        topic_code: q.topic_code || '',
                        explanation: formatForQuill(q.explanation)
                    };
                });
            };

            let allExtractedSections: SectionData[] = [];

            const readFileAsync = (file: File): Promise<any> => {
                return new Promise((resolve, reject) => {
                    const reader = new FileReader();
                    reader.onload = (event) => {
                        try {
                            resolve(JSON.parse(event.target?.result as string));
                        } catch (err) {
                            reject(new Error(`Invalid JSON in ${file.name}`));
                        }
                    };
                    reader.onerror = reject;
                    reader.readAsText(file);
                });
            };

            const parsedFiles = await Promise.all(files.map(f => readFileAsync(f)));

            parsedFiles.forEach((json, index) => {
                // If it's the old flat array format
                if (Array.isArray(json) && (!json[0] || !json[0].questions)) {
                    const isValid = json.every(q => q.question_text !== undefined);
                    if (isValid) {
                        const formattedQuestions = processQuestions(json);
                        // Convert flat arrays into a temporary general section for merging later
                        allExtractedSections.push({
                            title: sections[activeSectionIndex]?.title || "Imported Section",
                            questions: formattedQuestions
                        });
                    } else {
                        console.warn(`Invalid flat format in file ${files[index].name}`);
                    }
                }
                // If it's the new nested sections format
                else if (Array.isArray(json) && json[0]?.title && Array.isArray(json[0]?.questions)) {
                    const formattedSections = json.map(sec => ({
                        ...sec,
                        questions: processQuestions(sec.questions || [])
                    }));
                    allExtractedSections = [...allExtractedSections, ...formattedSections];
                }
            });

            if (allExtractedSections.length > 0) {
                console.log("React preparing to merge sections:", allExtractedSections.length);
                allExtractedSections.forEach(s => console.log(`Incoming: ${s.title} (${s.questions?.length})`));
                setSections(prev => {
                    let newSectionsState = [...prev];

                    // If the first section in state is the default empty one, wipe it
                    if (prev.length === 1 && prev[0].title === "General Section" && prev[0].questions.length === 0) {
                        newSectionsState = [];
                    }

                    // Intelligently merge all incoming sections with the same title
                    allExtractedSections.forEach(newSec => {
                        const existingSecIndex = newSectionsState.findIndex(s => s.title === newSec.title);
                        if (existingSecIndex >= 0) {
                            newSectionsState[existingSecIndex] = {
                                ...newSectionsState[existingSecIndex],
                                questions: [
                                    ...newSectionsState[existingSecIndex].questions,
                                    ...newSec.questions
                                ]
                            };
                        } else {
                            newSectionsState.push(newSec);
                        }
                    });

                    // Failsafe: if somehow completely empty, restore empty section
                    return newSectionsState.length > 0 ? newSectionsState : [{ title: "General Section", questions: [] }];
                });

                alert(`Successfully merged ${files.length} file(s) into your workspace!`);
            } else {
                alert("No valid data found in the uploaded file(s).");
            }

        } catch (err) {
            console.error("Batch parsing failed", err);
            alert(`Error reading JSON files: ${err instanceof Error ? err.message : 'Unknown error'}`);
        } finally {
            // Reset the input value so the exact same files can be uploaded again if needed
            e.target.value = '';
            setJsonFileCount(0); // Just clear visual representation if multiple
            setLoading(false);
        }
    };

    const handleScrape = async () => {
        setLoading(true);
        try {
            if (inputMode === 'pdf') {
                if (!file) return;
                const formData = new FormData();
                formData.append('file', file);
                const queryParams = new URLSearchParams({
                    ai_classify: aiClassify.toString(),
                    ai_model: aiModel
                });
                const res = await api.post(`/admin/questions/scrape-pdf?${queryParams.toString()}`, formData, {
                    headers: { 'Content-Type': 'multipart/form-data' }
                });
                const newSections = [...sections];
                newSections[activeSectionIndex].questions = [...newSections[activeSectionIndex].questions, ...res.data.data.map((q: any) => ({ ...q, topic_code: q.topic_code || '' }))];
                setSections(newSections);
                alert(aiClassify
                    ? `Scraping (${aiModel.toUpperCase()}) + AI Classification complete.`
                    : `Scraping (${aiModel.toUpperCase()}) complete.`
                );
            } else {
                if (!rawText.trim()) return;
                const res = await api.post('/admin/questions/scrape-text', {
                    raw_text: rawText,
                    ai_classify: aiClassify
                });
                const newSections = [...sections];
                newSections[activeSectionIndex].questions = [...newSections[activeSectionIndex].questions, ...res.data.data.map((q: any) => ({ ...q, topic_code: q.topic_code || '' }))];
                setSections(newSections);
                alert(aiClassify ? `Raw Text Extraction + AI Classification complete.` : `Raw Text Extraction complete.`);
            }
        } catch (error) {
            console.error(error);
            alert("Failed to extract data. See console for details.");
        } finally {
            setLoading(false);
        }
    };

    // ── Compute validation issues reactively ──
    const allIssues: ValidationIssue[] = useMemo(() => {
        const issues: ValidationIssue[] = [];
        sections.forEach((sec, sIdx) => {
            sec.questions.forEach((q, qIdx) => {
                // Missing or invalid topic_code
                if (!q.topic_code || (validCodesSet.size > 0 && !validCodesSet.has(q.topic_code))) {
                    issues.push({ sectionIdx: sIdx, questionIdx: qIdx, type: 'code', label: `Q${qIdx + 1} (${sec.title}): ${!q.topic_code ? 'Missing topic_code' : `Invalid code "${q.topic_code}"`}` });
                }
                // Image required but not yet provided
                if (q.image_url === 'REQUIRED' || q.image_url === 'required') {
                    issues.push({ sectionIdx: sIdx, questionIdx: qIdx, type: 'image', label: `Q${qIdx + 1} (${sec.title}): Image required` });
                }
            });
        });
        return issues;
    }, [sections, validCodesSet]);

    const codeIssueCount = allIssues.filter(i => i.type === 'code').length;
    const imageIssueCount = allIssues.filter(i => i.type === 'image').length;
    const hasIssues = allIssues.length > 0;

    // Clamp currentIssueIdx when issues shrink (e.g. after fixing a question)
    React.useEffect(() => {
        if (currentIssueIdx >= allIssues.length && allIssues.length > 0) {
            setCurrentIssueIdx(allIssues.length - 1);
        } else if (allIssues.length === 0) {
            setCurrentIssueIdx(0);
        }
    }, [allIssues.length, currentIssueIdx]);

    const navigateToIssue = useCallback((direction: 'next' | 'prev') => {
        if (allIssues.length === 0) return;
        let newIdx = currentIssueIdx;
        if (direction === 'next') newIdx = (currentIssueIdx + 1) % allIssues.length;
        else newIdx = (currentIssueIdx - 1 + allIssues.length) % allIssues.length;
        setCurrentIssueIdx(newIdx);
        const issue = allIssues[newIdx];
        // Switch to the correct section
        setActiveSectionIndex(issue.sectionIdx);
        // Scroll to the question after a tick (to let section switch render)
        setTimeout(() => {
            const key = `${issue.sectionIdx}_${issue.questionIdx}`;
            questionRefs.current[key]?.scrollIntoView({ behavior: 'smooth', block: 'center' });
        }, 100);
    }, [allIssues, currentIssueIdx]);

    const handleTopicCodeChange = (qIndex: number, code: string) => {
        const match = topicCodes.find((tc: any) => tc.code === code);
        const newSec = [...sections];
        newSec[activeSectionIndex].questions[qIndex].topic_code = code;
        if (match) {
            newSec[activeSectionIndex].questions[qIndex].subject = match.subject;
            newSec[activeSectionIndex].questions[qIndex].topic = match.topic;
        }
        setSections(newSec);
    };

    const handlePublish = async (is_published: boolean) => {
        // Gate: if publishing, block if there are issues
        if (is_published && hasIssues) {
            const msgs: string[] = [];
            if (codeIssueCount > 0) msgs.push(`${codeIssueCount} question(s) have missing/invalid topic codes`);
            if (imageIssueCount > 0) msgs.push(`${imageIssueCount} question(s) need images`);
            alert(`❌ Cannot publish!\n\n${msgs.join('\n')}\n\nFix all issues first, or save as Draft to continue later.`);
            return;
        }

        // Warn if saving draft with issues
        if (!is_published && hasIssues) {
            const msgs: string[] = [];
            if (codeIssueCount > 0) msgs.push(`${codeIssueCount} question(s) have missing/invalid topic codes`);
            if (imageIssueCount > 0) msgs.push(`${imageIssueCount} question(s) need images`);
            const proceed = confirm(`⚠️ Saving as draft with issues:\n\n${msgs.join('\n')}\n\nYou can fix these later. Continue?`);
            if (!proceed) return;
        }

        let finalCategory = "Scraped Import";
        const cat = dbCategories.find(c => c.id === selectedCategory);
        if (cat) {
            finalCategory = cat.name;
            const sub = cat.subcategories?.find((s: any) => s.id === selectedSubCategory);
            if (sub) {
                finalCategory += ` - ${sub.name}`;
            }
        }

        const payload = {
            id: draftId,
            title: testTitle.trim() || 'Untitled Test',
            category: finalCategory,
            is_published: is_published,
            sections: sections.map(sec => {
                const secPayload: any = {
                    title: sec.title,
                    questions: sec.questions.map(q => {
                        const qPayload: any = {
                            question_text: q.question_text,
                            image_url: q.image_url === 'REQUIRED' || q.image_url === 'required' ? null : q.image_url,
                            explanation: q.explanation,
                            difficulty: q.difficulty,
                            subject: q.subject,
                            topic: q.topic,
                            topic_code: q.topic_code || null,
                            options: q.options.map(o => {
                                const oPayload: any = {
                                    option_text: o.option_text,
                                    is_correct: o.is_correct
                                };
                                if (draftToEdit?.id && (o as any).id) oPayload.id = (o as any).id;
                                return oPayload;
                            })
                        };
                        if (draftToEdit?.id && (q as any).id) qPayload.id = (q as any).id;
                        return qPayload;
                    })
                };
                if (draftToEdit?.id && sec.id) secPayload.id = sec.id;
                return secPayload;
            })
        };

        if (draftToEdit?.id) {
            payload.id = draftToEdit.id;
        }

        try {
            if (draftToEdit?.id) {
                await api.put(`/tests/${draftToEdit.id}`, payload);
            } else {
                await api.post('/tests/bulk', payload);
            }
            if (is_published) {
                alert("✅ Successfully published! You can now link this test in the Course Manager.");
            } else {
                alert("💾 Successfully saved to Backend Drafts! You can view it in the Admin Dashboard.");
            }
            setSections([{ title: "General Section", questions: [] }]);
            setFile(null);
            if (onClearDraft) onClearDraft();
            if (refreshDrafts) refreshDrafts();
        } catch (error) {
            alert("Failed to publish to server.");
            console.error(error);
        }
    };

    const updateQuestion = (qIndex: number, field: string, value: any) => {
        const newSections = [...sections];
        (newSections[activeSectionIndex].questions[qIndex] as any)[field] = value;
        setSections(newSections);
    };

    const updateOption = (qIndex: number, optIndex: number, field: string, value: any) => {
        const newSections = [...sections];
        (newSections[activeSectionIndex].questions[qIndex].options[optIndex] as any)[field] = value;
        setSections(newSections);
    };

    const addOption = (qIndex: number) => {
        const newSections = [...sections];
        newSections[activeSectionIndex].questions[qIndex].options.push({ option_text: "", is_correct: false });
        setSections(newSections);
    };

    const removeOption = (qIndex: number, optIndex: number) => {
        const newSections = [...sections];
        newSections[activeSectionIndex].questions[qIndex].options.splice(optIndex, 1);
        setSections(newSections);
    };

    const getGlobalQuestionNumber = (qIndex: number) => {
        let count = 0;
        for (let i = 0; i < activeSectionIndex; i++) {
            count += sections[i].questions.length;
        }
        return count + qIndex + 1;
    };

    return (
        <div className="flex flex-col h-[90vh] bg-gray-50 dark:bg-gray-900 border border-gray-200 dark:border-gray-800 rounded-lg shadow-lg">

            {/* Header Control Bar */}
            <div className="bg-white dark:bg-gray-800 p-4 border-b flex flex-wrap justify-between items-center shadow-sm z-50 gap-y-3 relative">
                <div className="flex items-center space-x-4 shrink-0">
                    <SplitSquareHorizontal className="text-orange-600" />
                    <h2 className="text-xl font-bold dark:text-white">Import & Review Workspace</h2>

                    {!sections.some(s => s.questions.length > 0) && (
                        <div className="flex bg-gray-100 dark:bg-gray-750 p-1 rounded-md ml-4 border">
                            <button
                                onClick={() => setInputMode('pdf')}
                                className={`px-3 py-1 text-sm font-medium rounded ${inputMode === 'pdf' ? 'bg-white shadow text-blue-600 dark:bg-gray-600 dark:text-gray-100' : 'text-gray-500 dark:text-gray-400'}`}
                            >PDF Upload</button>
                            <button
                                onClick={() => setInputMode('text')}
                                className={`px-3 py-1 text-sm font-medium rounded ${inputMode === 'text' ? 'bg-white shadow text-blue-600 dark:bg-gray-600 dark:text-gray-100' : 'text-gray-500 dark:text-gray-400'}`}
                            >Raw Text / HTML</button>
                            <button
                                onClick={() => setInputMode('json')}
                                className={`px-3 py-1 text-sm font-medium rounded ${inputMode === 'json' ? 'bg-white shadow text-blue-600 dark:bg-gray-600 dark:text-gray-100' : 'text-gray-500 dark:text-gray-400'}`}
                            >Upload JSON</button>
                        </div>
                    )}
                </div>

                <div className="flex items-center gap-x-4 ml-auto">
                    {!sections.some(s => s.questions.length > 0) && inputMode !== 'json' && (
                        <div className="flex items-center space-x-3">
                            {inputMode === 'pdf' && (
                                <>
                                    <input type="file" accept=".pdf" onChange={handleFileChange} className="text-sm border p-1 rounded max-w-[200px]" />
                                    <select
                                        value={aiModel}
                                        onChange={e => setAiModel(e.target.value)}
                                        className="border p-1.5 rounded text-sm bg-gray-50 text-gray-700 max-w-44"
                                    >
                                        <option value="pymupdf">PyMuPDF (Text PDF)</option>
                                        <option value="tesseract">Tesseract (Image PDF)</option>
                                        <option value="gemini">Gemini 3 Flash</option>
                                        <option value="chatgpt">ChatGPT 5.2 Vision</option>
                                    </select>
                                </>
                            )}

                            <label className="flex items-center space-x-1.5 bg-purple-50 border border-purple-200 rounded px-3 py-1.5 cursor-pointer select-none">
                                <input type="checkbox" checked={aiClassify} onChange={e => setAiClassify(e.target.checked)} className="w-4 h-4 text-purple-600 rounded" />
                                <Sparkles className="w-4 h-4 text-purple-600" />
                                <span className="text-sm font-semibold text-purple-700">AI Auto-Tag</span>
                            </label>
                            <button onClick={handleScrape} disabled={(inputMode === 'pdf' ? !file : !rawText) || loading} className="bg-blue-600 hover:bg-blue-700 text-white px-5 py-1.5 rounded disabled:opacity-50 font-medium">
                                {loading ? "Extracting..." : "1. Auto-Extract"}
                            </button>
                        </div>
                    )}
                </div>

                {sections.some(s => s.questions.length > 0) && (
                    <div className="flex items-center space-x-2 bg-orange-50 p-2 rounded border border-orange-200 ml-auto flex-wrap">
                        <select
                            value={selectedCategory}
                            onChange={e => {
                                if (e.target.value === 'ADD_NEW') {
                                    setShowAddCategoryModal(true);
                                } else {
                                    setSelectedCategory(e.target.value);
                                    setSelectedSubCategory('');
                                }
                            }}
                            className="p-1 border rounded text-sm bg-white"
                        >
                            <option value="">Main Category...</option>
                            {dbCategories.map(cat => <option key={cat.id} value={cat.id}>{cat.name}</option>)}
                            <option value="ADD_NEW" className="text-blue-600 font-semibold">+ Add New Category...</option>
                        </select>
                        <select
                            value={selectedSubCategory}
                            onChange={e => {
                                if (e.target.value === 'ADD_NEW') {
                                    setShowAddSubCategoryModal(true);
                                } else {
                                    setSelectedSubCategory(e.target.value);
                                }
                            }}
                            disabled={!selectedCategory}
                            className={`p-1 border rounded text-sm ${!selectedCategory ? 'bg-gray-100 text-gray-400' : 'bg-white'}`}
                        >
                            <option value="">Sub-Category...</option>
                            {selectedCategory && dbCategories.find(c => c.id === selectedCategory)?.subcategories?.map((sub: any) => (
                                <option key={sub.id} value={sub.id}>{sub.name}</option>
                            ))}
                            <option value="ADD_NEW" className="text-blue-600 font-semibold">+ Add New Sub-Category...</option>
                        </select>
                        <input type="text" value={testTitle} onChange={e => setTestTitle(e.target.value)} placeholder="Exam Title" className="p-1 border rounded text-sm w-48 mx-1" />

                        <div className="flex items-center space-x-1 border-l border-orange-200 pl-2 ml-1">
                            <button onClick={handleDownloadCurrent} title="Download as JSON" className="p-1.5 text-blue-600 hover:bg-blue-50 rounded mr-2">
                                <Download className="w-4 h-4" />
                            </button>
                        </div>

                        {draftToEdit && (
                            <button onClick={() => {
                                setSections([{ title: "General Section", questions: [] }]);
                                setActiveSectionIndex(0);
                                setTestTitle('Scraped Exam Paper');
                                if (onClearDraft) onClearDraft();
                            }} className="text-sm font-semibold text-gray-500 hover:text-gray-700 mx-2">
                                Cancel Edit
                            </button>
                        )}

                        {draftToEdit?.is_published ? (
                            <button onClick={() => handlePublish(true)} className={`text-white px-3 py-1.5 rounded text-sm font-bold flex items-center ${hasIssues ? 'bg-gray-400 cursor-not-allowed' : 'bg-green-600 hover:bg-green-700'}`}>
                                <Save className="w-4 h-4 mr-1.5" /> Update Published Test
                                {hasIssues && <AlertTriangle className="w-3.5 h-3.5 ml-1.5 text-yellow-200" />}
                            </button>
                        ) : (
                            <>
                                <button onClick={() => handlePublish(false)} className="bg-yellow-500 hover:bg-yellow-600 text-white px-3 py-1.5 rounded text-sm font-bold flex items-center">
                                    {draftToEdit ? "Update Draft" : "Save as Draft"}
                                </button>
                                <button onClick={() => handlePublish(true)} className={`text-white px-3 py-1.5 rounded text-sm font-bold flex items-center ml-2 ${hasIssues ? 'bg-gray-400 cursor-not-allowed' : 'bg-green-600 hover:bg-green-700'}`}>
                                    <Save className="w-4 h-4 mr-1.5" /> Publish Directly
                                    {hasIssues && <AlertTriangle className="w-3.5 h-3.5 ml-1.5 text-yellow-200" />}
                                </button>
                            </>
                        )}
                    </div>
                )}
            </div>

            {/* Split Screen Workspace */}
            <div className="flex flex-1 overflow-hidden">

                {/* LEFT PANE: Original Content */}
                <div className="w-1/2 bg-gray-200 dark:bg-gray-950 overflow-y-auto border-r border-gray-300 relative">
                    {inputMode === 'pdf' ? (
                        !file ? (
                            <div className="flex items-center justify-center h-full text-gray-500">
                                Upload a PDF to view original document here
                            </div>
                        ) : (
                            <div className="p-4 flex flex-col items-center">
                                <div className="mb-4 bg-white p-2 rounded shadow flex space-x-4 items-center z-10 sticky top-0">
                                    <button onClick={() => setPageNumber(p => Math.max(1, p - 1))} className="px-2 bg-gray-200 rounded">Prev</button>
                                    <span>Page {pageNumber} of {numPages || '--'}</span>
                                    <button onClick={() => setPageNumber(p => Math.min(numPages, p + 1))} className="px-2 bg-gray-200 rounded">Next</button>
                                </div>
                                <Document file={file} onLoadSuccess={({ numPages }) => setNumPages(numPages)}>
                                    <Page pageNumber={pageNumber} renderTextLayer={false} renderAnnotationLayer={false} width={600} className="shadow-lg" />
                                </Document>
                            </div>
                        )
                    ) : inputMode === 'text' ? (
                        <div className="p-4 flex flex-col items-center h-full">
                            <div className="w-full max-w-2xl h-full flex flex-col">
                                <label className="text-sm font-bold text-gray-700 dark:text-gray-300 mb-2">Paste Raw HTML or Text directly into this box</label>
                                <textarea
                                    value={rawText}
                                    onChange={e => setRawText(e.target.value)}
                                    className="flex-1 w-full border border-gray-300 dark:border-gray-700 rounded p-4 text-sm font-mono focus:outline-blue-500 dark:bg-gray-900 dark:text-gray-200 shadow-inner"
                                    placeholder="Paste website HTML source, raw paragraph text, or anything containing a test here. Our Regex extraction engine will hunt for questions..."
                                />
                            </div>
                        </div>
                    ) : (
                        <div className="p-4 flex flex-col items-center justify-center h-full w-full">
                            <div className="bg-white dark:bg-gray-800 p-8 rounded-xl shadow-md border border-gray-200 dark:border-gray-700 text-center max-w-md w-full">
                                <div className="mb-6 flex justify-center">
                                    <SplitSquareHorizontal className="w-16 h-16 text-blue-500" />
                                </div>
                                <h3 className="text-xl font-bold dark:text-white mb-2">Upload JSON Data</h3>
                                <p className="text-sm text-gray-500 dark:text-gray-400 mb-6">Import a pre-structured array of questions directly into the workspace.</p>

                                <div className="relative mb-4">
                                    <input
                                        type="file"
                                        accept=".json"
                                        multiple
                                        onChange={handleJsonUpload}
                                        className="absolute inset-0 w-full h-full opacity-0 cursor-pointer"
                                    />
                                    <button className="w-full bg-blue-50 text-blue-600 hover:bg-blue-100 border-2 border-dashed border-blue-300 font-semibold py-3 px-4 rounded-lg flex items-center justify-center transition-colors">
                                        Browse JSON Files
                                    </button>
                                </div>
                                {jsonFileCount > 0 && (
                                    <p className="text-sm font-mono bg-gray-100 dark:bg-gray-900 p-2 rounded text-center text-gray-700 dark:text-gray-300">
                                        {jsonFileCount} file(s) prepared for extraction
                                    </p>
                                )}
                            </div>

                            <div className="mt-8 text-left max-w-md text-sm text-gray-500">
                                <strong>Expected Format:</strong>
                                <pre className="mt-2 bg-gray-100 dark:bg-gray-800 p-3 rounded-md overflow-x-auto text-xs border">
                                    {`[
  {
    "question_text": "Q1...",
    "explanation": "...",
    "difficulty": "MEDIUM",
    "options": [
      { "option_text": "A", "is_correct": true },
      { "option_text": "B", "is_correct": false }
    ]
  }
]`}
                                </pre>
                            </div>
                        </div>
                    )}
                </div>

                {/* RIGHT PANE: Editable Forms & Sections */}
                <div className="w-1/2 bg-white dark:bg-gray-800 overflow-y-auto flex flex-col">

                    {/* Section Tabs Container */}
                    <div className="bg-gray-100 dark:bg-gray-900 border-b border-gray-200 dark:border-gray-700 flex overflow-x-auto p-2 items-end shrink-0">
                        {sections.map((sec, idx) => (
                            <div key={idx} className={`group flex items-center px-4 py-2 border border-b-0 rounded-t-lg cursor-pointer mr-1 relative transition-colors ${activeSectionIndex === idx ? 'bg-white dark:bg-gray-800 border-gray-300 dark:border-gray-600 z-10' : 'bg-gray-50 dark:bg-gray-800 border-transparent hover:bg-gray-200 dark:hover:bg-gray-700 text-gray-500'}`}
                                onClick={() => setActiveSectionIndex(idx)}>

                                {activeSectionIndex === idx ? (
                                    <input
                                        type="text"
                                        value={sec.title}
                                        onChange={(e) => {
                                            const newSec = [...sections];
                                            newSec[idx].title = e.target.value;
                                            setSections(newSec);
                                        }}
                                        className="bg-transparent font-bold text-gray-800 dark:text-gray-100 focus:outline-none w-32"
                                        placeholder="Section Name"
                                    />
                                ) : (
                                    <span className="font-medium truncate max-w-24">{sec.title}</span>
                                )}
                                <span className="ml-2 text-xs bg-gray-200 dark:bg-gray-700 text-gray-600 dark:text-gray-300 px-1.5 py-0.5 rounded-full">{sec.questions.length}</span>

                                {sections.length > 1 && (
                                    <button onClick={(e) => {
                                        e.stopPropagation();
                                        const newSec = [...sections];
                                        newSec.splice(idx, 1);
                                        setSections(newSec);
                                        if (activeSectionIndex >= newSec.length) setActiveSectionIndex(Math.max(0, newSec.length - 1));
                                    }} className="ml-2 opacity-0 group-hover:opacity-100 text-red-400 hover:text-red-600"><X className="w-3 h-3" /></button>
                                )}
                            </div>
                        ))}
                        <button onClick={() => {
                            setSections([...sections, { title: "New Section", questions: [] }]);
                            setActiveSectionIndex(sections.length);
                        }} className="px-3 py-1.5 ml-2 text-sm text-blue-600 font-bold hover:bg-blue-50 rounded dark:hover:bg-gray-800">+ Add Section</button>
                    </div>

                    {/* ── Validation Bar ── */}
                    {sections.some(s => s.questions.length > 0) && (
                        <div className={`px-4 py-2 flex items-center gap-3 border-b shrink-0 ${hasIssues ? 'bg-red-50 dark:bg-red-900/20 border-red-200' : 'bg-green-50 dark:bg-green-900/20 border-green-200'}`}>
                            {hasIssues ? (
                                <>
                                    <AlertTriangle className="w-5 h-5 text-red-500 flex-shrink-0" />
                                    <span className="text-sm font-semibold text-red-700 dark:text-red-400 flex-1">
                                        {codeIssueCount > 0 && <span className="mr-3">🏷️ {codeIssueCount} missing/invalid code{codeIssueCount > 1 ? 's' : ''}</span>}
                                        {imageIssueCount > 0 && <span>🖼️ {imageIssueCount} image{imageIssueCount > 1 ? 's' : ''} needed</span>}
                                        <span className="text-xs text-red-400 ml-2">({currentIssueIdx + 1}/{allIssues.length})</span>
                                    </span>
                                    <div className="flex items-center gap-1">
                                        <button onClick={() => navigateToIssue('prev')} title="Previous issue" className="p-1.5 bg-red-100 hover:bg-red-200 rounded-lg transition-colors">
                                            <ArrowUp className="w-4 h-4 text-red-600" />
                                        </button>
                                        <button onClick={() => navigateToIssue('next')} title="Next issue" className="p-1.5 bg-red-100 hover:bg-red-200 rounded-lg transition-colors">
                                            <ArrowDown className="w-4 h-4 text-red-600" />
                                        </button>
                                    </div>
                                    <span className="text-[10px] text-red-400 font-medium">Fix all → Publish</span>
                                </>
                            ) : (
                                <>
                                    <CheckCircle className="w-5 h-5 text-green-500" />
                                    <span className="text-sm font-semibold text-green-700">All questions validated ✓ Ready to publish</span>
                                </>
                            )}
                        </div>
                    )}

                    <div className="p-6 space-y-6 flex-1">
                        {activeQuestions.length === 0 ? (
                            <div className="flex flex-col items-center justify-center h-full text-gray-400">
                                <p>Scraped questions will appear here for manual review.</p>
                                <p className="text-sm mt-2">Enable "AI Auto-Tag" to get subject, topic, and difficulty auto-filled!</p>

                                <button onClick={() => {
                                    const newSec = [...sections];
                                    newSec[activeSectionIndex].questions.push({
                                        question_text: "New Question...",
                                        _ui_id: Math.random().toString(36).substring(7),
                                        explanation: "",
                                        difficulty: "MEDIUM",
                                        subject: "",
                                        topic: "",
                                        topic_code: "",
                                        image_url: null,
                                        options: [{ option_text: "A", is_correct: true }, { option_text: "B", is_correct: false }, { option_text: "C", is_correct: false }, { option_text: "D", is_correct: false }]
                                    });
                                    setSections(newSec);
                                }} className="mt-8 px-4 py-2 bg-white border border-gray-300 dark:bg-gray-700 dark:border-gray-600 rounded text-gray-600 dark:text-gray-300 font-semibold shadow-sm hover:shadow">
                                    + Add Empty Question Manually
                                </button>
                            </div>
                        ) : (
                            activeQuestions.map((q, qIndex) => {
                                const qHasCodeIssue = !q.topic_code || (validCodesSet.size > 0 && !validCodesSet.has(q.topic_code));
                                const qHasImageIssue = q.image_url === 'REQUIRED' || q.image_url === 'required';
                                const qHasIssue = qHasCodeIssue || qHasImageIssue;
                                // Check if this is the currently highlighted issue
                                const isCurrentIssue = allIssues.length > 0 && allIssues[currentIssueIdx]?.sectionIdx === activeSectionIndex && allIssues[currentIssueIdx]?.questionIdx === qIndex;
                                return (
                                    <div key={q._ui_id || qIndex}
                                        ref={el => { questionRefs.current[`${activeSectionIndex}_${qIndex}`] = el; }}
                                        className={`rounded-lg p-4 shadow-sm transition-all ${isCurrentIssue ? 'border-2 border-red-400 ring-2 ring-red-300 bg-red-50 dark:bg-red-900/20' :
                                            qHasIssue ? 'border-2 border-orange-300 bg-orange-50/50 dark:bg-orange-900/10' :
                                                'border border-gray-200 dark:border-gray-700 bg-gray-50 dark:bg-gray-750'
                                            }`}>
                                        <div className="flex justify-between items-center mb-2">
                                            <span className="font-bold text-gray-700 dark:text-gray-300">Question {getGlobalQuestionNumber(qIndex)}</span>
                                            <button onClick={() => {
                                                const newSec = [...sections];
                                                newSec[activeSectionIndex].questions.splice(qIndex, 1);
                                                setSections(newSec);
                                            }} className="text-red-500 hover:text-red-700 text-sm"><X className="w-4 h-4" /></button>
                                        </div>

                                        <div className="space-y-3">
                                            <ReactQuill
                                                ref={(el) => { quillRefs.current[`q_${q._ui_id || qIndex}`] = el; }}
                                                key={`q_quill_${q._ui_id || qIndex}`}
                                                theme="snow"
                                                value={q.question_text}
                                                onChange={(val: string) => updateQuestion(qIndex, 'question_text', val)}
                                                modules={getQuillModules(`q_${q._ui_id || qIndex}`)}
                                                className="bg-white dark:bg-gray-800 dark:text-white"
                                            />

                                            {(q.image_url === 'REQUIRED' || q.image_url === 'required') ? (
                                                <div className="bg-red-100 dark:bg-red-900/30 border-2 border-dashed border-red-300 p-3 rounded-lg flex flex-col items-center">
                                                    <span className="text-xs font-bold text-red-600 flex items-center gap-1 mb-1">
                                                        <AlertTriangle className="w-3.5 h-3.5" /> IMAGE REQUIRED
                                                    </span>
                                                    <p className="text-xs text-red-500">Upload an image using the Quill editor toolbar above, or replace "REQUIRED" with a URL</p>
                                                    <input type="text" placeholder="Paste image URL here to resolve..."
                                                        className="mt-2 w-full px-2 py-1 border border-red-300 rounded text-xs focus:ring-2 focus:ring-red-400"
                                                        onBlur={(e) => { if (e.target.value.trim()) updateQuestion(qIndex, 'image_url', e.target.value.trim()); }}
                                                    />
                                                </div>
                                            ) : q.image_url ? (
                                                <div className="bg-gray-200 p-2 rounded flex flex-col items-center">
                                                    <span className="text-xs text-gray-500 mb-1 flex items-center"><ImageIcon className="w-3 h-3 mr-1" /> Scraped Image Attached</span>
                                                    <img src={q.image_url.startsWith('http') ? q.image_url : `${API_BASE}${q.image_url}`} alt="question" className="max-h-32 object-contain" />
                                                </div>
                                            ) : null}

                                            {/* Topic Code + Subject / Topic / Difficulty */}
                                            <div className={`rounded-lg p-2 mb-1 ${qHasCodeIssue ? 'bg-red-50 dark:bg-red-900/20 border border-red-200' : ''}`}>
                                                <div className="mb-2">
                                                    <label className={`text-xs font-bold flex items-center gap-1 mb-1 ${qHasCodeIssue ? 'text-red-600' : 'text-orange-600'}`}>
                                                        <Code className="w-3 h-3" /> Topic Code {qHasCodeIssue && <AlertTriangle className="w-3 h-3 text-red-500" />}
                                                    </label>
                                                    <SmartTopicSelector
                                                        value={q.topic_code || ''}
                                                        onChange={code => handleTopicCodeChange(qIndex, code)}
                                                        topicCodes={topicCodes}
                                                        hasError={qHasCodeIssue}
                                                        validCodesSet={validCodesSet}
                                                    />
                                                </div>
                                                <div className="grid grid-cols-3 gap-2">
                                                    <div>
                                                        <label className="text-xs font-semibold text-gray-500">Subject</label>
                                                        <input type="text" value={q.subject || ''} onChange={e => updateQuestion(qIndex, 'subject', e.target.value)}
                                                            className="border p-1.5 rounded text-sm w-full" placeholder="e.g. Polity" readOnly={!!q.topic_code && validCodesSet.has(q.topic_code)} />
                                                    </div>
                                                    <div>
                                                        <label className="text-xs font-semibold text-gray-500">Topic</label>
                                                        <input type="text" value={q.topic || ''} onChange={e => updateQuestion(qIndex, 'topic', e.target.value)}
                                                            className="border p-1.5 rounded text-sm w-full" placeholder="e.g. Fundamental Rights" readOnly={!!q.topic_code && validCodesSet.has(q.topic_code)} />
                                                    </div>
                                                    <div>
                                                        <label className="text-xs font-semibold text-gray-500">Difficulty</label>
                                                        <select value={q.difficulty || 'MEDIUM'} onChange={e => updateQuestion(qIndex, 'difficulty', e.target.value)}
                                                            className="border p-1.5 rounded text-sm w-full">
                                                            <option value="EASY">Easy</option>
                                                            <option value="MEDIUM">Medium</option>
                                                            <option value="HARD">Hard</option>
                                                        </select>
                                                    </div>
                                                </div>
                                            </div>
                                            <div>
                                                <label className="text-xs font-semibold text-gray-500 mb-1 block">Explanation</label>
                                                <ReactQuill
                                                    ref={(el) => { quillRefs.current[`exp_${q._ui_id || qIndex}`] = el; }}
                                                    key={`exp_quill_${q._ui_id || qIndex}`}
                                                    theme="snow"
                                                    value={q.explanation || ''}
                                                    onChange={(val: string) => updateQuestion(qIndex, 'explanation', val)}
                                                    modules={getQuillModules(`exp_${q._ui_id || qIndex}`)}
                                                    className="bg-white dark:bg-gray-800 dark:text-white"
                                                    placeholder="Write explanation here... click the Image button to upload pictures."
                                                />
                                            </div>

                                            {/* Options */}
                                            <div className="mt-4 space-y-2">
                                                <p className="text-sm font-semibold text-gray-600 dark:text-gray-400">Options (Select Correct)</p>
                                                {q.options.map((opt, optIndex) => (
                                                    <div key={optIndex} className="flex items-center space-x-2">
                                                        <input
                                                            type="radio"
                                                            name={`correct_opt_${qIndex}`}
                                                            checked={opt.is_correct}
                                                            onChange={() => {
                                                                const newSections = [...sections];
                                                                newSections[activeSectionIndex].questions[qIndex].options.forEach(o => o.is_correct = false);
                                                                newSections[activeSectionIndex].questions[qIndex].options[optIndex].is_correct = true;
                                                                setSections(newSections);
                                                            }}
                                                            className="w-4 h-4 text-green-600"
                                                        />
                                                        <input
                                                            type="text"
                                                            value={opt.option_text.replace(/<[^>]*>?/gm, '')}
                                                            onChange={(e) => updateOption(qIndex, optIndex, 'option_text', e.target.value)}
                                                            className={`border p-1.5 flex-1 rounded text-sm ${opt.is_correct ? 'border-green-500 bg-green-50' : 'border-gray-300'}`}
                                                        />
                                                        <button onClick={() => removeOption(qIndex, optIndex)} className="text-gray-400 hover:text-red-500"><X className="w-4 h-4" /></button>
                                                    </div>
                                                ))}
                                                <button onClick={() => addOption(qIndex)} className="text-xs text-blue-600 font-medium">+ Add Option</button>
                                            </div>
                                        </div>
                                    </div>
                                );
                            })
                        )}
                    </div>
                </div>
            </div>

            {/* Modals for Adding Categories */}
            {showAddCategoryModal && (
                <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-[100]">
                    <div className="bg-white dark:bg-gray-800 p-6 rounded-lg shadow-xl w-96">
                        <h3 className="text-lg font-bold mb-4 dark:text-white">Add New Main Category</h3>
                        <input
                            type="text"
                            value={newCategoryName}
                            onChange={(e) => setNewCategoryName(e.target.value)}
                            className="w-full border p-2 rounded mb-4"
                            placeholder="e.g. RRB Exams"
                            autoFocus
                        />
                        <div className="flex justify-end space-x-2">
                            <button onClick={() => setShowAddCategoryModal(false)} className="px-4 py-2 text-gray-500 hover:bg-gray-100 rounded">Cancel</button>
                            <button onClick={handleAddCategory} className="px-4 py-2 bg-blue-600 text-white rounded hover:bg-blue-700">Save Category</button>
                        </div>
                    </div>
                </div>
            )}

            {showAddSubCategoryModal && (
                <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-[100]">
                    <div className="bg-white dark:bg-gray-800 p-6 rounded-lg shadow-xl w-96">
                        <h3 className="text-lg font-bold mb-4 dark:text-white">Add New Sub-Category</h3>
                        <p className="text-xs text-gray-500 mb-2">Adding under: {dbCategories.find(c => c.id === selectedCategory)?.name}</p>
                        <input
                            type="text"
                            value={newSubCategoryName}
                            onChange={(e) => setNewSubCategoryName(e.target.value)}
                            className="w-full border p-2 rounded mb-4"
                            placeholder="e.g. RRB NTPC"
                            autoFocus
                        />
                        <div className="flex justify-end space-x-2">
                            <button onClick={() => setShowAddSubCategoryModal(false)} className="px-4 py-2 text-gray-500 hover:bg-gray-100 rounded">Cancel</button>
                            <button onClick={handleAddSubCategory} className="px-4 py-2 bg-blue-600 text-white rounded hover:bg-blue-700">Save Sub-Category</button>
                        </div>
                    </div>
                </div>
            )}

        </div>
    );
};
