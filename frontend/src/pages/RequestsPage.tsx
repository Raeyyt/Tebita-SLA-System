import { useState, useEffect } from 'react';
import { useLocation } from 'react-router-dom';
import { useAuth } from '../contexts/AuthContext';
import { api } from '../services/api';
import type { Request } from '../types';
import { PDFViewerModal } from '../components/PDFViewerModal';

export const RequestsPage = () => {
    const { token } = useAuth();
    const location = useLocation();
    const initialFilter = (location.state as { filter?: string })?.filter || '';
    const [requests, setRequests] = useState<Request[]>([]);
    const [loading, setLoading] = useState(true);
    const [filter, setFilter] = useState(initialFilter);
    const [searchTerm, setSearchTerm] = useState('');
    const [selectedRequest, setSelectedRequest] = useState<Request | null>(null);
    const [isPdfOpen, setIsPdfOpen] = useState(false);

    useEffect(() => {
        const loadRequests = async () => {
            if (!token) return;
            try {
                const data = await api.getRequests(token);
                setRequests(data);
            } catch (err) {
                console.error('Failed to load requests:', err);
            } finally {
                setLoading(false);
            }
        };
        loadRequests();
    }, [token]);

    // Filter requests by search term and status
    const filteredRequests = requests.filter(request => {
        const matchesSearch = !searchTerm ||
            request.request_id.toLowerCase().includes(searchTerm.toLowerCase()) ||
            request.description?.toLowerCase().includes(searchTerm.toLowerCase());

        let matchesFilter = true;
        if (filter === 'OVERDUE') {
            // Calculate if overdue
            if (['COMPLETED', 'REJECTED', 'CANCELLED'].includes(request.status)) {
                matchesFilter = false;
            } else if (request.created_at && request.sla_completion_time_hours) {
                const deadline = new Date(new Date(request.created_at).getTime() + request.sla_completion_time_hours * 60 * 60 * 1000);
                matchesFilter = new Date() > deadline;
            } else {
                matchesFilter = false;
            }
        } else {
            matchesFilter = !filter || request.status === filter;
        }

        return matchesSearch && matchesFilter;
    });

    const getStatusBadge = (status: string) => {
        const classMap: Record<string, string> = {
            'PENDING': 'badge-pending',
            'APPROVAL_PENDING': 'badge-warning',
            'APPROVED': 'badge-info',
            'IN_PROGRESS': 'badge-info',
            'COMPLETED': 'badge-success',
            'REJECTED': 'badge-error',
            'CANCELLED': 'badge-error',
        };
        return `badge ${classMap[status] || 'badge-pending'}`;
    };

    const getPriorityBadge = (priority: string) => {
        const classMap: Record<string, string> = {
            'HIGH': 'badge-error',
            'MEDIUM': 'badge-warning',
            'LOW': 'badge-info',
        };
        return `badge ${classMap[priority] || 'badge-info'}`;
    };

    const openPdfModal = (request: Request) => {
        setSelectedRequest(request);
        setIsPdfOpen(true);
    };

    const closePdfModal = () => {
        setIsPdfOpen(false);
        setSelectedRequest(null);
    };

    const handleExport = async () => {
        if (!token) return;
        try {
            const blob = await api.exportRequestLogs(token, 30);
            const url = window.URL.createObjectURL(new Blob([blob]));
            const link = document.createElement('a');
            link.href = url;
            link.setAttribute('download', `requests_log_${new Date().toISOString().split('T')[0]}.csv`);
            document.body.appendChild(link);
            link.click();
            link.parentNode?.removeChild(link);
        } catch (err) {
            console.error('Failed to export logs:', err);
            alert('Failed to export CSV');
        }
    };

    if (loading) {
        return <div className="spinner"></div>;
    }

    return (
        <div>
            <div className="card-header">
                <div>
                    <h1 className="card-title">All Requests</h1>
                    <p className="text-muted">{filteredRequests.length} requests</p>
                </div>

                <div className="flex gap-sm">
                    <button
                        className="btn btn-outline"
                        onClick={handleExport}
                        style={{ borderColor: 'var(--success)', color: 'var(--success)' }}
                    >
                        Export CSV
                    </button>
                    {/* Modern Search Bar */}
                    <div className="modern-search-bar">
                        <input
                            type="text"
                            placeholder="Search..."
                            value={searchTerm}
                            onChange={(e) => setSearchTerm(e.target.value)}
                            className="modern-search-input"
                        />
                        <button className="modern-search-button" type="button">
                            <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
                                <circle cx="11" cy="11" r="8" />
                                <path d="m21 21-4.35-4.35" />
                            </svg>
                        </button>
                    </div>
                </div>
            </div>

            <div className="card">
                {/* Status Filters */}
                <div className="flex gap-md" style={{ marginBottom: '1.5rem', flexWrap: 'wrap' }}>
                    <button
                        className={`btn ${!filter ? 'btn-primary' : 'btn-outline'}`}
                        onClick={() => setFilter('')}
                    >
                        All
                    </button>
                    <button
                        className={`btn ${filter === 'PENDING' ? 'btn-primary' : 'btn-outline'}`}
                        onClick={() => setFilter('PENDING')}
                    >
                        Pending
                    </button>
                    <button
                        className={`btn ${filter === 'IN_PROGRESS' ? 'btn-primary' : 'btn-outline'}`}
                        onClick={() => setFilter('IN_PROGRESS')}
                    >
                        In Progress
                    </button>
                    <button
                        className={`btn ${filter === 'COMPLETED' ? 'btn-primary' : 'btn-outline'}`}
                        onClick={() => setFilter('COMPLETED')}
                    >
                        Completed
                    </button>
                    <button
                        className={`btn ${filter === 'OVERDUE' ? 'btn-primary' : 'btn-outline'}`}
                        onClick={() => setFilter('OVERDUE')}
                        style={filter === 'OVERDUE' ? { background: 'var(--error)', borderColor: 'var(--error)' } : { color: 'var(--error)', borderColor: 'var(--error)' }}
                    >
                        Overdue
                    </button>
                </div>

                {filteredRequests.length === 0 ? (
                    <p className="text-muted">No requests found</p>
                ) : (
                    <div className="table-wrapper">
                        <table>
                            <thead>
                                <tr>
                                    <th>Request ID</th>
                                    <th>Sender</th>
                                    <th>Recipient</th>
                                    <th>Description</th>
                                    <th>Priority</th>
                                    <th>Status</th>
                                    <th>Created</th>
                                    <th>Actions</th>
                                </tr>
                            </thead>
                            <tbody>
                                {filteredRequests.map((request) => (
                                    <tr key={request.id}>
                                        <td className="font-bold">{request.request_id}</td>
                                        <td>
                                            <div>
                                                <div className="font-bold">{request.requester?.full_name || 'N/A'}</div>
                                                <div className="text-small text-muted">
                                                    {request.requester_subdepartment?.name ||
                                                        request.requester_department?.name ||
                                                        request.requester_division?.name || ''}
                                                </div>
                                            </div>
                                        </td>
                                        <td>
                                            <div className="text-small text-muted">
                                                {request.assigned_subdepartment?.name ||
                                                    request.assigned_department?.name ||
                                                    request.assigned_division?.name || 'Unassigned'}
                                            </div>
                                        </td>
                                        <td style={{ maxWidth: '250px', overflow: 'hidden', textOverflow: 'ellipsis', whiteSpace: 'nowrap' }}>
                                            {request.description}
                                        </td>
                                        <td>
                                            <span className={getPriorityBadge(request.priority)}>
                                                {request.priority}
                                            </span>
                                        </td>
                                        <td>
                                            <span className={getStatusBadge(request.status)}>
                                                {request.status.replace(/_/g, ' ')}
                                            </span>
                                        </td>
                                        <td>{new Date(request.created_at).toLocaleDateString()}</td>
                                        <td>
                                            <button
                                                className="btn btn-outline"
                                                style={{ padding: '0.5rem 1rem' }}
                                                onClick={() => openPdfModal(request)}
                                            >
                                                View PDF
                                            </button>
                                        </td>
                                    </tr>
                                ))}
                            </tbody>
                        </table>
                    </div>
                )}
            </div>
            {selectedRequest && (
                <PDFViewerModal
                    requestId={selectedRequest.id}
                    requestNumber={selectedRequest.request_id}
                    isOpen={isPdfOpen}
                    onClose={closePdfModal}
                />
            )}
        </div>
    );
};
