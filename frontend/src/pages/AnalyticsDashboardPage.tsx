import { useState, useEffect } from 'react';
import { useAuth } from '../contexts/AuthContext';
import { api } from '../services/api';

export const AnalyticsDashboardPage = () => {
    const { token } = useAuth();
    const [dashboard, setDashboard] = useState<ComprehensiveDashboard | null>(null);
    const [loading, setLoading] = useState(true);
    const [days, setDays] = useState(30);
    const [activeTab, setActiveTab] = useState<'overview' | 'fleet' | 'hr' | 'finance' | 'ict' | 'logistics'>('overview');

    useEffect(() => {
        fetchDashboard();
    }, [days]);

    const fetchDashboard = async () => {
        if (!token) return;
        try {
            setLoading(true);
            const data = await api.getAnalyticsDashboard(token, days);
            setDashboard(data);
        } catch (error) {
            console.error('Failed to fetch dashboard:', error);
        } finally {
            setLoading(false);
        }
    };

    if (loading) {
        return <div className="spinner"></div>;
    }

    if (!dashboard) {
        return (
            <div className="card">
                <p className="text-muted">Failed to load dashboard data</p>
                <button onClick={fetchDashboard} className="btn btn-primary" style={{ marginTop: '1rem' }}>
                    Retry
                </button>
            </div>
        );
    }

    return (
        <div>
            {/* Header */}
            <div className="card-header">
                <div>
                    <h1 className="card-title">Analytics Dashboard</h1>
                    <p className="text-muted">Comprehensive M&E KPI Analytics and Scorecard</p>
                </div>
                <div className="flex gap-sm">
                    <button
                        className={`btn ${days === 7 ? 'btn-primary' : 'btn-outline'}`}
                        onClick={() => setDays(7)}
                    >
                        7 Days
                    </button>
                    <button
                        className={`btn ${days === 30 ? 'btn-primary' : 'btn-outline'}`}
                        onClick={() => setDays(30)}
                    >
                        30 Days
                    </button>
                    <button
                        className={`btn ${days === 90 ? 'btn-primary' : 'btn-outline'}`}
                        onClick={() => setDays(90)}
                    >
                        90 Days
                    </button>
                    <button className="btn btn-outline" onClick={fetchDashboard}>
                        🔄 Refresh
                    </button>
                </div>
            </div>

            {/* Tabs */}
            <div className="card" style={{ marginBottom: '1.5rem', padding: '0' }}>
                <div className="flex" style={{ borderBottom: '1px solid var(--gray-200)' }}>
                    <button
                        className={`tab-button ${activeTab === 'overview' ? 'active' : ''}`}
                        onClick={() => setActiveTab('overview')}
                    >
                        Overview
                    </button>
                    <button
                        className={`tab-button ${activeTab === 'fleet' ? 'active' : ''}`}
                        onClick={() => setActiveTab('fleet')}
                    >
                        🚗 Fleet
                    </button>
                    <button
                        className={`tab-button ${activeTab === 'hr' ? 'active' : ''}`}
                        onClick={() => setActiveTab('hr')}
                    >
                        HR
                    </button>
                    <button
                        className={`tab-button ${activeTab === 'finance' ? 'active' : ''}`}
                        onClick={() => setActiveTab('finance')}
                    >
                        Finance
                    </button>
                    <button
                        className={`tab-button ${activeTab === 'ict' ? 'active' : ''}`}
                        onClick={() => setActiveTab('ict')}
                    >
                        ICT
                    </button>
                    <button
                        className={`tab-button ${activeTab === 'logistics' ? 'active' : ''}`}
                        onClick={() => setActiveTab('logistics')}
                    >
                        Logistics
                    </button>
                </div>
            </div>

            {/* Overview Tab */}
            {activeTab === 'overview' && (
                <>
                    {/* Scorecard */}
                    <div className="card" style={{
                        background: 'linear-gradient(135deg, var(--primary) 0%, var(--primary-dark) 100%)',
                        color: 'var(--white)',
                        padding: '2rem'
                    }}>
                        <h2 className="card-title" style={{ color: 'var(--white)', marginBottom: '1.5rem' }}>Overall Scorecard</h2>
                        <div className="grid grid-2" style={{ gap: '2rem' }}>
                            <div style={{ textAlign: 'center' }}>
                                <div style={{ fontSize: '0.875rem', opacity: 0.9, marginBottom: '0.5rem' }}>Total Score</div>
                                <div style={{ fontSize: '4rem', fontWeight: '800', lineHeight: 1 }}>
                                    {dashboard.scorecard.total_score.toFixed(1)}
                                </div>
                                <div style={{
                                    fontSize: '1.25rem',
                                    fontWeight: '600',
                                    marginTop: '1rem',
                                    background: 'rgba(255, 255, 255, 0.2)',
                                    padding: '0.5rem 1rem',
                                    borderRadius: 'var(--radius)',
                                    display: 'inline-block'
                                }}>
                                    {dashboard.scorecard.rating.replace(/_/g, ' ')}
                                </div>
                            </div>
                            <div className="grid grid-2" style={{ gap: '1rem' }}>
                                <div style={{ background: 'rgba(255, 255, 255, 0.15)', padding: '1rem', borderRadius: 'var(--radius)' }}>
                                    <div className="text-small" style={{ opacity: 0.9 }}>Service Efficiency</div>
                                    <div style={{ fontSize: '2rem', fontWeight: '700' }}>
                                        {dashboard.scorecard.service_efficiency_score.toFixed(1)}%
                                    </div>
                                    <div className="text-small" style={{ opacity: 0.8 }}>Weight: 25%</div>
                                </div>
                                <div style={{ background: 'rgba(255, 255, 255, 0.15)', padding: '1rem', borderRadius: 'var(--radius)' }}>
                                    <div className="text-small" style={{ opacity: 0.9 }}>Compliance</div>
                                    <div style={{ fontSize: '2rem', fontWeight: '700' }}>
                                        {dashboard.scorecard.compliance_score.toFixed(1)}%
                                    </div>
                                    <div className="text-small" style={{ opacity: 0.8 }}>Weight: 30%</div>
                                </div>
                                <div style={{ background: 'rgba(255, 255, 255, 0.15)', padding: '1rem', borderRadius: 'var(--radius)' }}>
                                    <div className="text-small" style={{ opacity: 0.9 }}>Cost Optimization</div>
                                    <div style={{ fontSize: '2rem', fontWeight: '700' }}>
                                        {dashboard.scorecard.cost_optimization_score.toFixed(1)}%
                                    </div>
                                    <div className="text-small" style={{ opacity: 0.8 }}>Weight: 20%</div>
                                </div>
                                <div style={{ background: 'rgba(255, 255, 255, 0.15)', padding: '1rem', borderRadius: 'var(--radius)' }}>
                                    <div className="text-small" style={{ opacity: 0.9 }}>Satisfaction</div>
                                    <div style={{ fontSize: '2rem', fontWeight: '700' }}>
                                        {dashboard.scorecard.satisfaction_score.toFixed(1)}%
                                    </div>
                                    <div className="text-small" style={{ opacity: 0.8 }}>Weight: 25%</div>
                                </div>
                            </div>
                        </div>
                    </div>

                    {/* General KPIs */}
                    <div className="card">
                        <h3 className="card-title" style={{ fontSize: '1.25rem', marginBottom: '1.5rem' }}>General Integration KPIs</h3>
                        <div className="grid grid-3" style={{ gap: '1.5rem' }}>
                            <div>
                                <div className="text-small text-muted">SLA Compliance Rate</div>
                                <div style={{ fontSize: '2.5rem', fontWeight: '700', color: 'var(--success)' }}>
                                    {dashboard.general_kpis.sla_compliance_rate.toFixed(1)}%
                                </div>
                                <div style={{ background: 'var(--gray-200)', height: '8px', borderRadius: '4px', overflow: 'hidden', marginTop: '0.5rem' }}>
                                    <div style={{
                                        background: 'var(--success)',
                                        height: '100%',
                                        width: `${dashboard.general_kpis.sla_compliance_rate}%`,
                                        transition: 'width 0.3s ease'
                                    }} />
                                </div>
                            </div>
                            <div>
                                <div className="text-small text-muted">Service Fulfillment Rate</div>
                                <div style={{ fontSize: '2.5rem', fontWeight: '700', color: 'var(--info)' }}>
                                    {dashboard.general_kpis.service_fulfillment_rate.toFixed(1)}%
                                </div>
                                <div style={{ background: 'var(--gray-200)', height: '8px', borderRadius: '4px', overflow: 'hidden', marginTop: '0.5rem' }}>
                                    <div style={{
                                        background: 'var(--info)',
                                        height: '100%',
                                        width: `${dashboard.general_kpis.service_fulfillment_rate}%`,
                                        transition: 'width 0.3s ease'
                                    }} />
                                </div>
                            </div>
                            <div>
                                <div className="text-small text-muted">Customer Satisfaction</div>
                                <div style={{ fontSize: '2.5rem', fontWeight: '700', color: 'var(--warning)' }}>
                                    {dashboard.general_kpis.customer_satisfaction_score.toFixed(1)}/5
                                </div>
                                <div style={{ background: 'var(--gray-200)', height: '8px', borderRadius: '4px', overflow: 'hidden', marginTop: '0.5rem' }}>
                                    <div style={{
                                        background: 'var(--warning)',
                                        height: '100%',
                                        width: `${(dashboard.general_kpis.customer_satisfaction_score / 5) * 100}%`,
                                        transition: 'width 0.3s ease'
                                    }} />
                                </div>
                            </div>
                        </div>
                    </div>

                    {/* Integration Index */}
                    <div className="card">
                        <h3 className="card-title" style={{ fontSize: '1.25rem', marginBottom: '1.5rem' }}>Integration Index</h3>
                        <div className="grid grid-4" style={{ gap: '1.5rem' }}>
                            <div>
                                <div className="text-small text-muted">Coordination Effectiveness</div>
                                <div style={{ fontSize: '2rem', fontWeight: '700', color: 'var(--primary)' }}>
                                    {dashboard.integration_index.components.coordination_effectiveness.toFixed(1)}%
                                </div>
                            </div>
                            <div>
                                <div className="text-small text-muted">Process Alignment</div>
                                <div style={{ fontSize: '2rem', fontWeight: '700', color: 'var(--success)' }}>
                                    {dashboard.integration_index.components.process_alignment.toFixed(1)}%
                                </div>
                            </div>
                            <div>
                                <div className="text-small text-muted">Reporting Timeliness</div>
                                <div style={{ fontSize: '2rem', fontWeight: '700', color: 'var(--info)' }}>
                                    {dashboard.integration_index.components.reporting_timeliness.toFixed(1)}%
                                </div>
                            </div>
                            <div>
                                <div className="text-small text-muted">Collaboration Score</div>
                                <div style={{ fontSize: '2rem', fontWeight: '700', color: 'var(--warning)' }}>
                                    {dashboard.integration_index.components.collaboration_score.toFixed(1)}%
                                </div>
                            </div>
                        </div>
                        <div style={{ marginTop: '1.5rem', padding: '1rem', background: 'var(--gray-100)', borderRadius: 'var(--radius)', textAlign: 'center' }}>
                            <div className="text-small text-muted">Overall Integration Index</div>
                            <div style={{ fontSize: '3rem', fontWeight: '800', color: 'var(--primary)' }}>
                                {dashboard.integration_index.integration_index.toFixed(1)}%
                            </div>
                        </div>
                    </div>
                </>
            )}

            {/* Fleet Tab */}
            {activeTab === 'fleet' && (
                <div className="card">
                    <h3 className="card-title" style={{ fontSize: '1.25rem', marginBottom: '1.5rem' }}>Fleet KPIs 🚗</h3>
                    <div className="grid grid-2" style={{ gap: '1.5rem' }}>
                        <div>
                            <div className="text-small text-muted">Trip Completion Rate</div>
                            <div style={{ fontSize: '2.5rem', fontWeight: '700', color: 'var(--success)' }}>
                                {dashboard.resource_kpis.fleet.trip_completion_rate.toFixed(1)}%
                            </div>
                        </div>
                        <div>
                            <div className="text-small text-muted">Fuel Efficiency (km/L)</div>
                            <div style={{ fontSize: '2.5rem', fontWeight: '700', color: 'var(--info)' }}>
                                {dashboard.resource_kpis.fleet.fuel_efficiency_km_per_liter.toFixed(2)}
                            </div>
                        </div>
                    </div>
                </div>
            )}

            {/* HR Tab */}
            {activeTab === 'hr' && (
                <div className="card">
                    <h3 className="card-title" style={{ fontSize: '1.25rem', marginBottom: '1.5rem' }}>HR KPIs</h3>
                    <div className="grid grid-2" style={{ gap: '1.5rem' }}>
                        <div>
                            <div className="text-small text-muted">Deployment Filling Rate</div>
                            <div style={{ fontSize: '2.5rem', fontWeight: '700', color: 'var(--success)' }}>
                                {dashboard.resource_kpis.hr.deployment_filling_rate.toFixed(1)}%
                            </div>
                        </div>
                        <div>
                            <div className="text-small text-muted">Overtime Usage Rate</div>
                            <div style={{ fontSize: '2.5rem', fontWeight: '700', color: 'var(--warning)' }}>
                                {dashboard.resource_kpis.hr.overtime_usage_rate.toFixed(1)}%
                            </div>
                        </div>
                    </div>
                </div>
            )}

            {/* Finance Tab */}
            {activeTab === 'finance' && (
                <div className="card">
                    <h3 className="card-title" style={{ fontSize: '1.25rem', marginBottom: '1.5rem' }}>Finance KPIs</h3>
                    <div className="grid grid-2" style={{ gap: '1.5rem' }}>
                        <div>
                            <div className="text-small text-muted">Payment Accuracy Rate</div>
                            <div style={{ fontSize: '2.5rem', fontWeight: '700', color: 'var(--success)' }}>
                                {dashboard.resource_kpis.finance.payment_accuracy_rate.toFixed(1)}%
                            </div>
                        </div>
                        <div>
                            <div className="text-small text-muted">Document Completeness Rate</div>
                            <div style={{ fontSize: '2.5rem', fontWeight: '700', color: 'var(--info)' }}>
                                {dashboard.resource_kpis.finance.document_completeness_rate.toFixed(1)}%
                            </div>
                        </div>
                    </div>
                </div>
            )}

            {/* ICT Tab */}
            {activeTab === 'ict' && (
                <div className="card">
                    <h3 className="card-title" style={{ fontSize: '1.25rem', marginBottom: '1.5rem' }}>ICT KPIs</h3>
                    <div className="grid grid-2" style={{ gap: '1.5rem' }}>
                        <div>
                            <div className="text-small text-muted">Ticket Resolution Rate</div>
                            <div style={{ fontSize: '2.5rem', fontWeight: '700', color: 'var(--success)' }}>
                                {dashboard.resource_kpis.ict.ticket_resolution_rate.toFixed(1)}%
                            </div>
                        </div>
                        <div>
                            <div className="text-small text-muted">Reopened Tickets Rate</div>
                            <div style={{ fontSize: '2.5rem', fontWeight: '700', color: 'var(--error)' }}>
                                {dashboard.resource_kpis.ict.reopened_tickets_rate.toFixed(1)}%
                            </div>
                        </div>
                    </div>
                </div>
            )}

            {/* Logistics Tab */}
            {activeTab === 'logistics' && (
                <div className="card">
                    <h3 className="card-title" style={{ fontSize: '1.25rem', marginBottom: '1.5rem' }}>Logistics KPIs</h3>
                    <div className="grid grid-2" style={{ gap: '1.5rem' }}>
                        <div>
                            <div className="text-small text-muted">On-Time Delivery Rate</div>
                            <div style={{ fontSize: '2.5rem', fontWeight: '700', color: 'var(--success)' }}>
                                {dashboard.resource_kpis.logistics.on_time_delivery_rate.toFixed(1)}%
                            </div>
                        </div>
                        <div>
                            <div className="text-small text-muted">Stock Fulfillment Rate</div>
                            <div style={{ fontSize: '2.5rem', fontWeight: '700', color: 'var(--info)' }}>
                                {dashboard.resource_kpis.logistics.stock_fulfillment_rate.toFixed(1)}%
                            </div>
                        </div>
                    </div>
                </div>
            )}
        </div>
    );
};
