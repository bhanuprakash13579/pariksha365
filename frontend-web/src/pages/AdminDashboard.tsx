import { useState, useEffect } from 'react';
import { FileText, Activity, FilePlus, Folder, Trash2, Edit, BarChart2, Download, HelpCircle } from 'lucide-react';
import { api, UserAPI } from '../services/api';
import { ScrapeReviewWorkspace } from './ScrapeReviewWorkspace';
import { FileExplorerCourseManager } from './FileExplorerCourseManager';
import { AdminAnalytics } from '../components/dashboard/AdminAnalytics';
import { AdminQuizPoolManager } from '../components/dashboard/AdminQuizPoolManager';
import { useNavigate } from 'react-router-dom';

export const AdminDashboard = () => {
    const navigate = useNavigate();
    const [courses, setCourses] = useState<any[]>([]);
    const [tests, setTests] = useState<any[]>([]);
    const [drafts, setDrafts] = useState<any[]>([]);
    const [dbCategories, setDbCategories] = useState<any[]>([]);
    const [activeTab, setActiveTab] = useState('courses');
    const [draftToEdit, setDraftToEdit] = useState<any>(null);

    const [isAuthorized, setIsAuthorized] = useState(false);

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
            const catRes = await api.get('/categories');
            setDbCategories(catRes.data);
        } catch (e) {
            console.error("Failed to fetch data", e);
        }
    };


    if (!isAuthorized) {
        return (
            <div className="flex bg-gray-100 h-screen items-center justify-center">
                <p className="text-gray-500 font-medium">Verifying Administrator Privileges...</p>
            </div>
        );
    }

    return (
        <div className="flex h-screen bg-gray-100 dark:bg-gray-900">
            {/* Sidebar */}
            <aside className="w-64 bg-white dark:bg-gray-800 shadow-md flex flex-col">
                <div className="p-4 border-b dark:border-gray-700">
                    <h2 className="text-2xl font-bold text-orange-600">AdminPanel</h2>
                </div>
                <nav className="flex-1 mt-4">
                    <button onClick={() => setActiveTab('overview')} className={`w-full flex items-center px-4 py-3 text-left ${activeTab === 'overview' ? 'text-orange-600 bg-orange-50 dark:bg-gray-700' : 'text-gray-600 dark:text-gray-400 hover:bg-gray-50 dark:hover:bg-gray-700'}`}>
                        <Activity className="w-5 h-5 mr-3" /> Dashboard Overview
                    </button>
                    <button onClick={() => setActiveTab('analytics')} className={`w-full flex items-center px-4 py-3 text-left ${activeTab === 'analytics' ? 'text-orange-600 bg-orange-50 dark:bg-gray-700' : 'text-gray-600 dark:text-gray-400 hover:bg-gray-50 dark:hover:bg-gray-700'}`}>
                        <BarChart2 className="w-5 h-5 mr-3" /> Intelligence Hub
                    </button>
                    <button onClick={() => setActiveTab('courses')} className={`w-full flex items-center px-4 py-3 text-left ${activeTab === 'courses' ? 'text-orange-600 bg-orange-50 dark:bg-gray-700' : 'text-gray-600 dark:text-gray-400 hover:bg-gray-50 dark:hover:bg-gray-700'}`}>
                        <FileText className="w-5 h-5 mr-3" /> Course Manager
                    </button>
                    <button onClick={() => { setActiveTab('scraper'); setDraftToEdit(null); }} className={`w-full flex items-center px-4 py-3 text-left ${activeTab === 'scraper' ? 'text-orange-600 bg-orange-50 dark:bg-gray-700' : 'text-gray-600 dark:text-gray-400 hover:bg-gray-50 dark:hover:bg-gray-700'}`}>
                        <FilePlus className="w-5 h-5 mr-3" /> PDF Scraper Hub
                    </button>
                    <button onClick={() => setActiveTab('drafts')} className={`w-full flex items-center px-4 py-3 text-left ${activeTab === 'drafts' ? 'text-orange-600 bg-orange-50 dark:bg-gray-700' : 'text-gray-600 dark:text-gray-400 hover:bg-gray-50 dark:hover:bg-gray-700'}`}>
                        <Folder className="w-5 h-5 mr-3" /> Drafts Vault
                    </button>
                    <button onClick={() => setActiveTab('quizpool')} className={`w-full flex items-center px-4 py-3 text-left ${activeTab === 'quizpool' ? 'text-orange-600 bg-orange-50 dark:bg-gray-700' : 'text-gray-600 dark:text-gray-400 hover:bg-gray-50 dark:hover:bg-gray-700'}`}>
                        <HelpCircle className="w-5 h-5 mr-3" /> Quiz Pool
                    </button>
                </nav>
            </aside>

            {/* Main Content */}
            <main className="flex-1 p-8 overflow-y-auto w-full">
                {activeTab === 'overview' && (
                    <>
                        <h1 className="text-3xl font-semibold text-gray-800 dark:text-white mb-6">Overview</h1>
                        <div className="grid grid-cols-1 md:grid-cols-4 gap-6 mb-8">
                            <div className="bg-white dark:bg-gray-800 p-6 rounded-lg shadow-sm border border-gray-100 dark:border-gray-700">
                                <h3 className="text-gray-500 text-sm font-medium">Active Courses</h3>
                                <p className="text-3xl font-bold text-gray-800 dark:text-white mt-2">{courses.length}</p>
                            </div>
                            <div className="bg-white dark:bg-gray-800 p-6 rounded-lg shadow-sm border border-gray-100 dark:border-gray-700">
                                <h3 className="text-gray-500 text-sm font-medium">Published Tests</h3>
                                <p className="text-3xl font-bold text-gray-800 dark:text-white mt-2">{tests.length}</p>
                            </div>
                        </div>
                        <p className="text-sm text-gray-400">👉 Head to <button className="text-orange-500 font-semibold" onClick={() => setActiveTab('analytics')}>Intelligence Hub</button> for deep analytics.</p>
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
                        <div className="flex justify-between items-center bg-yellow-50 dark:bg-gray-800 p-6 rounded-lg border border-yellow-200 dark:border-gray-700">
                            <div>
                                <h1 className="text-3xl font-semibold text-gray-800 dark:text-white">Drafts Vault</h1>
                                <p className="text-gray-600 dark:text-gray-400 mt-1">Manage mock tests that have been saved but not yet published to the main Course Manager.</p>
                            </div>
                            <div className="bg-yellow-100 text-yellow-800 px-4 py-2 rounded-full font-bold">
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
            </main>
        </div>
    );
};

