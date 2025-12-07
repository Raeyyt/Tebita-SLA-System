import { useState, useEffect } from 'react';
import { useAuth } from '../contexts/AuthContext';
import { api } from '../services/api';
import { Link } from 'react-router-dom';

interface AdminDashboardData {
    role: string;
    summary: {
        total_requests: number;
        pending: number;
        in_progress: number;
        completed: number;
    };
    divisions: Array<{
        id: number;
        name: string;
        total_requests: number;
    }>;
    departments: Array<{
        id: number;
        name: string;
        division_id: number;
        total_requests: number;
    }>;
    recent_requests: Array<{
        id: number;
        request_id: string;
        status: string;
        created_at: string;
    }>;
}

interface RealTimeKPIs {
    total_requests: number;
    sla_compliance_rate: number;
    avg_resolution_time_hours: number;
    pending_requests: number;
    priority_breakdown: {
        high: number;
        medium: number;
        low: number;
    };
}

export const AdminDashboardPage = () => {
    const { token } = useAuth();
    const [data, setData] = useState<AdminDashboardData | null>(null);
    const [kpis, setKpis] = useState<RealTimeKPIs | null>(null);
    const [loading, setLoading] = useState(true);
    const [error, setError] = useState('');

    useEffect(() => {
        const loadData = async () => {
            if (!token) return;
            try {
                const [dashboardData, kpiData] = await Promise.all([
                    api.getAdminDashboard(token),
                    api.getRealTimeKPIs(token)
                ]);
                setData(dashboardData);
                setKpis(kpiData);
            } catch (err) {
                setError('Failed to load dashboard data');
                console.error(err);
            } finally {
                setLoading(false);
            }
        };
        loadData();

        // Poll for real-time updates every 30 seconds
        const interval = setInterval(async () => {
            if (!token) return;
            try {
                const kpiData = await api.getRealTimeKPIs(token);
                setKpis(kpiData);
            } catch (err) {
                console.error('Error polling KPIs:', err);
            }
        }, 30000);

        return () => clearInterval(interval);
    }, [token]);

    if (loading) return <div className="container">Loading...</div>;
    if (error) return <div className="container"><div className="alert alert-error">{error}</div></div>;
    if (!data) return <div className="container"><div className="alert alert-error">No data available</div></div>;

    return (
        <div className="container">
            <div className="page-header">
                <h1 className="page-title">System Dashboard</h1>
                <p className="page-subtitle">Administrator Overview</p>
            </div>

            {/* Real-Time SLA Overview */}
            {kpis && (
                <div className="card" style={{ marginBottom: '2rem', borderLeft: '4px solid var(--primary)' }}>
                    <div className="card-header" style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
                        <h3 className="card-title" style={{ display: 'flex', alignItems: 'center', gap: '0.5rem' }}>
                            <span style={{
                                display: 'inline-block',
                                width: '10px',
                                height: '10px',
                                borderRadius: '50%',
                                background: '#e74c3c',
                                boxShadow: '0 0 0 2px rgba(231, 76, 60, 0.2)'
                            }}></span>
                            Real-Time SLA Engine
                        </h3>
                        <span style={{ fontSize: '0.8rem', color: 'var(--gray-500)' }}>Auto-refreshing every 30s</span>
                    </div>
                    <div style={{ padding: '1.5rem' }}>
                        <div className="grid grid-4" style={{ gap: '1.5rem' }}>
                            <div style={{ textAlign: 'center' }}>
                                <div style={{ fontSize: '2rem', fontWeight: '700', color: kpis.sla_compliance_rate >= 90 ? 'var(--success)' : 'var(--warning)' }}>
                                    {kpis.sla_compliance_rate}%
                                </div>
                                <div style={{ fontSize: '0.9rem', color: 'var(--gray-600)' }}>SLA Compliance</div>
                            </div>
                            <div style={{ textAlign: 'center' }}>
                                <div style={{ fontSize: '2rem', fontWeight: '700', color: 'var(--primary)' }}>
                                    {kpis.avg_resolution_time_hours}h
                                </div>
                                <div style={{ fontSize: '0.9rem', color: 'var(--gray-600)' }}>Avg Resolution</div>
                            </div>
                            <div style={{ textAlign: 'center' }}>
                                <div style={{ fontSize: '2rem', fontWeight: '700', color: '#e74c3c' }}>
                                    {kpis.priority_breakdown.high}
                                </div>
                                <div style={{ fontSize: '0.9rem', color: 'var(--gray-600)' }}>High Priority</div>
                            </div>
                            <div style={{ textAlign: 'center' }}>
                                <div style={{ fontSize: '2rem', fontWeight: '700', color: 'var(--gray-700)' }}>
                                    {kpis.pending_requests}
                                </div>
                                <div style={{ fontSize: '0.9rem', color: 'var(--gray-600)' }}>Active Requests</div>
                            </div>
                        </div>
                    </div>
                </div>
            )}

            {/* System-Wide Summary */}
            <div className="grid grid-4" style={{ marginBottom: '2rem' }}>
                <div className="card">
                    <div style={{ padding: '1.5rem', textAlign: 'center' }}>
                        <div style={{ fontSize: '2.5rem', fontWeight: '700', color: 'var(--primary)' }}>
                            {data.summary.total_requests}
                        </div>
                        <p className="text-muted">Total Requests</p>
                    </div>
                </div>
                <div className="card">
                    <div style={{ padding: '1.5rem', textAlign: 'center' }}>
                        <div style={{ fontSize: '2.5rem', fontWeight: '700', color: 'var(--warning)' }}>
                            {data.summary.pending}
                        </div>
                        <p className="text-muted">Pending</p>
                    </div>
                </div>
                <div className="card">
                    <div style={{ padding: '1.5rem', textAlign: 'center' }}>
                        <div style={{ fontSize: '2.5rem', fontWeight: '700', color: 'var(--info)' }}>
                            {data.summary.in_progress}
                        </div>
                        <p className="text-muted">In Progress</p>
                    </div>
                </div>
                <div className="card">
                    <div style={{ padding: '1.5rem', textAlign: 'center' }}>
                        <div style={{ fontSize: '2.5rem', fontWeight: '700', color: 'var(--success)' }}>
                            {data.summary.completed}
                        </div>
                        <p className="text-muted">Completed</p>
                    </div>
                </div>
            </div>

            {/* Division Overview */}
            <div className="card" style={{ marginBottom: '2rem' }}>
                <div className="card-header">
                    <h3 className="card-title">Division Overview</h3>
                </div>
                <div style={{ padding: '1.5rem' }}>
                    <div className="grid grid-3" style={{ gap: '1rem' }}>
                        {data.divisions.map(div => (
                            <div key={div.id} className="card">
                                <div style={{ padding: '1.5rem' }}>
                                    <div style={{ fontWeight: '600', fontSize: '1.1rem', marginBottom: '0.5rem' }}>
                                        {div.name}
                                    </div>
                                    <div style={{ fontSize: '1.5rem', fontWeight: '700', color: 'var(--primary)' }}>
                                        {div.total_requests} <span style={{ fontSize: '0.875rem', color: 'var(--gray-500)' }}>requests</span>
                                    </div>
                                </div>
                            </div>
                        ))}
                    </div>
                </div>
            </div>

            {/* Department Overview */}
            <div className="card">
                <div className="card-header">
                    <h3 className="card-title">Department Overview</h3>
                </div>
                <div style={{ padding: '1.5rem' }}>
                    <div className="grid grid-4" style={{ gap: '1rem' }}>
                        {data.departments.map(dept => (
                            <div key={dept.id} className="card">
                                <div style={{ padding: '1rem' }}>
                                    <div style={{ fontWeight: '600', fontSize: '0.95rem', marginBottom: '0.5rem' }}>
                                        {dept.name}
                                    </div>
                                    <div style={{ fontSize: '1.25rem', fontWeight: '700', color: 'var(--primary)' }}>
                                        {dept.total_requests}
                                    </div>
                                </div>
                            </div>
                        ))}
                    </div>
                </div>
            </div>

            {/* Quick Actions */}
            <div className="grid grid-4" style={{ marginTop: '2rem', gap: '1rem' }}>
                <Link to="/requests" className="btn btn-primary" style={{ padding: '1.5rem' }}>
                    All Requests
                </Link>
                <Link to="/analytics" className="btn btn-outline" style={{ padding: '1.5rem' }}>
                    Analytics
                </Link>
                <Link to="/kpis" className="btn btn-outline" style={{ padding: '1.5rem' }}>
                    KPIs & Scorecard
                </Link>
                <Link to="/ratings" className="btn btn-outline" style={{ padding: '1.5rem' }}>
                    Department Ratings
                </Link>
                <Link to="/sla" className="btn btn-outline" style={{ padding: '1.5rem' }}>
                    SLA Monitoring
                </Link>
            </div>
        </div>
    );
};
