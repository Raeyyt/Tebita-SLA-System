import React from 'react';

interface KPICardProps {
    title: string;
    value: number | string;
    unit?: string;
    trend?: 'up' | 'down' | 'neutral';
    trendValue?: number;
    icon?: React.ReactNode;
    color?: 'blue' | 'green' | 'yellow' | 'red' | 'purple';
}

const KPICard: React.FC<KPICardProps> = ({
    title,
    value,
    unit = '%',
    trend,
    trendValue,
    icon,
    color = 'blue'
}) => {
    const colorClasses = {
        blue: 'bg-blue-50 border-blue-200 text-blue-700',
        green: 'bg-green-50 border-green-200 text-green-700',
        yellow: 'bg-yellow-50 border-yellow-200 text-yellow-700',
        red: 'bg-red-50 border-red-200 text-red-700',
        purple: 'bg-purple-50 border-purple-200 text-purple-700'
    };

    const trendColors = {
        up: 'text-green-600',
        down: 'text-red-600',
        neutral: 'text-gray-500'
    };

    return (
        <div className={`p-6 rounded-lg border-2 ${colorClasses[color]} transition-all hover:shadow-lg`}>
            <div className="flex items-start justify-between">
                <div className="flex-1">
                    <p className="text-sm font-medium opacity-75 mb-1">{title}</p>
                    <div className="flex items-baseline gap-2">
                        <h3 className="text-3xl font-bold">
                            {typeof value === 'number' ? value.toFixed(1) : value}
                        </h3>
                        {unit && <span className="text-lg font-medium opacity-75">{unit}</span>}
                    </div>
                    {trend && trendValue !== undefined && (
                        <div className={`flex items-center gap-1 mt-2 text-sm ${trendColors[trend]}`}>
                            {trend === 'up' && '↑'}
                            {trend === 'down' && '↓'}
                            {trend === 'neutral' && '→'}
                            <span className="font-medium">{Math.abs(trendValue)}%</span>
                            <span className="text-gray-500">vs last period</span>
                        </div>
                    )}
                </div>
                {icon && (
                    <div className="text-3xl opacity-50">
                        {icon}
                    </div>
                )}
            </div>
        </div>
    );
};

export default KPICard;
