import axios from 'axios';
import AsyncStorage from '@react-native-async-storage/async-storage';

export const API_BASE_URL = process.env.EXPO_PUBLIC_API_URL || 'https://api.pariksha365.in/api/v1';

export const api = axios.create({
    baseURL: API_BASE_URL,
    headers: {
        'Content-Type': 'application/json',
    },
});

// Auto-attach token to every request
api.interceptors.request.use(async (config) => {
    const token = await AsyncStorage.getItem('token');
    if (token && config.headers) {
        config.headers.Authorization = `Bearer ${token}`;
    }
    return config;
});

export const AuthAPI = {
    login: (email: string, password: string) => api.post('/auth/login', { email, password }),
    signup: (name: string, email: string, password: string) => api.post('/auth/signup', { name, email, password }),
    googleLogin: (token: string) => api.post('/auth/google', { token }),
};

export const UserAPI = {
    getMe: () => api.get('/users/me'),
    updateMe: (data: { name?: string; phone?: string }) => api.put('/users/me', data),
    changePassword: (old_password: string, new_password: string) => api.put('/users/me/password', { old_password, new_password }),
    getEnrollments: () => api.get('/users/me/enrollments'),
    updateExamPreference: (categoryId: string) => api.put('/users/me/exam-preference', { selected_exam_category_id: categoryId }),
};

export const AnalyticsAPI = {
    getAttemptAnalytics: (attemptId: string) => api.get(`/analytics/attempt/${attemptId}`),
    getSeriesAnalytics: (courseId: string) => api.get(`/analytics/series/${courseId}`),
    getHierarchy: () => api.get('/analytics/hierarchy'),
    getCourseOverallAnalytics: (courseId: string) => api.get(`/analytics/course/${courseId}/overall`),
    getSpecificTestAnalytics: (courseId: string, testSeriesId: string) => api.get(`/analytics/course/${courseId}/test/${testSeriesId}`),
    getPostTestResults: (attemptId: string) => api.get(`/analytics/attempt/${attemptId}/results`)
};

export const CourseAPI = {
    list: (category?: string) => api.get('/courses', { params: category ? { subcategory_id: category } : {} }),
    getById: (id: string) => api.get(`/courses/${id}`),
    enroll: (courseId: string) => api.post(`/courses/${courseId}/enroll`),
};

export const CategoryAPI = {
    list: () => api.get('/categories'),
};

export const AttemptAPI = {
    list: () => api.get('/attempts'),
    start: (test_series_id: string) => api.post(`/attempts/start/${test_series_id}`),
    saveAnswer: (attemptId: string, data: any) => api.post(`/attempts/${attemptId}/answers`, data),
    submit: (attemptId: string) => api.post(`/attempts/${attemptId}/submit`),
    getAnswers: (attemptId: string) => api.get(`/attempts/${attemptId}/answers`),
};

export const SearchAPI = {
    globalSearch: (query: string) => api.get(`/search?q=${query}`)
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
};

