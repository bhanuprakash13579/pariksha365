import { configureStore } from '@reduxjs/toolkit';
import authReducer from './slices/authSlice';
import testSeriesReducer from './slices/testSeriesSlice';

export const store = configureStore({
    reducer: {
        auth: authReducer,
        testSeries: testSeriesReducer,
    },
});

export type RootState = ReturnType<typeof store.getState>;
export type AppDispatch = typeof store.dispatch;
