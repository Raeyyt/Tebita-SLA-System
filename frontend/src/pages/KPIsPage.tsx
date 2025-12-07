import { useState, useEffect } from 'react';
import { useAuth } from '../contexts/AuthContext';
import { api } from '../services/api';

export const KPIsPage = () => {
    const { token } = useAuth();
    const [dashboard, setDashboard] = useState<any>(null);
    const [metrics, setMetrics] = useState<any>(null);
    const [period, setPeriod] = useState('month');
    const [loading, setLoading] = useState(true);

    useEffect(() => {
        const loadData = async () => {
            if (!token) return;
            setLoading(true);
            try {
                const [dashboardData, metricsData] = await Promise.all([
                    api.getKPIDashboard(token),
                    api.getKPIMetrics(token, period),
                ]);
                setDashboard(dashboardData);
                setMetrics(metricsData);
            } catch (err) {
                console.error('Failed to load KPI data:', err);
            } finally {
                setLoading(false);
            }
        };
        loadData();
    }, [token, period]);

    if (loading) {
        return <div className="spinner"></div>;
    }

    return (
        <div>
            <div className="card-header">
                <div>
                    <h1 className="card-title">KPI Dashboard</h1>
                    <p className="text-muted">Key Performance Indicators</p>
                </div>
                <div className="flex gap-sm">
                    <button
                        className={`btn ${period === 'day' ? 'btn-primary' : 'btn-outline'}`}
                        onClick={() => setPeriod('day')}
                    >
                        Day
                    </button>
                    <button
                        className={`btn ${period === 'week' ? 'btn-primary' : 'btn-outline'}`}
                        onClick={() => setPeriod('week')}
                    >
                        Week
                    </button>
                    <button
                        className={`btn ${period === 'month' ? 'btn-primary' : 'btn-outline'}`}
                        onClick={() => setPeriod('month')}
                    >
                        Month
                    </button>
                    <button
                        className={`btn ${period === 'quarter' ? 'btn-primary' : 'btn-outline'}`}
                        onClick={() => setPeriod('quarter')}
                    >
                        Quarter
                    </button>
                </div>
            </div>

            {/* Overview Cards */}
            {dashboard && (
                <div className="grid grid-4">
                    <div className="stat-card">
                        <div className="stat-label">Total Requests</div>
                        <div className="stat-value">{dashboard.total_requests}</div>
                        <div className="stat-change">This {period}</div>
                    </div>

                    <div className="stat-card light">
                        <div className="stat-label">Avg Completion Time</div>
                        <div className="stat-value">{dashboard.avg_completion_time}h</div>
                        <div className="stat-change">Hours</div>
                    </div>

                    <div className="stat-card light">
                        <div className="stat-label">SLA Compliance</div>
                        <div className="stat-value" style={{ color: dashboard.sla_compliance_rate >= 80 ? 'var(--success)' : 'var(--error)' }}>
                            {dashboard.sla_compliance_rate}%
                        </div>
                        <div className="stat-change">Target: 90%</div>
                    </div>

                    <div className="stat-card light">
                        <div className="stat-label">Satisfaction Score</div>
                        <div className="stat-value">{dashboard.satisfaction_avg || 'N/A'}</div>
                        <div className="stat-change">Out of 5</div>
                    </div>
                </div>
            )}

            {/* Metrics Details */}
            {metrics && (
                <div className="card">
                    <div className="card-header">
                        <h2 className="card-title">Performance Metrics</h2>
                    </div>

                    {Array.isArray(metrics) ? (
                        <div className="table-wrapper">
                            <table>
                                <thead>
                                    <tr>
                                        <th>Metric Name</th>
                                        <th>Type</th>
                                        <th>Target</th>
                                        <th>Actual</th>
                                        <th>Status</th>
                                    </tr>
                                </thead>
                                <tbody>
                                    {metrics.map((metric: any, index: number) => (
                                        <tr key={index}>
                                            <td className="font-bold">{metric.metric_name}</td>
                                            <td>{metric.metric_type}</td>
                                            <td>{metric.target_value}</td>
                                            <td>{metric.actual_value}</td>
                                            <td>
                                                {metric.actual_value >= metric.target_value ? (
                                                    <span className="badge badge-success">On Track</span>
                                                ) : (
                                                    <span className="badge badge-warning">Below Target</span>
                                                )}
                                            </td>
                                        </tr>
                                    ))}
                                </tbody>
                            </table>
                        </div>
                    ) : (
                        <div className="grid grid-2">
                            <div>
                                <div className="text-small text-muted">Total Requests</div>
                                <div style={{ fontSize: '2rem', fontWeight: '700' }}>{metrics.total_requests}</div>
                            </div>
                            <div>
                                <div className="text-small text-muted">Completed</div>
                                <div style={{ fontSize: '2rem', fontWeight: '700', color: 'var(--success)' }}>
                                    {metrics.completed_requests}
                                </div>
                            </div>
                            <div>
                                <div className="text-small text-muted">Pending</div>
                                <div style={{ fontSize: '2rem', fontWeight: '700', color: 'var(--warning)' }}>
                                    {metrics.pending_requests}
                                </div>
                            </div>
                            <div>
                                <div className="text-small text-muted">Completion Rate</div>
                                <div style={{ fontSize: '2rem', fontWeight: '700' }}>{metrics.completion_rate}%</div>
                            </div>
                        </div>
                    )}
                </div>
            )}
        </div>
    );
};
