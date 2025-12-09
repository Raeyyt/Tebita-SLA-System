/**
 * BarChart Component
 * Reusable bar chart using Chart.js
 */
import React from 'react';
import { Bar } from 'react-chartjs-2';
import {
    Chart as ChartJS,
    CategoryScale,
    LinearScale,
    BarElement,
    Title,
    Tooltip,
    Legend,
} from 'chart.js';
import { defaultChartOptions, chartColorArray } from '../../utils/chartHelpers';

ChartJS.register(
    CategoryScale,
    LinearScale,
    BarElement,
    Title,
    Tooltip,
    Legend
);

interface Dataset {
    label: string;
    data: number[];
    backgroundColor?: string | string[];
    borderColor?: string | string[];
}

interface BarChartProps {
    labels: string[];
    datasets: Dataset[];
    chartId: string;
    stacked?: boolean;
    horizontal?: boolean;
    yAxisLabel?: string;
}

const BarChart: React.FC<BarChartProps> = ({
    labels,
    datasets,
    chartId,
    stacked = false,
    horizontal = false,
    yAxisLabel
}) => {
    const data = {
        labels,
        datasets: datasets.map((dataset, index) => ({
            label: dataset.label,
            data: dataset.data,
            backgroundColor: dataset.backgroundColor || chartColorArray[index % chartColorArray.length],
            borderColor: dataset.borderColor || chartColorArray[index % chartColorArray.length],
            borderWidth: 1,
        })),
    };

    const options = {
        ...defaultChartOptions,
        indexAxis: horizontal ? ('y' as const) : ('x' as const),
        scales: {
            x: {
                ...defaultChartOptions.scales.x,
                stacked: stacked,
                grid: { display: false },
            },
            y: {
                ...defaultChartOptions.scales.y,
                stacked: stacked,
                title: yAxisLabel ? {
                    display: true,
                    text: yAxisLabel,
                    font: { size: 12, weight: 'bold' as const },
                } : undefined,
            },
        },
    };

    return <Bar id={chartId} data={data} options={options} />;
};

export default BarChart;
