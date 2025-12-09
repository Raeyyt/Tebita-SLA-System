/**
 * LineChart Component
 * Reusable line chart using Chart.js
 */
import React from 'react';
import { Line } from 'react-chartjs-2';
import {
    Chart as ChartJS,
    CategoryScale,
    LinearScale,
    PointElement,
    LineElement,
    Title,
    Tooltip,
    Legend,
    Filler,
} from 'chart.js';
import { defaultChartOptions, chartColorArray } from '../../utils/chartHelpers';

// Register Chart.js components
ChartJS.register(
    CategoryScale,
    LinearScale,
    PointElement,
    LineElement,
    Title,
    Tooltip,
    Legend,
    Filler
);

interface Dataset {
    label: string;
    data: number[];
    backgroundColor?: string | string[];
    borderColor?: string | string[];
}

interface LineChartProps {
    labels: string[];
    datasets: Dataset[];
    chartId: string;
    yAxisLabel?: string;
    fill?: boolean;
}

const LineChart: React.FC<LineChartProps> = ({
    labels,
    datasets,
    chartId,
    yAxisLabel,
    fill = false
}) => {
    const data = {
        labels,
        datasets: datasets.map((dataset, index) => ({
            label: dataset.label,
            data: dataset.data,
            borderColor: dataset.borderColor || chartColorArray[index % chartColorArray.length],
            backgroundColor: dataset.backgroundColor || (fill
                ? `${chartColorArray[index % chartColorArray.length]}33`
                : 'transparent'),
            borderWidth: 2,
            pointRadius: 3,
            pointHoverRadius: 5,
            fill: fill,
            tension: 0.4, // Smooth curves
        })),
    };

    const options = {
        ...defaultChartOptions,
        scales: {
            ...defaultChartOptions.scales,
            y: {
                ...defaultChartOptions.scales.y,
                title: yAxisLabel ? {
                    display: true,
                    text: yAxisLabel,
                    font: { size: 12, weight: 'bold' as const },
                } : undefined,
            },
        },
    };

    return <Line id={chartId} data={data} options={options} />;
};

export default LineChart;
