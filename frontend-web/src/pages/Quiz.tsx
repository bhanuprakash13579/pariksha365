import { DailyQuizzes } from '../components/dashboard/DailyQuizzes';

/**
 * Quiz page — redirects to the DailyQuizzes component.
 * This page existed as a standalone route; now it reuses the dashboard component
 * to avoid duplicate hardcoded data.
 */
export const Quiz = () => {
    return <DailyQuizzes />;
};
