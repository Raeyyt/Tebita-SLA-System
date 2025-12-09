import React from 'react';

interface AnalyticsProps {
    data: any;
    loading?: boolean;
    error?: string | null;
}

export const AnalyticsCard: React.FC<AnalyticsProps> = ({ data, loading, error }) => {
    if (loading) {
        return (
            <div className="card" style={{ padding: '2rem', textAlign: 'center', color: '#666' }}>
                <div className="spinner" style={{ margin: '0 auto 1rem' }}></div>
                Loading Analytics...
            </div>
        );
    }

    if (error) {
        return (
            <div className="card" style={{ padding: '2rem', borderLeft: '4px solid #dc2626' }}>
                <h3 style={{ color: '#dc2626', margin: 0 }}>Analytics Unavailable</h3>
                <p style={{ color: '#666', marginTop: '0.5rem' }}>{error}</p>
            </div>
        );
    }

    if (!data) return null;

    // Safe accessors for Integration Index
    const index = Number(data.integration_index || 0);
    const components = data.components || {};
    const coordination = Number(components.coordination_effectiveness || 0);
    const alignment = Number(components.process_alignment || 0);
    const timeliness = Number(components.reporting_timeliness || 0);
    const collaboration = Number(components.collaboration_score || 0);

    // Safe accessors for General KPIs (if present in the same object, or passed differently)
    // Assuming 'data' is the result of getAnalyticsDashboard which has 'integration_index' and 'general_kpis'
    const general = data.general_kpis || {};
    const slaRate = Number(general.sla_compliance_rate || 0);
    const fulfillmentRate = Number(general.service_fulfillment_rate || 0);
    const satisfaction = Number(general.customer_satisfaction_score || 0);

    return (
        <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(300px, 1fr))', gap: '2rem' }}>

            {/* Integration Index Card */}
            <div className="card" style={{ padding: '0', overflow: 'hidden', border: '1px solid #e5e7eb', boxShadow: '0 4px 6px -1px rgba(0, 0, 0, 0.1)' }}>
                <div style={{
                    background: 'linear-gradient(135deg, #B67E7D 0%, #640000 100%)',
                    padding: '1.5rem',
                    color: 'white',
                    display: 'flex',
                    justifyContent: 'space-between',
                    alignItems: 'center'
                }}>
                    <div>
                        <h2 style={{ margin: 0, fontSize: '1.25rem', fontWeight: 600 }}>Integration Index</h2>
                        <p style={{ margin: '0.25rem 0 0', opacity: 0.9, fontSize: '0.875rem' }}>Cross-functional Performance</p>
                    </div>
                    <div style={{ fontSize: '2rem', fontWeight: 'bold' }}>{index.toFixed(1)}</div>
                </div>

                <div style={{ padding: '1.5rem' }}>
                    <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '1rem' }}>
                        <div style={{ padding: '0.75rem', background: '#f9fafb', borderRadius: '0.5rem' }}>
                            <div style={{ fontSize: '0.75rem', color: '#6b7280' }}>Coordination</div>
                            <div style={{ fontSize: '1.125rem', fontWeight: 'bold', color: '#111827' }}>{coordination.toFixed(1)}%</div>
                        </div>
                        <div style={{ padding: '0.75rem', background: '#f9fafb', borderRadius: '0.5rem' }}>
                            <div style={{ fontSize: '0.75rem', color: '#6b7280' }}>Alignment</div>
                            <div style={{ fontSize: '1.125rem', fontWeight: 'bold', color: '#111827' }}>{alignment.toFixed(1)}%</div>
                        </div>
                        <div style={{ padding: '0.75rem', background: '#f9fafb', borderRadius: '0.5rem' }}>
                            <div style={{ fontSize: '0.75rem', color: '#6b7280' }}>Timeliness</div>
                            <div style={{ fontSize: '1.125rem', fontWeight: 'bold', color: '#111827' }}>{timeliness.toFixed(1)}%</div>
                        </div>
                        <div style={{ padding: '0.75rem', background: '#f9fafb', borderRadius: '0.5rem' }}>
                            <div style={{ fontSize: '0.75rem', color: '#6b7280' }}>Collaboration</div>
                            <div style={{ fontSize: '1.125rem', fontWeight: 'bold', color: '#111827' }}>{collaboration.toFixed(1)}%</div>
                        </div>
                    </div>
                </div>
            </div>

            {/* General KPIs Card */}
            <div className="card" style={{ padding: '0', overflow: 'hidden', border: '1px solid #e5e7eb', boxShadow: '0 4px 6px -1px rgba(0, 0, 0, 0.1)' }}>
                <div style={{
                    background: 'linear-gradient(135deg, #040B15 0%, #1f2937 100%)',
                    padding: '1.5rem',
                    color: 'white'
                }}>
                    <h2 style={{ margin: 0, fontSize: '1.25rem', fontWeight: 600 }}>General KPIs</h2>
                    <p style={{ margin: '0.25rem 0 0', opacity: 0.7, fontSize: '0.875rem' }}>Key Performance Indicators</p>
                </div>

                <div style={{ padding: '1.5rem' }}>
                    <div style={{ marginBottom: '1.5rem' }}>
                        <div style={{ display: 'flex', justifyContent: 'space-between', marginBottom: '0.5rem' }}>
                            <span style={{ color: '#4b5563', fontWeight: 500 }}>SLA Compliance</span>
                            <span style={{ fontWeight: 'bold', color: slaRate >= 90 ? '#059669' : '#D97706' }}>{slaRate.toFixed(1)}%</span>
                        </div>
                        <div style={{ width: '100%', height: '8px', background: '#e5e7eb', borderRadius: '4px', overflow: 'hidden' }}>
                            <div style={{ width: `${Math.min(slaRate, 100)}%`, height: '100%', background: slaRate >= 90 ? '#059669' : '#D97706' }}></div>
                        </div>
                    </div>

                    <div style={{ marginBottom: '1.5rem' }}>
                        <div style={{ display: 'flex', justifyContent: 'space-between', marginBottom: '0.5rem' }}>
                            <span style={{ color: '#4b5563', fontWeight: 500 }}>Fulfillment Rate</span>
                            <span style={{ fontWeight: 'bold', color: '#111827' }}>{fulfillmentRate.toFixed(1)}%</span>
                        </div>
                        <div style={{ width: '100%', height: '8px', background: '#e5e7eb', borderRadius: '4px', overflow: 'hidden' }}>
                            <div style={{ width: `${Math.min(fulfillmentRate, 100)}%`, height: '100%', background: '#4b5563' }}></div>
                        </div>
                    </div>

                    <div>
                        <div style={{ display: 'flex', justifyContent: 'space-between', marginBottom: '0.5rem' }}>
                            <span style={{ color: '#4b5563', fontWeight: 500 }}>Customer Satisfaction</span>
                            <span style={{ fontWeight: 'bold', color: '#D97706' }}>{satisfaction.toFixed(1)} / 5.0</span>
                        </div>
                        <div style={{ width: '100%', height: '8px', background: '#e5e7eb', borderRadius: '4px', overflow: 'hidden' }}>
                            <div style={{ width: `${(satisfaction / 5) * 100}%`, height: '100%', background: '#D97706' }}></div>
                        </div>
                    </div>
                </div>
            </div>
        </div>
    );
};
