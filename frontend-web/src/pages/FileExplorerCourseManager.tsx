import React, { useState } from 'react';
import { Folder, FolderOpen, Plus, Trash2, FileText, ChevronRight, Home, ArrowLeft, Clock, Download } from 'lucide-react';

interface Props {
    dbCategories: any[];
    courses: any[];
    tests: any[];
    api: any;
    fetchData: () => void;
    setDraftToEdit: (d: any) => void;
    setActiveTab: (tab: string) => void;
}

type BreadcrumbItem = { label: string; id: string; level: number };

// Psychological nudge config per category
const CATEGORY_CONFIG: Record<string, { emoji: string; color: string; border: string; bg: string; badge?: string; badgeColor?: string }> = {
    Bank: { emoji: '🏦', color: 'text-blue-700', border: 'border-blue-400', bg: 'bg-blue-50', badge: '🔥 Trending', badgeColor: 'bg-blue-100 text-blue-700' },
    Judicial: { emoji: '⚖️', color: 'text-violet-700', border: 'border-violet-400', bg: 'bg-violet-50', badge: '⚡ High Demand', badgeColor: 'bg-violet-100 text-violet-700' },
    ESIC: { emoji: '🏥', color: 'text-teal-700', border: 'border-teal-400', bg: 'bg-teal-50' },
    Railway: { emoji: '🚂', color: 'text-amber-700', border: 'border-amber-400', bg: 'bg-amber-50', badge: '🎯 Most Attempted', badgeColor: 'bg-amber-100 text-amber-700' },
    Defence: { emoji: '🛡️', color: 'text-red-700', border: 'border-red-400', bg: 'bg-red-50', badge: '💪 Competitive', badgeColor: 'bg-red-100 text-red-700' },
    PSUs: { emoji: '🏭', color: 'text-slate-700', border: 'border-slate-400', bg: 'bg-slate-50' },
    UPSC: { emoji: '🏛️', color: 'text-purple-700', border: 'border-purple-400', bg: 'bg-purple-50', badge: '👑 Premium', badgeColor: 'bg-purple-100 text-purple-700' },
    SSC: { emoji: '📋', color: 'text-orange-700', border: 'border-orange-400', bg: 'bg-orange-50', badge: '🔥 Trending', badgeColor: 'bg-orange-100 text-orange-700' },
    Police: { emoji: '👮', color: 'text-indigo-700', border: 'border-indigo-400', bg: 'bg-indigo-50' },
    PSCs: { emoji: '🏢', color: 'text-green-700', border: 'border-green-400', bg: 'bg-green-50', badge: '⭐ State Exams', badgeColor: 'bg-green-100 text-green-700' },
    'Post-Office': { emoji: '📬', color: 'text-yellow-700', border: 'border-yellow-400', bg: 'bg-yellow-50' },
};

const ORDERED_CATEGORIES = ['Bank', 'Judicial', 'ESIC', 'Railway', 'Defence', 'PSUs', 'UPSC', 'SSC', 'Police', 'PSCs', 'Post-Office'];

export const FileExplorerCourseManager: React.FC<Props> = ({
    dbCategories, courses, tests, api, fetchData, setDraftToEdit, setActiveTab
}) => {
    const [breadcrumb, setBreadcrumb] = useState<BreadcrumbItem[]>([{ label: 'Home', id: '', level: 0 }]);
    const [newItemName, setNewItemName] = useState('');
    const [isAdding, setIsAdding] = useState(false);
    const [newCoursePrice, setNewCoursePrice] = useState(0);

    // Drag events state
    const [draggedItemId, setDraggedItemId] = useState<string | null>(null);
    const [dragOverItemId, setDragOverItemId] = useState<string | null>(null);

    const currentLevel = breadcrumb[breadcrumb.length - 1].level;
    const currentId = breadcrumb[breadcrumb.length - 1].id;

    const navigateTo = (label: string, id: string, nextLevel: number) => {
        setBreadcrumb(prev => [...prev, { label, id, level: nextLevel }]);
        setIsAdding(false);
        setNewItemName('');
    };

    const navigateToCrumb = (index: number) => {
        setBreadcrumb(prev => prev.slice(0, index + 1));
        setIsAdding(false);
        setNewItemName('');
    };

    const getChildren = (): { id: string; name: string; count: number }[] => {
        if (currentLevel === 1) {
            const cat = dbCategories.find(c => c.id === currentId);
            return (cat?.subcategories || []).map((sub: any) => ({
                id: sub.id, name: sub.name,
                count: courses.filter(c => c.subcategory_id === sub.id).length,
            }));
        }
        if (currentLevel === 2) {
            return courses.filter(c => c.subcategory_id === currentId).map(c => ({
                id: c.id, name: c.title, count: (c.folders || []).length
            }));
        }
        if (currentLevel === 3) {
            const course = courses.find(c => c.id === currentId);
            return (course?.folders || []).map((f: any) => ({
                id: f.id, name: f.title, count: (f.tests || []).length
            }));
        }
        return [];
    };

    const getLinkedTests = (): any[] => {
        if (currentLevel !== 4) return [];
        for (const course of courses) {
            for (const folder of (course.folders || [])) {
                if (folder.id === currentId) {
                    return (folder.tests || []).map((link: any) => {
                        const t = tests.find(tt => tt.id === link.test_id);
                        return { linkId: link.id, testId: link.test_id, title: t?.title || 'Unknown', category: t?.category || '' };
                    });
                }
            }
        }
        return [];
    };

    const levelLabel = ['', 'Sub-Category', 'Course Pack', 'Folder', 'Test'][currentLevel] || 'Item';

    const handleCreate = async () => {
        if (!newItemName.trim()) return;
        try {
            if (currentLevel === 1) await api.post('/categories/subcategories', { category_id: currentId, name: newItemName.trim() });
            else if (currentLevel === 2) await api.post('/courses', { title: newItemName.trim(), subcategory_id: currentId, price: newCoursePrice, is_published: true });
            else if (currentLevel === 3) await api.post(`/courses/${currentId}/folders`, { title: newItemName.trim(), is_free: true });
            setNewItemName(''); setNewCoursePrice(0); setIsAdding(false); fetchData();
        } catch { alert(`Failed to create ${levelLabel}`); }
    };

    const handleLinkTest = async (testId: string) => {
        try { await api.post(`/courses/folders/${currentId}/tests`, { test_id: testId }); fetchData(); }
        catch { alert('Failed to link test.'); }
    };

    const handleDelete = async (itemId: string, itemName: string) => {
        if (!confirm(`Delete "${itemName}"?`)) return;
        try {
            if (currentLevel === 2) await api.delete(`/courses/${itemId}`);
            else if (currentLevel === 3) await api.delete(`/courses/folders/${itemId}`);
            fetchData();
        } catch { alert(`Failed to delete "${itemName}"`); }
    };

    const allLinkedTestIds = new Set<string>();
    courses.forEach(c => (c.folders || []).forEach((f: any) => (f.tests || []).forEach((l: any) => allLinkedTestIds.add(l.test_id))));
    const availableTests = tests.filter(t => !allLinkedTestIds.has(t.id));

    // For drag/drop: dynamically use a local state to sort visually first before API hit
    const [localChildren, setLocalChildren] = useState(getChildren());
    const [localLinkedTests, setLocalLinkedTests] = useState(getLinkedTests());

    // Update local state when DB context changes or levels change
    React.useEffect(() => {
        setLocalChildren(getChildren());
        setLocalLinkedTests(getLinkedTests());
    }, [currentLevel, currentId, courses, dbCategories, tests]);

    const handleDragStart = (e: React.DragEvent, id: string) => {
        setDraggedItemId(id);
        e.dataTransfer.effectAllowed = 'move';
        // Optional: reduce opacity of dragged item
        if (e.target instanceof HTMLElement) {
            e.target.style.opacity = '0.4';
        }
    };

    const handleDragOver = (e: React.DragEvent, id: string) => {
        e.preventDefault();
        e.dataTransfer.dropEffect = 'move';
        if (id !== dragOverItemId) {
            setDragOverItemId(id);
        }
    };

    const handleDragEnd = (e: React.DragEvent) => {
        setDraggedItemId(null);
        setDragOverItemId(null);
        if (e.target instanceof HTMLElement) {
            e.target.style.opacity = '1';
        }
    };

    const handleDrop = async (e: React.DragEvent, dropItemId: string) => {
        e.preventDefault();
        if (!draggedItemId || draggedItemId === dropItemId) {
            handleDragEnd(e);
            return;
        }

        // Reorder behavior
        if (isInsideFolder) {
            // Reordering tests
            const items = [...localLinkedTests];
            const dragIdx = items.findIndex(t => t.linkId === draggedItemId);
            const dropIdx = items.findIndex(t => t.linkId === dropItemId);
            if (dragIdx === -1 || dropIdx === -1) return;

            // Move item
            const [dragged] = items.splice(dragIdx, 1);
            items.splice(dropIdx, 0, dragged);

            setLocalLinkedTests([...items]); // Visual update immediately
            handleDragEnd(e);

            // API Push
            const updatePayload = items.map((item, idx) => ({ id: item.linkId, order: idx }));
            try {
                await api.put(`/courses/folders/${currentId}/tests/order`, { items: updatePayload });
                fetchData(); // Sync up
            } catch {
                alert("Failed to save new order");
            }
        } else {
            // Reordering folders (currentLevel === 3)
            if (currentLevel !== 3) {
                handleDragEnd(e);
                return; // Only support sorting folders for now
            }

            const items = [...localChildren];
            const dragIdx = items.findIndex(f => f.id === draggedItemId);
            const dropIdx = items.findIndex(f => f.id === dropItemId);
            if (dragIdx === -1 || dropIdx === -1) return;

            const [dragged] = items.splice(dragIdx, 1);
            items.splice(dropIdx, 0, dragged);
            setLocalChildren([...items]);
            handleDragEnd(e);

            const updatePayload = items.map((item, idx) => ({ id: item.id, order: idx }));
            try {
                const parentCourseId = breadcrumb[2].id;
                await api.put(`/courses/${parentCourseId}/folders/order`, { items: updatePayload });
                fetchData();
            } catch {
                alert("Failed to save new folder order");
            }
        }
    };

    const isInsideFolder = currentLevel === 4;

    // ── LEVEL 0: Clean Category Root View (Admin) ──
    if (currentLevel === 0) {
        const sortedCats = [...dbCategories].sort((a, b) => {
            const ai = ORDERED_CATEGORIES.indexOf(a.name);
            const bi = ORDERED_CATEGORIES.indexOf(b.name);
            return (ai === -1 ? 99 : ai) - (bi === -1 ? 99 : bi);
        });

        return (
            <div className="space-y-6">
                <div className="flex items-center justify-between">
                    <div>
                        <h1 className="text-2xl font-black text-gray-900">📂 Course Manager</h1>
                        <p className="text-sm text-gray-500 mt-0.5">{sortedCats.length} exam categories · {courses.length} course packs · {tests.length} published tests</p>
                    </div>
                </div>

                {/* Category Grid */}
                <div className="grid grid-cols-2 md:grid-cols-3 xl:grid-cols-4 gap-4">
                    {sortedCats.map(cat => {
                        const cfg = CATEGORY_CONFIG[cat.name] || { emoji: '📚', color: 'text-gray-700', border: 'border-gray-300', bg: 'bg-gray-50' };
                        const catCourses = courses.filter((c: any) =>
                            (cat.subcategories || []).some((s: any) => s.id === c.subcategory_id)
                        );
                        const courseCount = catCourses.length;
                        const testCount = catCourses.reduce((total: number, c: any) =>
                            total + (c.folders || []).reduce((fTotal: number, f: any) =>
                                fTotal + (f.tests || []).length, 0), 0);

                        return (
                            <button
                                key={cat.id}
                                onClick={() => navigateTo(cat.name, cat.id, 1)}
                                className={`relative group text-left border-l-4 ${cfg.border} ${cfg.bg} border border-gray-100 rounded-xl p-5 shadow-sm hover:shadow-md transition-all duration-200 hover:scale-[1.02]`}
                            >
                                <div className="text-2xl mb-2">{cfg.emoji}</div>
                                <h3 className={`text-base font-black ${cfg.color} mb-2`}>{cat.name}</h3>
                                <div className="flex gap-3 text-xs text-gray-500">
                                    <span>{testCount} tests</span>
                                    <span>·</span>
                                    <span>{courseCount} courses</span>
                                </div>
                                <ChevronRight className="absolute bottom-4 right-4 w-4 h-4 text-gray-300 group-hover:text-gray-500 transition-colors" />
                            </button>
                        );
                    })}

                    {/* Create New Category */}
                    {!isAdding ? (
                        <button
                            onClick={() => setIsAdding(true)}
                            className="border-2 border-dashed border-gray-200 hover:border-orange-400 rounded-xl p-5 flex flex-col items-center justify-center gap-2 text-gray-300 hover:text-orange-500 transition-all group min-h-[120px]"
                        >
                            <Plus className="w-7 h-7 group-hover:scale-110 transition-transform" />
                            <span className="text-xs font-bold">New Category</span>
                        </button>
                    ) : (
                        <div className="border-2 border-orange-400 rounded-xl p-4 bg-orange-50 flex flex-col gap-3">
                            <h4 className="font-bold text-orange-700 text-sm">New Category</h4>
                            <input
                                autoFocus type="text" placeholder="Category name..."
                                className="border border-orange-200 p-2 rounded-lg text-sm focus:ring-2 focus:ring-orange-400 outline-none bg-white"
                                value={newItemName} onChange={e => setNewItemName(e.target.value)}
                                onKeyDown={e => {
                                    if (e.key === 'Enter') handleCreate();
                                    if (e.key === 'Escape') setIsAdding(false);
                                }}
                            />
                            <div className="flex gap-2">
                                <button
                                    onClick={handleCreate}
                                    className="flex-1 bg-orange-600 hover:bg-orange-700 text-white py-1.5 rounded-lg text-sm font-bold transition-colors"
                                >
                                    Create
                                </button>
                                <button
                                    onClick={() => { setIsAdding(false); setNewItemName(''); }}
                                    className="px-3 py-1.5 text-gray-500 hover:bg-gray-100 rounded-lg text-sm transition-colors"
                                >
                                    Cancel
                                </button>
                            </div>
                        </div>
                    )}
                </div>
            </div>
        );
    }

    // ── LEVELS 1-4: Deep Navigation View ──
    const currentCatName = breadcrumb.length > 1 ? breadcrumb[1].label : '';
    const cfg = CATEGORY_CONFIG[currentCatName] || { emoji: '📂', color: 'text-gray-700', border: 'border-gray-400', bg: 'bg-gray-50' };

    return (
        <div className="space-y-4">
            {/* Header */}
            <div className="flex items-center justify-between">
                <div className="flex items-center gap-3">
                    <span className="text-2xl">{cfg.emoji}</span>
                    <div>
                        <h1 className="text-xl font-black text-gray-900">{currentCatName}</h1>
                        <p className="text-xs text-gray-400">{['', 'Sub-categories', 'Course Packs', 'Folders', 'Tests'][currentLevel]}</p>
                    </div>
                </div>
                <button onClick={() => navigateToCrumb(0)} className="flex items-center gap-2 text-sm text-gray-500 hover:text-orange-600 font-semibold transition-colors">
                    <Home className="w-4 h-4" /> All Categories
                </button>
            </div>

            {/* Breadcrumb */}
            <div className={`border-l-4 ${cfg.border} bg-white border border-gray-100 rounded-lg px-4 py-2.5 flex items-center gap-1 flex-wrap shadow-sm`}>
                {breadcrumb.map((crumb, i) => (
                    <React.Fragment key={i}>
                        {i > 0 && <ChevronRight className="w-3.5 h-3.5 text-gray-300 mx-0.5" />}
                        <button
                            onClick={() => navigateToCrumb(i)}
                            className={`flex items-center gap-1 px-2.5 py-1 rounded-lg text-xs font-bold transition-colors ${i === breadcrumb.length - 1 ? 'bg-orange-100 text-orange-700' : 'text-gray-500 hover:bg-gray-100'
                                }`}
                        >
                            {i === 0 ? <Home className="w-3 h-3" /> : <Folder className="w-3 h-3" />}
                            {crumb.label}
                        </button>
                    </React.Fragment>
                ))}
            </div>

            <div className="flex gap-5">
                {/* Main Area */}
                <div className="flex-1 min-w-0">
                    {currentLevel > 0 && (
                        <button onClick={() => navigateToCrumb(breadcrumb.length - 2)} className="flex items-center gap-1.5 text-gray-400 hover:text-gray-700 mb-4 text-sm font-medium transition-colors">
                            <ArrowLeft className="w-4 h-4" /> Back to {breadcrumb[breadcrumb.length - 2].label}
                        </button>
                    )}

                    {!isInsideFolder && (
                        <div className="grid grid-cols-2 md:grid-cols-3 gap-3">
                            {localChildren.map(child => {
                                const isDraggable = currentLevel === 3;
                                return (
                                    <div
                                        key={child.id}
                                        draggable={isDraggable}
                                        onDragStart={isDraggable ? (e) => handleDragStart(e, child.id) : undefined}
                                        onDragOver={isDraggable ? (e) => handleDragOver(e, child.id) : undefined}
                                        onDrop={isDraggable ? (e) => handleDrop(e, child.id) : undefined}
                                        onDragEnd={isDraggable ? handleDragEnd : undefined}
                                        className={`relative group border-l-4 ${cfg.border} bg-white border border-gray-100 rounded-xl p-4 shadow-sm hover:shadow-md transition-all cursor-pointer hover:scale-[1.02] ${dragOverItemId === child.id ? 'border-orange-500 bg-orange-50/50 scale-[1.03] z-10' : ''
                                            }`}
                                        onClick={() => navigateTo(child.name, child.id, currentLevel + 1)}
                                    >
                                        <div className="flex items-center justify-between mb-3">
                                            <div className="flex items-center gap-2">
                                                {isDraggable && <div className="text-gray-300 group-hover:text-gray-400 cursor-grab px-1">⋮⋮</div>}
                                                <FolderOpen className={`w-7 h-7 ${cfg.color} opacity-80`} />
                                            </div>
                                            <button
                                                onClick={e => { e.stopPropagation(); handleDelete(child.id, child.name); }}
                                                className="opacity-0 group-hover:opacity-100 p-1.5 text-red-400 hover:bg-red-50 rounded-lg transition-all"
                                            >
                                                <Trash2 className="w-3.5 h-3.5" />
                                            </button>
                                        </div>
                                        <h3 className="font-bold text-gray-800 text-sm leading-tight mb-1">{child.name}</h3>
                                        <p className="text-xs text-gray-400">{child.count} {['', 'courses', 'folders', 'tests', ''][currentLevel]} inside</p>
                                        {/* Urgency nudge if empty */}
                                        {child.count === 0 && (
                                            <p className="text-[10px] text-amber-500 font-semibold mt-1.5">⚠️ Empty — students can't access this</p>
                                        )}
                                    </div>
                                )
                            })}

                            {/* New Item Card */}
                            {currentLevel < 4 && !isAdding && (
                                <button onClick={() => setIsAdding(true)} className="border-2 border-dashed border-gray-200 hover:border-orange-400 rounded-xl p-4 flex flex-col items-center justify-center gap-2 text-gray-300 hover:text-orange-500 transition-all min-h-[110px] group">
                                    <Plus className="w-7 h-7 group-hover:scale-110 transition-transform" />
                                    <span className="text-xs font-bold">New {levelLabel}</span>
                                </button>
                            )}

                            {isAdding && (
                                <div className="border-2 border-orange-400 rounded-xl p-4 bg-orange-50 flex flex-col gap-3">
                                    <h4 className="font-bold text-orange-700 text-sm">New {levelLabel}</h4>
                                    <input
                                        autoFocus type="text" placeholder={`${levelLabel} name...`}
                                        className="border border-orange-200 p-2 rounded-lg text-sm focus:ring-2 focus:ring-orange-400 outline-none bg-white"
                                        value={newItemName} onChange={e => setNewItemName(e.target.value)}
                                        onKeyDown={e => { if (e.key === 'Enter') handleCreate(); if (e.key === 'Escape') setIsAdding(false); }}
                                    />
                                    {currentLevel === 2 && (
                                        <div className="flex items-center border border-orange-200 p-2 rounded-lg bg-white">
                                            <span className="text-gray-400 text-xs border-r pr-2 mr-2">₹</span>
                                            <input type="number" value={newCoursePrice} onChange={e => setNewCoursePrice(Number(e.target.value))} className="flex-1 outline-none text-sm font-semibold" placeholder="Price" />
                                        </div>
                                    )}
                                    <div className="flex gap-2">
                                        <button onClick={handleCreate} className="flex-1 bg-orange-600 hover:bg-orange-700 text-white py-1.5 rounded-lg text-sm font-bold transition-colors">Create</button>
                                        <button onClick={() => { setIsAdding(false); setNewItemName(''); }} className="px-3 py-1.5 text-gray-500 hover:bg-gray-100 rounded-lg text-sm transition-colors">Cancel</button>
                                    </div>
                                </div>
                            )}
                        </div>
                    )}

                    {/* Tests inside folder */}
                    {isInsideFolder && (
                        <div className="space-y-2">
                            <h3 className="text-base font-bold text-gray-700 flex items-center gap-2">
                                <FileText className="w-4 h-4" /> Tests in this folder
                                <span className="ml-auto text-xs text-gray-400 font-normal">{localLinkedTests.length} linked</span>
                            </h3>
                            {localLinkedTests.length === 0 ? (
                                <div className="bg-amber-50 border border-amber-200 rounded-xl p-8 text-center">
                                    <div className="text-3xl mb-2">📭</div>
                                    <p className="font-bold text-amber-800 mb-1">No tests here yet!</p>
                                    <p className="text-sm text-amber-600">Students who purchase this course will see this folder as empty.<br />Add tests from the panel on the right →</p>
                                </div>
                            ) : localLinkedTests.map(lt => (
                                <div
                                    key={lt.linkId}
                                    draggable
                                    onDragStart={(e) => handleDragStart(e, lt.linkId)}
                                    onDragOver={(e) => handleDragOver(e, lt.linkId)}
                                    onDrop={(e) => handleDrop(e, lt.linkId)}
                                    onDragEnd={handleDragEnd}
                                    className={`bg-white border border-gray-100 rounded-xl p-3.5 flex items-center justify-between shadow-sm hover:shadow-md transition-all cursor-grab active:cursor-grabbing group ${dragOverItemId === lt.linkId ? 'border-orange-500 bg-orange-50/50 scale-[1.01]' : ''
                                        }`}
                                >
                                    <div className="flex items-center gap-3">
                                        <div className="text-gray-300 group-hover:text-gray-400 px-1 hover:text-orange-500">⋮⋮</div>
                                        <div className="w-8 h-8 bg-green-50 rounded-lg flex items-center justify-center">
                                            <FileText className="w-4 h-4 text-green-600" />
                                        </div>
                                        <div>
                                            <h4 className="font-semibold text-gray-800 text-sm">{lt.title}</h4>
                                            <span className="text-xs text-gray-400">{lt.category}</span>
                                        </div>
                                    </div>
                                    <div className="flex gap-2">
                                        <button onClick={async () => { try { const r = await api.get(`/tests/${lt.testId}`); setDraftToEdit(r.data); setActiveTab('scraper'); } catch { alert('Failed'); } }} className="text-blue-500 hover:bg-blue-50 px-2.5 py-1.5 rounded-lg text-xs font-bold transition-colors">Edit</button>
                                        <button onClick={async () => { if (!confirm(`Unlink "${lt.title}"?`)) return; try { await api.delete(`/courses/folders/${currentId}/tests/${lt.testId}`); fetchData(); } catch { alert('Failed'); } }} className="text-red-400 hover:bg-red-50 px-2.5 py-1.5 rounded-lg text-xs font-bold transition-colors">Unlink</button>
                                        <button onClick={async e => {
                                            e.stopPropagation();
                                            try {
                                                const res = await api.get(`/tests/${lt.testId}`);
                                                const exportData = res.data.sections && res.data.sections.length > 0 ? res.data.sections : [res.data];
                                                const dataStr = "data:text/json;charset=utf-8," + encodeURIComponent(JSON.stringify(exportData, null, 2));
                                                const a = document.createElement('a');
                                                a.href = dataStr;
                                                a.download = `${lt.title.replace(/\s+/g, '_')}_export.json`;
                                                document.body.appendChild(a);
                                                a.click();
                                                a.remove();
                                            } catch (e) {
                                                alert("Failed to download test.");
                                            }
                                        }} className="text-purple-600 hover:bg-purple-50 px-2.5 py-1.5 rounded-lg text-xs font-bold transition-colors">JSON</button>
                                    </div>
                                </div>
                            ))}
                        </div>
                    )}

                    {/* Empty state */}
                    {!isInsideFolder && localChildren.length === 0 && !isAdding && (
                        <div className="bg-gray-50 border-2 border-dashed border-gray-200 rounded-xl p-12 text-center">
                            <Folder className="w-12 h-12 text-gray-200 mx-auto mb-3" />
                            <p className="font-bold text-gray-400 mb-1">Nothing here yet</p>
                            <p className="text-sm text-gray-400 mb-4">Add a {levelLabel.toLowerCase()} to get started</p>
                            <button onClick={() => setIsAdding(true)} className="bg-orange-500 hover:bg-orange-600 text-white px-5 py-2 rounded-lg font-bold text-sm transition-colors">
                                + Create {levelLabel}
                            </button>
                        </div>
                    )}
                </div>

                {/* Published Tests Sidebar */}
                <div className="w-72 flex-shrink-0">
                    <div className="bg-white border border-gray-100 rounded-xl shadow-sm sticky top-8 overflow-hidden">
                        <div className="p-4 border-b border-gray-50 bg-gradient-to-br from-green-50 to-emerald-50">
                            <div className="flex items-center justify-between mb-1">
                                <h3 className="font-bold text-green-800 text-sm flex items-center gap-2">
                                    <FileText className="w-4 h-4" /> Published Tests
                                </h3>
                                <span className="text-xs font-bold text-green-600 bg-green-100 px-2 py-0.5 rounded-full">{availableTests.length} unlinked</span>
                            </div>
                            <p className="text-xs text-green-600">
                                {isInsideFolder ? '👆 Click "+ Add" to link a test into this folder' : '⬅️ Navigate into a folder first to add tests'}
                            </p>
                        </div>

                        {/* Nudge: urgency if many unlinked */}
                        {availableTests.length > 3 && (
                            <div className="px-4 py-2 bg-amber-50 border-b border-amber-100 flex items-center gap-2">
                                <Clock className="w-3.5 h-3.5 text-amber-500 flex-shrink-0" />
                                <p className="text-[11px] text-amber-700 font-semibold">{availableTests.length} tests waiting to be organized!</p>
                            </div>
                        )}

                        <div className="max-h-[60vh] overflow-y-auto divide-y divide-gray-50">
                            {availableTests.length === 0 ? (
                                <div className="p-6 text-center">
                                    <div className="text-2xl mb-2">{tests.length === 0 ? '📭' : '🎉'}</div>
                                    <p className="text-gray-400 text-xs">{tests.length === 0 ? 'No published tests yet' : 'All tests linked!'}</p>
                                </div>
                            ) : availableTests.map(t => (
                                <div key={t.id} className="px-3 py-2.5 hover:bg-gray-50 transition-colors flex items-center justify-between gap-2 group">
                                    <div className="flex-1 min-w-0">
                                        <h4 className="text-xs font-semibold text-gray-800 truncate" title={t.title}>{t.title}</h4>
                                        <span className="text-[10px] text-gray-400">{t.category}</span>
                                    </div>
                                    <div className="flex items-center gap-1 flex-shrink-0">
                                        <button onClick={async e => { e.stopPropagation(); if (!confirm(`Delete "${t.title}"?`)) return; try { await api.delete(`/tests/${t.id}`); fetchData(); } catch { alert('Failed'); } }} className="opacity-0 group-hover:opacity-100 p-1 text-red-400 hover:bg-red-50 rounded transition-all">
                                            <Trash2 className="w-3 h-3" />
                                        </button>
                                        <button onClick={async e => {
                                            e.stopPropagation();
                                            try {
                                                const res = await api.get(`/tests/${t.id}`);
                                                const exportData = res.data.sections && res.data.sections.length > 0 ? res.data.sections : [res.data];
                                                const dataStr = "data:text/json;charset=utf-8," + encodeURIComponent(JSON.stringify(exportData, null, 2));
                                                const a = document.createElement('a');
                                                a.href = dataStr;
                                                a.download = `${t.title.replace(/\s+/g, '_')}_export.json`;
                                                document.body.appendChild(a);
                                                a.click();
                                                a.remove();
                                            } catch (e) {
                                                alert("Failed to download test.");
                                            }
                                        }} className="opacity-0 group-hover:opacity-100 p-1 text-purple-600 hover:bg-purple-50 rounded transition-all" title="Download JSON">
                                            <Download className="w-3 h-3" />
                                        </button>
                                        {isInsideFolder && (
                                            <button onClick={() => handleLinkTest(t.id)} className="bg-green-500 hover:bg-green-600 text-white text-[10px] px-2.5 py-1 rounded-lg font-bold transition-colors whitespace-nowrap">
                                                + Add
                                            </button>
                                        )}
                                    </div>
                                </div>
                            ))}
                        </div>
                    </div>
                </div>
            </div>
        </div>
    );
};
