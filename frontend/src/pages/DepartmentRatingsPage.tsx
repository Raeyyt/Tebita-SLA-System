import { useState, useEffect } from 'react';
import { useAuth } from '../contexts/AuthContext';
import { api } from '../services/api';
import { Link } from 'react-router-dom';

interface DepartmentRating {
    department_id: number;
    department_name: string;
    total_ratings: number;
    average_overall: number;
    average_timeliness: number;
    average_quality: number;
    average_communication: number;
    average_professionalism: number;
    recent_ratings_count: number;
    recent_comments: Array<{
        comment: string;
        submitted_at: string;
        request_id: number;
    }>;
}

interface AnalyticsData {
    departments: DepartmentRating[];
    total_departments_rated: number;
    top_performer: DepartmentRating | null;
    needs_improvement: DepartmentRating | null;
}

export const DepartmentRatingsPage = () => {
    const { token } = useAuth();
    const [analytics, setAnalytics] = useState<AnalyticsData | null>(null);
    const [loading, setLoading] = useState(true);
    const [selectedDepartment, setSelectedDepartment] = useState<DepartmentRating | null>(null);

    useEffect(() => {
        const fetchAnalytics = async () => {
            if (!token) return;

            try {
                const data = await api.getAllDepartmentsRatingAnalytics(token);
                setAnalytics(data);
            } catch (err) {
                console.error('Failed to load rating analytics:', err);
            } finally {
                setLoading(false);
            }
        };

        fetchAnalytics();
    }, [token]);

    const getRatingColor = (score: number) => {
        if (score >= 4.5) return '#10B981'; // green
        if (score >= 3.5) return '#F59E0B'; // yellow
        return '#EF4444'; // red
    };

    const getRatingLabel = (score: number) => {
        if (score >= 4.5) return 'Excellent';
        if (score >= 3.5) return 'Good';
        if (score >= 2.5) return 'Average';
        return 'Needs Improvement';
    };

    if (loading) {
        return (
            <div style={{ padding: '2rem' }}>
                <div className="card">
                    <div style={{ padding: '3rem', textAlign: 'center' }}>
                        Loading rating analytics...
                    </div>
                </div>
            </div>
        );
    }

    if (!analytics || analytics.departments.length === 0) {
        return (
            <div style={{ padding: '2rem' }}>
                <div className="card">
                    <div className="card-header">
                        <h1 className="card-title">Department Ratings</h1>
                    </div>
                    <div style={{ padding: '3rem', textAlign: 'center' }}>
                        <p style={{ fontSize: '1.2rem', color: 'var(--text-muted)' }}>
                            No rating data available yet. Ratings will appear here once requests are completed and rated.
                        </p>
                    </div>
                </div>
            </div>
        );
    }

    return (
        <div style={{ padding: '2rem' }}>
            {/* Header */}
            <div className="card-header" style={{ marginBottom: '2rem' }}>
                <div>
                    <h1 className="card-title">Department Performance Ratings</h1>
                    <p className="text-muted">{analytics.total_departments_rated} departments rated</p>
                </div>
            </div>

            {/* Top Performer & Needs Improvement Cards */}
            <div className="grid grid-2" style={{ gap: '1.5rem', marginBottom: '2rem' }}>
                {analytics.top_performer && (
                    <div className="card" style={{ border: '2px solid #10B981' }}>
                        <div style={{ padding: '1.5rem' }}>
                            <div style={{ fontSize: '0.875rem', color: '#10B981', fontWeight: '600', marginBottom: '0.5rem' }}>
                                TOP PERFORMER
                            </div>
                            <div style={{ fontSize: '1.5rem', fontWeight: '700', marginBottom: '0.5rem' }}>
                                {analytics.top_performer.department_name}
                            </div>
                            <div style={{ fontSize: '3rem', fontWeight: '800', color: '#10B981' }}>
                                {analytics.top_performer.average_overall.toFixed(1)} / 5.0
                            </div>
                            <div style={{ fontSize: '0.875rem', color: 'var(--text-muted)', marginTop: '0.5rem' }}>
                                Based on {analytics.top_performer.total_ratings} ratings
                            </div>
                        </div>
                    </div>
                )}

                {analytics.needs_improvement && analytics.departments.length > 1 && (
                    <div className="card" style={{ border: '2px solid #F59E0B' }}>
                        <div style={{ padding: '1.5rem' }}>
                            <div style={{ fontSize: '0.875rem', color: '#F59E0B', fontWeight: '600', marginBottom: '0.5rem' }}>
                                IMPROVEMENT OPPORTUNITY
                            </div>
                            <div style={{ fontSize: '1.5rem', fontWeight: '700', marginBottom: '0.5rem' }}>
                                {analytics.needs_improvement.department_name}
                            </div>
                            <div style={{ fontSize: '3rem', fontWeight: '800', color: '#F59E0B' }}>
                                {analytics.needs_improvement.average_overall.toFixed(1)} / 5.0
                            </div>
                            <div style={{ fontSize: '0.875rem', color: 'var(--text-muted)', marginTop: '0.5rem' }}>
                                Based on {analytics.needs_improvement.total_ratings} ratings
                            </div>
                        </div>
                    </div>
                )}
            </div>

            {/* Department Rankings Table */}
            <div className="card">
                <div className="card-header">
                    <h2 className="card-title">Department Rankings</h2>
                </div>

                <div style={{ overflowX: 'auto' }}>
                    <table className="data-table">
                        <thead>
                            <tr>
                                <th>Rank</th>
                                <th>Department</th>
                                <th style={{ textAlign: 'center' }}>Overall</th>
                                <th style={{ textAlign: 'center' }}>Timeliness</th>
                                <th style={{ textAlign: 'center' }}>Quality</th>
                                <th style={{ textAlign: 'center' }}>Communication</th>
                                <th style={{ textAlign: 'center' }}>Professionalism</th>
                                <th style={{ textAlign: 'center' }}>Total Ratings</th>
                                <th style={{ textAlign: 'center' }}>Last 30 Days</th>
                                <th style={{ textAlign: 'center' }}>Actions</th>
                            </tr>
                        </thead>
                        <tbody>
                            {analytics.departments.map((dept, index) => (
                                <tr key={dept.department_id}>
                                    <td style={{ fontWeight: '700', fontSize: '1.2rem' }}>
                                        #{index + 1}
                                    </td>
                                    <td style={{ fontWeight: '600' }}>{dept.department_name}</td>
                                    <td style={{ textAlign: 'center' }}>
                                        <div style={{
                                            fontWeight: '700',
                                            fontSize: '1.1rem',
                                            color: getRatingColor(dept.average_overall)
                                        }}>
                                            {dept.average_overall.toFixed(1)}
                                        </div>
                                        <div style={{ fontSize: '0.75rem', color: 'var(--text-muted)' }}>
                                            {getRatingLabel(dept.average_overall)}
                                        </div>
                                    </td>
                                    <td style={{ textAlign: 'center' }}>{dept.average_timeliness.toFixed(1)}</td>
                                    <td style={{ textAlign: 'center' }}>{dept.average_quality.toFixed(1)}</td>
                                    <td style={{ textAlign: 'center' }}>{dept.average_communication.toFixed(1)}</td>
                                    <td style={{ textAlign: 'center' }}>{dept.average_professionalism.toFixed(1)}</td>
                                    <td style={{ textAlign: 'center' }}>{dept.total_ratings}</td>
                                    <td style={{ textAlign: 'center' }}>
                                        <span className="badge badge-primary">
                                            {dept.recent_ratings_count}
                                        </span>
                                    </td>
                                    <td style={{ textAlign: 'center' }}>
                                        <button
                                            className="btn btn-sm btn-outline"
                                            onClick={() => setSelectedDepartment(dept)}
                                        >
                                            View Details
                                        </button>
                                    </td>
                                </tr>
                            ))}
                        </tbody>
                    </table>
                </div>
            </div>

            {/* Department Details Modal */}
            {selectedDepartment && (
                <div className="modal-overlay" onClick={() => setSelectedDepartment(null)}>
                    <div className="modal-content" onClick={(e) => e.stopPropagation()} style={{ maxWidth: '800px', maxHeight: '80vh', overflowY: 'auto' }}>
                        <div className="modal-header">
                            <h2>{selectedDepartment.department_name} - Detailed Ratings</h2>
                            <button className="modal-close" onClick={() => setSelectedDepartment(null)}>×</button>
                        </div>

                        <div style={{ padding: '2rem' }}>
                            {/* Score Breakdown */}
                            <div className="grid grid-2" style={{ gap: '1rem', marginBottom: '2rem' }}>
                                <div>
                                    <div style={{ fontSize: '0.875rem', color: 'var(--text-muted)', marginBottom: '0.25rem' }}>
                                        Timeliness
                                    </div>
                                    <div style={{ fontSize: '1.5rem', fontWeight: '700' }}>
                                        {selectedDepartment.average_timeliness.toFixed(1)} / 5
                                    </div>
                                </div>
                                <div>
                                    <div style={{ fontSize: '0.875rem', color: 'var(--text-muted)', marginBottom: '0.25rem' }}>
                                        Quality
                                    </div>
                                    <div style={{ fontSize: '1.5rem', fontWeight: '700' }}>
                                        {selectedDepartment.average_quality.toFixed(1)} / 5
                                    </div>
                                </div>
                                <div>
                                    <div style={{ fontSize: '0.875rem', color: 'var(--text-muted)', marginBottom: '0.25rem' }}>
                                        Communication
                                    </div>
                                    <div style={{ fontSize: '1.5rem', fontWeight: '700' }}>
                                        {selectedDepartment.average_communication.toFixed(1)} / 5
                                    </div>
                                </div>
                                <div>
                                    <div style={{ fontSize: '0.875rem', color: 'var(--text-muted)', marginBottom: '0.25rem' }}>
                                        Professionalism
                                    </div>
                                    <div style={{ fontSize: '1.5rem', fontWeight: '700' }}>
                                        {selectedDepartment.average_professionalism.toFixed(1)} / 5
                                    </div>
                                </div>
                            </div>

                            {/* Recent Comments */}
                            {selectedDepartment.recent_comments.length > 0 && (
                                <div>
                                    <h3 style={{ fontSize: '1.1rem', fontWeight: '600', marginBottom: '1rem' }}>
                                        Recent Comments ({selectedDepartment.recent_comments.length})
                                    </h3>
                                    <div style={{ display: 'flex', flexDirection: 'column', gap: '1rem' }}>
                                        {selectedDepartment.recent_comments.map((comment, idx) => (
                                            <div
                                                key={idx}
                                                style={{
                                                    padding: '1rem',
                                                    background: 'rgba(0, 0, 0, 0.02)',
                                                    borderRadius: '8px',
                                                    border: '1px solid rgba(0, 0, 0, 0.1)'
                                                }}
                                            >
                                                <div style={{ marginBottom: '0.5rem', fontStyle: 'italic' }}>
                                                    "{comment.comment}"
                                                </div>
                                                <div style={{ fontSize: '0.75rem', color: 'var(--text-muted)' }}>
                                                    {new Date(comment.submitted_at).toLocaleDateString()} •{' '}
                                                    <Link to={`/requests/${comment.request_id}`} style={{ color: 'var(--primary)' }}>
                                                        View Request
                                                    </Link>
                                                </div>
                                            </div>
                                        ))}
                                    </div>
                                </div>
                            )}

                            {selectedDepartment.recent_comments.length === 0 && (
                                <div style={{ padding: '2rem', textAlign: 'center', color: 'var(--text-muted)' }}>
                                    No comments available for this department
                                </div>
                            )}
                        </div>
                    </div>
                </div>
            )}
        </div>
    );
};
