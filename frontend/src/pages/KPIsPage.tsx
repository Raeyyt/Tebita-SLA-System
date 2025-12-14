import { useState, useEffect } from 'react';
import { useAuth } from '../contexts/AuthContext';
import { api } from '../services/api';
import { ScorecardCard } from '../components/kpi/ScorecardCard';
import { AnalyticsCard } from '../components/kpi/AnalyticsCard';

export const KPIsPage = () => {
    const { token } = useAuth();
    const [dashboard, setDashboard] = useState<any>(null);
    const [metrics, setMetrics] = useState<any>(null);
    const [scorecard, setScorecard] = useState<any>(null);
    const [analytics, setAnalytics] = useState<any>(null);
    const [loading, setLoading] = useState(true);
    const [error, setError] = useState<string | null>(null);
    const [period, setPeriod] = useState('month');

    useEffect(() => {
        if (!token) {
            setLoading(false);
            return;
        }

        const loadData = async () => {
            setLoading(true);
            setError(null);

            // Map period to days for analytics
            let days = 30;
            if (period === 'day') days = 1;
            if (period === 'week') days = 7;
            if (period === 'quarter') days = 90;

            try {
                const dashboardData = await api.getKPIDashboard(token);
                setDashboard(dashboardData);
            } catch (err: any) {
                console.error('Dashboard error:', err);
                setError(prev => prev ? `${prev}, Dashboard failed` : 'Dashboard failed');
            }

            try {
                const metricsData = await api.getKPIMetrics(token, period);
                setMetrics(metricsData);
            } catch (err: any) {
                console.error('Metrics error:', err);
            }

            try {
                const scorecardData = await api.getScorecard(token, period);
                setScorecard(scorecardData);
            } catch (err: any) {
                console.error('Scorecard error:', err);
            }

            try {
                const analyticsData = await api.getAnalyticsDashboard(token, days);
                setAnalytics(analyticsData);
            } catch (err: any) {
                console.error('Analytics error:', err);
            } finally {
                setLoading(false);
            }
        };

        loadData();
    }, [token, period]);

    if (!token) return <div style={{ padding: '2rem' }}>Please log in</div>;

    return (
        <div style={{ padding: '2rem', maxWidth: '1600px', margin: '0 auto' }}>
            <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '2rem' }}>
                <div>
                    <h1 style={{ margin: 0, fontSize: '2rem', fontWeight: 'bold', color: '#111827' }}>KPI Dashboard</h1>
                    <p style={{ margin: '0.5rem 0 0', color: '#6b7280' }}>Performance Metrics & Analytics</p>
                </div>
                <div style={{ display: 'flex', gap: '0.5rem', background: '#f3f4f6', padding: '0.25rem', borderRadius: '0.5rem' }}>
                    {['day', 'week', 'month', 'quarter'].map((p) => (
                        <button
                            key={p}
                            onClick={() => setPeriod(p)}
                            style={{
                                padding: '0.5rem 1rem',
                                borderRadius: '0.375rem',
                                border: 'none',
                                background: period === p ? '#fff' : 'transparent',
                                color: period === p ? '#111827' : '#6b7280',
                                boxShadow: period === p ? '0 1px 2px 0 rgba(0, 0, 0, 0.05)' : 'none',
                                fontWeight: 500,
                                textTransform: 'capitalize',
                                cursor: 'pointer'
                            }}
                        >
                            {p}
                        </button>
                    ))}
                </div>
            </div>

            {error && <div style={{ padding: '1rem', color: '#dc2626', background: '#fee2e2', borderRadius: '0.5rem', marginBottom: '2rem' }}>Warning: {error}</div>}

            {loading && !dashboard ? (
                <div style={{ padding: '4rem', textAlign: 'center', color: '#6b7280' }}>
                    <div className="spinner" style={{ margin: '0 auto 1rem' }}></div>
                    Loading Dashboard...
                </div>
            ) : (
                <>
                    {/* Overview Cards */}
                    {dashboard && (
                        <div style={{ display: 'grid', gridTemplateColumns: 'repeat(5, 1fr)', gap: '1.5rem', marginBottom: '2rem' }}>
                            <div className="card" style={{ padding: '1.5rem', borderLeft: '4px solid #B67E7D' }}>
                                <div style={{ color: '#6b7280', fontSize: '0.875rem', fontWeight: 500 }}>Total Requests</div>
                                <div style={{ fontSize: '2rem', fontWeight: 'bold', color: '#111827', marginTop: '0.5rem' }}>{dashboard.total_requests}</div>
                                <div style={{ fontSize: '0.75rem', color: '#6b7280', marginTop: '0.25rem' }}>This {period}</div>
                            </div>
                            <div className="card" style={{ padding: '1.5rem', borderLeft: '4px solid #640000' }}>
                                <div style={{ color: '#6b7280', fontSize: '0.875rem', fontWeight: 500 }}>SLA Compliance</div>
                                <div style={{ fontSize: '2rem', fontWeight: 'bold', color: dashboard.sla_compliance_rate >= 90 ? '#059669' : '#D97706', marginTop: '0.5rem' }}>
                                    {dashboard.sla_compliance_rate}%
                                </div>
                                <div style={{ fontSize: '0.75rem', color: '#6b7280', marginTop: '0.25rem' }}>Target: 90%</div>
                            </div>
                            <div className="card" style={{ padding: '1.5rem', borderLeft: '4px solid #D97706' }}>
                                <div style={{ color: '#6b7280', fontSize: '0.875rem', fontWeight: 500 }}>Avg Completion Time</div>
                                <div style={{ fontSize: '2rem', fontWeight: 'bold', color: '#111827', marginTop: '0.5rem' }}>{dashboard.avg_completion_time}h</div>
                                <div style={{ fontSize: '0.75rem', color: '#6b7280', marginTop: '0.25rem' }}>Hours</div>
                            </div>
                            <div className="card" style={{ padding: '1.5rem', borderLeft: '4px solid #040B15' }}>
                                <div style={{ color: '#6b7280', fontSize: '0.875rem', fontWeight: 500 }}>Satisfaction Score</div>
                                <div style={{ fontSize: '2rem', fontWeight: 'bold', color: '#111827', marginTop: '0.5rem' }}>{dashboard.satisfaction_avg || 'N/A'}</div>
                                <div style={{ fontSize: '0.75rem', color: '#6b7280', marginTop: '0.25rem' }}>Out of 5.0</div>
                            </div>
                            <div className="card" style={{ padding: '1.5rem', borderLeft: '4px solid #EF4444' }}>
                                <div style={{ color: '#6b7280', fontSize: '0.875rem', fontWeight: 500 }}>Rejection Rate</div>
                                <div style={{ fontSize: '2rem', fontWeight: 'bold', color: '#111827', marginTop: '0.5rem' }}>{dashboard.rejection_rate}%</div>
                                <div style={{ fontSize: '0.75rem', color: '#6b7280', marginTop: '0.25rem' }}>Of Total Requests</div>
                            </div>
                        </div>
                    )}

                    {/* Scorecard Section */}
                    <div style={{ marginBottom: '2rem' }}>
                        <ScorecardCard data={scorecard} loading={loading && !scorecard} />
                    </div>

                    {/* Analytics Section */}
                    <div style={{ marginBottom: '2rem' }}>
                        <AnalyticsCard data={analytics} loading={loading && !analytics} />
                    </div>

                    {/* Detailed Metrics Table */}
                    {metrics && Array.isArray(metrics) && (
                        <div className="card" style={{ padding: '0', overflow: 'hidden', border: '1px solid #e5e7eb', boxShadow: '0 4px 6px -1px rgba(0, 0, 0, 0.1)' }}>
                            <div style={{
                                background: '#f9fafb',
                                padding: '1.5rem',
                                borderBottom: '1px solid #e5e7eb'
                            }}>
                                <h2 style={{ margin: 0, fontSize: '1.25rem', fontWeight: 600, color: '#111827' }}>Detailed Metrics</h2>
                            </div>
                            <div className="table-wrapper">
                                <table style={{ width: '100%', borderCollapse: 'collapse' }}>
                                    <thead>
                                        <tr style={{ textAlign: 'left', borderBottom: '1px solid #e5e7eb', background: '#f9fafb' }}>
                                            <th style={{ padding: '1rem', fontSize: '0.75rem', fontWeight: 600, textTransform: 'uppercase', color: '#6b7280' }}>Metric Name</th>
                                            <th style={{ padding: '1rem', fontSize: '0.75rem', fontWeight: 600, textTransform: 'uppercase', color: '#6b7280' }}>Type</th>
                                            <th style={{ padding: '1rem', fontSize: '0.75rem', fontWeight: 600, textTransform: 'uppercase', color: '#6b7280' }}>Target</th>
                                            <th style={{ padding: '1rem', fontSize: '0.75rem', fontWeight: 600, textTransform: 'uppercase', color: '#6b7280' }}>Actual</th>
                                            <th style={{ padding: '1rem', fontSize: '0.75rem', fontWeight: 600, textTransform: 'uppercase', color: '#6b7280' }}>Status</th>
                                        </tr>
                                    </thead>
                                    <tbody>
                                        {metrics.map((metric: any, index: number) => (
                                            <tr key={index} style={{ borderBottom: '1px solid #e5e7eb' }}>
                                                <td style={{ padding: '1rem', fontWeight: 500, color: '#111827' }}>{metric.metric_name}</td>
                                                <td style={{ padding: '1rem', color: '#6b7280' }}>{metric.metric_type}</td>
                                                <td style={{ padding: '1rem', color: '#6b7280' }}>{metric.target_value}</td>
                                                <td style={{ padding: '1rem', fontWeight: 500, color: '#111827' }}>{metric.actual_value}</td>
                                                <td style={{ padding: '1rem' }}>
                                                    {metric.actual_value >= metric.target_value ? (
                                                        <span style={{
                                                            background: '#d1fae5',
                                                            color: '#065f46',
                                                            padding: '0.25rem 0.75rem',
                                                            borderRadius: '999px',
                                                            fontSize: '0.75rem',
                                                            fontWeight: 600
                                                        }}>On Track</span>
                                                    ) : (
                                                        <span style={{
                                                            background: '#fef3c7',
                                                            color: '#92400e',
                                                            padding: '0.25rem 0.75rem',
                                                            borderRadius: '999px',
                                                            fontSize: '0.75rem',
                                                            fontWeight: 600
                                                        }}>Below Target</span>
                                                    )}
                                                </td>
                                            </tr>
                                        ))}
                                    </tbody>
                                </table>
                            </div>
                        </div>
                    )}
                </>
            )}
        </div>
    );
};
