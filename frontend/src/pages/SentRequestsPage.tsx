import { useEffect, useState } from 'react';
import { Link } from 'react-router-dom';
import { useAuth } from '../contexts/AuthContext';
import { api } from '../services/api';
import type { Request } from '../types';
import { formatDate } from '../utils/dateUtils';

const badgeStyle = (color: string) => ({
    display: 'inline-block',
    padding: '0.25rem 0.75rem',
    borderRadius: '999px',
    fontSize: '0.75rem',
    background: color,
    color: '#fff',
});

const statusColors: Record<string, string> = {
    PENDING: '#f59e0b',
    APPROVAL_PENDING: '#f59e0b',
    APPROVED: '#3b82f6',
    IN_PROGRESS: '#0ea5e9',
    COMPLETED: '#10b981',
    REJECTED: '#ef4444',
    CANCELLED: '#ef4444',
};

const priorityColors: Record<string, string> = {
    HIGH: '#ef4444',
    MEDIUM: '#f97316',
    LOW: '#3b82f6',
};

export const SentRequestsPage = () => {
    const { token } = useAuth();
    const [requests, setRequests] = useState<Request[]>([]);
    const [loading, setLoading] = useState(true);
    const [error, setError] = useState<string | null>(null);

    useEffect(() => {
        const load = async () => {
            if (!token) return;
            try {
                setLoading(true);
                const data = await api.getSentRequests(token);
                setRequests(data);
            } catch (err) {
                console.error('Failed to load sent requests', err);
                setError('Failed to load sent requests');
            } finally {
                setLoading(false);
            }
        };
        load();
    }, [token]);

    if (loading) return <div className="spinner"></div>;

    return (
        <div>
            <div className="card-header">
                <div>
                    <h1 className="card-title">Sent Requests</h1>
                    <p className="text-muted">Track the status and accountability of requests you submitted.</p>
                </div>
                <Link to="/requests/new" className="btn btn-primary">
                    + New Request
                </Link>
            </div>

            {error && (
                <div className="alert alert-error" style={{ marginBottom: '1rem' }}>
                    {error}
                </div>
            )}

            <div className="card">
                {requests.length === 0 ? (
                    <p className="text-muted">You haven't submitted any requests yet.</p>
                ) : (
                    <div className="table-wrapper">
                        <table>
                            <thead>
                                <tr>
                                    <th>Request ID</th>
                                    <th>Recipient</th>
                                    <th>Description</th>
                                    <th>Priority</th>
                                    <th>Status</th>
                                    <th>Submitted</th>
                                    <th>Acknowledged</th>
                                    <th>Completed</th>
                                    <th>Actions</th>
                                </tr>
                            </thead>
                            <tbody>
                                {requests.map((request) => (
                                    <tr key={request.id}>
                                        <td className="font-bold">{request.request_id}</td>
                                        <td>
                                            <div className="text-small text-muted">
                                                {request.assigned_subdepartment?.name ||
                                                    request.assigned_department?.name ||
                                                    request.assigned_division?.name || 'Unassigned'}
                                            </div>
                                        </td>
                                        <td style={{ maxWidth: '280px' }}>{request.description}</td>
                                        <td>
                                            <span style={badgeStyle(priorityColors[request.priority])}>{request.priority}</span>
                                        </td>
                                        <td>
                                            <span
                                                style={badgeStyle(statusColors[request.status] || '#6b7280')}
                                            >
                                                {request.status.replace(/_/g, ' ')}
                                            </span>
                                        </td>
                                        <td>{formatDate(request.submitted_at || request.created_at)}</td>
                                        <td>{request.acknowledged_at ? formatDate(request.acknowledged_at) : 'Pending'}</td>
                                        <td>
                                            {request.completed_at
                                                ? formatDate(request.completed_at)
                                                : '—'}
                                        </td>
                                        <td>
                                            <Link to={`/requests/${request.id}`} className="btn btn-outline">
                                                View
                                            </Link>
                                        </td>
                                    </tr>
                                ))}
                            </tbody>
                        </table>
                    </div>
                )}
            </div>
        </div>
    );
};
