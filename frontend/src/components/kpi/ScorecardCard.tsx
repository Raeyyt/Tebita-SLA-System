import React from 'react';

interface ScorecardProps {
    data: any;
    loading?: boolean;
    error?: string | null;
}

export const ScorecardCard: React.FC<ScorecardProps> = ({ data, loading, error }) => {
    if (loading) {
        return (
            <div className="card" style={{ padding: '2rem', textAlign: 'center', color: '#666' }}>
                <div className="spinner" style={{ margin: '0 auto 1rem' }}></div>
                Loading Scorecard...
            </div>
        );
    }

    if (error) {
        return (
            <div className="card" style={{ padding: '2rem', borderLeft: '4px solid #dc2626' }}>
                <h3 style={{ color: '#dc2626', margin: 0 }}>Scorecard Unavailable</h3>
                <p style={{ color: '#666', marginTop: '0.5rem' }}>{error}</p>
            </div>
        );
    }

    if (!data) return null;

    // Safe accessors with fallbacks
    const efficiency = Number(data.service_efficiency_score || 0);
    const compliance = Number(data.compliance_score || 0);
    const cost = Number(data.cost_optimization_score || 0);
    const satisfaction = Number(data.satisfaction_score || 0);
    const total = Number(data.total_score || 0);
    const rating = data.rating || 'N/A';

    // Helper for rating color
    const getRatingColor = (r: string) => {
        switch (r) {
            case 'OUTSTANDING': return '#059669'; // Green
            case 'VERY_GOOD': return '#10B981';
            case 'GOOD': return '#D97706'; // Gold
            case 'NEEDS_IMPROVEMENT': return '#F59E0B';
            case 'UNSATISFACTORY': return '#DC2626'; // Red
            default: return '#6B7280';
        }
    };

    return (
        <div className="card" style={{ padding: '0', overflow: 'hidden', border: '1px solid #e5e7eb', boxShadow: '0 4px 6px -1px rgba(0, 0, 0, 0.1)' }}>
            <div style={{
                background: 'linear-gradient(135deg, #640000 0%, #420001 100%)',
                padding: '1.5rem',
                color: 'white',
                display: 'flex',
                justifyContent: 'space-between',
                alignItems: 'center'
            }}>
                <div>
                    <h2 style={{ margin: 0, fontSize: '1.25rem', fontWeight: 600 }}>Performance Scorecard</h2>
                    <p style={{ margin: '0.25rem 0 0', opacity: 0.9, fontSize: '0.875rem' }}>Overall Efficiency & Compliance</p>
                </div>
                <div style={{ textAlign: 'right' }}>
                    <div style={{ fontSize: '2rem', fontWeight: 'bold' }}>{total.toFixed(1)}%</div>
                    <div style={{
                        background: 'rgba(255,255,255,0.2)',
                        padding: '0.25rem 0.75rem',
                        borderRadius: '999px',
                        fontSize: '0.75rem',
                        fontWeight: 600,
                        display: 'inline-block',
                        marginTop: '0.25rem'
                    }}>
                        {rating.replace('_', ' ')}
                    </div>
                </div>
            </div>

            <div style={{ padding: '1.5rem' }}>
                <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(200px, 1fr))', gap: '1.5rem' }}>
                    {/* Service Efficiency */}
                    <div style={{ padding: '1rem', background: '#f9fafb', borderRadius: '0.5rem', borderLeft: '4px solid #B67E7D' }}>
                        <div style={{ fontSize: '0.875rem', color: '#6b7280', marginBottom: '0.5rem' }}>Service Efficiency</div>
                        <div style={{ fontSize: '1.5rem', fontWeight: 'bold', color: '#111827' }}>{efficiency.toFixed(1)}%</div>
                        <div style={{ fontSize: '0.75rem', color: '#6b7280', marginTop: '0.25rem' }}>Weight: 25%</div>
                    </div>

                    {/* Compliance */}
                    <div style={{ padding: '1rem', background: '#f9fafb', borderRadius: '0.5rem', borderLeft: '4px solid #640000' }}>
                        <div style={{ fontSize: '0.875rem', color: '#6b7280', marginBottom: '0.5rem' }}>SLA Compliance</div>
                        <div style={{ fontSize: '1.5rem', fontWeight: 'bold', color: '#111827' }}>{compliance.toFixed(1)}%</div>
                        <div style={{ fontSize: '0.75rem', color: '#6b7280', marginTop: '0.25rem' }}>Weight: 30%</div>
                    </div>

                    {/* Cost Optimization */}
                    <div style={{ padding: '1rem', background: '#f9fafb', borderRadius: '0.5rem', borderLeft: '4px solid #D97706' }}>
                        <div style={{ fontSize: '0.875rem', color: '#6b7280', marginBottom: '0.5rem' }}>Cost Optimization</div>
                        <div style={{ fontSize: '1.5rem', fontWeight: 'bold', color: '#111827' }}>{cost.toFixed(1)}%</div>
                        <div style={{ fontSize: '0.75rem', color: '#6b7280', marginTop: '0.25rem' }}>Weight: 20%</div>
                    </div>

                    {/* Satisfaction */}
                    <div style={{ padding: '1rem', background: '#f9fafb', borderRadius: '0.5rem', borderLeft: '4px solid #040B15' }}>
                        <div style={{ fontSize: '0.875rem', color: '#6b7280', marginBottom: '0.5rem' }}>Satisfaction</div>
                        <div style={{ fontSize: '1.5rem', fontWeight: 'bold', color: '#111827' }}>{satisfaction.toFixed(1)}%</div>
                        <div style={{ fontSize: '0.75rem', color: '#6b7280', marginTop: '0.25rem' }}>Weight: 25%</div>
                    </div>
                </div>
            </div>
        </div>
    );
};
