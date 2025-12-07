import type { ReactNode } from 'react';
import { Navigate } from 'react-router-dom';
import { useAuth } from '../contexts/AuthContext';
import type { UserRole } from '../types';

interface ProtectedRouteProps {
    children: ReactNode;
    roles?: UserRole[];
}

export const ProtectedRoute = ({ children, roles }: ProtectedRouteProps) => {
    const { user, token, loading } = useAuth();

    if (loading) {
        return (
            <div className="flex-center" style={{ minHeight: '100vh' }}>
                <div className="spinner"></div>
            </div>
        );
    }

    if (!token || !user) {
        return <Navigate to="/login" replace />;
    }

    if (roles && !roles.includes(user.role)) {
        return (
            <div className="flex-center" style={{ minHeight: '100vh' }}>
                <div className="alert alert-error">
                    You do not have permission to access this page.
                </div>
            </div>
        );
    }

    return <>{children}</>;
};
