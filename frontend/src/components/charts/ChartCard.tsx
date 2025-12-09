/**
 * ChartCard Component
 * Wrapper for charts with download button
 * Matches design language of other pages
 */
import React from 'react';

interface ChartCardProps {
    title: string;
    children: React.ReactNode;
    chartId: string;
    onDownload: () => void;
}

const ChartCard: React.FC<ChartCardProps> = ({ title, children, chartId, onDownload }) => {
    return (
        <div className="card" style={{ height: '450px', display: 'flex', flexDirection: 'column' }}>
            <div style={{
                display: 'flex',
                justifyContent: 'space-between',
                alignItems: 'center',
                borderBottom: '1px solid var(--gray-200)',
                paddingBottom: '1rem',
                marginBottom: '1rem'
            }}>
                <h3 style={{ margin: 0, fontSize: '1.1rem', fontWeight: 600 }}>{title}</h3>
                <button
                    onClick={onDownload}
                    className="btn btn-outline"
                    style={{ padding: '0.25rem 0.75rem', fontSize: '0.875rem' }}
                    title="Download Chart"
                >
                    📥 Download
                </button>
            </div>
            <div
                id={`chart-container-${chartId}`}
                style={{ flex: 1, position: 'relative', minHeight: 0 }}
            >
                {children}
            </div>
        </div>
    );
};

export default ChartCard;
