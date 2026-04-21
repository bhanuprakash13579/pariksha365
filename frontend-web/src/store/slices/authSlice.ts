import { createSlice, createAsyncThunk } from '@reduxjs/toolkit';
import { api } from '../../services/api';

interface AuthState {
    user: any | null;
    token: string | null;
    loading: boolean;
    error: string | null;
}

const initialState: AuthState = {
    user: null,
    token: localStorage.getItem('token'),
    loading: false,
    error: null,
};

export const loginUser = createAsyncThunk(
    'auth/login',
    async (credentials: any, { rejectWithValue }) => {
        try {
            const response = await api.post('/auth/login', credentials);
            localStorage.setItem('token', response.data.access_token);
            return response.data;
        } catch (error: any) {
            return rejectWithValue(error.response.data);
        }
    }
);

export const signupUser = createAsyncThunk(
    'auth/signup',
    async (userData: { name: string; email: string; password: string }, { rejectWithValue }) => {
        try {
            const response = await api.post('/auth/signup', userData);
            return response.data;
        } catch (error: any) {
            return rejectWithValue(error.response?.data || { detail: 'Signup failed' });
        }
    }
);

export const googleLogin = createAsyncThunk(
    'auth/google',
    async (token: string, { rejectWithValue }) => {
        try {
            const response = await api.post('/auth/google', { token });
            localStorage.setItem('token', response.data.access_token);
            return response.data;
        } catch (error: any) {
            // Surface the real cause when possible — network error, 401, 500 etc.
            // Makes production debugging much easier than the previous opaque
            // "Google Login failed" string.
            const backendDetail = error?.response?.data?.detail;
            const status = error?.response?.status;
            const msg = error?.message;
            const combined =
                backendDetail ||
                (status ? `Google login failed (HTTP ${status})` : undefined) ||
                msg ||
                'Google Login failed';
            // eslint-disable-next-line no-console
            console.error('[Google login] error', {
                status,
                backendDetail,
                msg,
                data: error?.response?.data,
            });
            return rejectWithValue({ detail: combined });
        }
    }
);

const authSlice = createSlice({
    name: 'auth',
    initialState,
    reducers: {
        logout: (state) => {
            state.user = null;
            state.token = null;
            localStorage.removeItem('token');
        },
    },
    extraReducers: (builder) => {
        builder
            .addCase(loginUser.pending, (state) => {
                state.loading = true;
                state.error = null;
            })
            .addCase(loginUser.fulfilled, (state, action) => {
                state.loading = false;
                state.token = action.payload.access_token;
            })
            .addCase(loginUser.rejected, (state, action: any) => {
                state.loading = false;
                state.error = action.payload?.detail || 'Login failed';
            })
            .addCase(googleLogin.pending, (state) => {
                state.loading = true;
                state.error = null;
            })
            .addCase(googleLogin.fulfilled, (state, action) => {
                state.loading = false;
                state.token = action.payload.access_token;
            })
            .addCase(googleLogin.rejected, (state, action: any) => {
                state.loading = false;
                state.error = action.payload?.detail || 'Google Login failed';
            });
    },
});

export const { logout } = authSlice.actions;
export default authSlice.reducer;
