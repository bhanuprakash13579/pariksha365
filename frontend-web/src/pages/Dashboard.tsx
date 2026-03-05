import { useState, useEffect, useRef, useMemo } from 'react';
import { useDispatch } from 'react-redux';
import { logout } from '../store/slices/authSlice';
import { useNavigate } from 'react-router-dom';
import { SearchAPI, CategoryAPI, UserAPI, AttemptAPI, CourseAPI, api } from '../services/api';

import { MyLearning } from '../components/dashboard/MyLearning';
import { DailyQuizzes } from '../components/dashboard/DailyQuizzes';
import { Analytics } from '../components/dashboard/Analytics';
import { Profile } from '../components/dashboard/Profile';
import { Lock, PlayCircle, CheckCircle } from 'lucide-react';

export const StudentDashboard = () => {
    const dispatch = useDispatch();
    const navigate = useNavigate();
    const [activeTab, setActiveTab] = useState('home');
    const [dbCategories, setDbCategories] = useState<any[]>([]);
    const [userName, setUserName] = useState('');
    const [userPoints, setUserPoints] = useState(0);
    const [userStars, setUserStars] = useState(0);

    const [selectedCourse, setSelectedCourse] = useState<any | null>(null);
    const [userEnrollments, setUserEnrollments] = useState<Set<string>>(new Set());

    // Value-First Data States
    const [allCourses, setAllCourses] = useState<any[]>([]);
    const [testAttempts, setTestAttempts] = useState<any[]>([]);

    // Global User Preference
    const [globalExamGoalId, setGlobalExamGoalId] = useState<string | null>(null);
    const [globalExamGoalName, setGlobalExamGoalName] = useState<string>('Select Goal');
    const [isGoalDropdownOpen, setIsGoalDropdownOpen] = useState(false);
    const [savingGoal, setSavingGoal] = useState(false);

    // Build a lookup: subcategory_id -> category_id
    const subcatToCatMap = useMemo(() => {
        const map = new Map<string, string>();
        for (const cat of dbCategories) {
            for (const sub of (cat.subcategories || [])) {
                map.set(sub.id, cat.id);
            }
        }
        return map;
    }, [dbCategories]);

    // Accordion State
    const [expandedFolders, setExpandedFolders] = useState<Set<string>>(new Set());
    const toggleFolder = (folderId: string, e: React.MouseEvent) => {
        e.stopPropagation();
        setExpandedFolders(prev => {
            const next = new Set(prev);
            if (next.has(folderId)) next.delete(folderId);
            else next.add(folderId);
            return next;
        });
    };

    // Smart Nudging System
    const [showNudge, setShowNudge] = useState(false);
    const [nudgeData, setNudgeData] = useState({ title: '', message: '', type: '' });

    // Daily Streak Info
    const [dailyStreak, setDailyStreak] = useState<any>(null);

    useEffect(() => {
        // Trigger a random active nudge 3.5 seconds after login
        const timer = setTimeout(() => {
            const nudges = [
                { title: '⏱️ Target Bounty', message: 'Complete 10 Geography questions in the next hour to unlock a 2x Streak Multiplier!', type: 'bounty' },
                { title: '🔥 Momentum', message: 'You are only 5 points away from matching the Top 10% average accuracy today!', type: 'ghost' },
                { title: '⚠️ Streak at Risk', message: 'Keep your 3-day streak alive! Take a quick 5-min mock test now.', type: 'streak' }
            ];
            setNudgeData(nudges[Math.floor(Math.random() * nudges.length)]);
            setShowNudge(true);
        }, 3500);
        return () => clearTimeout(timer);
    }, []);

    useEffect(() => {
        const fetchInitial = async () => {
            try {
                const [catRes, userRes, attemptRes, coursesRes] = await Promise.all([
                    CategoryAPI.list(),
                    UserAPI.getMe(),
                    AttemptAPI.list().catch(() => ({ data: [] })),
                    CourseAPI.list().catch(() => ({ data: [] }))
                ]);
                setDbCategories(catRes.data);
                setUserName(userRes.data.name || '');
                setUserPoints(userRes.data.points || 0);
                setUserStars(userRes.data.stars || 0);
                setTestAttempts(attemptRes.data || []);

                try {
                    const streakRes = await api.get('/quiz/streak');
                    setDailyStreak(streakRes.data);
                } catch (e) { console.error(e) }

                setAllCourses(coursesRes.data || []);

                const preferredGoalId = userRes.data.selected_exam_category_id;
                setGlobalExamGoalId(preferredGoalId);
                if (preferredGoalId && catRes.data) {
                    const foundCat = catRes.data.find((c: any) => c.id === preferredGoalId);
                    if (foundCat) setGlobalExamGoalName(foundCat.name);
                }

                try {
                    const enrollRes = await UserAPI.getEnrollments();
                    const enrolledCourseIds = new Set<string>((enrollRes.data || []).map((e: any) => e.course_id));
                    setUserEnrollments(enrolledCourseIds);
                } catch (e) { console.error("Failed to load enrollments", e); }

            } catch (err) { console.error("Failed to fetch initial data", err); }
        };
        fetchInitial();
    }, []);

    const [searchQuery, setSearchQuery] = useState('');
    const [searchResults, setSearchResults] = useState<{ categories: any[], courses: any[], tests: any[] }>({ categories: [], courses: [], tests: [] });
    const [isSearching, setIsSearching] = useState(false);
    const [showSearchDropdown, setShowSearchDropdown] = useState(false);
    const searchRef = useRef<HTMLDivElement>(null);

    useEffect(() => {
        const handleClickOutside = (event: MouseEvent) => {
            if (searchRef.current && !searchRef.current.contains(event.target as Node)) {
                setShowSearchDropdown(false);
            }
        };
        document.addEventListener('mousedown', handleClickOutside);
        return () => document.removeEventListener('mousedown', handleClickOutside);
    }, []);

    useEffect(() => {
        const delayDebounceFn = setTimeout(async () => {
            if (searchQuery.trim().length >= 2) {
                setIsSearching(true);
                try {
                    const res = await SearchAPI.globalSearch(searchQuery);
                    setSearchResults(res.data);
                    setShowSearchDropdown(true);
                } catch (err) {
                    console.error("Search failed", err);
                } finally {
                    setIsSearching(false);
                }
            } else {
                setSearchResults({ categories: [], courses: [], tests: [] });
                setShowSearchDropdown(false);
            }
        }, 300);

        return () => clearTimeout(delayDebounceFn);
    }, [searchQuery]);

    const NAV_ITEMS = [
        { id: 'home', label: 'Home', icon: 'M3 12l2-2m0 0l7-7 7 7M5 10v10a1 1 0 001 1h3m10-11l2 2m-2-2v10a1 1 0 01-1 1h-3m-6 0a1 1 0 001-1v-4a1 1 0 011-1h2a1 1 0 011 1v4a1 1 0 001 1m-6 0h6' },
        { id: 'learning', label: 'My Learning', icon: 'M12 6.253v13m0-13C10.832 5.477 9.246 5 7.5 5S4.168 5.477 3 6.253v13C4.168 18.477 5.754 18 7.5 18s3.332.477 4.5 1.253m0-13C13.168 5.477 14.754 5 16.5 5c1.747 0 3.332.477 4.5 1.253v13C19.832 18.477 18.247 18 16.5 18c-1.746 0-3.332.477-4.5 1.253' },
        { id: 'quiz', label: 'Daily Quizzes', icon: 'M13 10V3L4 14h7v7l9-11h-7z' },
        { id: 'analytics', label: 'Analytics', icon: 'M9 19v-6a2 2 0 00-2-2H5a2 2 0 00-2 2v6a2 2 0 002 2h2a2 2 0 002-2zm0 0V9a2 2 0 012-2h2a2 2 0 012 2v10m-6 0a2 2 0 002 2h2a2 2 0 002-2m0 0V5a2 2 0 012-2h2a2 2 0 012 2v14a2 2 0 01-2 2h-2a2 2 0 01-2-2z' },
        { id: 'profile', label: 'Profile', icon: 'M16 7a4 4 0 11-8 0 4 4 0 018 0zM12 14a7 7 0 00-7 7h14a7 7 0 00-7-7z' },
    ];

    const handleLogout = () => {
        dispatch(logout());
        navigate('/auth');
    };

    return (
        <div className="min-h-screen bg-gray-50 flex">
            {/* Desktop Sidebar (Left) */}
            <aside className="w-64 bg-gradient-to-b from-gray-900 via-gray-900 to-gray-950 hidden md:flex flex-col shadow-2xl relative z-10">
                <div className="py-6 flex flex-col items-center border-b border-white/10">
                    <div className="w-40 h-40 rounded-full bg-white shadow-lg shadow-orange-500/20 ring-4 ring-orange-400/30 flex items-center justify-center overflow-hidden mb-3 relative">
                        <img src="/logo_square.png" alt="Pariksha365 Logo" className="absolute top-0 left-0 w-full h-full object-cover object-center mix-blend-multiply drop-shadow-sm transition-transform duration-300 hover:scale-[2.8] scale-[2.7] translate-y-3 transform origin-center" />
                    </div>
                    <span className="text-white font-black text-lg tracking-tight">Pariksha365</span>
                    <span className="text-gray-500 text-[10px] font-semibold uppercase tracking-[0.2em] mt-0.5">Mock Test Platform</span>
                </div>

                <nav className="flex-1 px-4 py-6 space-y-1.5">
                    {NAV_ITEMS.map((item) => (
                        <button
                            key={item.id}
                            onClick={() => setActiveTab(item.id)}
                            className={`w-full flex items-center px-4 py-3 text-sm font-medium rounded-xl transition-all duration-200 ${activeTab === item.id
                                ? 'bg-orange-500/15 text-orange-400 shadow-sm shadow-orange-500/10 border border-orange-500/20'
                                : 'text-gray-400 hover:bg-white/5 hover:text-gray-200 border border-transparent'
                                }`}
                        >
                            <svg className={`mr-3 h-5 w-5 ${activeTab === item.id ? 'text-orange-400' : 'text-gray-500'}`} fill="none" viewBox="0 0 24 24" stroke="currentColor">
                                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d={item.icon} />
                            </svg>
                            {item.label}
                        </button>
                    ))}
                </nav>

                <div className="p-4 border-t border-white/10">
                    <button
                        onClick={handleLogout}
                        className="w-full flex items-center px-4 py-3 text-sm font-medium text-red-400 hover:bg-red-500/10 rounded-xl transition-colors border border-transparent hover:border-red-500/20"
                    >
                        <svg className="mr-3 h-5 w-5 text-red-400" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M17 16l4-4m0 0l-4-4m4 4H7m6 4v1a3 3 0 01-3 3H6a3 3 0 01-3-3V7a3 3 0 013-3h4a3 3 0 013 3v1" />
                        </svg>
                        Logout
                    </button>
                </div>
            </aside>

            {/* Main Content Area (Right) */}
            <div className="flex-1 flex flex-col min-h-screen overflow-hidden relative">

                {/* Top Header */}
                <header className="h-16 bg-white border-b border-gray-200 flex items-center justify-between px-4 sm:px-6 lg:px-8 shadow-sm relative z-10 w-full">

                    {/* Mobile Logo (hidden on desktop) */}
                    <div className="md:hidden flex items-center">
                        <img src="/logo_square.png" alt="Pariksha365" className="h-10 w-10 object-contain rounded-full bg-white shadow-sm ring-2 ring-orange-300/30 p-1 mix-blend-multiply" />
                    </div>

                    {/* Search Bar */}
                    <div className="flex-1 flex justify-center px-2 lg:ml-6 lg:justify-start">
                        <div className="max-w-lg w-full lg:max-w-xs relative" ref={searchRef}>
                            <label htmlFor="search" className="sr-only">Search</label>
                            <div className="relative">
                                <div className="absolute inset-y-0 left-0 pl-3 flex items-center pointer-events-none">
                                    <svg className="h-5 w-5 text-gray-400" fill="currentColor" viewBox="0 0 20 20">
                                        <path fillRule="evenodd" d="M8 4a4 4 0 100 8 4 4 0 000-8zM2 8a6 6 0 1110.89 3.476l4.817 4.817a1 1 0 01-1.414 1.414l-4.816-4.816A6 6 0 012 8z" clipRule="evenodd" />
                                    </svg>
                                </div>
                                <input
                                    id="search"
                                    value={searchQuery}
                                    onChange={(e) => setSearchQuery(e.target.value)}
                                    onFocus={() => searchQuery.trim().length >= 2 && setShowSearchDropdown(true)}
                                    className="block w-full pl-10 pr-3 py-2 border border-gray-300 rounded-full leading-5 bg-gray-50 placeholder-gray-500 focus:outline-none focus:placeholder-gray-400 focus:ring-1 focus:ring-orange-500 focus:border-orange-500 focus:bg-white sm:text-sm transition-colors"
                                    placeholder="Search exams, mock tests..."
                                    type="search"
                                />
                            </div>

                            {/* Search Dropdown */}
                            {showSearchDropdown && (
                                <div className="absolute top-full left-0 right-0 mt-2 bg-white rounded-xl shadow-lg border border-gray-100 max-h-96 overflow-y-auto z-50">
                                    {isSearching ? (
                                        <div className="p-4 text-center text-gray-500 text-sm">Searching...</div>
                                    ) : (
                                        <>
                                            {searchResults.categories.length > 0 && (
                                                <div className="p-2 border-b border-gray-50">
                                                    <div className="px-2 py-1 text-xs font-semibold text-gray-400 uppercase">Categories</div>
                                                    {searchResults.categories.map(cat => (
                                                        <div key={cat.id} className="px-3 py-2 hover:bg-orange-50 rounded-lg cursor-pointer text-sm text-gray-700 font-medium truncate">
                                                            {cat.name}
                                                        </div>
                                                    ))}
                                                </div>
                                            )}
                                            {searchResults.courses.length > 0 && (
                                                <div className="p-2 border-b border-gray-50">
                                                    <div className="px-2 py-1 text-xs font-semibold text-gray-400 uppercase">Courses</div>
                                                    {searchResults.courses.map(course => (
                                                        <div key={course.id} onClick={() => { setSelectedCourse(course); setShowSearchDropdown(false); }} className="px-3 py-2 hover:bg-orange-50 rounded-lg cursor-pointer text-sm text-gray-700 font-medium truncate">
                                                            {course.title}
                                                        </div>
                                                    ))}
                                                </div>
                                            )}
                                            {searchResults.tests.length > 0 && (
                                                <div className="p-2">
                                                    <div className="px-2 py-1 text-xs font-semibold text-gray-400 uppercase">Test Series</div>
                                                    {searchResults.tests.map(test => (
                                                        <div key={test.id} className="px-3 py-2 hover:bg-orange-50 rounded-lg cursor-pointer text-sm text-gray-700 font-medium truncate">
                                                            {test.title}
                                                        </div>
                                                    ))}
                                                </div>
                                            )}
                                            {searchResults.categories.length === 0 && searchResults.courses.length === 0 && searchResults.tests.length === 0 && (
                                                <div className="p-4 text-center text-gray-500 text-sm">No results found for "{searchQuery}"</div>
                                            )}
                                        </>
                                    )}
                                </div>
                            )}
                        </div>
                    </div>

                    {/* Global Goal Switcher */}
                    <div className="hidden lg:block relative ml-4">
                        <button
                            onClick={() => setIsGoalDropdownOpen(!isGoalDropdownOpen)}
                            disabled={savingGoal}
                            className="flex items-center gap-2 bg-orange-50 hover:bg-orange-100 border border-orange-200 px-4 py-2 rounded-xl text-orange-900 font-bold transition-colors"
                        >
                            🎯 Target: {savingGoal ? 'Saving...' : globalExamGoalName}
                            <svg className={`w-4 h-4 transition-transform ${isGoalDropdownOpen ? 'rotate-180' : ''}`} fill="none" viewBox="0 0 24 24" stroke="currentColor">
                                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M19 9l-7 7-7-7" />
                            </svg>
                        </button>

                        {isGoalDropdownOpen && (
                            <div className="absolute top-full right-0 mt-2 w-56 bg-white rounded-xl shadow-xl border border-gray-100 py-2 z-50">
                                <div className="px-4 py-2 text-xs font-semibold text-gray-500 uppercase tracking-wider border-b border-gray-50 mb-2">
                                    Change Exam Goal
                                </div>
                                {dbCategories.map(cat => (
                                    <button
                                        key={cat.id}
                                        onClick={async () => {
                                            if (cat.id === globalExamGoalId) {
                                                setIsGoalDropdownOpen(false);
                                                return;
                                            }
                                            setSavingGoal(true);
                                            try {
                                                await UserAPI.updateExamPreference(cat.id);
                                                setGlobalExamGoalId(cat.id);
                                                setGlobalExamGoalName(cat.name);
                                            } catch (e) {
                                                console.error("Failed to update goal");
                                            } finally {
                                                setSavingGoal(false);
                                                setIsGoalDropdownOpen(false);
                                            }
                                        }}
                                        className={`w-full text-left px-4 py-2.5 text-sm font-medium transition-colors ${globalExamGoalId === cat.id ? 'bg-orange-50 text-orange-700' : 'text-gray-700 hover:bg-gray-50'}`}
                                    >
                                        {cat.name}
                                    </button>
                                ))}
                            </div>
                        )}
                    </div>

                    {/* Right User Actions */}
                    <div className="ml-4 flex items-center md:ml-6 space-x-4">
                        <button className="bg-white p-1 rounded-full text-gray-400 hover:text-gray-500 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-orange-500 transition-colors">
                            <span className="sr-only">View notifications</span>
                            <svg className="h-6 w-6" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M15 17h5l-1.405-1.405A2.032 2.032 0 0118 14.158V11a6.002 6.002 0 00-4-5.659V5a2 2 0 10-4 0v.341C7.67 6.165 6 8.388 6 11v3.159c0 .538-.214 1.055-.595 1.436L4 17h5m6 0v1a3 3 0 11-6 0v-1m6 0H9" />
                            </svg>
                        </button>

                        <div className="flex flex-col items-end mr-3 hidden sm:flex">
                            <div className="flex items-center gap-1.5 bg-yellow-400/10 px-2 py-0.5 rounded-full border border-yellow-400/20">
                                <span className="text-yellow-500 text-sm">⭐</span>
                                <span className="text-yellow-700 font-bold text-xs">{userStars}</span>
                            </div>
                            <div className="text-[10px] font-bold text-gray-500 mt-0.5 tracking-wider uppercase">
                                {userPoints} Pts
                            </div>
                        </div>

                        <div className="relative">
                            <button
                                onClick={() => setActiveTab('profile')}
                                className="max-w-xs bg-white flex items-center text-sm rounded-full focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-orange-500"
                            >
                                <span className="sr-only">Open user menu</span>
                                <div className="h-8 w-8 rounded-full bg-orange-100 flex items-center justify-center border border-orange-200 shadow-sm relative overflow-hidden">
                                    {userStars >= 1 && (
                                        <div className="absolute inset-0 bg-gradient-to-tr from-yellow-300/30 to-orange-400/30"></div>
                                    )}
                                    <span className="text-orange-700 font-bold text-xs relative z-10">
                                        {(userName || 'ST').slice(0, 2).toUpperCase()}
                                    </span>
                                </div>
                            </button>
                        </div>
                    </div>
                </header>

                {/* Main Scrollable Content */}
                <main className="flex-1 relative z-0 overflow-y-auto focus:outline-none">
                    <div className="py-6 px-4 pb-24 md:pb-6 sm:px-6 lg:px-8 max-w-7xl mx-auto">


                        {(() => {
                            switch (activeTab) {
                                case 'home':
                                    return (
                                        <>
                                            {/* Daily Quiz Hero Banner (Habit Builder) */}
                                            <div
                                                onClick={() => setActiveTab('quiz')}
                                                className="mb-8 relative overflow-hidden bg-gradient-to-r from-orange-500 to-pink-500 rounded-2xl shadow-lg border border-orange-400 group cursor-pointer"
                                            >
                                                <div className="absolute top-0 right-0 -mr-10 -mt-20 w-48 h-48 bg-white opacity-10 rounded-full blur-2xl group-hover:scale-110 transition-transform duration-700"></div>
                                                <div className="absolute bottom-0 right-10 w-24 h-24 bg-orange-300 opacity-20 rounded-full blur-xl group-hover:-translate-y-4 transition-transform duration-700"></div>

                                                <div className="relative z-10 p-6 md:p-8 flex flex-col md:flex-row items-center justify-between gap-6">
                                                    <div className="flex items-center gap-6">
                                                        <div className="w-16 h-16 bg-white/20 backdrop-blur-md rounded-2xl flex items-center justify-center flex-shrink-0 border border-white/30 shadow-inner group-hover:scale-105 transition-transform duration-300">
                                                            <span className="text-3xl">⚡</span>
                                                        </div>
                                                        <div>
                                                            <div className="text-orange-100 font-bold text-xs uppercase tracking-widest mb-1 flex items-center gap-2">
                                                                <span className="w-2 h-2 rounded-full bg-green-400 animate-pulse"></span>
                                                                {dailyStreak?.current_streak > 0 ? `🔥 ${dailyStreak.current_streak}-Day Streak Live!` : "Daily Challenge Live"}
                                                            </div>
                                                            <h2 className="text-2xl md:text-3xl font-black text-white tracking-tight mb-2">Build Your Prep Streak</h2>
                                                            <p className="text-orange-50 font-medium text-sm md:text-base opacity-90">10 Questions • 10 Minutes • Earn Points & Stars</p>
                                                        </div>
                                                    </div>
                                                    <button className="w-full md:w-auto px-8 py-3.5 bg-white text-orange-600 rounded-xl font-bold hover:bg-orange-50 hover:shadow-lg transition-all active:scale-95 flex items-center justify-center gap-2 group-hover:text-orange-700">
                                                        Play Today's Quiz
                                                        <svg className="w-5 h-5 transition-transform group-hover:translate-x-1" fill="none" viewBox="0 0 24 24" stroke="currentColor"><path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2.5" d="M14 5l7 7m0 0l-7 7m7-7H3" /></svg>
                                                    </button>
                                                </div>
                                            </div>

                                            {/* ROW 2: Previous Year Papers (Trust Builder) */}
                                            <div className="mb-10">
                                                <div className="flex justify-between items-end mb-4">
                                                    <h2 className="text-2xl font-black text-gray-900 tracking-tight flex items-center gap-2">
                                                        <span className="text-blue-500">📚</span> Previous Year Papers (100% Free)
                                                    </h2>
                                                </div>
                                                <div className="flex overflow-x-auto snap-x snap-mandatory gap-6 pb-4 scrollbar-hide">
                                                    {allCourses.filter(c =>
                                                        (subcatToCatMap.get(c.subcategory_id) === globalExamGoalId) &&
                                                        (c.title.toLowerCase().includes('pyq') || c.title.toLowerCase().includes('previous year') || c.title.toLowerCase().includes('past paper'))
                                                    ).map(course => (
                                                        (course.folders || []).map((folder: any) => (
                                                            <FolderCard key={folder.id} folder={folder} course={course} isEnrolled={userEnrollments.has(course.id)} onClick={() => setSelectedCourse(course)} />
                                                        ))
                                                    ))}
                                                    {allCourses.filter(c =>
                                                        (subcatToCatMap.get(c.subcategory_id) === globalExamGoalId) &&
                                                        (c.title.toLowerCase().includes('pyq') || c.title.toLowerCase().includes('previous year'))
                                                    ).length === 0 && (
                                                            <div className="w-full text-center py-8 text-gray-400 text-sm italic bg-white border border-dashed border-gray-200 rounded-2xl">
                                                                No Previous Year Papers available for this selection yet.
                                                            </div>
                                                        )}
                                                </div>
                                            </div>

                                            {/* ROW 3: Premium Mock Tests (Upsell) */}
                                            <div className="mb-10">
                                                <div className="flex justify-between items-end mb-4">
                                                    <h2 className="text-2xl font-black text-gray-900 tracking-tight flex items-center gap-2">
                                                        <span className="text-green-500">🌟</span> Complete Mock Test Series
                                                    </h2>
                                                </div>
                                                <div className="flex overflow-x-auto snap-x snap-mandatory gap-6 pb-4 scrollbar-hide">
                                                    {allCourses.filter(c =>
                                                        (subcatToCatMap.get(c.subcategory_id) === globalExamGoalId) &&
                                                        !(c.title.toLowerCase().includes('pyq') || c.title.toLowerCase().includes('previous year') || c.title.toLowerCase().includes('past paper'))
                                                    ).map(course => (
                                                        (course.folders || []).map((folder: any) => (
                                                            <FolderCard key={folder.id} folder={folder} course={course} isEnrolled={userEnrollments.has(course.id)} onClick={() => setSelectedCourse(course)} />
                                                        ))
                                                    ))}
                                                    {allCourses.filter(c =>
                                                        (subcatToCatMap.get(c.subcategory_id) === globalExamGoalId) &&
                                                        !(c.title.toLowerCase().includes('pyq') || c.title.toLowerCase().includes('previous year'))
                                                    ).length === 0 && (
                                                            <div className="w-full text-center py-8 text-gray-400 text-sm italic bg-white border border-dashed border-gray-200 rounded-2xl">
                                                                No Mock Tests available for this selection yet.
                                                            </div>
                                                        )}
                                                </div>
                                            </div>
                                        </>
                                    );
                                case 'learning':
                                    return <MyLearning onSelectCourse={setSelectedCourse} />;
                                case 'quiz':
                                    return <DailyQuizzes />;
                                case 'analytics':
                                    return <Analytics />;
                                case 'profile':
                                    return <Profile />;
                                default:
                                    return <div>Tab not found</div>;
                            }
                        })()}
                    </div>
                </main>
            </div>

            {/* Mobile Bottom Navigation (Visible only on small screens) */}
            <div className="md:hidden fixed bottom-0 left-0 right-0 bg-white border-t border-gray-200 z-50 flex justify-around items-center h-16 pb-safe">
                {NAV_ITEMS.map((item) => (
                    <button
                        key={item.id}
                        onClick={() => setActiveTab(item.id)}
                        className={`flex flex-col items-center justify-center w-16 h-full ${activeTab === item.id ? 'text-orange-600' : 'text-gray-400'}`}
                    >
                        <svg className={`w-6 h-6 mb-1 ${activeTab === item.id ? '' : 'stroke-current fill-none'}`} fill={activeTab === item.id ? 'currentColor' : 'none'} viewBox="0 0 24 24">
                            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={activeTab === item.id ? "0" : "2"} d={item.icon} />
                        </svg>
                        <span className="text-[10px] font-medium">{item.label}</span>
                    </button>
                ))}
            </div>

            {/* Smart Nudge Toast */}
            {showNudge && (
                <div className="fixed bottom-20 right-4 md:bottom-8 md:right-8 z-50 animate-fade-in-up translate-y-0 opacity-100 transition-all duration-500 ease-out">
                    <div className="bg-white rounded-2xl shadow-2xl border border-gray-100 p-4 max-w-sm flex items-start space-x-4 relative overflow-hidden">
                        <div className={`absolute top-0 left-0 w-1.5 h-full ${nudgeData.type === 'bounty' ? 'bg-indigo-500' : nudgeData.type === 'streak' ? 'bg-red-500' : 'bg-orange-500'}`}></div>

                        <div className="flex-1 pl-1">
                            <div className="flex justify-between items-start">
                                <h4 className="text-sm font-bold text-gray-900">{nudgeData.title}</h4>
                                <button onClick={() => setShowNudge(false)} className="text-gray-400 hover:text-gray-600 focus:outline-none ml-2 bg-gray-50 rounded-full p-1 border border-gray-100">
                                    <svg className="h-3.5 w-3.5" fill="none" viewBox="0 0 24 24" stroke="currentColor"><path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2.5" d="M6 18L18 6M6 6l12 12" /></svg>
                                </button>
                            </div>
                            <p className="text-xs text-gray-600 mt-1.5 pr-2 font-medium leading-relaxed">{nudgeData.message}</p>

                            <button onClick={() => { setShowNudge(false); setActiveTab(nudgeData.type === 'streak' ? 'quiz' : 'learning'); }} className="mt-3 text-xs font-bold text-orange-600 hover:text-orange-700 transition-colors inline-flex border border-orange-200 bg-orange-50 px-3 py-1.5 rounded-lg shadow-sm">
                                Take Action &rarr;
                            </button>
                        </div>
                    </div>
                </div>
            )}

            {/* Course Details Modal Overlay */}
            {selectedCourse && (
                <div
                    className="fixed inset-0 z-[100] flex items-center justify-center bg-gray-900/60 backdrop-blur-sm p-4 animate-fade-in overflow-y-auto"
                    onClick={() => { setSelectedCourse(null); setExpandedFolders(new Set()); }} // Clicking the backdrop closes the modal
                >
                    <div
                        className="bg-white rounded-3xl shadow-2xl w-full max-w-4xl max-h-[90vh] flex flex-col overflow-hidden animate-slide-up relative my-auto"
                        onClick={(e) => e.stopPropagation()} // Prevent clicks inside modal from closing it or bubbling up
                    >
                        {/* Header */}
                        <div className="bg-gradient-to-br from-gray-900 via-gray-800 to-gray-900 p-8 text-white relative flex-shrink-0">
                            <div className="absolute top-0 right-0 -mr-16 -mt-16 w-64 h-64 rounded-full bg-orange-500/20 blur-3xl"></div>
                            <button
                                onClick={(e) => { e.stopPropagation(); setSelectedCourse(null); }}
                                className="absolute top-6 right-6 w-10 h-10 bg-white/10 hover:bg-white/20 rounded-full flex items-center justify-center transition-colors backdrop-blur-md"
                            >
                                <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M6 18L18 6M6 6l12 12" /></svg>
                            </button>

                            <div className="relative z-10 pr-12">
                                <div className="flex items-center gap-3 mb-4">
                                    <span className="px-3 py-1 text-xs font-bold uppercase tracking-widest bg-white/20 rounded-md backdrop-blur-md border border-white/20 text-white">
                                        Course Contents
                                    </span>
                                </div>
                                <h2 className="text-3xl md:text-4xl font-black mb-3 leading-tight">{selectedCourse.title}</h2>
                                <p className="text-gray-300 text-sm md:text-base max-w-2xl leading-relaxed">{selectedCourse.description}</p>
                            </div>
                        </div>

                        {/* Content Area */}
                        <div className="flex-1 overflow-y-auto p-6 md:p-8 bg-gray-50 flex flex-col md:flex-row gap-8">

                            {/* Left: Folders & Tests List */}
                            <div className="flex-1 space-y-6">
                                {(!selectedCourse.folders || selectedCourse.folders.length === 0) ? (
                                    <div className="text-center p-12 bg-white rounded-2xl border border-gray-100 shadow-sm">
                                        <div className="w-16 h-16 bg-gray-50 rounded-full flex items-center justify-center mx-auto mb-4">
                                            <svg className="w-8 h-8 text-gray-300" fill="none" viewBox="0 0 24 24" stroke="currentColor"><path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M20 13V6a2 2 0 00-2-2H6a2 2 0 00-2 2v7m16 0v5a2 2 0 01-2 2H6a2 2 0 01-2-2v-5m16 0h-2.586a1 1 0 00-.707.293l-2.414 2.414a1 1 0 01-.707.293h-3.172a1 1 0 01-.707-.293l-2.414-2.414A1 1 0 006.586 13H4" /></svg>
                                        </div>
                                        <p className="text-gray-500 font-medium">No contents available for this course yet.</p>
                                    </div>
                                ) : (
                                    selectedCourse.folders.map((folder: any, fIdx: number) => {
                                        const isExpanded = expandedFolders.has(folder.id) || selectedCourse.folders.length === 1;
                                        return (
                                            <div key={folder.id} className="bg-white rounded-2xl shadow-sm border border-gray-100 overflow-hidden cursor-pointer hover:border-orange-200 transition-colors" onClick={(e) => toggleFolder(folder.id, e)}>
                                                <div className="bg-gray-50/80 px-5 py-4 flex items-center justify-between border-b border-gray-100">
                                                    <div className="flex items-center gap-3">
                                                        <div className={`transition-transform duration-300 ${isExpanded ? 'rotate-90 text-orange-600' : 'text-gray-400'}`}>
                                                            <svg className="w-5 h-5" fill="none" viewBox="0 0 24 24" stroke="currentColor"><path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2.5" d="M9 5l7 7-7 7" /></svg>
                                                        </div>
                                                        <div className="w-8 h-8 bg-orange-100 rounded-lg flex items-center justify-center text-orange-600 font-black text-sm">{fIdx + 1}</div>
                                                        <div>
                                                            <h3 className="font-bold text-gray-900">{folder.title}</h3>
                                                            <p className="text-xs text-gray-500">{(folder.tests || []).length} mock tests</p>
                                                        </div>
                                                    </div>
                                                    {folder.is_free && (
                                                        <span className="bg-green-100 text-green-700 px-3 py-1 text-xs font-bold rounded-full border border-green-200 uppercase tracking-wide">
                                                            Freemium
                                                        </span>
                                                    )}
                                                </div>

                                                {isExpanded && (
                                                    <div className="divide-y divide-gray-50 animate-fade-in">
                                                        {(folder.tests || []).length === 0 ? (
                                                            <div className="p-6 text-sm text-gray-400 italic text-center">Folder contains no tests</div>
                                                        ) : (
                                                            (folder.tests || []).map((link: any) => {
                                                                const test = link.test_series;
                                                                if (!test) return null;

                                                                const isEnrolled = userEnrollments.has(selectedCourse.id);
                                                                const isUnlocked = isEnrolled || folder.is_free;
                                                                const activeAttempt = testAttempts.find((a: any) => a.test_series_id === test.id && a.status === 'IN_PROGRESS');

                                                                return (
                                                                    <div key={link.id} className={`p-4 flex items-center justify-between hover:bg-gray-50 transition-colors ${!isUnlocked ? 'opacity-70' : ''}`} onClick={(e) => e.stopPropagation()}>
                                                                        <div className="flex items-center gap-4 flex-1 min-w-0">
                                                                            <div className={`w-10 h-10 rounded-xl flex items-center justify-center flex-shrink-0 ${isUnlocked ? 'bg-orange-50 text-orange-600' : 'bg-gray-100 text-gray-400'}`}>
                                                                                {isUnlocked ? <PlayCircle className="w-5 h-5" /> : <Lock className="w-5 h-5" />}
                                                                            </div>
                                                                            <div className="flex-1 min-w-0 pr-4">
                                                                                <h4 className={`text-sm font-bold truncate ${isUnlocked ? 'text-gray-900' : 'text-gray-500'}`}>{test.title}</h4>
                                                                                <div className="flex items-center gap-3 mt-1 text-xs text-gray-400 font-medium">
                                                                                    <span>{test.total_questions || 100} Questions</span>
                                                                                    <span>•</span>
                                                                                    <span>{test.duration_minutes || 60} Mins</span>
                                                                                </div>
                                                                            </div>
                                                                        </div>

                                                                        <button
                                                                            disabled={!isUnlocked}
                                                                            onClick={(e) => { e.stopPropagation(); navigate(`/mock-test/${test.id}`); }}
                                                                            className={`px-4 py-2 rounded-lg text-sm font-bold transition-all flex-shrink-0 border ${isUnlocked
                                                                                ? (activeAttempt ? 'bg-orange-50 border-orange-200 text-orange-700 hover:bg-orange-100 hover:border-orange-300 shadow-sm' : 'bg-white border-gray-200 text-gray-700 hover:border-orange-500 hover:text-orange-600 shadow-sm')
                                                                                : 'bg-gray-50 border-gray-100 text-gray-400 cursor-not-allowed'
                                                                                }`}
                                                                        >
                                                                            {!isUnlocked ? 'Locked' : (activeAttempt ? 'Resume' : 'Start Test')}
                                                                        </button>
                                                                    </div>
                                                                );
                                                            })
                                                        )}
                                                    </div>
                                                )}
                                            </div>
                                        );
                                    })
                                )}
                            </div>

                            {/* Right: Checkout / Enrollment Card */}
                            <div className="w-full md:w-72 flex-shrink-0 mt-6 md:mt-0">
                                <div className="bg-white rounded-3xl p-6 shadow-xl border border-gray-100 sticky top-8">
                                    <h3 className="font-black text-gray-900 text-lg mb-1">Get Access</h3>
                                    <p className="text-xs text-gray-500 mb-6 pb-6 border-b border-gray-100">Unlock all tests and papers inside this package permanently.</p>

                                    <div className="mb-6">
                                        <div className="text-3xl font-black text-gray-900 mb-2">
                                            {selectedCourse.price > 0 ? `₹${selectedCourse.price}` : 'FREE'}
                                        </div>
                                        <div className="flex items-center gap-2 text-sm font-bold text-green-600 bg-green-50 px-3 py-2 rounded-xl">
                                            <svg className="w-4 h-4" fill="none" viewBox="0 0 24 24" stroke="currentColor"><path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2.5" d="M13 7h8m0 0v8m0-8l-8 8-4-4-6 6" /></svg>
                                            {selectedCourse.validity_days || 365} Days Validity
                                        </div>
                                    </div>

                                    {userEnrollments.has(selectedCourse.id) ? (
                                        <div className="w-full bg-green-50 text-green-700 py-3.5 rounded-xl text-center font-bold border border-green-200 flex items-center justify-center gap-2">
                                            <CheckCircle className="w-5 h-5" /> Subscribed
                                        </div>
                                    ) : (
                                        <button
                                            onClick={async (e) => {
                                                e.stopPropagation();
                                                if (selectedCourse.price > 0) {
                                                    alert("Payment gateway integration pending checkout screen.");
                                                } else {
                                                    try {
                                                        await api.post(`/courses/${selectedCourse.id}/enroll`);
                                                        const res = await UserAPI.getEnrollments();
                                                        setUserEnrollments(new Set((res.data || []).map((e: any) => e.course_id)));
                                                        alert("Successfully enrolled!");
                                                    } catch (err: any) {
                                                        console.error("Enrollment error:", err);
                                                        alert("Failed to enroll: " + (err.response?.data?.detail || err.message));
                                                    }
                                                }
                                            }}
                                            className={`w-full py-4 rounded-xl text-center font-bold text-white shadow-lg transition-all active:scale-95 flex items-center justify-center gap-2 ${selectedCourse.price > 0
                                                ? 'bg-gray-900 hover:bg-gray-800 shadow-gray-900/20'
                                                : 'bg-orange-600 hover:bg-orange-700 shadow-orange-500/20'
                                                }`}
                                        >
                                            {selectedCourse.price > 0 ? 'Buy Now securely' : 'Enroll for Free'}
                                            <svg className="w-4 h-4" fill="none" viewBox="0 0 24 24" stroke="currentColor"><path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2.5" d="M14 5l7 7m0 0l-7 7m7-7H3" /></svg>
                                        </button>
                                    )}

                                    <ul className="mt-6 space-y-3 text-sm text-gray-500 font-medium">
                                        <li className="flex gap-2.5"><CheckCircle className="w-5 h-5 text-green-500 flex-shrink-0" /> Full length mock tests</li>
                                        <li className="flex gap-2.5"><CheckCircle className="w-5 h-5 text-green-500 flex-shrink-0" /> Previous year papers</li>
                                        <li className="flex gap-2.5"><CheckCircle className="w-5 h-5 text-green-500 flex-shrink-0" /> Detailed analytics insights</li>
                                    </ul>
                                </div>
                            </div>
                        </div>
                    </div>
                </div>
            )}

        </div>
    );
};



export default StudentDashboard;

// FolderCard (Playing Card style)
const FolderCard = ({ folder, course, isEnrolled, onClick }: { folder: any, course: any, isEnrolled: boolean, onClick: () => void }) => {
    const totalTests = (folder.tests || []).length;
    return (
        <div
            onClick={onClick}
            className="snap-start flex-shrink-0 w-72 bg-white rounded-2xl border border-gray-100 shadow-[0_2px_10px_rgba(0,0,0,0.02)] hover:shadow-[0_8px_30px_rgba(0,0,0,0.08)] transition-all cursor-pointer overflow-hidden flex flex-col group hover:-translate-y-1 duration-300"
        >
            <div className="h-32 bg-gradient-to-br from-indigo-900 via-gray-900 to-indigo-950 p-5 flex flex-col justify-between relative overflow-hidden">
                <div className="absolute top-0 right-0 -mr-8 -mt-8 w-32 h-32 rounded-full bg-white/5 blur-2xl group-hover:bg-white/10 transition-colors"></div>
                <div className="absolute bottom-0 left-0 -ml-12 -mb-12 w-32 h-32 rounded-full bg-orange-500/20 blur-2xl group-hover:bg-orange-500/30 transition-colors"></div>

                <div className="z-10 flex justify-between items-start w-full">
                    <div className="bg-white/10 backdrop-blur-md px-2.5 py-1 rounded-lg text-[10px] font-bold text-white uppercase tracking-widest border border-white/20 truncate max-w-[60%]">
                        {course.title}
                    </div>
                    {folder.is_free && (
                        <div className="bg-green-500/20 text-green-300 px-2 py-0.5 rounded text-[10px] font-bold border border-green-500/30">FREE</div>
                    )}
                </div>

                <div className="z-10 flex justify-between items-end mt-auto">
                    <span className={`text-sm font-black px-4 py-1.5 rounded-xl shadow-lg border border-white/10 ${course.price > 0 ? 'bg-white text-gray-900' : 'bg-green-500 text-white border-green-400'}`}>
                        {course.price > 0 ? `₹${course.price}` : 'FREE'}
                    </span>
                    {isEnrolled && (
                        <span className="flex items-center gap-1.5 text-xs font-bold text-green-400 bg-green-400/10 border border-green-400/20 px-3 py-1.5 rounded-xl backdrop-blur-md">
                            <CheckCircle className="w-3.5 h-3.5" /> Enrolled
                        </span>
                    )}
                </div>
            </div>
            <div className="p-5 flex-1 flex flex-col bg-[url('https://www.transparenttextures.com/patterns/cubes.png')] bg-blend-soft-light">
                <h3 className="text-xl font-black text-gray-900 group-hover:text-orange-600 transition-colors leading-tight mb-2">{folder.title}</h3>
                <p className="text-xs text-gray-500 line-clamp-2 leading-relaxed flex-1">
                    {folder.description || "Collection of highly curated mock tests and practice material."}
                </p>
                <div className="mt-4 pt-3 border-t border-gray-100 flex items-center justify-between text-[11px] font-bold text-gray-400">
                    <div className="flex items-center gap-1.5 text-gray-600 bg-gray-50 px-2.5 py-1.5 rounded-lg border border-gray-100 group-hover:bg-orange-50 group-hover:border-orange-100 group-hover:text-orange-700 transition-colors">
                        <PlayCircle className="w-3.5 h-3.5" />
                        {totalTests} Tests Included
                    </div>
                </div>
            </div>
        </div>
    );
};
