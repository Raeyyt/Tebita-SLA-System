/**
 * Visual Analytics Dashboard Page
 * Modern analytics design with Tebita color scheme (Strict User Request)
 * Clean, light theme with metric cards and charts
 */
import React, { useState, useEffect } from 'react';
import { useAuth } from '../contexts/AuthContext';
import { getApiUrl } from '../services/api';
import axios from 'axios';
import jsPDF from 'jspdf';
import html2canvas from 'html2canvas';

import LineChart from '../components/charts/LineChart';
import BarChart from '../components/charts/BarChart';
import PieChart from '../components/charts/PieChart';

// Tebita Color Palette (New User Request)
const COLORS = {
    primary: '#D62828', // Red
    secondary: '#F77F00', // Orange
    tertiary: '#FCBF49', // Yellow
    quaternary: '#003049', // Dark Blue
    quinary: '#EAE2B7', // Beige
    senary: '#D62828', // Red (Repeat)

    success: '#003049', // Dark Blue (Using palette for positive)
    info: '#FCBF49', // Yellow (Using palette for info)
    dark: '#003049', // Dark Blue
    light: '#EAE2B7', // Beige
    white: '#FFFFFF',
    text: '#003049', // Dark Blue
    textLight: '#4B5563', // Gray 600
    border: '#E5E7EB', // Gray 200
};

// Chart Color Array for Pie/Donut charts
const CHART_COLORS = [
    '#003049', // Dark Blue
    '#D62828', // Red
    '#F77F00', // Orange
    '#FCBF49', // Yellow
    '#EAE2B7', // Beige
];

interface DashboardData {
    period: string;
    generated_at: string;
    request_volume: {
        labels: string[];
        datasets: Array<{ label: string; data: number[] }>;
    };
    sla_compliance: {
        labels: string[];
        datasets: Array<{ label: string; data: number[] }>;
    };
    requests_by_division: {
        labels: string[];
        data: number[];
    };
    requests_by_priority: {
        labels: string[];
        datasets: Array<{ label: string; data: number[] }>;
    };
    service_efficiency: {
        labels: string[];
        datasets: Array<{ label: string; data: number[] }>;
    };
    status_distribution: {
        labels: string[];
        data: number[];
    };
    satisfaction_trend: {
        labels: string[];
        datasets: Array<{ label: string; data: number[] }>;
    };
    summary_kpis: {
        sla_compliance: number;
        fulfillment_rate: number;
        completed_count: number;
        satisfaction: number;
        integration_index: number;
        resource_optimization: number;
        avg_cost_per_request: number;
    };
}

const VisualAnalyticsPage: React.FC = () => {
    const { token } = useAuth();
    const [period, setPeriod] = useState<'daily' | 'weekly' | 'monthly' | 'yearly'>('monthly');
    const [loading, setLoading] = useState(true);
    const [data, setData] = useState<DashboardData | null>(null);
    const [error, setError] = useState<string | null>(null);
    const [exporting, setExporting] = useState(false);

    useEffect(() => {
        if (token) {
            fetchData();
        }
        // eslint-disable-next-line react-hooks/exhaustive-deps
    }, [period, token]);

    const fetchData = async () => {
        if (!token) return;

        setLoading(true);
        setError(null);
        try {
            const response = await axios.get(`${getApiUrl()}/visual-analytics/dashboard`, {
                params: { period },
                headers: {
                    Authorization: `Bearer ${token}`,
                },
            });
            setData(response.data);
        } catch (err: any) {
            setError(err.response?.data?.detail || 'Failed to load analytics data');
            console.error('Visual analytics error:', err);
        } finally {
            setLoading(false);
        }
    };

    const exportDashboardPDF = async () => {
        setExporting(true);
        try {
            window.scrollTo(0, 0);
            await new Promise(resolve => setTimeout(resolve, 500));

            const dashboardElement = document.getElementById('analytics-page-container');
            if (!dashboardElement) return;

            const canvas = await html2canvas(dashboardElement, {
                scale: 2,
                backgroundColor: '#f5f7fa',
                useCORS: true,
                logging: false,
                windowHeight: dashboardElement.scrollHeight
            });

            const imgData = canvas.toDataURL('image/png');
            const pdf = new jsPDF('p', 'mm', 'a4');
            const pdfWidth = pdf.internal.pageSize.getWidth();
            const pdfHeight = pdf.internal.pageSize.getHeight();
            const imgWidth = pdfWidth;
            const imgHeight = (canvas.height * imgWidth) / canvas.width;

            let heightLeft = imgHeight;
            let position = 0;

            pdf.addImage(imgData, 'PNG', 0, position, imgWidth, imgHeight);
            heightLeft -= pdfHeight;

            while (heightLeft >= 0) {
                position = heightLeft - imgHeight;
                pdf.addPage();
                pdf.addImage(imgData, 'PNG', 0, position, imgWidth, imgHeight);
                heightLeft -= pdfHeight;
            }

            pdf.save(`tebita-analytics-${period}-${new Date().toISOString().split('T')[0]}.pdf`);
        } catch (err) {
            console.error('PDF export failed:', err);
            alert('Failed to export PDF');
        } finally {
            setExporting(false);
        }
    };

    const downloadChart = async (chartId: string, title: string) => {
        const element = document.getElementById(chartId);
        if (!element) return;

        try {
            const canvas = await html2canvas(element, { scale: 2, backgroundColor: '#ffffff' });
            const link = document.createElement('a');
            link.download = `${title.toLowerCase().replace(/\s+/g, '-')}.png`;
            link.href = canvas.toDataURL('image/png');
            link.click();
        } catch (err) {
            console.error('Chart download failed:', err);
        }
    };

    if (loading) {
        return <div className="spinner"></div>;
    }

    if (error) {
        return (
            <div className="card">
                <p className="text-muted" style={{ color: 'red' }}>{error}</p>
                <button onClick={fetchData} className="btn btn-primary" style={{ marginTop: '1rem' }}>
                    Retry
                </button>
            </div>
        );
    }

    if (!data) return null;

    const totalRequests = data.request_volume.datasets[0]?.data.reduce((a, b) => a + b, 0) || 0;

    const getPeriodLabel = (period: string) => {
        switch (period) {
            case 'daily': return 'Last 30 days';
            case 'weekly': return 'Last 12 weeks';
            case 'monthly': return 'Last 12 months';
            case 'yearly': return 'Last 3 years';
            default: return 'This period';
        }
    };

    const ChartContainer = ({ title, id, children }: { title: string, id: string, children: React.ReactNode }) => (
        <div id={id} style={{
            background: 'white',
            borderRadius: '12px',
            padding: '1.5rem',
            boxShadow: '0 2px 8px rgba(0,0,0,0.04)',
            position: 'relative',
            borderTop: `3px solid ${COLORS.primary}`
        }}>
            <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '1.5rem' }}>
                <h3 style={{ margin: 0, fontSize: '1.1rem', fontWeight: 600, color: COLORS.text }}>
                    {title}
                </h3>
                <button
                    onClick={() => downloadChart(id, title)}
                    style={{
                        background: 'transparent',
                        border: `1px solid ${COLORS.border}`,
                        borderRadius: '6px',
                        padding: '0.25rem 0.5rem',
                        cursor: 'pointer',
                        color: COLORS.textLight,
                        fontSize: '0.8rem'
                    }}
                    title="Download Chart"
                >
                    ⬇️
                </button>
            </div>
            {children}
        </div>
    );

    // Apply custom colors to datasets
    const applyColors = (datasets: any[], type: 'line' | 'bar' = 'line') => {
        return datasets.map((ds, index) => ({
            ...ds,
            backgroundColor: type === 'line' ? `${CHART_COLORS[index % CHART_COLORS.length]}20` : CHART_COLORS[index % CHART_COLORS.length],
            borderColor: CHART_COLORS[index % CHART_COLORS.length],
            pointBackgroundColor: CHART_COLORS[index % CHART_COLORS.length],
        }));
    };

    return (
        <div id="analytics-page-container" style={{ background: '#f5f7fa', minHeight: '100vh', padding: '2rem' }}>
            {/* Header */}
            <div style={{
                background: 'white',
                borderRadius: '12px',
                padding: '1.5rem 2rem',
                marginBottom: '2rem',
                boxShadow: '0 2px 8px rgba(0,0,0,0.04)',
                display: 'flex',
                justifyContent: 'space-between',
                alignItems: 'center',
                borderLeft: `5px solid ${COLORS.primary}`
            }}>
                <div>
                    <h1 style={{ margin: 0, fontSize: '1.75rem', fontWeight: 600, color: COLORS.dark }}>
                        Visual Analytics
                    </h1>
                    <p style={{ margin: '0.25rem 0 0 0', color: COLORS.textLight, fontSize: '0.9rem' }}>
                        {new Date().toLocaleDateString('en-US', { month: 'long', day: 'numeric', year: 'numeric' })}
                    </p>
                </div>
                <div style={{ display: 'flex', gap: '0.75rem', alignItems: 'center' }}>
                    <select
                        value={period}
                        onChange={(e) => setPeriod(e.target.value as any)}
                        style={{
                            padding: '0.5rem 1rem',
                            borderRadius: '8px',
                            border: `1px solid ${COLORS.border}`,
                            background: 'white',
                            fontSize: '0.9rem',
                            cursor: 'pointer',
                            color: COLORS.text
                        }}
                    >
                        <option value="daily">Daily</option>
                        <option value="weekly">Weekly</option>
                        <option value="monthly">Monthly</option>
                        <option value="yearly">Yearly</option>
                    </select>
                    <button
                        onClick={exportDashboardPDF}
                        disabled={exporting}
                        style={{
                            padding: '0.5rem 1.25rem',
                            borderRadius: '8px',
                            border: 'none',
                            background: COLORS.primary,
                            color: 'white',
                            fontSize: '0.9rem',
                            cursor: 'pointer',
                            fontWeight: 500,
                            boxShadow: '0 2px 4px rgba(100, 0, 0, 0.2)'
                        }}
                    >
                        {exporting ? 'Exporting...' : 'Export PDF'}
                    </button>
                </div>
            </div>

            <div id="analytics-dashboard">
                {/* Metric Cards Row */}
                <div style={{
                    display: 'grid',
                    gridTemplateColumns: 'repeat(4, 1fr)',
                    gap: '1.5rem',
                    marginBottom: '2rem'
                }}>
                    {/* SLA Compliance */}
                    <div style={{
                        background: 'white',
                        borderRadius: '12px',
                        padding: '1.5rem',
                        boxShadow: '0 2px 8px rgba(0,0,0,0.04)',
                        borderTop: `4px solid ${COLORS.success}`
                    }}>
                        <div style={{ display: 'flex', alignItems: 'center', gap: '0.75rem', marginBottom: '0.75rem' }}>
                            <div style={{
                                width: '40px',
                                height: '40px',
                                borderRadius: '8px',
                                background: '#ecfdf5',
                                display: 'flex',
                                alignItems: 'center',
                                justifyContent: 'center',
                                fontSize: '1.25rem',
                                color: COLORS.success,
                                fontWeight: 'bold'
                            }}>
                                ✓
                            </div>
                            <span style={{ color: COLORS.textLight, fontSize: '0.85rem' }}>SLA Compliance</span>
                        </div>
                        <div style={{ fontSize: '2rem', fontWeight: 700, color: COLORS.dark, marginBottom: '0.25rem' }}>
                            {data.summary_kpis.sla_compliance.toFixed(1)}%
                        </div>
                        <div style={{ fontSize: '0.8rem', color: COLORS.success }}>
                            Target: 85%
                        </div>
                    </div>

                    {/* Total Requests */}
                    <div style={{
                        background: 'white',
                        borderRadius: '12px',
                        padding: '1.5rem',
                        boxShadow: '0 2px 8px rgba(0,0,0,0.04)',
                        borderTop: `4px solid ${COLORS.info}`
                    }}>
                        <div style={{ display: 'flex', alignItems: 'center', gap: '0.75rem', marginBottom: '0.75rem' }}>
                            <div style={{
                                width: '40px',
                                height: '40px',
                                borderRadius: '8px',
                                background: '#F3F4F6',
                                display: 'flex',
                                alignItems: 'center',
                                justifyContent: 'center',
                                fontSize: '1.25rem',
                                color: COLORS.info,
                                fontWeight: 'bold'
                            }}>
                                #
                            </div>
                            <span style={{ color: COLORS.textLight, fontSize: '0.85rem' }}>Total Requests</span>
                        </div>
                        <div style={{ fontSize: '2rem', fontWeight: 700, color: COLORS.dark, marginBottom: '0.25rem' }}>
                            {totalRequests.toLocaleString()}
                        </div>
                        <div style={{ fontSize: '0.8rem', color: COLORS.textLight }}>
                            {getPeriodLabel(period)}
                        </div>
                    </div>

                    {/* Satisfaction */}
                    <div style={{
                        background: 'white',
                        borderRadius: '12px',
                        padding: '1.5rem',
                        boxShadow: '0 2px 8px rgba(0,0,0,0.04)',
                        borderTop: `4px solid ${COLORS.secondary}`
                    }}>
                        <div style={{ display: 'flex', alignItems: 'center', gap: '0.75rem', marginBottom: '0.75rem' }}>
                            <div style={{
                                width: '40px',
                                height: '40px',
                                borderRadius: '8px',
                                background: '#FFF1F2',
                                display: 'flex',
                                alignItems: 'center',
                                justifyContent: 'center',
                                fontSize: '1.25rem',
                                color: COLORS.secondary,
                                fontWeight: 'bold'
                            }}>
                                ★
                            </div>
                            <span style={{ color: COLORS.textLight, fontSize: '0.85rem' }}>Satisfaction</span>
                        </div>
                        <div style={{ fontSize: '2rem', fontWeight: 700, color: COLORS.dark, marginBottom: '0.25rem' }}>
                            {data.summary_kpis.satisfaction.toFixed(1)}/5
                        </div>
                        <div style={{ fontSize: '0.8rem', color: COLORS.secondary }}>
                            Excellent rating
                        </div>
                    </div>

                    {/* Completed */}
                    <div style={{
                        background: 'white',
                        borderRadius: '12px',
                        padding: '1.5rem',
                        boxShadow: '0 2px 8px rgba(0,0,0,0.04)',
                        borderTop: `4px solid ${COLORS.primary}`
                    }}>
                        <div style={{ display: 'flex', alignItems: 'center', gap: '0.75rem', marginBottom: '0.75rem' }}>
                            <div style={{
                                width: '40px',
                                height: '40px',
                                borderRadius: '8px',
                                background: '#FEF2F2',
                                display: 'flex',
                                alignItems: 'center',
                                justifyContent: 'center',
                                fontSize: '1.25rem',
                                color: COLORS.primary,
                                fontWeight: 'bold'
                            }}>
                                ✓
                            </div>
                            <span style={{ color: COLORS.textLight, fontSize: '0.85rem' }}>Completed</span>
                        </div>
                        <div style={{ fontSize: '2rem', fontWeight: 700, color: COLORS.dark, marginBottom: '0.25rem' }}>
                            {data.summary_kpis.completed_count.toLocaleString()}
                        </div>
                        <div style={{ fontSize: '0.8rem', color: COLORS.primary }}>
                            {data.summary_kpis.fulfillment_rate.toFixed(1)}% completion rate
                        </div>
                    </div>
                </div>

                {/* Charts Grid */}
                <div style={{ display: 'grid', gridTemplateColumns: '2fr 1fr', gap: '1.5rem', marginBottom: '1.5rem' }}>
                    {/* Request Volume Chart */}
                    <ChartContainer title="Request Volume Trends" id="chart-volume">
                        <div style={{ height: '300px' }}>
                            <BarChart
                                labels={data.request_volume.labels}
                                datasets={applyColors(data.request_volume.datasets, 'bar')}
                                chartId="request-volume"
                                yAxisLabel=""
                            />
                        </div>
                    </ChartContainer>

                    {/* Division Distribution */}
                    <ChartContainer title="By Division" id="chart-division">
                        <div style={{ height: '300px' }}>
                            <PieChart
                                labels={data.requests_by_division.labels}
                                data={data.requests_by_division.data}
                                chartId="division-dist"
                                isDoughnut={true}
                                customColors={CHART_COLORS}
                            />
                        </div>
                    </ChartContainer>
                </div>

                {/* Second Row of Charts */}
                <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '1.5rem', marginBottom: '1.5rem' }}>
                    {/* SLA Compliance Trend */}
                    <ChartContainer title="SLA Compliance Over Time" id="chart-compliance">
                        <div style={{ height: '280px' }}>
                            <LineChart
                                labels={data.sla_compliance.labels}
                                datasets={applyColors(data.sla_compliance.datasets, 'line')}
                                chartId="sla-compliance"
                                yAxisLabel=""
                                fill={true}
                            />
                        </div>
                    </ChartContainer>

                    {/* Service Efficiency Trend (NEW) */}
                    <ChartContainer title="Service Efficiency Trend" id="chart-efficiency">
                        <div style={{ height: '280px' }}>
                            <LineChart
                                labels={data.service_efficiency.labels}
                                datasets={applyColors(data.service_efficiency.datasets, 'line')}
                                chartId="service-efficiency"
                                yAxisLabel=""
                                fill={true}
                            />
                        </div>
                    </ChartContainer>
                </div>

                {/* Third Row */}
                <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '1.5rem' }}>
                    {/* Priority Distribution */}
                    <ChartContainer title="Requests by Priority" id="chart-priority">
                        <div style={{ height: '280px' }}>
                            <BarChart
                                labels={data.requests_by_priority.labels}
                                datasets={applyColors(data.requests_by_priority.datasets, 'bar')}
                                chartId="priority-dist"
                                stacked={true}
                                yAxisLabel=""
                            />
                        </div>
                    </ChartContainer>

                    {/* Status Distribution */}
                    <ChartContainer title="Request Status" id="chart-status">
                        <div style={{ height: '280px' }}>
                            <PieChart
                                labels={data.status_distribution.labels}
                                data={data.status_distribution.data}
                                chartId="status-dist"
                                isDoughnut={true}
                                customColors={CHART_COLORS}
                            />
                        </div>
                    </ChartContainer>
                </div>
            </div>
        </div>
    );
};

export default VisualAnalyticsPage;
