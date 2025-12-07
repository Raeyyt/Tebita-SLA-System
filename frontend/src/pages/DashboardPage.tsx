import { useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import { useAuth } from '../contexts/AuthContext';

export const DashboardPage = () => {
    const { user } = useAuth();
    const navigate = useNavigate();

    useEffect(() => {
        if (!user) return;

        // Route to appropriate dashboard based on role
        switch (user.role) {
            case 'ADMIN':
                navigate('/dashboard/admin');
                break;
            case 'DIVISION_MANAGER':
                navigate('/dashboard/division');
                break;
            case 'DEPARTMENT_HEAD':
                navigate('/dashboard/department');
                break;
            case 'SUB_DEPARTMENT_STAFF':
                navigate('/dashboard/staff');
                break;
            default:
                // Fallback to staff dashboard for unknown roles
                navigate('/dashboard/staff');
        }
    }, [user, navigate]);

    return (
        <div className="container" style={{ padding: '3rem', textAlign: 'center' }}>
            <div style={{ fontSize: '1.2rem', color: 'var(--gray-600)' }}>
                Loading dashboard...
            </div>
        </div>
    );
};
