import React, { useState, useEffect } from 'react';
import { Settings, Users, FileText, Activity, Plus, Folder, Link as LinkIcon } from 'lucide-react';
import { api } from '../services/api';

export const AdminDashboard = () => {
    const [courses, setCourses] = useState<any[]>([]);
    const [tests, setTests] = useState<any[]>([]);
    const [activeTab, setActiveTab] = useState('courses');

    // Forms state
    const [newCategory, setNewCategory] = useState({ name: '', image_url: '' });
    const [newCourse, setNewCourse] = useState({ title: '', description: '', price: 0, category: '' });
    const [newFolder, setNewFolder] = useState({ course_id: '', title: '', is_free: false });
    const [newLink, setNewLink] = useState({ folder_id: '', test_id: '' });

    const fetchData = async () => {
        try {
            const courseRes = await api.get('/courses');
            setCourses(courseRes.data);
            const testRes = await api.get('/tests');
            setTests(testRes.data);
        } catch (e) {
            console.error("Failed to fetch data", e);
        }
    };

    useEffect(() => {
        fetchData();
    }, []);

    const handleCreateCourse = async (e: React.FormEvent) => {
        e.preventDefault();
        try {
            await api.post('/courses', { ...newCourse, is_published: true });
            setNewCourse({ title: '', description: '', price: 0, category: '' });
            fetchData();
            alert('Course created successfully!');
        } catch (err) { alert('Failed to create course'); }
    };

    const handleCreateCategory = async (e: React.FormEvent) => {
        e.preventDefault();
        try {
            await api.post('/categories', newCategory);
            setNewCategory({ name: '', image_url: '' });
            fetchData();
            alert('Category created successfully!');
        } catch (err) { alert('Failed to create category'); }
    };

    const handleCreateFolder = async (e: React.FormEvent) => {
        e.preventDefault();
        try {
            await api.post(`/courses/${newFolder.course_id}/folders`, { title: newFolder.title, is_free: newFolder.is_free });
            setNewFolder({ course_id: '', title: '', is_free: false });
            fetchData();
            alert('Folder created successfully!');
        } catch (err) { alert('Failed to create folder'); }
    };

    const handleLinkTest = async (e: React.FormEvent) => {
        e.preventDefault();
        try {
            await api.post(`/courses/folders/${newLink.folder_id}/tests`, { test_id: newLink.test_id });
            setNewLink({ folder_id: '', test_id: '' });
            fetchData();
            alert('Test linked successfully!');
        } catch (err) { alert('Failed to link test'); }
    };

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
                    <button onClick={() => setActiveTab('courses')} className={`w-full flex items-center px-4 py-3 text-left ${activeTab === 'courses' ? 'text-orange-600 bg-orange-50 dark:bg-gray-700' : 'text-gray-600 dark:text-gray-400 hover:bg-gray-50 dark:hover:bg-gray-700'}`}>
                        <FileText className="w-5 h-5 mr-3" /> Course Manager
                    </button>
                </nav>
            </aside>

            {/* Main Content */}
            <main className="flex-1 p-8 overflow-y-auto">
                {activeTab === 'overview' && (
                    <>
                        <h1 className="text-3xl font-semibold text-gray-800 dark:text-white mb-6">Overview</h1>
                        <div className="grid grid-cols-1 md:grid-cols-4 gap-6 mb-8">
                            <div className="bg-white dark:bg-gray-800 p-6 rounded-lg shadow-sm border border-gray-100 dark:border-gray-700">
                                <h3 className="text-gray-500 text-sm font-medium">Active Courses</h3>
                                <p className="text-3xl font-bold text-gray-800 dark:text-white mt-2">{courses.length}</p>
                            </div>
                            <div className="bg-white dark:bg-gray-800 p-6 rounded-lg shadow-sm border border-gray-100 dark:border-gray-700">
                                <h3 className="text-gray-500 text-sm font-medium">Standalone Tests</h3>
                                <p className="text-3xl font-bold text-gray-800 dark:text-white mt-2">{tests.length}</p>
                            </div>
                        </div>
                    </>
                )}

                {activeTab === 'courses' && (
                    <div className="space-y-8">
                        <div className="flex justify-between items-center">
                            <h1 className="text-3xl font-semibold text-gray-800 dark:text-white">Course & Content Manager</h1>
                        </div>

                        {/* Create Category Form */}
                        <div className="bg-white dark:bg-gray-800 p-6 rounded-lg shadow-sm border border-gray-100 dark:border-gray-700">
                            <h2 className="text-xl font-bold mb-4 flex items-center"><Plus className="mr-2" /> Create New Exam Category</h2>
                            <form onSubmit={handleCreateCategory} className="grid grid-cols-2 gap-4">
                                <input type="text" placeholder="Category Name (e.g. UPSC)" className="border p-2 rounded" value={newCategory.name} onChange={e => setNewCategory({ ...newCategory, name: e.target.value })} required />
                                <input type="text" placeholder="Custom Image URL (Optional)" className="border p-2 rounded" value={newCategory.image_url} onChange={e => setNewCategory({ ...newCategory, image_url: e.target.value })} />
                                <button type="submit" className="col-span-2 bg-purple-600 text-white py-2 rounded font-bold hover:bg-purple-700">Create Category</button>
                            </form>
                        </div>

                        {/* Create Course Form */}
                        <div className="bg-white dark:bg-gray-800 p-6 rounded-lg shadow-sm border border-gray-100 dark:border-gray-700">
                            <h2 className="text-xl font-bold mb-4 flex items-center"><Plus className="mr-2" /> Create New Course (Pack)</h2>
                            <form onSubmit={handleCreateCourse} className="grid grid-cols-2 gap-4">
                                <input type="text" placeholder="Course Title (e.g. SSC CGL Master Pack)" className="border p-2 rounded" value={newCourse.title} onChange={e => setNewCourse({ ...newCourse, title: e.target.value })} required />
                                <input type="text" placeholder="Category (e.g. SSC)" className="border p-2 rounded" value={newCourse.category} onChange={e => setNewCourse({ ...newCourse, category: e.target.value })} />
                                <input type="number" placeholder="Price (₹)" className="border p-2 rounded" value={newCourse.price} onChange={e => setNewCourse({ ...newCourse, price: Number(e.target.value) })} required />
                                <input type="text" placeholder="Short Description" className="border p-2 rounded" value={newCourse.description} onChange={e => setNewCourse({ ...newCourse, description: e.target.value })} />
                                <button type="submit" className="col-span-2 bg-orange-600 text-white py-2 rounded font-bold hover:bg-orange-700">Create Course</button>
                            </form>
                        </div>

                        {/* Create Folder Form */}
                        <div className="bg-white dark:bg-gray-800 p-6 rounded-lg shadow-sm border border-gray-100 dark:border-gray-700">
                            <h2 className="text-xl font-bold mb-4 flex items-center"><Folder className="mr-2" /> Add Segment/Folder to Course</h2>
                            <form onSubmit={handleCreateFolder} className="grid grid-cols-2 gap-4">
                                <select className="border p-2 rounded" value={newFolder.course_id} onChange={e => setNewFolder({ ...newFolder, course_id: e.target.value })} required>
                                    <option value="">Select Target Course</option>
                                    {courses.map(c => <option key={c.id} value={c.id}>{c.title}</option>)}
                                </select>
                                <input type="text" placeholder="Folder Name (e.g. Previous Year Papers)" className="border p-2 rounded" value={newFolder.title} onChange={e => setNewFolder({ ...newFolder, title: e.target.value })} required />
                                <label className="flex items-center space-x-2">
                                    <input type="checkbox" checked={newFolder.is_free} onChange={e => setNewFolder({ ...newFolder, is_free: e.target.checked })} />
                                    <span>Make all tests in this folder completely FREE</span>
                                </label>
                                <button type="submit" className="col-span-2 bg-blue-600 text-white py-2 rounded font-bold hover:bg-blue-700">Create Segment Folder</button>
                            </form>
                        </div>

                        {/* Map Test to Folder Form */}
                        <div className="bg-white dark:bg-gray-800 p-6 rounded-lg shadow-sm border border-gray-100 dark:border-gray-700">
                            <h2 className="text-xl font-bold mb-4 flex items-center"><LinkIcon className="mr-2" /> Map Individual Mock Test into a Folder</h2>
                            <form onSubmit={handleLinkTest} className="grid grid-cols-2 gap-4">
                                <select className="border p-2 rounded" value={newLink.test_id} onChange={e => setNewLink({ ...newLink, test_id: e.target.value })} required>
                                    <option value="">Select Existing Mock Test</option>
                                    {tests.map(t => <option key={t.id} value={t.id}>{t.title} ({t.category})</option>)}
                                </select>
                                <select className="border p-2 rounded" value={newLink.folder_id} onChange={e => setNewLink({ ...newLink, folder_id: e.target.value })} required>
                                    <option value="">Select Target Folder</option>
                                    {courses.flatMap(c => (c.folders || []).map((f: any) => (
                                        <option key={f.id} value={f.id}>{c.title} - {f.title}</option>
                                    )))}
                                </select>
                                <button type="submit" className="col-span-2 bg-green-600 text-white py-2 rounded font-bold hover:bg-green-700">Link Test to Folder</button>
                            </form>
                        </div>

                        {/* Existing Courses List */}
                        <div className="bg-white dark:bg-gray-800 p-6 rounded-lg shadow-sm border border-gray-100 dark:border-gray-700">
                            <h2 className="text-xl font-bold mb-4">Current Course Hierarchy</h2>
                            {courses.map(course => (
                                <div key={course.id} className="mb-4 p-4 border rounded bg-gray-50">
                                    <h3 className="font-bold text-lg text-orange-600">{course.title} <span className="text-sm text-gray-500 font-normal ml-2">₹{course.price}</span></h3>
                                    <div className="mt-2 ml-4">
                                        {(course.folders || []).length === 0 ? <p className="text-sm text-gray-400">No folders yet</p> : null}
                                        {course.folders?.map((folder: any) => (
                                            <div key={folder.id} className="mb-2 p-2 border-l-4 border-blue-400 bg-white shadow-sm">
                                                <h4 className="font-semibold text-gray-700">{folder.title} {folder.is_free && <span className="text-green-500 text-xs ml-2">FREE</span>}</h4>
                                                <ul className="ml-4 list-disc list-inside text-sm text-gray-500 mt-1">
                                                    {(folder.tests || []).map((mapped: any) => {
                                                        const targetTest = tests.find(t => t.id === mapped.test_id);
                                                        return <li key={mapped.id}>{targetTest?.title || 'Unknown Test'}</li>;
                                                    })}
                                                </ul>
                                            </div>
                                        ))}
                                    </div>
                                </div>
                            ))}
                        </div>

                    </div>
                )}
            </main>
        </div>
    );
};
