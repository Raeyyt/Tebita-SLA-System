import { useEffect, useMemo, useState } from 'react';
import { api } from '../services/api';
import { useAuth } from '../contexts/AuthContext';
import { useNavigate } from 'react-router-dom';
import type { Request } from '../types';
import { formatDate } from '../utils/dateUtils';

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
    MEDIUM: '#f59e0b',
    LOW: '#3b82f6',
};

export const RequestInboxPage = () => {
    const navigate = useNavigate();
    const { token, user } = useAuth();
    const [requests, setRequests] = useState<Request[]>([]);
    const [loading, setLoading] = useState(true);
    const [actionLoading, setActionLoading] = useState<number | null>(null);
    const [error, setError] = useState<string | null>(null);

    useEffect(() => {
        const load = async () => {
            if (!token) return;
            try {
                setLoading(true);
                const data = await api.getIncomingRequests(token);
                setRequests(data);
            } catch (err) {
                console.error('Failed to load incoming requests', err);
                setError('Failed to load incoming requests');
            } finally {
                setLoading(false);
            }
        };
        load();
    }, [token]);

    const handleAcknowledge = async (requestId: number) => {
        if (!token) return;
        console.log('Acknowledging request:', requestId);
        try {
            setActionLoading(requestId);
            await api.acknowledgeRequest(token, requestId);
            console.log('Acknowledge successful - reloading page');
            // Force page reload to ensure UI updates
            window.location.reload();
        } catch (err: any) {
            console.error('Failed to acknowledge request', err);
            const errorMessage = err.response?.data?.detail || 'Failed to acknowledge request';
            setError(errorMessage);
            setActionLoading(null);
        }
    };

    const handleComplete = async (requestId: number) => {
        if (!token) return;
        try {
            setActionLoading(requestId);
            await api.completeRequest(token, requestId);
            window.location.reload();
        } catch (err: any) {
            console.error('Failed to complete request', err);
            setError(err.response?.data?.detail || 'Failed to complete request');
            setActionLoading(null);
        }
    };

    const handleValidate = async (requestId: number) => {
        if (!token) return;
        try {
            setActionLoading(requestId);
            await api.validateRequestCompletion(token, requestId);
            window.location.reload();
        } catch (err: any) {
            console.error('Failed to validate completion', err);
            setError(err.response?.data?.detail || 'Failed to validate completion');
            setActionLoading(null);
        }
    };

    const pendingAcknowledgement = useMemo(
        () => requests.filter((req) => !req.acknowledged_at),
        [requests]
    );

    const pendingValidation = useMemo(
        () => requests.filter((req) => req.completed_at && !req.completion_validated_at),
        [requests]
    );

    const acknowledgedRequests = useMemo(
        () => requests.filter((req) => req.acknowledged_at && !req.completed_at),
        [requests]
    );

    const completedRequests = useMemo(
        () => requests.filter((req) => req.completed_at),
        [requests]
    );

    if (loading) {
        return <div className="spinner"></div>;
    }

    return (
        <div>
            <div className="card-header">
                <div>
                    <h1 className="card-title">Incoming Requests</h1>
                    <p className="text-muted">
                        Requests assigned to {user?.department_id ? 'your department' : 'you'}
                    </p>
                </div>
            </div>

            {error && (
                <div className="alert alert-error" style={{ marginBottom: '1rem' }}>
                    {error}
                </div>
            )}

            <section className="card" style={{ marginBottom: '2rem' }}>
                <div className="card-header" style={{ marginBottom: '1rem' }}>
                    <div>
                        <h2 className="card-title">Awaiting Acknowledgement</h2>
                        <p className="text-muted">{pendingAcknowledgement.length} requests</p>
                    </div>
                </div>
                {pendingAcknowledgement.length === 0 ? (
                    <p className="text-muted">No requests awaiting acknowledgement.</p>
                ) : (
                    <div className="table-wrapper">
                        <table>
                            <thead>
                                <tr>
                                    <th>Request ID</th>
                                    <th>Sender</th>
                                    <th>Description</th>
                                    <th>Priority</th>
                                    <th>Status</th>
                                    <th>Submitted</th>
                                    <th>Action</th>
                                </tr>
                            </thead>
                            <tbody>
                                {pendingAcknowledgement.map((request) => (
                                    <tr key={request.id}>
                                        <td className="font-bold">{request.request_id}</td>
                                        <td>
                                            <div className="font-bold">{request.requester?.full_name}</div>
                                            <div className="text-small text-muted">
                                                {request.requester_subdepartment?.name ||
                                                    request.requester_department?.name ||
                                                    request.requester_division?.name}
                                            </div>
                                        </td>
                                        <td style={{ maxWidth: '260px' }}>{request.description}</td>
                                        <td>
                                            <span
                                                style={{
                                                    display: 'inline-block',
                                                    padding: '0.25rem 0.75rem',
                                                    borderRadius: '999px',
                                                    fontSize: '0.75rem',
                                                    background: priorityColors[request.priority],
                                                    color: '#fff',
                                                }}
                                            >
                                                {request.priority}
                                            </span>
                                        </td>
                                        <td>
                                            <span
                                                style={{
                                                    display: 'inline-block',
                                                    padding: '0.25rem 0.75rem',
                                                    borderRadius: '999px',
                                                    fontSize: '0.75rem',
                                                    background: statusColors[request.status] || '#6b7280',
                                                    color: '#fff',
                                                }}
                                            >
                                                {request.status.replace(/_/g, ' ')}
                                            </span>
                                        </td>
                                        <td>{formatDate(request.submitted_at || request.created_at)}</td>
                                        <td>
                                            <div style={{ display: 'flex', gap: '0.5rem' }}>
                                                <button
                                                    className="btn btn-outline"
                                                    onClick={() => navigate(`/requests/${request.id}`)}
                                                >
                                                    View
                                                </button>
                                                <button
                                                    className="btn btn-primary"
                                                    disabled={actionLoading === request.id}
                                                    onClick={() => handleAcknowledge(request.id)}
                                                >
                                                    {actionLoading === request.id ? 'Processing...' : 'Acknowledge'}
                                                </button>
                                            </div>
                                        </td>
                                    </tr>
                                ))}
                            </tbody>
                        </table>
                    </div>
                )}
            </section>

            <section className="card" style={{ marginBottom: '2rem' }}>
                <div className="card-header" style={{ marginBottom: '1rem' }}>
                    <div>
                        <h2 className="card-title">Acknowledged / In Progress</h2>
                        <p className="text-muted">{acknowledgedRequests.length} requests</p>
                    </div>
                </div>
                {acknowledgedRequests.length === 0 ? (
                    <p className="text-muted">No acknowledged requests in progress.</p>
                ) : (
                    <div className="table-wrapper">
                        <table>
                            <thead>
                                <tr>
                                    <th>Request ID</th>
                                    <th>Sender</th>
                                    <th>Description</th>
                                    <th>Priority</th>
                                    <th>Status</th>
                                    <th>Submitted</th>
                                    <th>Action</th>
                                </tr>
                            </thead>
                            <tbody>
                                {acknowledgedRequests.map((request) => (
                                    <tr key={request.id}>
                                        <td className="font-bold">{request.request_id}</td>
                                        <td>
                                            <div className="font-bold">{request.requester?.full_name}</div>
                                            <div className="text-small text-muted">
                                                {request.requester_subdepartment?.name ||
                                                    request.requester_department?.name ||
                                                    request.requester_division?.name}
                                            </div>
                                        </td>
                                        <td style={{ maxWidth: '260px' }}>{request.description}</td>
                                        <td>
                                            <span
                                                style={{
                                                    display: 'inline-block',
                                                    padding: '0.25rem 0.75rem',
                                                    borderRadius: '999px',
                                                    fontSize: '0.75rem',
                                                    background: priorityColors[request.priority],
                                                    color: '#fff',
                                                }}
                                            >
                                                {request.priority}
                                            </span>
                                        </td>
                                        <td>
                                            <span
                                                style={{
                                                    display: 'inline-block',
                                                    padding: '0.25rem 0.75rem',
                                                    borderRadius: '999px',
                                                    fontSize: '0.75rem',
                                                    background: statusColors[request.status] || '#6b7280',
                                                    color: '#fff',
                                                }}
                                            >
                                                {request.status.replace(/_/g, ' ')}
                                            </span>
                                        </td>
                                        <td>{new Date(request.submitted_at || request.created_at).toLocaleString()}</td>
                                        <td>
                                            <div style={{ display: 'flex', gap: '0.5rem' }}>
                                                <button
                                                    className="btn btn-outline"
                                                    onClick={() => navigate(`/requests/${request.id}`)}
                                                >
                                                    View
                                                </button>
                                                <button
                                                    className="btn btn-success"
                                                    disabled={actionLoading === request.id}
                                                    onClick={() => handleComplete(request.id)}
                                                >
                                                    {actionLoading === request.id ? 'Processing...' : 'Mark as Complete'}
                                                </button>
                                            </div>
                                        </td>
                                    </tr>
                                ))}
                            </tbody>
                        </table>
                    </div>
                )}
            </section>

            <section className="card" style={{ marginBottom: '2rem' }}>
                <div className="card-header" style={{ marginBottom: '1rem' }}>
                    <div>
                        <h2 className="card-title">Completed Requests</h2>
                        <p className="text-muted">{completedRequests.length} requests</p>
                    </div>
                </div>
                {completedRequests.length === 0 ? (
                    <p className="text-muted">No completed requests.</p>
                ) : (
                    <div className="table-wrapper">
                        <table>
                            <thead>
                                <tr>
                                    <th>Request ID</th>
                                    <th>Sender</th>
                                    <th>Description</th>
                                    <th>Priority</th>
                                    <th>Status</th>
                                    <th>Completed</th>
                                    <th>Action</th>
                                </tr>
                            </thead>
                            <tbody>
                                {completedRequests.map((request) => (
                                    <tr key={request.id}>
                                        <td className="font-bold">{request.request_id}</td>
                                        <td>
                                            <div className="font-bold">{request.requester?.full_name}</div>
                                            <div className="text-small text-muted">
                                                {request.requester_subdepartment?.name ||
                                                    request.requester_department?.name ||
                                                    request.requester_division?.name}
                                            </div>
                                        </td>
                                        <td style={{ maxWidth: '260px' }}>{request.description}</td>
                                        <td>
                                            <span
                                                style={{
                                                    display: 'inline-block',
                                                    padding: '0.25rem 0.75rem',
                                                    borderRadius: '999px',
                                                    fontSize: '0.75rem',
                                                    background: priorityColors[request.priority],
                                                    color: '#fff',
                                                }}
                                            >
                                                {request.priority}
                                            </span>
                                        </td>
                                        <td>
                                            <span
                                                style={{
                                                    display: 'inline-block',
                                                    padding: '0.25rem 0.75rem',
                                                    borderRadius: '999px',
                                                    fontSize: '0.75rem',
                                                    background: statusColors[request.status] || '#6b7280',
                                                    color: '#fff',
                                                }}
                                            >
                                                {request.status.replace(/_/g, ' ')}
                                            </span>
                                        </td>
                                        <td>{request.completed_at ? formatDate(request.completed_at) : 'N/A'}</td>
                                        <td>
                                            <button
                                                className="btn btn-outline"
                                                onClick={() => navigate(`/requests/${request.id}`)}
                                            >
                                                View
                                            </button>
                                        </td>
                                    </tr>
                                ))}
                            </tbody>
                        </table>
                    </div>
                )}
            </section>
        </div>
    );
};
