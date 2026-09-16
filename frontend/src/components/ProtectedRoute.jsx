import { Navigate } from "react-router-dom";

import { useAuth } from "../context/AuthContext";

/**
 * Guards staff/admin routes. Redirects to /login when unauthenticated,
 * and to the dashboard when an admin-only route is hit by a non-admin.
 */
export default function ProtectedRoute({ children, adminOnly = false }) {
    const { isAuthenticated, isAdmin, loading } = useAuth();

    if (loading) {
        return (
            <div className="min-h-screen flex items-center justify-center text-gray-500">
                Loading...
            </div>
        );
    }

    if (!isAuthenticated) {
        return <Navigate to="/login" replace />;
    }

    if (adminOnly && !isAdmin) {
        return <Navigate to="/staff" replace />;
    }

    return children;
}
