import { createSlice, createAsyncThunk } from '@reduxjs/toolkit';
import { api } from '../../services/api';

interface TestSeriesState {
    tests: any[];
    currentTest: any | null;
    loading: boolean;
    error: string | null;
}

const initialState: TestSeriesState = {
    tests: [],
    currentTest: null,
    loading: false,
    error: null,
};

export const fetchTests = createAsyncThunk(
    'testSeries/fetchTests',
    async (_, { rejectWithValue }) => {
        try {
            // Need to change depending on user role. Admin gets all, Student gets published
            const response = await api.get('/tests/');
            return response.data;
        } catch (error: any) {
            return rejectWithValue(error.response.data);
        }
    }
);

const testSeriesSlice = createSlice({
    name: 'testSeries',
    initialState,
    reducers: {},
    extraReducers: (builder) => {
        builder
            .addCase(fetchTests.pending, (state) => {
                state.loading = true;
                state.error = null;
            })
            .addCase(fetchTests.fulfilled, (state, action) => {
                state.loading = false;
                state.tests = action.payload;
            })
            .addCase(fetchTests.rejected, (state, action: any) => {
                state.loading = false;
                state.error = action.payload?.detail || 'Failed to fetch tests';
            });
    },
});

export default testSeriesSlice.reducer;
