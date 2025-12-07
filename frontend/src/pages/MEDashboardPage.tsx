import { useState, useEffect } from 'react';
import { useAuth } from '../contexts/AuthContext';
import { api } from '../services/api';

export const MEDashboardPage = () => {
    const { token, user } = useAuth();
    const [dashboard, setDashboard] = useState<any>(null);
    const [loading, setLoading] = useState(true);
    const [downloading, setDownloading] = useState(false);
    const [downloadError, setDownloadError] = useState<string | null>(null);
    const [showAllDivisionRequests, setShowAllDivisionRequests] = useState(false);

    useEffect(() => {
        const loadDashboard = async () => {
            if (!token) return;
            try {
                const data = await api.getMEDashboard(token);
                setDashboard(data);
            } catch (err) {
                console.error('Failed to load M&E dashboard:', err);
            } finally {
                setLoading(false);
            }
        };
        loadDashboard();
    }, [token]);

    const handleDownloadLog = async () => {
        if (!token) return;
        setDownloadError(null);
        try {
            setDownloading(true);
            const blob = await api.downloadRequestActivityLog(token);
            const url = window.URL.createObjectURL(blob);
            const link = document.createElement('a');
            link.href = url;
            link.download = `request_activity_logs_${new Date().toISOString().slice(0,19).replace(/[-:T]/g, '')}.csv`;
            document.body.appendChild(link);
            link.click();
            link.remove();
            window.URL.revokeObjectURL(url);
        } catch (err) {
            console.error('Failed to download activity log', err);
            setDownloadError('Failed to download activity log.');
        } finally {
            setDownloading(false);
        }
    };

    if (loading) {
        return <div className="spinner"></div>;
    }

    if (!dashboard) {
        return <div className="alert alert-error">Failed to load dashboard</div>;
    }

    return (
        <div>
            <div className="card-header" style={{ alignItems: 'flex-start' }}>
                <div>
                    <h1 className="card-title">M&E Monitoring Dashboard</h1>
                    <p className="text-muted">Central monitoring and evaluation hub</p>
                    {downloadError && <div className="text-muted" style={{ color: 'var(--error)' }}>{downloadError}</div>}
                </div>
                {user?.role === 'ADMIN' && (
                    <button
                        className="btn btn-primary"
                        onClick={handleDownloadLog}
                        disabled={downloading}
                    >
                        {downloading ? 'Preparing Log...' : 'Download Activity Log'}
                    </button>
                )}
            </div>

            {/* Key Metrics */}
            <div className="grid grid-4">
                <div className="stat-card">
                    <div className="stat-label">Total Requests</div>
                    <div className="stat-value">{dashboard.total_requests}</div>
                    <div className="stat-change">All time</div>
                </div>

                <div className="stat-card light">
                    <div className="stat-label">SLA Compliance</div>
                    <div className="stat-value">{dashboard.sla_compliance_month}%</div>
                    <div className="stat-change">This month</div>
                </div>

                <div className="stat-card light">
                    <div className="stat-label">Overdue Requests</div>
                    <div className="stat-value">{dashboard.overdue_requests}</div>
                    <div className="stat-change negative">Requires attention</div>
                </div>

                <div className="stat-card light">
                    <div className="stat-label">Completed Today</div>
                    <div className="stat-value">{dashboard.today.completed}</div>
                    <div className="stat-change">{dashboard.today.submitted} submitted</div>
                </div>
            </div>

            {/* Status Breakdown */}
            <div className="card">
                <div className="card-header">
                    <h2 className="card-title">Request Status Breakdown</h2>
                </div>
                <div className="grid grid-4">
                    <div style={{ padding: '1rem', background: 'var(--gray-50)', borderRadius: 'var(--radius)' }}>
                        <div className="text-small text-muted">Pending</div>
                        <div style={{ fontSize: '2rem', fontWeight: '700', color: 'var(--gray-700)' }}>
                            {dashboard.status_breakdown.pending}
                        </div>
                    </div>
                    <div style={{ padding: '1rem', background: 'var(--gray-50)', borderRadius: 'var(--radius)' }}>
                        <div className="text-small text-muted">Approval Pending</div>
                        <div style={{ fontSize: '2rem', fontWeight: '700', color: 'var(--warning)' }}>
                            {dashboard.status_breakdown.approval_pending}
                        </div>
                    </div>
                    <div style={{ padding: '1rem', background: 'var(--gray-50)', borderRadius: 'var(--radius)' }}>
                        <div className="text-small text-muted">In Progress</div>
                        <div style={{ fontSize: '2rem', fontWeight: '700', color: 'var(--info)' }}>
                            {dashboard.status_breakdown.in_progress}
                        </div>
                    </div>
                    <div style={{ padding: '1rem', background: 'var(--gray-50)', borderRadius: 'var(--radius)' }}>
                        <div className="text-small text-muted">Completed</div>
                        <div style={{ fontSize: '2rem', fontWeight: '700', color: 'var(--success)' }}>
                            {dashboard.status_breakdown.completed}
                        </div>
                    </div>
                </div>
            </div>

            {/* Division Statistics */}
            <div className="card">
                <div className="card-header">
                    <h2 className="card-title">Requests by Division</h2>
                    {dashboard.division_requests?.length > 10 && (
                        <button
                            type="button"
                            className="btn btn-outline"
                            onClick={() => setShowAllDivisionRequests(!showAllDivisionRequests)}
                        >
                            {showAllDivisionRequests ? 'Show Less' : 'Show More'}
                        </button>
                    )}
                </div>
                {dashboard.division_stats.length === 0 ? (
                    <p className="text-muted">No data available</p>
                ) : (
                    <>
                        <div className="table-wrapper" style={{ marginBottom: '1.5rem' }}>
                            <table>
                                <thead>
                                    <tr>
                                        <th>Division</th>
                                        <th>Total Requests</th>
                                    </tr>
                                </thead>
                                <tbody>
                                    {dashboard.division_stats.map((stat: any) => (
                                        <tr key={stat.division}>
                                            <td className="font-bold">{stat.division}</td>
                                            <td>{stat.count}</td>
                                        </tr>
                                    ))}
                                </tbody>
                            </table>
                        </div>

                        {dashboard.division_requests && dashboard.division_requests.length > 0 && (
                            <div className="table-wrapper">
                                <table>
                                    <thead>
                                        <tr>
                                            <th>Division</th>
                                            <th>Department</th>
                                            <th>Request ID</th>
                                            <th>Description</th>
                                            <th>Date</th>
                                            <th>Time</th>
                                        </tr>
                                    </thead>
                                    <tbody>
                                        {(showAllDivisionRequests
                                            ? dashboard.division_requests
                                            : dashboard.division_requests.slice(0, 10)
                                        ).map((req: any) => {
                                            const date = req.created_at ? new Date(req.created_at) : null;
                                            const dateString = date ? date.toLocaleDateString() : '—';
                                            const timeString = date ? date.toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' }) : '—';
                                            return (
                                                <tr key={req.request_id}>
                                                    <td>{req.division || 'N/A'}</td>
                                                    <td>{req.department || 'N/A'}</td>
                                                    <td className="font-bold">{req.request_id}</td>
                                                    <td style={{ maxWidth: '250px' }}>{req.description}</td>
                                                    <td>{dateString}</td>
                                                    <td>{timeString}</td>
                                                </tr>
                                            );
                                        })}
                                    </tbody>
                                </table>
                            </div>
                        )}
                    </>
                )}
            </div>
        </div>
    );
};
