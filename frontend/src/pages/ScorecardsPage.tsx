import { useState, useEffect } from 'react';
import { useAuth } from '../contexts/AuthContext';
import { api } from '../services/api';

export const ScorecardsPage = () => {
    const { token } = useAuth();
    const [scorecard, setScorecard] = useState<any>(null);
    const [period, setPeriod] = useState('month');
    const [loading, setLoading] = useState(true);

    useEffect(() => {
        const loadScorecard = async () => {
            if (!token) return;
            setLoading(true);
            try {
                const data = await api.getScorecard(token, period);
                setScorecard(data);
            } catch (err) {
                console.error('Failed to load scorecard:', err);
            } finally {
                setLoading(false);
            }
        };
        loadScorecard();
    }, [token, period]);

    if (loading) {
        return <div className="spinner"></div>;
    }

    const getRatingColor = (rating: string) => {
        const colorMap: Record<string, string> = {
            'OUTSTANDING': 'var(--success)',
            'VERY_GOOD': 'var(--info)',
            'GOOD': 'var(--primary)',
            'NEEDS_IMPROVEMENT': 'var(--warning)',
            'UNSATISFACTORY': 'var(--error)',
        };
        return colorMap[rating] || 'var(--gray-700)';
    };

    const getRatingLabel = (rating: string) => {
        return rating.replace(/_/g, ' ');
    };

    const handleDownload = async () => {
        if (!token) return;
        try {
            const daysMap: Record<string, number> = { 'week': 7, 'month': 30, 'quarter': 90 };
            const blob = await api.downloadScorecard(token, daysMap[period]);

            // Create download link
            const url = window.URL.createObjectURL(new Blob([blob]));
            const link = document.createElement('a');
            link.href = url;
            link.setAttribute('download', `scorecard_${period}_${new Date().toISOString().split('T')[0]}.pdf`);
            document.body.appendChild(link);
            link.click();
            link.parentNode?.removeChild(link);
        } catch (err) {
            console.error('Failed to download scorecard:', err);
            alert('Failed to download PDF');
        }
    };

    return (
        <div>
            <div className="card-header">
                <div>
                    <h1 className="card-title">Performance Scorecard</h1>
                    <p className="text-muted">4-Dimension Performance Evaluation</p>
                </div>
                <div className="flex gap-sm">
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
                    <button
                        className="btn btn-outline"
                        onClick={handleDownload}
                        style={{ marginLeft: '1rem', borderColor: 'var(--primary)', color: 'var(--primary)' }}
                    >
                        Download PDF
                    </button>
                </div>
            </div>

            {scorecard && (
                <>
                    {/* Overall Score */}
                    <div className="card" style={{ textAlign: 'center', padding: '3rem' }}>
                        <div style={{ fontSize: '1rem', fontWeight: '600', color: 'var(--gray-600)', marginBottom: '1rem' }}>
                            Overall Performance Score
                        </div>
                        <div style={{ fontSize: '5rem', fontWeight: '800', color: getRatingColor(scorecard.rating), lineHeight: 1 }}>
                            {Number(scorecard.total_score).toFixed(1)}
                        </div>
                        <div style={{ fontSize: '1.5rem', fontWeight: '600', color: getRatingColor(scorecard.rating), marginTop: '1rem' }}>
                            {getRatingLabel(scorecard.rating)}
                        </div>
                    </div>

                    {/* 4 Dimensions */}
                    <div className="grid grid-2">
                        {/* Service Efficiency - 25% */}
                        <div className="card">
                            <div style={{ marginBottom: '1rem' }}>
                                <div className="text-small text-muted">Service Efficiency (25%)</div>
                                <div style={{ fontSize: '2.5rem', fontWeight: '700', color: Number(scorecard.service_efficiency_score) >= 75 ? 'var(--success)' : 'var(--warning)' }}>
                                    {Number(scorecard.service_efficiency_score).toFixed(1)}
                                </div>
                            </div>
                            <div style={{ background: 'var(--gray-200)', height: '12px', borderRadius: '6px', overflow: 'hidden' }}>
                                <div
                                    style={{
                                        background: Number(scorecard.service_efficiency_score) >= 75 ? 'var(--success)' : 'var(--warning)',
                                        height: '100%',
                                        width: `${scorecard.service_efficiency_score}%`,
                                        transition: 'width 0.3s ease',
                                    }}
                                />
                            </div>
                            <p className="text-small text-muted" style={{ marginTop: '0.5rem' }}>
                                Based on average completion time and resource utilization
                            </p>
                        </div>

                        {/* SLA Compliance - 30% */}
                        <div className="card">
                            <div style={{ marginBottom: '1rem' }}>
                                <div className="text-small text-muted">SLA Compliance & Data Quality (30%)</div>
                                <div style={{ fontSize: '2.5rem', fontWeight: '700', color: Number(scorecard.compliance_score) >= 80 ? 'var(--success)' : 'var(--error)' }}>
                                    {Number(scorecard.compliance_score).toFixed(1)}
                                </div>
                            </div>
                            <div style={{ background: 'var(--gray-200)', height: '12px', borderRadius: '6px', overflow: 'hidden' }}>
                                <div
                                    style={{
                                        background: Number(scorecard.compliance_score) >= 80 ? 'var(--success)' : 'var(--error)',
                                        height: '100%',
                                        width: `${scorecard.compliance_score}%`,
                                        transition: 'width 0.3s ease',
                                    }}
                                />
                            </div>
                            <p className="text-small text-muted" style={{ marginTop: '0.5rem' }}>
                                Percentage of requests completed within SLA
                            </p>
                        </div>

                        {/* Cost Optimization - 20% */}
                        <div className="card">
                            <div style={{ marginBottom: '1rem' }}>
                                <div className="text-small text-muted">Cost & Resource Optimization (20%)</div>
                                <div style={{ fontSize: '2.5rem', fontWeight: '700', color: 'var(--primary)' }}>
                                    {Number(scorecard.cost_optimization_score).toFixed(1)}
                                </div>
                            </div>
                            <div style={{ background: 'var(--gray-200)', height: '12px', borderRadius: '6px', overflow: 'hidden' }}>
                                <div
                                    style={{
                                        background: 'var(--primary)',
                                        height: '100%',
                                        width: `${scorecard.cost_optimization_score}%`,
                                        transition: 'width 0.3s ease',
                                    }}
                                />
                            </div>
                            <p className="text-small text-muted" style={{ marginTop: '0.5rem' }}>
                                Efficient use of resources and budget management
                            </p>
                        </div>

                        {/* Customer Satisfaction - 25% */}
                        <div className="card">
                            <div style={{ marginBottom: '1rem' }}>
                                <div className="text-small text-muted">Customer Satisfaction & Integration (25%)</div>
                                <div style={{ fontSize: '2.5rem', fontWeight: '700', color: 'var(--info)' }}>
                                    {Number(scorecard.satisfaction_score).toFixed(1)}
                                </div>
                            </div>
                            <div style={{ background: 'var(--gray-200)', height: '12px', borderRadius: '6px', overflow: 'hidden' }}>
                                <div
                                    style={{
                                        background: 'var(--info)',
                                        height: '100%',
                                        width: `${scorecard.satisfaction_score}%`,
                                        transition: 'width 0.3s ease',
                                    }}
                                />
                            </div>
                            <p className="text-small text-muted" style={{ marginTop: '0.5rem' }}>
                                Based on user feedback and satisfaction surveys
                            </p>
                        </div>
                    </div>

                    {/* Period Info */}
                    <div className="card">
                        <div className="card-header">
                            <h2 className="card-title">Scorecard Details</h2>
                        </div>
                        <div className="grid grid-2">
                            <div>
                                <div className="text-small text-muted">Period Start</div>
                                <div className="font-bold">{new Date(scorecard.period_start).toLocaleDateString()}</div>
                            </div>
                            <div>
                                <div className="text-small text-muted">Period End</div>
                                <div className="font-bold">{new Date(scorecard.period_end).toLocaleDateString()}</div>
                            </div>
                            <div>
                                <div className="text-small text-muted">Generated</div>
                                <div className="font-bold">{new Date(scorecard.created_at).toLocaleDateString()}</div>
                            </div>
                            <div>
                                <div className="text-small text-muted">Rating</div>
                                <div className="font-bold" style={{ color: getRatingColor(scorecard.rating) }}>
                                    {getRatingLabel(scorecard.rating)}
                                </div>
                            </div>
                        </div>
                    </div>
                </>
            )}
        </div>
    );
};
