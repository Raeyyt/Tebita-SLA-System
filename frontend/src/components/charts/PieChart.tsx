/**
 * PieChart Component
 * Reusable pie/doughnut chart using Chart.js
 */
import React from 'react';
import { Pie, Doughnut } from 'react-chartjs-2';
import {
    Chart as ChartJS,
    ArcElement,
    Tooltip,
    Legend,
} from 'chart.js';
import { pieChartOptions, chartColorArray } from '../../utils/chartHelpers';

ChartJS.register(ArcElement, Tooltip, Legend);

interface PieChartProps {
    labels: string[];
    data: number[];
    chartId: string;
    isDoughnut?: boolean;
    customColors?: string[];
}

const PieChart: React.FC<PieChartProps> = ({ labels, data, chartId, isDoughnut = false, customColors }) => {
    const chartData = {
        labels,
        datasets: [
            {
                data,
                backgroundColor: customColors || chartColorArray,
                borderColor: '#fff',
                borderWidth: 2,
            },
        ],
    };

    const ChartComponent = isDoughnut ? Doughnut : Pie;

    return <ChartComponent id={chartId} data={chartData} options={pieChartOptions} />;
};

export default PieChart;
