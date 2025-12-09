/**
 * Chart Helper Utilities
 * Provides colors, gradients, and common chart configurations
 */

// Professional color palette
export const chartColors = {
    primary: '#1976d2',      // Blue
    success: '#2e7d32',      // Green
    warning: '#ed6c02',      // Orange
    danger: '#d32f2f',       // Red
    info: '#0288d1',         // Light Blue
    purple: '#9c27b0',       // Purple
    teal: '#00897b',         // Teal
    amber: '#f57c00',        // Amber
    pink: '#e91e63',         // Pink
    indigo: '#3f51b5',       // Indigo
};

// Chart color arrays for multi-dataset charts
export const chartColorArray = [
    chartColors.primary,
    chartColors.success,
    chartColors.warning,
    chartColors.info,
    chartColors.purple,
    chartColors.teal,
    chartColors.amber,
    chartColors.pink,
    chartColors.indigo,
];

// Gradient colors
export const gradients = {
    blue: {
        start: 'rgba(25, 118, 210, 0.8)',
        end: 'rgba(25, 118, 210, 0.1)',
    },
    green: {
        start: 'rgba(46, 125, 50, 0.8)',
        end: 'rgba(46, 125, 50, 0.1)',
    },
    orange: {
        start: 'rgba(237, 108, 2, 0.8)',
        end: 'rgba(237, 108, 2, 0.1)',
    },
};

// Create gradient for line/area charts
export const createGradient = (ctx: CanvasRenderingContext2D, color: string) => {
    const gradient = ctx.createLinearGradient(0, 0, 0, 400);

    if (color === chartColors.primary) {
        gradient.addColorStop(0, gradients.blue.start);
        gradient.addColorStop(1, gradients.blue.end);
    } else if (color === chartColors.success) {
        gradient.addColorStop(0, gradients.green.start);
        gradient.addColorStop(1, gradients.green.end);
    } else {
        gradient.addColorStop(0, `${color}CC`);
        gradient.addColorStop(1, `${color}1A`);
    }

    return gradient;
};

// Default chart options (professional look)
export const defaultChartOptions = {
    responsive: true,
    maintainAspectRatio: true,
    plugins: {
        legend: {
            position: 'top' as const,
            labels: {
                font: {
                    family: 'Roboto, sans-serif',
                    size: 12,
                },
                padding: 15,
                usePointStyle: true,
            },
        },
        tooltip: {
            backgroundColor: 'rgba(0, 0, 0, 0.8)',
            padding: 12,
            titleFont: { size: 14, weight: 'bold' as const },
            bodyFont: { size: 13 },
            borderColor: chartColors.primary,
            borderWidth: 1,
        },
    },
    scales: {
        x: {
            grid: { display: false },
            ticks: { font: { size: 11 } },
        },
        y: {
            grid: { color: 'rgba(0, 0, 0, 0.05)' },
            ticks: { font: { size: 11 } },
        },
    },
    animation: {
        duration: 1000,
        easing: 'easeInOutQuart' as const,
    },
};

// Doughnut/Pie chart options
export const pieChartOptions = {
    responsive: true,
    maintainAspectRatio: true,
    plugins: {
        legend: {
            position: 'right' as const,
            labels: {
                font: {
                    family: 'Roboto, sans-serif',
                    size: 12,
                },
                padding: 10,
                usePointStyle: true,
            },
        },
        tooltip: {
            backgroundColor: 'rgba(0, 0, 0, 0.8)',
            padding: 12,
            titleFont: { size: 14, weight: 'bold' as const },
            bodyFont: { size: 13 },
        },
    },
    animation: {
        duration: 1000,
        easing: 'easeInOutQuart' as const,
    },
};

// Download chart as PNG
export const downloadChart = (chartId: string, filename: string) => {
    const canvas = document.getElementById(chartId) as HTMLCanvasElement;
    if (!canvas) return;

    const url = canvas.toDataURL('image/png');
    const link = document.createElement('a');
    link.download = `${filename}-${new Date().toISOString().split('T')[0]}.png`;
    link.href = url;
    link.click();
};

// Format number with commas
export const formatNumber = (num: number): string => {
    return new Intl.NumberFormat('en-US').format(num);
};

// Format percentage
export const formatPercent = (num: number): string => {
    return `${num.toFixed(2)}%`;
};
