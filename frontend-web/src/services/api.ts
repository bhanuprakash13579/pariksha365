import axios from 'axios';

const API_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000/api/v1';

export const api = axios.create({
    baseURL: API_URL,
    headers: {
        'Content-Type': 'application/json',
    },
});

api.interceptors.request.use((config) => {
    const token = localStorage.getItem('token');
    if (token && config.headers) {
        config.headers.Authorization = `Bearer ${token}`;
    }
    return config;
});

export const UserAPI = {
    getMe: () => api.get('/users/me'),
    updateMe: (data: { name?: string; phone?: string }) => api.put('/users/me', data),
    getEnrollments: () => api.get('/users/me/enrollments'),
    changePassword: (old_password: string, new_password: string) => api.put('/users/me/password', { old_password, new_password }),
    updateExamPreference: (categoryId: string) => api.put('/users/me/exam-preference', { selected_exam_category_id: categoryId }),
};

export const TestAPI = {
    list: (category?: string) => api.get('/tests', { params: category ? { category } : {} }),
    getById: (id: string) => api.get(`/tests/${id}`),
};

export const AttemptAPI = {
    list: () => api.get('/attempts'),
    start: (test_series_id: string) => api.post('/attempts/start', { test_series_id }),
    saveAnswer: (attemptId: string, data: any) => api.post(`/attempts/${attemptId}/answers`, data),
    submit: (attemptId: string) => api.post(`/attempts/${attemptId}/submit`),
    getAnswers: (attemptId: string) => api.get(`/attempts/${attemptId}/answers`),
};

export const AnalyticsAPI = {
    getSeriesAnalytics: (seriesId: string) => api.get(`/analytics/series/${seriesId}`),
    getHierarchy: () => api.get('/analytics/hierarchy'),
    getCourseOverallAnalytics: (courseId: string) => api.get(`/analytics/course/${courseId}/overall`),
    getSpecificTestAnalytics: (courseId: string, testSeriesId: string) => api.get(`/analytics/course/${courseId}/test/${testSeriesId}`),
    getPostTestResults: (attemptId: string) => api.get(`/analytics/attempt/${attemptId}/results`)
};

export const SearchAPI = {
    globalSearch: (query: string) => api.get(`/search?q=${query}`)
};

export const CategoryAPI = {
    list: () => api.get('/categories')
};

export const CourseAPI = {
    list: () => api.get('/courses'),
    getById: (id: string) => api.get(`/courses/${id}`),
    enroll: (courseId: string) => api.post(`/courses/${courseId}/enroll`),
};

export const QuizAPI = {
    getCategories: () => api.get('/quiz/categories'),
    getDailyQuiz: (subject: string, limit?: number) => api.get(`/quiz/daily/${subject}`, { params: limit ? { limit } : {} }),
    getWeakTopicQuiz: (limit?: number) => api.get('/quiz/weak-topics', { params: limit ? { limit } : {} }),
    getMorePractice: (subject: string, topic?: string, excludeIds?: string[]) =>
        api.post(`/quiz/more-practice?subject=${encodeURIComponent(subject)}${topic ? `&topic=${encodeURIComponent(topic)}` : ''}&exclude_ids=${(excludeIds || []).join(',')}`),
    submitQuiz: (answers: { question_id: string; selected_option_index: number | null }[]) =>
        api.post('/quiz/submit', { answers }),
    getStreak: () => api.get('/quiz/streak'),
    getWeakTopicsList: () => api.get('/quiz/weak-topics/list'),
    // Admin CRUD
    adminListQuestions: (params?: { subject?: string; topic?: string; search?: string; page?: number; per_page?: number }) =>
        api.get('/quiz/admin/questions', { params }),
    adminCreateQuestion: (data: any) => api.post('/quiz/admin/questions', data),
    adminUpdateQuestion: (id: string, data: any) => api.put(`/quiz/admin/questions/${id}`, data),
    adminDeleteQuestion: (id: string) => api.delete(`/quiz/admin/questions/${id}`),
    // Bulk upload
    adminBulkUpload: (questions: any[]) => api.post('/quiz/admin/bulk-upload', { questions }),
    // Taxonomy
    adminGetTaxonomy: () => api.get('/quiz/admin/taxonomy'),
    adminGetTopicCodes: () => api.get('/quiz/admin/taxonomy/codes'),
    adminCreateTaxonomy: (data: { subject: string; topic: string; topic_code: string; aliases?: string[] }) => api.post('/quiz/admin/taxonomy', data),
    adminUpdateTaxonomy: (id: string, data: any) => api.put(`/quiz/admin/taxonomy/${id}`, data),
    adminDeleteTaxonomy: (id: string) => api.delete(`/quiz/admin/taxonomy/${id}`),
    adminSeedTaxonomy: () => api.post('/quiz/admin/taxonomy/seed'),
};
