import { Settings, Users, FileText, Activity } from 'lucide-react';

export const AdminDashboard = () => {
    return (
        <div className="flex h-screen bg-gray-100 dark:bg-gray-900">
            {/* Sidebar */}
            <aside className="w-64 bg-white dark:bg-gray-800 shadow-md">
                <div className="p-4">
                    <h2 className="text-2xl font-bold text-blue-600">AdminPanel</h2>
                </div>
                <nav className="mt-4">
                    <a href="#" className="flex items-center px-4 py-3 text-gray-700 dark:text-gray-200 bg-gray-100 dark:bg-gray-700">
                        <Activity className="w-5 h-5 mr-3" /> Dashboard
                    </a>
                    <a href="#" className="flex items-center px-4 py-3 text-gray-600 dark:text-gray-400 hover:bg-gray-50 dark:hover:bg-gray-700">
                        <Users className="w-5 h-5 mr-3" /> Users
                    </a>
                    <a href="#" className="flex items-center px-4 py-3 text-gray-600 dark:text-gray-400 hover:bg-gray-50 dark:hover:bg-gray-700">
                        <FileText className="w-5 h-5 mr-3" /> Test Series
                    </a>
                    <a href="#" className="flex items-center px-4 py-3 text-gray-600 dark:text-gray-400 hover:bg-gray-50 dark:hover:bg-gray-700">
                        <Settings className="w-5 h-5 mr-3" /> Settings
                    </a>
                </nav>
            </aside>

            {/* Main Content */}
            <main className="flex-1 p-8 overflow-y-auto">
                <h1 className="text-3xl font-semibold text-gray-800 dark:text-white mb-6">Dashboard Overview</h1>

                <div className="grid grid-cols-1 md:grid-cols-4 gap-6 mb-8">
                    {[
                        { label: 'Total Users', value: '12,345' },
                        { label: 'Revenue', value: '₹4,50,000' },
                        { label: 'Active Tests', value: '142' },
                        { label: 'Recent Payments', value: '89' },
                    ].map((stat, i) => (
                        <div key={i} className="bg-white dark:bg-gray-800 p-6 rounded-lg shadow-sm border border-gray-100 dark:border-gray-700">
                            <h3 className="text-gray-500 text-sm font-medium">{stat.label}</h3>
                            <p className="text-3xl font-bold text-gray-800 dark:text-white mt-2">{stat.value}</p>
                        </div>
                    ))}
                </div>

                <div className="bg-white dark:bg-gray-800 rounded-lg shadow-sm border border-gray-100 dark:border-gray-700 p-6">
                    <h3 className="text-lg font-semibold text-gray-800 dark:text-white mb-4">Recent Tests</h3>
                    <p className="text-gray-500">List of recently created tests will go here...</p>
                </div>
            </main>
        </div>
    );
};
