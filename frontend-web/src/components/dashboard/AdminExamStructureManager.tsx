import { useEffect, useState } from 'react';
import { Eye, EyeOff, IndianRupee, CalendarDays, ChevronDown, ChevronRight, Tag, Check } from 'lucide-react';
import { ExamStructureAPI } from '../../services/api';

type Stage = {
    id: string;
    name: string;
    slug: string;
    order: number;
    is_enabled: boolean;
    price_inr: number;
    validity_days: number;
};

type SubCategory = {
    id: string;
    name: string;
    slug: string;
    is_enabled: boolean;
    exam_stages: Stage[];
};

type Category = {
    id: string;
    name: string;
    is_enabled: boolean;
    subcategories: SubCategory[];
};

export const AdminExamStructureManager = () => {
    const [tree, setTree] = useState<Category[]>([]);
    const [loading, setLoading] = useState(true);
    const [expanded, setExpanded] = useState<Set<string>>(new Set());
    const [editingStage, setEditingStage] = useState<string | null>(null);
    const [editPrice, setEditPrice] = useState<string>('');
    const [editValidity, setEditValidity] = useState<string>('');
    const [saving, setSaving] = useState(false);

    const load = async () => {
        try {
            const res = await ExamStructureAPI.adminList();
            setTree(res.data);
        } catch (e) {
            console.error('Failed to load exam structure', e);
        } finally {
            setLoading(false);
        }
    };

    useEffect(() => {
        load();
    }, []);

    const toggle = (id: string) => {
        setExpanded(prev => {
            const next = new Set(prev);
            if (next.has(id)) next.delete(id); else next.add(id);
            return next;
        });
    };

    const flipCategory = async (cat: Category) => {
        try {
            await ExamStructureAPI.adminToggleCategoryVisibility(cat.id, !cat.is_enabled);
            load();
        } catch (e) { alert('Failed to toggle category'); }
    };

    const flipSubCategory = async (sub: SubCategory) => {
        try {
            await ExamStructureAPI.adminToggleSubCategoryVisibility(sub.id, !sub.is_enabled);
            load();
        } catch (e) { alert('Failed to toggle subcategory'); }
    };

    const flipStage = async (st: Stage) => {
        try {
            await ExamStructureAPI.adminToggleExamStageVisibility(st.id, !st.is_enabled);
            load();
        } catch (e) { alert('Failed to toggle stage'); }
    };

    const startEditPricing = (st: Stage) => {
        setEditingStage(st.id);
        setEditPrice(String(st.price_inr));
        setEditValidity(String(st.validity_days));
    };

    const savePricing = async (stageId: string) => {
        const price = parseInt(editPrice, 10);
        const validity = parseInt(editValidity, 10);
        if (Number.isNaN(price) || price < 0) { alert('Price must be a non-negative integer (₹).'); return; }
        if (Number.isNaN(validity) || validity < 1) { alert('Validity must be at least 1 day.'); return; }
        setSaving(true);
        try {
            await ExamStructureAPI.adminUpdateExamStagePricing(stageId, price, validity);
            setEditingStage(null);
            load();
        } catch (e: any) {
            alert(e?.response?.data?.detail || 'Failed to update pricing');
        } finally {
            setSaving(false);
        }
    };

    if (loading) {
        return <p className="text-gray-500">Loading exam structure…</p>;
    }

    return (
        <div className="space-y-6">
            <div className="bg-white dark:bg-gray-800 p-6 rounded-lg border border-gray-100 dark:border-gray-700">
                <h1 className="text-2xl font-bold text-gray-800 dark:text-white">Exam Structure &amp; Pricing</h1>
                <p className="text-sm text-gray-500 dark:text-gray-400 mt-1">
                    Control visibility (student sees only enabled rows) and set price per exam stage.
                    PYQ papers stay free regardless of stage price — only MOCK papers are gated.
                </p>
            </div>

            <div className="bg-white dark:bg-gray-800 rounded-lg border border-gray-100 dark:border-gray-700 divide-y divide-gray-100 dark:divide-gray-700">
                {tree.map(cat => {
                    const catOpen = expanded.has(cat.id);
                    return (
                        <div key={cat.id}>
                            <div className="flex items-center gap-3 px-4 py-3">
                                <button onClick={() => toggle(cat.id)} className="text-gray-400 hover:text-gray-700">
                                    {catOpen ? <ChevronDown className="w-4 h-4" /> : <ChevronRight className="w-4 h-4" />}
                                </button>
                                <span className="flex-1 font-semibold text-gray-800 dark:text-white">{cat.name}</span>
                                <span className="text-xs text-gray-400">{cat.subcategories.length} exams</span>
                                <button
                                    onClick={() => flipCategory(cat)}
                                    className={`flex items-center gap-1 px-3 py-1 rounded-full text-xs font-semibold ${cat.is_enabled ? 'bg-green-50 text-green-700 border border-green-200' : 'bg-gray-100 text-gray-500 border border-gray-200'}`}
                                    title={cat.is_enabled ? 'Click to hide' : 'Click to show'}
                                >
                                    {cat.is_enabled ? <Eye className="w-3 h-3" /> : <EyeOff className="w-3 h-3" />}
                                    {cat.is_enabled ? 'Visible' : 'Hidden'}
                                </button>
                            </div>
                            {catOpen && (
                                <div className="bg-gray-50 dark:bg-gray-900/40">
                                    {cat.subcategories.map(sub => {
                                        const subOpen = expanded.has(sub.id);
                                        return (
                                            <div key={sub.id} className="border-t border-gray-100 dark:border-gray-700">
                                                <div className="flex items-center gap-3 px-4 py-3 pl-10">
                                                    <button onClick={() => toggle(sub.id)} className="text-gray-400 hover:text-gray-700">
                                                        {subOpen ? <ChevronDown className="w-4 h-4" /> : <ChevronRight className="w-4 h-4" />}
                                                    </button>
                                                    <span className="flex-1 text-gray-800 dark:text-gray-100">{sub.name}</span>
                                                    <span className="text-xs text-gray-400">{sub.exam_stages.length} stages</span>
                                                    <button
                                                        onClick={() => flipSubCategory(sub)}
                                                        className={`flex items-center gap-1 px-3 py-1 rounded-full text-xs font-semibold ${sub.is_enabled ? 'bg-green-50 text-green-700 border border-green-200' : 'bg-gray-100 text-gray-500 border border-gray-200'}`}
                                                    >
                                                        {sub.is_enabled ? <Eye className="w-3 h-3" /> : <EyeOff className="w-3 h-3" />}
                                                        {sub.is_enabled ? 'Visible' : 'Hidden'}
                                                    </button>
                                                </div>
                                                {subOpen && (
                                                    <div className="bg-white dark:bg-gray-800">
                                                        {sub.exam_stages.length === 0 && (
                                                            <p className="px-4 pl-20 py-3 text-xs text-gray-400">No stages under this exam yet.</p>
                                                        )}
                                                        {sub.exam_stages.map(st => {
                                                            const isEditing = editingStage === st.id;
                                                            const isFree = st.price_inr === 0;
                                                            return (
                                                                <div key={st.id} className="border-t border-gray-100 dark:border-gray-700 px-4 pl-20 py-3 flex items-center gap-3 flex-wrap">
                                                                    <span className="font-medium text-gray-700 dark:text-gray-100 min-w-[8rem]">{st.name}</span>
                                                                    {!isEditing && (
                                                                        <>
                                                                            <span className={`inline-flex items-center gap-1 px-2.5 py-1 rounded-full text-xs font-semibold ${isFree ? 'bg-blue-50 text-blue-700 border border-blue-200' : 'bg-orange-50 text-orange-700 border border-orange-200'}`}>
                                                                                <IndianRupee className="w-3 h-3" />
                                                                                {isFree ? 'Free' : `₹${st.price_inr}`}
                                                                            </span>
                                                                            <span className="inline-flex items-center gap-1 px-2.5 py-1 rounded-full text-xs font-semibold bg-gray-100 text-gray-700 border border-gray-200">
                                                                                <CalendarDays className="w-3 h-3" />
                                                                                {st.validity_days}d validity
                                                                            </span>
                                                                        </>
                                                                    )}
                                                                    {isEditing && (
                                                                        <>
                                                                            <div className="flex items-center gap-1">
                                                                                <IndianRupee className="w-4 h-4 text-gray-400" />
                                                                                <input
                                                                                    type="number"
                                                                                    min={0}
                                                                                    value={editPrice}
                                                                                    onChange={e => setEditPrice(e.target.value)}
                                                                                    className="w-24 px-2 py-1 border border-gray-300 rounded text-sm"
                                                                                    placeholder="Price"
                                                                                />
                                                                            </div>
                                                                            <div className="flex items-center gap-1">
                                                                                <CalendarDays className="w-4 h-4 text-gray-400" />
                                                                                <input
                                                                                    type="number"
                                                                                    min={1}
                                                                                    value={editValidity}
                                                                                    onChange={e => setEditValidity(e.target.value)}
                                                                                    className="w-24 px-2 py-1 border border-gray-300 rounded text-sm"
                                                                                    placeholder="Days"
                                                                                />
                                                                                <span className="text-xs text-gray-400">days</span>
                                                                            </div>
                                                                        </>
                                                                    )}
                                                                    <div className="ml-auto flex gap-2">
                                                                        {!isEditing ? (
                                                                            <>
                                                                                <button
                                                                                    onClick={() => startEditPricing(st)}
                                                                                    className="flex items-center gap-1 px-3 py-1 rounded text-xs font-semibold bg-orange-50 text-orange-700 border border-orange-200 hover:bg-orange-100"
                                                                                >
                                                                                    <Tag className="w-3 h-3" /> Set Price
                                                                                </button>
                                                                                <button
                                                                                    onClick={() => flipStage(st)}
                                                                                    className={`flex items-center gap-1 px-3 py-1 rounded-full text-xs font-semibold ${st.is_enabled ? 'bg-green-50 text-green-700 border border-green-200' : 'bg-gray-100 text-gray-500 border border-gray-200'}`}
                                                                                >
                                                                                    {st.is_enabled ? <Eye className="w-3 h-3" /> : <EyeOff className="w-3 h-3" />}
                                                                                    {st.is_enabled ? 'Visible' : 'Hidden'}
                                                                                </button>
                                                                            </>
                                                                        ) : (
                                                                            <>
                                                                                <button
                                                                                    disabled={saving}
                                                                                    onClick={() => savePricing(st.id)}
                                                                                    className="flex items-center gap-1 px-3 py-1 rounded text-xs font-semibold bg-green-600 text-white hover:bg-green-700 disabled:opacity-50"
                                                                                >
                                                                                    <Check className="w-3 h-3" /> {saving ? 'Saving…' : 'Save'}
                                                                                </button>
                                                                                <button
                                                                                    onClick={() => setEditingStage(null)}
                                                                                    className="px-3 py-1 rounded text-xs font-semibold bg-gray-100 text-gray-600 hover:bg-gray-200"
                                                                                >
                                                                                    Cancel
                                                                                </button>
                                                                            </>
                                                                        )}
                                                                    </div>
                                                                </div>
                                                            );
                                                        })}
                                                    </div>
                                                )}
                                            </div>
                                        );
                                    })}
                                    {cat.subcategories.length === 0 && (
                                        <p className="px-4 pl-10 py-3 text-xs text-gray-400">No exams under this body yet.</p>
                                    )}
                                </div>
                            )}
                        </div>
                    );
                })}
                {tree.length === 0 && (
                    <p className="px-4 py-6 text-sm text-gray-400">No categories found. Seed the exam structure first.</p>
                )}
            </div>
        </div>
    );
};
