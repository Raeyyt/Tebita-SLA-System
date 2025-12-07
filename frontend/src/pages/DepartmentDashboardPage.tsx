import { useState, useEffect } from 'react';
import { useAuth } from '../contexts/AuthContext';
import { api } from '../services/api';
import { Link } from 'react-router-dom';

interface DepartmentDashboardData {
    role: string;
    department: {
        id: number;
        name: string;
        division_id: number;
    };
    summary: {
        total_requests: number;
        pending: number;
        in_progress: number;
        completed: number;
    };
    subdepartments: Array<{
        id: number;
        name: string;
        total_requests: number;
    }>;
}

export const DepartmentDashboardPage = () => {
    const { token } = useAuth();
    const [data, setData] = useState<DepartmentDashboardData | null>(null);
    const [loading, setLoading] = useState(true);
    const [error, setError] = useState('');

    useEffect(() => {
        const loadData = async () => {
            if (!token) return;
            try {
                const dashboardData = await api.getDepartmentDashboard(token);
                setData(dashboardData);
            } catch (err) {
                setError('Failed to load dashboard data');
                console.error(err);
            } finally {
                setLoading(false);
            }
        };
        loadData();
    }, [token]);

    if (loading) return <div className="container">Loading...</div>;
    if (error) return <div className="container"><div className="alert alert-error">{error}</div></div>;
    if (!data) return <div className="container"><div className="alert alert-error">No data available</div></div>;

    return (
        <div className="container">
            <div className="page-header">
                <h1 className="page-title">{data.department.name} - Department Dashboard</h1>
                <p className="page-subtitle">Manage and monitor your department</p>
            </div>

            {/* Summary Stats */}
            <div className="grid grid-4" style={{ marginBottom: '2rem' }}>
                <div className="card">
                    <div style={{ padding: '1.5rem', textAlign: 'center' }}>
                        <div style={{ fontSize: '2rem', fontWeight: '700', color: 'var(--primary)' }}>
                            {data.summary.total_requests}
                        </div>
                        <p className="text-muted">Total Requests</p>
                    </div>
                </div>
                <div className="card">
                    <div style={{ padding: '1.5rem', textAlign: 'center' }}>
                        <div style={{ fontSize: '2rem', fontWeight: '700', color: 'var(--warning)' }}>
                            {data.summary.pending}
                        </div>
                        <p className="text-muted">Pending</p>
                    </div>
                </div>
                <div className="card">
                    <div style={{ padding: '1.5rem', textAlign: 'center' }}>
                        <div style={{ fontSize: '2rem', fontWeight: '700', color: 'var(--info)' }}>
                            {data.summary.in_progress}
                        </div>
                        <p className="text-muted">In Progress</p>
                    </div>
                </div>
                <div className="card">
                    <div style={{ padding: '1.5rem', textAlign: 'center' }}>
                        <div style={{ fontSize: '2rem', fontWeight: '700', color: 'var(--success)' }}>
                            {data.summary.completed}
                        </div>
                        <p className="text-muted">Completed</p>
                    </div>
                </div>
            </div>

            {/* Sub-Departments */}
            <div className="card">
                <div className="card-header">
                    <h3 className="card-title">Sub-Department Performance</h3>
                </div>
                <div style={{ padding: '1.5rem' }}>
                    {data.subdepartments.length > 0 ? (
                        <div className="grid grid-2" style={{ gap: '1rem' }}>
                            {data.subdepartments.map(subdept => (
                                <div key={subdept.id} className="card">
                                    <div style={{ padding: '1.5rem' }}>
                                        <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
                                            <div>
                                                <div style={{ fontWeight: '600', fontSize: '1.1rem' }}>
                                                    {subdept.name}
                                                </div>
                                                <div className="text-muted" style={{ fontSize: '0.875rem', marginTop: '0.25rem' }}>
                                                    Sub-Department
                                                </div>
                                            </div>
                                            <div style={{ textAlign: 'right' }}>
                                                <div style={{ fontSize: '1.5rem', fontWeight: '700', color: 'var(--primary)' }}>
                                                    {subdept.total_requests}
                                                </div>
                                                <div className="text-muted" style={{ fontSize: '0.75rem' }}>
                                                    requests
                                                </div>
                                            </div>
                                        </div>
                                    </div>
                                </div>
                            ))}
                        </div>
                    ) : (
                        <p className="text-muted">No sub-departments found</p>
                    )}
                </div>
            </div>

            {/* Quick Actions */}
            <div className="grid grid-2" style={{ marginTop: '2rem' }}>
                <Link to="/requests" className="btn btn-primary" style={{ padding: '1.5rem' }}>
                    View All Requests
                </Link>
                <Link to="/requests/inbox" className="btn btn-outline" style={{ padding: '1.5rem' }}>
                    Department Inbox
                </Link>
            </div>
        </div>
    );
};
