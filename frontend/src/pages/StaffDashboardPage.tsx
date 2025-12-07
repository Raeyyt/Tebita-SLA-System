import { useState, useEffect } from 'react';
import { useAuth } from '../contexts/AuthContext';
import { api } from '../services/api';
import { Link } from 'react-router-dom';

interface StaffDashboardData {
    role: string;
    summary: {
        sent_requests: number;
        received_requests: number;
        pending_to_handle: number;
    };
}

export const StaffDashboardPage = () => {
    const { token } = useAuth();
    const [data, setData] = useState<StaffDashboardData | null>(null);
    const [loading, setLoading] = useState(true);
    const [error, setError] = useState('');

    useEffect(() => {
        const loadData = async () => {
            if (!token) return;
            try {
                const dashboardData = await api.getStaffDashboard(token);
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

    if (loading) {
        return <div className="container">Loading...</div>;
    }

    if (error) {
        return <div className="container"><div className="alert alert-error">{error}</div></div>;
    }

    if (!data) {
        return <div className="container"><div className="alert alert-error">No data available</div></div>;
    }

    return (
        <div className="container">
            <div className="page-header">
                <h1 className="page-title">My Dashboard</h1>
                <p className="page-subtitle">Track your requests and activity</p>
            </div>

            {/* Quick Stats */}
            <div className="grid grid-3" style={{ marginBottom: '2rem' }}>
                <div className="card">
                    <div className="card-header">
                        <h3 className="card-title">Requests I Sent</h3>
                    </div>
                    <div style={{ padding: '2rem', textAlign: 'center' }}>
                        <div style={{ fontSize: '3rem', fontWeight: '700', color: 'var(--primary)' }}>
                            {data.summary.sent_requests}
                        </div>
                        <p className="text-muted">Total requests submitted</p>
                        <Link to="/requests/sent" className="btn btn-outline" style={{ marginTop: '1rem' }}>
                            View All
                        </Link>
                    </div>
                </div>

                <div className="card">
                    <div className="card-header">
                        <h3 className="card-title">Requests Received</h3>
                    </div>
                    <div style={{ padding: '2rem', textAlign: 'center' }}>
                        <div style={{ fontSize: '3rem', fontWeight: '700', color: 'var(--success)' }}>
                            {data.summary.received_requests}
                        </div>
                        <p className="text-muted">Requests to my unit</p>
                        <Link to="/requests/inbox" className="btn btn-outline" style={{ marginTop: '1rem' }}>
                            View Inbox
                        </Link>
                    </div>
                </div>

                <div className="card">
                    <div className="card-header">
                        <h3 className="card-title">Pending Action</h3>
                    </div>
                    <div style={{ padding: '2rem', textAlign: 'center' }}>
                        <div style={{ fontSize: '3rem', fontWeight: '700', color: 'var(--warning)' }}>
                            {data.summary.pending_to_handle}
                        </div>
                        <p className="text-muted">Awaiting your response</p>
                        <Link to="/requests/inbox" className="btn btn-primary" style={{ marginTop: '1rem' }}>
                            Handle Now
                        </Link>
                    </div>
                </div>
            </div>

            {/* Quick Actions */}
            <div className="card">
                <div className="card-header">
                    <h3 className="card-title">Quick Actions</h3>
                </div>
                <div style={{ padding: '1.5rem' }}>
                    <div className="grid grid-2" style={{ gap: '1rem' }}>
                        <Link to="/requests/new" className="btn btn-primary" style={{ padding: '1.5rem' }}>
                            <div style={{ fontSize: '1.1rem', fontWeight: '600' }}>New Request</div>
                            <div style={{ fontSize: '0.875rem', marginTop: '0.5rem', opacity: 0.9 }}>
                                Submit a new service request
                            </div>
                        </Link>
                        <Link to="/requests/inbox" className="btn btn-outline" style={{ padding: '1.5rem' }}>
                            <div style={{ fontSize: '1.1rem', fontWeight: '600' }}>View Inbox</div>
                            <div style={{ fontSize: '0.875rem', marginTop: '0.5rem', opacity: 0.9 }}>
                                Check incoming requests
                            </div>
                        </Link>
                    </div>
                </div>
            </div>
        </div>
    );
};
