import { DailyQuizzes } from '../components/dashboard/DailyQuizzes';

/**
 * Standalone Quiz route. The private-module "Invite-only" card and the swap
 * into the module-scoped quiz view now live inside DailyQuizzes itself, so
 * this route and the Dashboard's quiz tab behave identically.
 */
export const Quiz = () => {
    return <DailyQuizzes />;
};
