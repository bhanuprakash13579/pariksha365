import axios from 'axios';
import AsyncStorage from '@react-native-async-storage/async-storage';

export const API_BASE_URL = 'https://pariksha365-backend-production.up.railway.app/api/v1';

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
};

export const UserAPI = {
    getMe: () => api.get('/users/me'),
    updateMe: (data: { name?: string; phone?: string }) => api.put('/users/me', data),
    changePassword: (old_password: string, new_password: string) => api.put('/users/me/password', { old_password, new_password }),
};

export const CourseAPI = {
    list: (category?: string) => api.get('/courses', { params: category ? { category } : {} }),
    getById: (id: string) => api.get(`/courses/${id}`),
};

export const AttemptAPI = {
    list: () => api.get('/attempts'),
    start: (test_series_id: string) => api.post(`/attempts/start/${test_series_id}`),
    saveAnswer: (attemptId: string, data: any) => api.post(`/attempts/${attemptId}/answers`, data),
    submit: (attemptId: string) => api.post(`/attempts/${attemptId}/submit`),
};
