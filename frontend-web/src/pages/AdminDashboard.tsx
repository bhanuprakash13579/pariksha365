import { useState, useEffect } from 'react';
import { FileText, Activity, FilePlus, Folder, Trash2, Edit, BarChart2, Download, HelpCircle, Layers, Menu, X } from 'lucide-react';
import { api, UserAPI } from '../services/api';
import { ScrapeReviewWorkspace } from './ScrapeReviewWorkspace';
import { FileExplorerCourseManager } from './FileExplorerCourseManager';
import { AdminAnalytics } from '../components/dashboard/AdminAnalytics';
import { AdminQuizPoolManager } from '../components/dashboard/AdminQuizPoolManager';
import { AdminExamStructureManager } from '../components/dashboard/AdminExamStructureManager';
import { useNavigate } from 'react-router-dom';

export const AdminDashboard = () => {
    const navigate = useNavigate();
    const [courses, setCourses] = useState<any[]>([]);
    const [tests, setTests] = useState<any[]>([]);
    const [drafts, setDrafts] = useState<any[]>([]);
    const [dbCategories, setDbCategories] = useState<any[]>([]);
    const [activeTab, setActiveTab] = useState('courses');
    const [draftToEdit, setDraftToEdit] = useState<any>(null);
    const [sidebarOpen, setSidebarOpen] = useState(false);

    const [isAuthorized, setIsAuthorized] = useState(false);

    // Close mobile drawer whenever we switch tabs (prevents the drawer from
    // staying open after the user picks a destination).
    const handleTabSelect = (tab: string) => {
        setActiveTab(tab);
        setSidebarOpen(false);
    };

    useEffect(() => {
        const checkAuth = async () => {
            try {
                const res = await UserAPI.getMe();
                if (res.data.role?.name?.toLowerCase() === 'admin') {
                    setIsAuthorized(true);
                    fetchData();
                } else {
                    alert("Access Denied. Admin Privileges Required.");
                    navigate('/dashboard');
                }
            } catch (e) {
                navigate('/auth');
            }
        };
        checkAuth();
    }, [navigate]);

    const fetchData = async () => {
        try {
            const courseRes = await api.get('/courses');
            setCourses(courseRes.data);
            const testRes = await api.get('/tests');
            setTests(testRes.data);
            const draftRes = await api.get('/tests?is_published=false');
            setDrafts(draftRes.data);
            // Use the admin-dedicated endpoint so disabled categories remain
            // visible in the admin panel. The public /categories endpoint
            // filters is_enabled=false rows, which once made the admin UI
            // appear broken after a migration (see feedback_migration_preserve_visibility).
            const catRes = await api.get('/categories/admin');
            setDbCategories(catRes.data);
        } catch (e) {
            console.error("Failed to fetch data", e);
            // Fallback to the public endpoint so a 404/older-backend deploy
            // doesn't blank the dashboard. Better to show enabled categories
            // than nothing at all.
            try {
                const catRes = await api.get('/categories');
                setDbCategories(catRes.data);
            } catch (fallbackErr) {
                console.error("Fallback /categories also failed", fallbackErr);
            }
        }
    };


    if (!isAuthorized) {
        return (
            <div className="flex bg-gray-100 h-screen items-center justify-center">
                <p className="text-gray-500 font-medium">Verifying Administrator Privileges...</p>
            </div>
        );
    }

    const NAV_BUTTONS: { id: string; label: string; icon: React.ReactNode; onSelect?: () => void }[] = [
        { id: 'overview', label: 'Dashboard Overview', icon: <Activity className="w-5 h-5 mr-3" /> },
        { id: 'analytics', label: 'Intelligence Hub', icon: <BarChart2 className="w-5 h-5 mr-3" /> },
        { id: 'courses', label: 'Course Manager', icon: <FileText className="w-5 h-5 mr-3" /> },
        { id: 'scraper', label: 'PDF Scraper Hub', icon: <FilePlus className="w-5 h-5 mr-3" />, onSelect: () => setDraftToEdit(null) },
        { id: 'drafts', label: 'Drafts Vault', icon: <Folder className="w-5 h-5 mr-3" /> },
        { id: 'quizpool', label: 'Quiz Pool', icon: <HelpCircle className="w-5 h-5 mr-3" /> },
        { id: 'exam-structure', label: 'Exam Structure', icon: <Layers className="w-5 h-5 mr-3" /> },
    ];

    const navLabel = NAV_BUTTONS.find(n => n.id === activeTab)?.label || 'Admin';

    const SidebarContents = (
        <>
            <div className="p-4 border-b dark:border-gray-700 flex items-center justify-between">
                <h2 className="text-2xl font-bold text-orange-600">AdminPanel</h2>
                <button
                    onClick={() => setSidebarOpen(false)}
                    className="md:hidden p-1.5 rounded-lg text-gray-500 hover:bg-gray-100 dark:hover:bg-gray-700"
                    aria-label="Close navigation"
                >
                    <X className="w-5 h-5" />
                </button>
            </div>
            <nav className="flex-1 mt-4 overflow-y-auto">
                {NAV_BUTTONS.map(item => (
                    <button
                        key={item.id}
                        onClick={() => { item.onSelect?.(); handleTabSelect(item.id); }}
                        className={`w-full flex items-center px-4 py-3 text-left ${activeTab === item.id ? 'text-orange-600 bg-orange-50 dark:bg-gray-700' : 'text-gray-600 dark:text-gray-400 hover:bg-gray-50 dark:hover:bg-gray-700'}`}
                    >
                        {item.icon} {item.label}
                    </button>
                ))}
            </nav>
        </>
    );

    return (
        <div className="flex h-screen bg-gray-100 dark:bg-gray-900 overflow-hidden">
            {/* Desktop Sidebar */}
            <aside className="w-64 bg-white dark:bg-gray-800 shadow-md hidden md:flex flex-col">
                {SidebarContents}
            </aside>

            {/* Mobile Drawer + Backdrop */}
            {sidebarOpen && (
                <div
                    className="md:hidden fixed inset-0 bg-gray-900/50 backdrop-blur-sm z-40"
                    onClick={() => setSidebarOpen(false)}
                    aria-hidden="true"
                />
            )}
            <aside
                className={`md:hidden fixed inset-y-0 left-0 w-72 max-w-[85vw] bg-white dark:bg-gray-800 shadow-2xl flex flex-col z-50 transform transition-transform duration-300 ease-out ${sidebarOpen ? 'translate-x-0' : '-translate-x-full'}`}
            >
                {SidebarContents}
            </aside>

            {/* Main Content */}
            <div className="flex-1 flex flex-col min-w-0">
                {/* Mobile Top Bar */}
                <div className="md:hidden flex items-center justify-between bg-white dark:bg-gray-800 border-b dark:border-gray-700 px-4 py-3 shadow-sm flex-shrink-0">
                    <button
                        onClick={() => setSidebarOpen(true)}
                        className="p-2 -ml-2 rounded-lg text-gray-600 dark:text-gray-300 hover:bg-gray-100 dark:hover:bg-gray-700"
                        aria-label="Open navigation"
                    >
                        <Menu className="w-5 h-5" />
                    </button>
                    <span className="font-bold text-gray-800 dark:text-white truncate">{navLabel}</span>
                    <span className="text-xs font-bold text-orange-600">Admin</span>
                </div>

                <main className="flex-1 p-4 sm:p-6 md:p-8 overflow-y-auto overflow-x-hidden w-full">
                {activeTab === 'overview' && (
                    <>
                        <h1 className="text-2xl sm:text-3xl font-semibold text-gray-800 dark:text-white mb-6">Overview</h1>
                        <div className="grid grid-cols-2 md:grid-cols-4 gap-4 sm:gap-6 mb-8">
                            <div className="bg-white dark:bg-gray-800 p-4 sm:p-6 rounded-lg shadow-sm border border-gray-100 dark:border-gray-700">
                                <h3 className="text-gray-500 text-xs sm:text-sm font-medium">Active Courses</h3>
                                <p className="text-2xl sm:text-3xl font-bold text-gray-800 dark:text-white mt-2">{courses.length}</p>
                            </div>
                            <div className="bg-white dark:bg-gray-800 p-4 sm:p-6 rounded-lg shadow-sm border border-gray-100 dark:border-gray-700">
                                <h3 className="text-gray-500 text-xs sm:text-sm font-medium">Published Tests</h3>
                                <p className="text-2xl sm:text-3xl font-bold text-gray-800 dark:text-white mt-2">{tests.length}</p>
                            </div>
                        </div>
                        <p className="text-sm text-gray-400">👉 Head to <button className="text-orange-500 font-semibold" onClick={() => handleTabSelect('analytics')}>Intelligence Hub</button> for deep analytics.</p>
                    </>
                )}

                {activeTab === 'analytics' && <AdminAnalytics />}

                {activeTab === 'scraper' && (
                    <ScrapeReviewWorkspace
                        draftToEdit={draftToEdit}
                        onClearDraft={() => setDraftToEdit(null)}
                        refreshDrafts={fetchData}
                    />
                )}

                {activeTab === 'drafts' && (
                    <div className="space-y-6">
                        <div className="flex flex-col sm:flex-row sm:justify-between sm:items-center gap-3 bg-yellow-50 dark:bg-gray-800 p-4 sm:p-6 rounded-lg border border-yellow-200 dark:border-gray-700">
                            <div>
                                <h1 className="text-2xl sm:text-3xl font-semibold text-gray-800 dark:text-white">Drafts Vault</h1>
                                <p className="text-sm text-gray-600 dark:text-gray-400 mt-1">Manage mock tests that have been saved but not yet published to the main Course Manager.</p>
                            </div>
                            <div className="bg-yellow-100 text-yellow-800 px-4 py-2 rounded-full font-bold self-start sm:self-auto">
                                {drafts.length} Drafts
                            </div>
                        </div>

                        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
                            {drafts.length === 0 ? (
                                <div className="p-8 text-center bg-white dark:bg-gray-800 rounded-lg shadow-sm border border-gray-100 md:col-span-2 lg:col-span-3">
                                    <p className="text-gray-400">No drafts currently saved. Go to the <span className="text-orange-500 font-semibold cursor-pointer" onClick={() => setActiveTab('scraper')}>Scraper Hub</span> to create one!</p>
                                </div>
                            ) : drafts.map(draft => (
                                <div key={draft.id} className="bg-white dark:bg-gray-800 p-6 rounded-lg shadow-sm border-t-4 border-yellow-400 flex flex-col justify-between">
                                    <div>
                                        <h3 className="font-bold text-lg text-gray-800 dark:text-white mb-1 line-clamp-2" title={draft.title}>{draft.title}</h3>
                                        <span className="inline-block bg-gray-100 text-gray-600 text-xs px-2 py-1 rounded-full mb-4 font-medium truncate max-w-full">
                                            {draft.category}
                                        </span>
                                    </div>
                                    <div className="flex items-center space-x-3 mt-4 pt-4 border-t border-gray-50 dark:border-gray-700">
                                        <button onClick={async () => {
                                            if (confirm(`Are you sure you want to publish "${draft.title}"?\nIt will become available to link in courses immediately.`)) {
                                                try {
                                                    await api.patch(`/tests/${draft.id}/publish`);
                                                    fetchData();
                                                    alert("Draft successully published!");
                                                } catch (e) {
                                                    alert("Failed to publish draft.");
                                                }
                                            }
                                        }} className="flex-1 bg-green-500 hover:bg-green-600 text-white flex justify-center items-center py-2.5 rounded text-sm font-semibold transition-colors">
                                            Publish Now
                                        </button>
                                        <button onClick={async () => {
                                            try {
                                                const res = await api.get(`/tests/${draft.id}`);
                                                setDraftToEdit(res.data);
                                                setActiveTab('scraper');
                                            } catch (e) {
                                                alert("Failed to fetch full draft details.");
                                            }
                                        }} className="p-2.5 bg-blue-50 hover:bg-blue-100 text-blue-500 rounded transition-colors" title="Edit Draft">
                                            <Edit className="w-5 h-5" />
                                        </button>
                                        <button onClick={async () => {
                                            if (confirm(`Permanently delete draft "${draft.title}"?\nThis cannot be undone.`)) {
                                                try {
                                                    await api.delete(`/tests/${draft.id}`);
                                                    fetchData();
                                                } catch (e) {
                                                    alert("Failed to delete draft.");
                                                }
                                            }
                                        }} className="p-2.5 bg-red-50 hover:bg-red-100 text-red-500 rounded transition-colors" title="Delete Draft">
                                            <Trash2 className="w-5 h-5" />
                                        </button>
                                        <button onClick={async () => {
                                            try {
                                                const res = await api.get(`/tests/${draft.id}`);
                                                const exportData = res.data.sections && res.data.sections.length > 0 ? res.data.sections : [res.data];
                                                const dataStr = "data:text/json;charset=utf-8," + encodeURIComponent(JSON.stringify(exportData, null, 2));
                                                const a = document.createElement('a');
                                                a.href = dataStr;
                                                a.download = `${draft.title.replace(/\s+/g, '_')}_export.json`;
                                                document.body.appendChild(a);
                                                a.click();
                                                a.remove();
                                            } catch (e) {
                                                alert("Failed to download test.");
                                            }
                                        }} className="p-2.5 bg-purple-50 hover:bg-purple-100 text-purple-600 rounded transition-colors" title="Download JSON">
                                            <Download className="w-5 h-5" />
                                        </button>
                                    </div>
                                </div>
                            ))}
                        </div>
                    </div>
                )}

                {activeTab === 'courses' && (() => {
                    // --- File Explorer State ---
                    // breadcrumb: [{label, id, level}]
                    // level 0 = Categories, 1 = SubCategories, 2 = Courses, 3 = Folders, 4 = Tests inside folder

                    // We use a simple approach: store navigation in component-level state
                    // Since hooks can't be conditional, we manage explorer state via the existing state variables
                    // explorerPath is stored as JSON string in a state we'll add
                    return <FileExplorerCourseManager
                        dbCategories={dbCategories}
                        courses={courses}
                        tests={tests}
                        api={api}
                        fetchData={fetchData}
                        setDraftToEdit={setDraftToEdit}
                        setActiveTab={setActiveTab}
                    />;
                })()}

                {activeTab === 'quizpool' && <AdminQuizPoolManager />}

                {activeTab === 'exam-structure' && <AdminExamStructureManager />}
                </main>
            </div>
        </div>
    );
};

