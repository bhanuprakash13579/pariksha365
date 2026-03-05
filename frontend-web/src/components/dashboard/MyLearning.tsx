import { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import { UserAPI, AttemptAPI } from '../../services/api';

export const MyLearning = ({ onSelectCourse }: { onSelectCourse?: (course: any) => void }) => {
    const [enrolledCourses, setEnrolledCourses] = useState<any[]>([]);
    const [attempts, setAttempts] = useState<any[]>([]);
    const [loading, setLoading] = useState(true);
    const navigate = useNavigate();

    useEffect(() => {
        const fetchData = async () => {
            try {
                const [enrollRes, attemptsRes] = await Promise.all([
                    UserAPI.getEnrollments(),
                    AttemptAPI.list()
                ]);
                setEnrolledCourses(enrollRes.data || []);
                setAttempts(attemptsRes.data || []);
            } catch (err) {
                console.error("Failed to fetch learning data:", err);
            } finally {
                setLoading(false);
            }
        };
        fetchData();
    }, []);

    // Calculate progress per course (tests attempted / total tests)
    const getCourseProgress = (course: any) => {
        if (!course.folders) return { attempted: 0, total: 0, percentage: 0 };
        let total = 0;
        let attempted = 0;
        for (const folder of course.folders) {
            if (folder.tests) {
                total += folder.tests.length;
                for (const test of folder.tests) {
                    const hasAttempt = attempts.some(
                        (a: any) => a.test_series_id === test.test_id && a.status === 'SUBMITTED'
                    );
                    if (hasAttempt) attempted++;
                }
            }
        }
        return {
            attempted,
            total,
            percentage: total > 0 ? Math.round((attempted / total) * 100) : 0
        };
    };

    if (loading) {
        return (
            <div className="flex justify-center items-center py-20">
                <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-orange-600"></div>
            </div>
        );
    }

    return (
        <div className="max-w-4xl mx-auto py-8">
            <h2 className="text-2xl font-bold text-gray-900 mb-6">My Learning</h2>

            {enrolledCourses.length === 0 ? (
                <div className="bg-white rounded-2xl p-10 text-center border border-gray-100 shadow-sm mt-4">
                    <svg className="w-16 h-16 text-gray-300 mx-auto mb-4" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 6.253v13m0-13C10.832 5.477 9.246 5 7.5 5S4.168 5.477 3 6.253v13C4.168 18.477 5.754 18 7.5 18s3.332.477 4.5 1.253m0-13C13.168 5.477 14.754 5 16.5 5c1.747 0 3.332.477 4.5 1.253v13C19.832 18.477 18.247 18 16.5 18c-1.746 0-3.332.477-4.5 1.253" /></svg>
                    <h3 className="text-lg font-medium text-gray-900">No active enrollments</h3>
                    <p className="mt-1 text-gray-500">You have not enrolled in any courses yet.</p>
                </div>
            ) : (
                <div className="grid gap-6">
                    {enrolledCourses.map((course: any) => {
                        const progress = getCourseProgress(course);
                        return (
                            <div key={course.id} className="bg-white rounded-xl p-6 border border-gray-100 shadow-sm hover:shadow-md transition-shadow">
                                <div className="flex items-start justify-between">
                                    <div className="flex-1">
                                        <h3 className="text-lg font-bold text-gray-900">{course.title}</h3>

                                        <div className="mt-4 flex items-center justify-between text-sm text-gray-500">
                                            <span>{progress.attempted} of {progress.total} tests completed</span>
                                            <span className="font-semibold text-gray-700">{progress.percentage}%</span>
                                        </div>
                                        <div className="w-full bg-gray-200 rounded-full h-2.5 mt-2">
                                            <div
                                                className={`h-2.5 rounded-full transition-all duration-500 ${progress.percentage >= 80 ? 'bg-green-500' :
                                                    progress.percentage >= 40 ? 'bg-orange-500' :
                                                        'bg-orange-400'
                                                    }`}
                                                style={{ width: `${progress.percentage}%` }}
                                            ></div>
                                        </div>

                                        {course.validity_days && (
                                            <div className="mt-4 text-sm text-gray-500 flex items-center">
                                                <svg className="w-4 h-4 mr-1" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 8v4l3 3m6-3a9 9 0 11-18 0 9 9 0 0118 0z" /></svg>
                                                Expires in: {course.validity_days} days
                                            </div>
                                        )}
                                    </div>

                                    <div className="ml-6 pl-6 border-l border-gray-100 flex items-center">
                                        <button
                                            onClick={() => onSelectCourse?.(course)}
                                            className="p-2 text-orange-600 hover:bg-orange-50 rounded-full transition-colors"
                                        >
                                            <svg className="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 5l7 7-7 7" /></svg>
                                        </button>
                                    </div>
                                </div>
                            </div>
                        );
                    })}
                </div>
            )}

            {/* Recent Attempts */}
            {attempts.length > 0 && (
                <div className="mt-10">
                    <h3 className="text-xl font-bold text-gray-900 mb-4">Recent Attempts</h3>
                    <div className="space-y-3">
                        {(() => {
                            // Deduplicate: keep only the latest attempt per test_series_id
                            const seen = new Set<string>();
                            return attempts.filter((a: any) => {
                                if (seen.has(a.test_series_id)) return false;
                                seen.add(a.test_series_id);
                                return true;
                            }).slice(0, 5);
                        })().map((attempt: any) => (
                            <div key={attempt.id}
                                onClick={() => attempt.status === 'SUBMITTED' && navigate(`/results/${attempt.id}`)}
                                className={`bg-white rounded-xl p-4 border border-gray-100 shadow-sm flex items-center justify-between ${attempt.status === 'SUBMITTED' ? 'cursor-pointer hover:shadow-md' : ''
                                    }`}
                            >
                                <div>
                                    <p className="font-semibold text-gray-900">{attempt.test_title || 'Test'}</p>
                                    <p className="text-xs text-gray-500 mt-1">
                                        {new Date(attempt.started_at).toLocaleDateString('en-IN', { day: 'numeric', month: 'short', year: 'numeric' })}
                                    </p>
                                </div>
                                <span className={`text-xs font-bold px-3 py-1 rounded-full ${attempt.status === 'SUBMITTED' ? 'bg-green-100 text-green-700' : 'bg-orange-100 text-orange-700'
                                    }`}>
                                    {attempt.status === 'SUBMITTED' ? 'View Results →' : 'In Progress'}
                                </span>
                            </div>
                        ))}
                    </div>
                </div>
            )}
        </div>
    );
};
