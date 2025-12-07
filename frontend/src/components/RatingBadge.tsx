import React from 'react';
import type { ScoreRating } from '../types/analytics';

interface RatingBadgeProps {
    rating: ScoreRating;
    score: number;
}

const RatingBadge: React.FC<RatingBadgeProps> = ({ rating, score }) => {
    const ratingConfig = {
        OUTSTANDING: {
            label: 'Outstanding',
            color: 'bg-green-100 text-green-800 border-green-300',
            icon: ''
        },
        VERY_GOOD: {
            label: 'Very Good',
            color: 'bg-blue-100 text-blue-800 border-blue-300',
            icon: '👍'
        },
        GOOD: {
            label: 'Good',
            color: 'bg-yellow-100 text-yellow-800 border-yellow-300',
            icon: ''
        },
        NEEDS_IMPROVEMENT: {
            label: 'Needs Improvement',
            color: 'bg-orange-100 text-orange-800 border-orange-300',
            icon: ''
        },
        UNSATISFACTORY: {
            label: 'Unsatisfactory',
            color: 'bg-red-100 text-red-800 border-red-300',
            icon: '✗'
        }
    };

    const config = ratingConfig[rating] || ratingConfig.GOOD;

    return (
        <div className={`inline-flex items-center gap-2 px-4 py-2 rounded-full border-2 font-semibold ${config.color}`}>
            <span className="text-xl">{config.icon}</span>
            <span>{config.label}</span>
            <span className="ml-1 text-sm">({score.toFixed(1)}%)</span>
        </div>
    );
};

export default RatingBadge;
