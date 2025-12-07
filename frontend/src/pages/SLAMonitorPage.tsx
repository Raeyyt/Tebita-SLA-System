import { useState, useEffect } from 'react';
import { useAuth } from '../contexts/AuthContext';
import { api } from '../services/api';

export const SLAMonitorPage = () => {
    const { token } = useAuth();
    const [dashboard, setDashboard] = useState<any>(null);
    const [compliance, setCompliance] = useState<any>(null);
    const [loading, setLoading] = useState(true);

    useEffect(() => {
        const loadData = async () => {
            if (!token) return;
            try {
                const [dashboardData, complianceData] = await Promise.all([
                    api.getSLADashboard?.(token) || {},
                    api.getSLACompliance(token),
                ]);
                setDashboard(dashboardData);
                setCompliance(complianceData);
            } catch (err) {
                console.error('Failed to load SLA data:', err);
            } finally {
                setLoading(false);
            }
        };
        loadData();
    }, [token]);

    if (loading) {
        return <div className="spinner"></div>;
    }

    return (
        <div>
            <div className="card-header">
                <h1 className="card-title">SLA Monitor</h1>
                <p className="text-muted">Real-time SLA compliance tracking</p>
            </div>

            {/* SLA Status Cards */}
            {dashboard && (
                <div className="grid grid-4">
                    <div className="stat-card" style={{ background: 'linear-gradient(135deg, var(--success) 0%, #059669 100%)' }}>
                        <div className="stat-label">On Track</div>
                        <div className="stat-value">{dashboard.on_track}</div>
                        <div className="stat-change">{'< 50% time used'}</div>
                    </div>

                    <div className="stat-card light" style={{ borderLeft: '4px solid var(--warning)' }}>
                        <div className="stat-label">At Risk (50-80%)</div>
                        <div className="stat-value" style={{ color: 'var(--warning)' }}>{dashboard.at_risk_50_percent}</div>
                        <div className="stat-change">Monitor closely</div>
                    </div>

                    <div className="stat-card light" style={{ borderLeft: '4px solid var(--error)' }}>
                        <div className="stat-label">Critical (80%+)</div>
                        <div className="stat-value" style={{ color: 'var(--error)' }}>{dashboard.critical_80_percent}</div>
                        <div className="stat-change">Immediate attention</div>
                    </div>

                    <div className="stat-card" style={{ background: 'linear-gradient(135deg, var(--error) 0%, #991B1B 100%)' }}>
                        <div className="stat-label">Overdue</div>
                        <div className="stat-value">{dashboard.overdue}</div>
                        <div className="stat-change negative">SLA breached</div>
                    </div>
                </div>
            )}

            {/* Compliance Metrics */}
            {compliance && (
                <div className="card">
                    <div className="card-header">
                        <h2 className="card-title">SLA Compliance (This Month)</h2>
                    </div>
                    <div className="grid grid-4">
                        <div>
                            <div className="text-small text-muted">Total Requests</div>
                            <div style={{ fontSize: '2rem', fontWeight: '700' }}>{compliance.total_requests}</div>
                        </div>
                        <div>
                            <div className="text-small text-muted">Within SLA</div>
                            <div style={{ fontSize: '2rem', fontWeight: '700', color: 'var(--success)' }}>
                                {compliance.within_sla}
                            </div>
                        </div>
                        <div>
                            <div className="text-small text-muted">Overdue</div>
                            <div style={{ fontSize: '2rem', fontWeight: '700', color: 'var(--error)' }}>
                                {compliance.overdue}
                            </div>
                        </div>
                        <div>
                            <div className="text-small text-muted">Compliance Rate</div>
                            <div style={{ fontSize: '2rem', fontWeight: '700', color: compliance.compliance_rate >= 80 ? 'var(--success)' : 'var(--warning)' }}>
                                {compliance.compliance_rate}%
                            </div>
                        </div>
                    </div>

                    <div style={{ marginTop: '2rem' }}>
                        <div className="text-small text-muted">Average Completion Time</div>
                        <div style={{ fontSize: '1.5rem', fontWeight: '600' }}>
                            {compliance.average_completion_time} hours
                        </div>
                    </div>
                </div>
            )}

            {/* Active Requests */}
            {dashboard && (
                <div className="card">
                    <div className="card-header">
                        <h2 className="card-title">Active Requests Summary</h2>
                    </div>
                    <p className="text-muted">
                        Monitoring {dashboard.active_requests} active requests
                    </p>
                </div>
            )}
        </div>
    );
};
