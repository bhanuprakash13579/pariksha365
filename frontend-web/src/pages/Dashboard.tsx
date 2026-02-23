import { Link } from 'react-router-dom';
import { LogOut, BookOpen, Clock, Award, ChevronRight } from 'lucide-react';
import { useDispatch } from 'react-redux';
import { logout } from '../store/slices/authSlice';

export const StudentDashboard = () => {
    const dispatch = useDispatch();

    const MOCK_TESTS = [
        { id: '1', title: 'SSC CGL Tier 1 Full Mock', tags: 'Mock Test / English', price: '₹149', isFree: false, questions: 100, mins: 60, validity: 365 },
        { id: '2', title: 'SBI PO Prelims Mini Test', tags: 'Mini Test / English', price: 'Free', isFree: true, questions: 30, mins: 20, validity: 30 },
        { id: '3', title: 'UPSC CSAT Complete Prep', tags: 'Subject Wise / Hindi', price: '₹299', isFree: false, questions: 80, mins: 120, validity: 180 },
    ];

    return (
        <div className="min-h-screen bg-gray-50 flex flex-col">
            {/* Navbar */}
            <nav className="bg-orange-600 px-6 py-4 shadow-md flex justify-between items-center text-white">
                <div className="text-2xl font-bold tracking-tight">EdTech Platform</div>
                <div className="flex space-x-6 items-center">
                    <button className="hover:text-orange-200 transition-colors">My Tests</button>
                    <button className="hover:text-orange-200 transition-colors">Performance</button>
                    <button onClick={() => dispatch(logout())} className="flex items-center hover:text-red-200 px-3 py-1 bg-orange-700 rounded transition-colors"><LogOut className="w-4 h-4 mr-2" /> Logout</button>
                </div>
            </nav>

            <main className="flex-1 max-w-7xl w-full mx-auto p-6 md:p-8">
                {/* Header Section */}
                <div className="mb-10">
                    <h1 className="text-3xl font-bold text-gray-900">Welcome back, Student!</h1>
                    <p className="text-gray-600 mt-2 text-lg">Your next exam is coming up in 12 days. Let's keep preparing.</p>
                </div>

                {/* Dashboard Stats */}
                <div className="grid grid-cols-1 md:grid-cols-3 gap-6 mb-10">
                    <div className="bg-white p-6 rounded-xl shadow-sm border border-gray-100 flex items-center">
                        <div className="bg-orange-100 p-4 rounded-full text-orange-600 mr-4"><BookOpen className="w-8 h-8" /></div>
                        <div>
                            <p className="text-sm font-medium text-gray-500">Tests Attempted</p>
                            <p className="text-2xl font-bold text-gray-900">14</p>
                        </div>
                    </div>
                    <div className="bg-white p-6 rounded-xl shadow-sm border border-gray-100 flex items-center">
                        <div className="bg-green-100 p-4 rounded-full text-green-600 mr-4"><Award className="w-8 h-8" /></div>
                        <div>
                            <p className="text-sm font-medium text-gray-500">Avg Percentile</p>
                            <p className="text-2xl font-bold text-gray-900">88.5%</p>
                        </div>
                    </div>
                    <div className="bg-white p-6 rounded-xl shadow-sm border border-gray-100 flex items-center">
                        <div className="bg-blue-100 p-4 rounded-full text-blue-600 mr-4"><Clock className="w-8 h-8" /></div>
                        <div>
                            <p className="text-sm font-medium text-gray-500">Study Hours</p>
                            <p className="text-2xl font-bold text-gray-900">42h</p>
                        </div>
                    </div>
                </div>

                {/* Test Listings */}
                <div>
                    <div className="flex justify-between items-center mb-6">
                        <h2 className="text-2xl font-bold text-gray-900">Recommended Test Series</h2>
                        <button className="text-orange-600 font-medium hover:text-orange-700">View All</button>
                    </div>

                    <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
                        {MOCK_TESTS.map(test => (
                            <div key={test.id} className="bg-white rounded-xl shadow-sm border border-gray-100 overflow-hidden hover:shadow-md transition-shadow">
                                <div className="p-6">
                                    <div className="flex justify-between items-start mb-4">
                                        <span className={`px-3 py-1 text-xs font-bold uppercase rounded-full ${test.isFree ? 'bg-green-100 text-green-800' : 'bg-orange-100 text-orange-800'}`}>
                                            {test.isFree ? 'Free' : 'Premium'}
                                        </span>
                                        <span className="font-bold text-gray-900 text-lg">{test.price}</span>
                                    </div>
                                    <h3 className="text-xl font-bold text-gray-900 mb-2">{test.title}</h3>
                                    <p className="text-sm text-gray-500 mb-4">{test.tags}</p>

                                    <div className="flex space-x-4 text-sm text-gray-600 mb-6">
                                        <span className="flex items-center"><BookOpen className="w-4 h-4 mr-1 text-gray-400" /> {test.questions} Qs</span>
                                        <span className="flex items-center"><Clock className="w-4 h-4 mr-1 text-gray-400" /> {test.mins} Mins</span>
                                    </div>
                                </div>
                                <div className="border-t border-gray-100 p-4 bg-gray-50">
                                    <Link to="/mock-test" className="w-full flex justify-center items-center text-orange-600 font-medium hover:text-orange-700">
                                        Start Test <ChevronRight className="w-4 h-4 ml-1" />
                                    </Link>
                                </div>
                            </div>
                        ))}
                    </div>
                </div>
            </main>
        </div>
    );
};
