import { useState, useEffect } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import { useAuth } from '../contexts/AuthContext';
import { api } from '../services/api';
import type { Request, FleetRequest, HRDeployment, FinanceTransaction, ICTTicket, LogisticsRequest } from '../types';
import { RatingModal, type RatingData } from '../components/RatingModal';

export const RequestViewPage = () => {
    const { id } = useParams<{ id: string }>();
    const navigate = useNavigate();
    const { token } = useAuth();
    const [request, setRequest] = useState<Request | null>(null);
    const [loading, setLoading] = useState(true);


    // Resource-specific state
    const [fleetDetails, setFleetDetails] = useState<FleetRequest | null>(null);
    const [_fleetLoading, setFleetLoading] = useState(false);
    const [fleetForm, setFleetForm] = useState<Partial<FleetRequest>>({});

    const [hrDetails, setHrDetails] = useState<HRDeployment | null>(null);
    const [_hrLoading, setHrLoading] = useState(false);
    const [hrForm, setHrForm] = useState<Partial<HRDeployment>>({});

    const [financeDetails, setFinanceDetails] = useState<FinanceTransaction | null>(null);
    const [_financeLoading, setFinanceLoading] = useState(false);
    const [financeForm, setFinanceForm] = useState<Partial<FinanceTransaction>>({});

    const [ictDetails, setIctDetails] = useState<ICTTicket | null>(null);
    const [_ictLoading, setIctLoading] = useState(false);
    const [ictForm, setIctForm] = useState<Partial<ICTTicket>>({});

    const [logisticsDetails, setLogisticsDetails] = useState<LogisticsRequest | null>(null);
    const [_logisticsLoading, setLogisticsLoading] = useState(false);
    const [logisticsForm, setLogisticsForm] = useState<Partial<LogisticsRequest>>({});

    // Rating state
    const [showRatingModal, setShowRatingModal] = useState(false);
    const [existingRating, setExistingRating] = useState<any>(null);
    const [_ratingLoading, setRatingLoading] = useState(false);

    useEffect(() => {
        const fetchRequest = async () => {
            if (!token || !id) return;

            try {
                const data = await api.getRequest(token, parseInt(id));
                setRequest(data);

                // Fetch resource-specific details if applicable
                if (data.resource_type === 'FLEET') {
                    setFleetLoading(true);
                    try {
                        const fleet = await api.getFleetDetails(token, parseInt(id));
                        setFleetDetails(fleet);
                        setFleetForm(fleet);
                    } catch (err) {
                        // Ignore 404 (no details yet)
                        console.log('No existing fleet details found');
                    } finally {
                        setFleetLoading(false);
                    }
                } else if (data.resource_type === 'HR') {
                    setHrLoading(true);
                    try {
                        const hr = await api.getHRDetails(token, parseInt(id));
                        setHrDetails(hr);
                        setHrForm(hr);
                    } catch (err) {
                        console.log('No existing HR details found');
                    } finally {
                        setHrLoading(false);
                    }
                } else if (data.resource_type === 'FINANCE') {
                    setFinanceLoading(true);
                    try {
                        const finance = await api.getFinanceDetails(token, parseInt(id));
                        setFinanceDetails(finance);
                        setFinanceForm(finance);
                    } catch (err) {
                        console.log('No existing Finance details found');
                    } finally {
                        setFinanceLoading(false);
                    }
                } else if (data.resource_type === 'ICT') {
                    setIctLoading(true);
                    try {
                        const ict = await api.getICTDetails(token, parseInt(id));
                        setIctDetails(ict);
                        setIctForm(ict);
                    } catch (err) {
                        console.log('No existing ICT details found');
                    } finally {
                        setIctLoading(false);
                    }
                } else if (data.resource_type === 'LOGISTICS') {
                    setLogisticsLoading(true);
                    try {
                        const logistics = await api.getLogisticsDetails(token, parseInt(id));
                        setLogisticsDetails(logistics);
                        setLogisticsForm(logistics);
                    } catch (err) {
                        console.log('No existing Logistics details found');
                    } finally {
                        setLogisticsLoading(false);
                    }
                }
            } catch (error) {
                console.error('Error fetching request:', error);
            } finally {
                setLoading(false);
            }
        };

        fetchRequest();
    }, [id, token]);

    // Fetch existing rating
    useEffect(() => {
        const fetchRating = async () => {
            if (!token || !id) return;

            setRatingLoading(true);
            try {
                const rating = await api.getRating(token, parseInt(id));
                setExistingRating(rating);
            } catch (err) {
                // No rating exists yet, this is fine
                console.log('No rating found');
            } finally {
                setRatingLoading(false);
            }
        };

        fetchRating();
    }, [id, token]);

    // Handle rating submission
    const handleSubmitRating = async (ratingData: RatingData) => {
        if (!token || !id) return;

        try {
            const newRating = await api.submitRating(token, parseInt(id), ratingData);
            setExistingRating(newRating);
            alert('Thank you for your feedback!');
        } catch (err: any) {
            console.error('Failed to submit rating:', err);
            throw err; // Re-throw to let modal handle it
        }
    };

    const handleSaveFleetDetails = async () => {
        if (!token || !request) return;

        try {
            let updated;
            if (fleetDetails) {
                updated = await api.updateFleetDetails(token, request.id, fleetForm);
            } else {
                updated = await api.createFleetDetails(token, request.id, fleetForm);
            }
            setFleetDetails(updated);
            setFleetForm(updated);
            alert('Fleet details saved successfully!');
        } catch (error: any) {
            console.error('Error saving fleet details:', error);
            alert('Failed to save fleet details: ' + (error.response?.data?.detail || error.message));
        }
    };

    const handleSaveHRDetails = async () => {
        if (!token || !request) return;

        try {
            let updated;
            if (hrDetails) {
                updated = await api.updateHRDetails(token, request.id, hrForm);
            } else {
                updated = await api.createHRDetails(token, request.id, hrForm);
            }
            setHrDetails(updated);
            setHrForm(updated);
            alert('HR details saved successfully!');
        } catch (error: any) {
            console.error('Error saving HR details:', error);
            alert('Failed to save HR details: ' + (error.response?.data?.detail || error.message));
        }
    };

    const handleSaveFinanceDetails = async () => {
        if (!token || !request) return;

        try {
            let updated;
            if (financeDetails) {
                updated = await api.updateFinanceDetails(token, request.id, financeForm);
            } else {
                updated = await api.createFinanceDetails(token, request.id, financeForm);
            }
            setFinanceDetails(updated);
            setFinanceForm(updated);
            alert('Finance details saved successfully!');
        } catch (error: any) {
            console.error('Error saving Finance details:', error);
            alert('Failed to save Finance details: ' + (error.response?.data?.detail || error.message));
        }
    };

    const handleSaveLogisticsDetails = async () => {
        if (!token || !request) return;

        try {
            let updated;
            if (logisticsDetails) {
                updated = await api.updateLogisticsDetails(token, request.id, logisticsForm);
            } else {
                updated = await api.createLogisticsDetails(token, request.id, logisticsForm);
            }
            setLogisticsDetails(updated);
            setLogisticsForm(updated);
            alert('Logistics details saved successfully!');
        } catch (error: any) {
            console.error('Error saving Logistics details:', error);
            alert('Failed to save Logistics details: ' + (error.response?.data?.detail || error.message));
        }
    };

    const handleSaveICTDetails = async () => {
        if (!token || !request) return;

        try {
            let updated;
            if (ictDetails) {
                updated = await api.updateICTDetails(token, request.id, ictForm);
            } else {
                updated = await api.createICTDetails(token, request.id, ictForm);
            }
            setIctDetails(updated);
            setIctForm(updated);
            alert('ICT details saved successfully!');
        } catch (error: any) {
            console.error('Error saving ICT details:', error);
            alert('Failed to save ICT details: ' + (error.response?.data?.detail || error.message));
        }
    };





    const getPriorityColor = (priority: string) => {
        const colors: Record<string, string> = {
            'HIGH': '#e74c3c',
            'MEDIUM': '#f39c12',
            'LOW': '#3498db'
        };
        return colors[priority] || '#7f8c8d';
    };

    // const calculateTotal = () => {
    //     if (!request?.items) return 0;
    //     return request.items.reduce((sum, item) => {
    //         const qty = item.quantity || 0;
    //         const price = item.unit_price || 0;
    //         return sum + (qty * price);
    //     }, 0);
    // };

    if (loading) {
        return <div className="spinner"></div>;
    }

    if (!request) {
        return (
            <div className="card">
                <div className="card-header">
                    <h2>Request Not Found</h2>
                </div>
                <button className="btn btn-secondary" onClick={() => navigate('/requests')}>
                    Back to Requests
                </button>
            </div>
        );
    }



    return (
        <div style={{ maxWidth: '900px', margin: '0 auto', background: 'white' }}>
            {/* Header Section */}
            <div style={{
                display: 'flex',
                justifyContent: 'space-between',
                alignItems: 'flex-start',
                padding: '2rem',
                borderBottom: '3px solid #E63946'
            }}>
                {/* Logo */}
                <div>
                    <img
                        src="/logo-full.png"
                        alt="Tebita Ambulance"
                        style={{ height: '60px', objectFit: 'contain' }}
                        onError={(e) => {
                            // Fallback if logo not found
                            e.currentTarget.style.display = 'none';
                        }}
                    />
                </div>

                {/* REQUEST FORM Title and PDF Button */}
                <div style={{ textAlign: 'right', display: 'flex', flexDirection: 'column', alignItems: 'flex-end', gap: '1rem' }}>
                    <div>
                        <h1 style={{
                            fontSize: '2rem',
                            fontWeight: '700',
                            color: '#E63946',
                            margin: 0,
                            letterSpacing: '1px'
                        }}>
                            REQUEST
                        </h1>
                        <h1 style={{
                            fontSize: '2rem',
                            fontWeight: '700',
                            color: '#E63946',
                            margin: 0,
                            letterSpacing: '1px'
                        }}>
                            FORM
                        </h1>
                    </div>
                </div>
            </div>

            {/* Request Number */}
            <div style={{
                textAlign: 'right',
                padding: '1rem 2rem',
                background: '#F8F9FA'
            }}>
                <div style={{ fontSize: '0.85rem', color: '#6C757D', marginBottom: '0.25rem' }}>
                    Request NO.
                </div>
                <div style={{ fontSize: '1.2rem', fontWeight: '700', color: '#1B1717' }}>
                    {request.request_id}
                </div>
            </div>

            {/* Sender/Recipient Section */}
            <div style={{
                display: 'grid',
                gridTemplateColumns: '1fr 1fr',
                gap: '2rem',
                padding: '2rem',
                background: 'white'
            }}>
                {/* SENDER */}
                <div>
                    <h3 style={{
                        fontSize: '0.95rem',
                        fontWeight: '700',
                        color: '#1B1717',
                        marginBottom: '0.75rem'
                    }}>
                        SENDER
                    </h3>
                    <div style={{ fontSize: '0.9rem', lineHeight: '1.6', color: '#495057' }}>
                        <div><strong>Division:</strong> {request.requester_division?.name || 'N/A'}</div>
                        <div><strong>Department:</strong> {request.requester_department?.name || 'N/A'}</div>
                        {request.requester_subdepartment && (
                            <div><strong>Sub-Department:</strong> {request.requester_subdepartment.name}</div>
                        )}
                    </div>
                </div>

                {/* RECIPIENT */}
                <div>
                    <h3 style={{
                        fontSize: '0.95rem',
                        fontWeight: '700',
                        color: '#1B1717',
                        marginBottom: '0.75rem'
                    }}>
                        RECIPIENT
                    </h3>
                    <div style={{ fontSize: '0.9rem', lineHeight: '1.6', color: '#495057' }}>
                        <div><strong>Division:</strong> {request.assigned_division?.name || 'N/A'}</div>
                        <div><strong>Department:</strong> {request.assigned_department?.name || 'N/A'}</div>
                        {request.assigned_subdepartment && (
                            <div><strong>Sub-Department:</strong> {request.assigned_subdepartment.name}</div>
                        )}
                    </div>
                </div>
            </div>

            <div style={{ padding: '0 2rem 2rem 2rem' }}>
                {/* Request Description */}
                <div style={{ marginBottom: '1.5rem' }}>
                    <h3 style={{
                        fontSize: '0.95rem',
                        fontWeight: '700',
                        color: '#1B1717',
                        marginBottom: '0.5rem'
                    }}>
                        REQUEST DESCRIPTION
                    </h3>
                    <div style={{
                        fontSize: '0.9rem',
                        color: '#495057',
                        lineHeight: '1.6',
                        padding: '1rem',
                        background: '#F8F9FA',
                        borderRadius: '4px'
                    }}>
                        {request.description}
                    </div>
                </div>

                {/* Request Attachment */}
                {request.attachments && request.attachments.length > 0 && (
                    <div style={{ marginBottom: '1.5rem' }}>
                        <h3 style={{
                            fontSize: '0.95rem',
                            fontWeight: '700',
                            color: '#1B1717',
                            marginBottom: '0.5rem'
                        }}>
                            ATTACHMENT
                        </h3>
                        {request.attachments.map((att: any, idx: number) => (
                            <div key={idx} style={{
                                display: 'flex',
                                alignItems: 'center',
                                gap: '0.5rem',
                                fontSize: '0.9rem',
                                color: '#495057'
                            }}>
                                <button
                                    onClick={async () => {
                                        if (token && att.attachment_path) {
                                            try {
                                                await api.downloadItemFile(token, att.attachment_path);
                                            } catch (error) {
                                                console.error('Error downloading file:', error);
                                                alert('Failed to download file');
                                            }
                                        }
                                    }}
                                    style={{
                                        background: '#3498db',
                                        color: 'white',
                                        border: 'none',
                                        borderRadius: '4px',
                                        padding: '0.4rem 0.8rem',
                                        fontSize: '0.85rem',
                                        fontWeight: '500',
                                        cursor: 'pointer',
                                        display: 'flex',
                                        alignItems: 'center',
                                        gap: '0.5rem',
                                        transition: 'background-color 0.2s'
                                    }}
                                    onMouseOver={(e) => e.currentTarget.style.background = '#2980b9'}
                                    onMouseOut={(e) => e.currentTarget.style.background = '#3498db'}
                                    title={att.attachment_filename} // Show filename on hover
                                >
                                    View Uploaded Document
                                </button>
                                <span style={{ fontSize: '0.8rem', color: '#6c757d' }}>
                                    {att.attachment_filename}
                                </span>
                            </div>
                        ))}
                    </div>
                )}

                {/* Priority Type */}
                <div style={{ marginBottom: '1.5rem' }}>
                    <h3 style={{
                        fontSize: '0.95rem',
                        fontWeight: '700',
                        color: '#1B1717',
                        marginBottom: '0.5rem'
                    }}>
                        PRIORITY TYPE
                    </h3>
                    <span style={{
                        display: 'inline-block',
                        padding: '0.4rem 1.2rem',
                        borderRadius: '4px',
                        background: getPriorityColor(request.priority),
                        color: 'white',
                        fontSize: '0.85rem',
                        fontWeight: '600'
                    }}>
                        {request.priority}
                    </span>
                </div>

                {/* Item Description (if single item) */}
                {request.items && request.items.length === 1 && (
                    <div style={{ marginBottom: '1.5rem' }}>
                        <h3 style={{
                            fontSize: '0.95rem',
                            fontWeight: '700',
                            color: '#1B1717',
                            marginBottom: '0.5rem'
                        }}>
                            ITEM DESCRIPTION
                        </h3>
                        <div style={{ fontSize: '0.9rem', color: '#495057' }}>
                            {request.items[0].item_description}
                        </div>
                    </div>
                )}

                {/* Item Description File */}
                {request.items && request.items.some(item => item.attachment_filename) && (
                    <div style={{ marginBottom: '1.5rem' }}>
                        <h3 style={{
                            fontSize: '0.95rem',
                            fontWeight: '700',
                            color: '#1B1717',
                            marginBottom: '0.5rem'
                        }}>
                            ITEM DESCRIPTION FILE
                        </h3>
                        {request.items.filter(item => item.attachment_filename).map((item, idx) => (
                            <div key={idx} style={{
                                display: 'flex',
                                alignItems: 'center',
                                gap: '0.5rem',
                                fontSize: '0.9rem',
                                color: '#495057'
                            }}>
                                <span style={{ fontSize: '1.2rem' }}></span>
                                <button
                                    onClick={async () => {
                                        if (token && item.attachment_filename) {
                                            try {
                                                await api.downloadItemFile(token, item.attachment_filename);
                                            } catch (error) {
                                                console.error('Error downloading file:', error);
                                                alert('Failed to download file');
                                            }
                                        }
                                    }}
                                    style={{
                                        background: 'none',
                                        border: 'none',
                                        color: '#3498db',
                                        textDecoration: 'underline',
                                        cursor: 'pointer',
                                        padding: 0,
                                        fontSize: '0.9rem',
                                        fontFamily: 'inherit'
                                    }}
                                >
                                    {item.attachment_filename}
                                </button>
                            </div>
                        ))}
                    </div>
                )}

                {/* Items Table */}
                {request.items && request.items.length > 0 && (
                    <div style={{ marginTop: '2rem' }}>
                        <table style={{
                            width: '100%',
                            borderCollapse: 'collapse',
                            fontSize: '0.85rem'
                        }}>
                            <thead>
                                <tr style={{ background: '#1D3557', color: 'white' }}>
                                    <th style={{
                                        padding: '0.75rem',
                                        textAlign: 'left',
                                        fontWeight: '600',
                                        fontSize: '0.8rem',
                                        letterSpacing: '0.5px'
                                    }}>
                                        ITEM TYPE
                                    </th>
                                    <th style={{
                                        padding: '0.75rem',
                                        textAlign: 'right',
                                        fontWeight: '600',
                                        fontSize: '0.8rem',
                                        letterSpacing: '0.5px'
                                    }}>
                                        PRICE
                                    </th>
                                    <th style={{
                                        padding: '0.75rem',
                                        textAlign: 'center',
                                        fontWeight: '600',
                                        fontSize: '0.8rem',
                                        letterSpacing: '0.5px'
                                    }}>
                                        QTY
                                    </th>
                                    <th style={{
                                        padding: '0.75rem',
                                        textAlign: 'right',
                                        fontWeight: '600',
                                        fontSize: '0.8rem',
                                        letterSpacing: '0.5px'
                                    }}>
                                        TOTAL
                                    </th>
                                </tr>
                            </thead>
                            <tbody>
                                {request.items.map((item, index) => (
                                    <tr key={item.id || index} style={{
                                        borderBottom: '1px solid #DEE2E6',
                                        background: index % 2 === 0 ? 'white' : '#F8F9FA'
                                    }}>
                                        <td style={{ padding: '0.75rem', color: '#495057' }}>
                                            {item.item_description || 'ITEM NAME'}
                                        </td>
                                        <td style={{ padding: '0.75rem', textAlign: 'right', color: '#495057' }}>
                                            ${item.unit_price?.toFixed(2) || '10.00'}
                                        </td>
                                        <td style={{ padding: '0.75rem', textAlign: 'center', color: '#495057' }}>
                                            {item.quantity || 1}
                                        </td>
                                        <td style={{ padding: '0.75rem', textAlign: 'right', color: '#495057', fontWeight: '500' }}>
                                            ${((item.quantity || 0) * (item.unit_price || 0)).toFixed(2)}
                                        </td>
                                    </tr>
                                ))}
                            </tbody>
                        </table>
                    </div>
                )}
            </div>

            {/* FLEET MANAGEMENT SECTION */}
            {request.resource_type === 'FLEET' && (
                <div style={{
                    marginTop: '2rem',
                    padding: '2rem',
                    background: '#F8F9FA',
                    borderTop: '1px solid #DEE2E6'
                }}>
                    <h3 style={{
                        fontSize: '1.1rem',
                        fontWeight: '700',
                        color: '#1B1717',
                        marginBottom: '1.5rem',
                        display: 'flex',
                        alignItems: 'center',
                        gap: '0.5rem'
                    }}>
                        FLEET MANAGEMENT
                    </h3>

                    <div style={{
                        display: 'grid',
                        gridTemplateColumns: '1fr 1fr',
                        gap: '1.5rem'
                    }}>
                        {/* Vehicle & Driver */}
                        <div>
                            <label style={{ display: 'block', marginBottom: '0.5rem', fontSize: '0.9rem', fontWeight: '600' }}>Vehicle Assigned</label>
                            <input
                                type="text"
                                className="form-control"
                                value={fleetForm.vehicle_assigned || ''}
                                onChange={e => setFleetForm({ ...fleetForm, vehicle_assigned: e.target.value })}
                                placeholder="e.g. Toyota Hilux (AA-1234)"
                                style={{ width: '100%', padding: '0.5rem', border: '1px solid #ced4da', borderRadius: '4px' }}
                            />
                        </div>
                        <div>
                            <label style={{ display: 'block', marginBottom: '0.5rem', fontSize: '0.9rem', fontWeight: '600' }}>Driver Assigned</label>
                            <input
                                type="text"
                                className="form-control"
                                value={fleetForm.driver_assigned || ''}
                                onChange={e => setFleetForm({ ...fleetForm, driver_assigned: e.target.value })}
                                placeholder="Driver Name"
                                style={{ width: '100%', padding: '0.5rem', border: '1px solid #ced4da', borderRadius: '4px' }}
                            />
                        </div>

                        {/* Times */}
                        <div>
                            <label style={{ display: 'block', marginBottom: '0.5rem', fontSize: '0.9rem', fontWeight: '600' }}>Dispatch Time</label>
                            <input
                                type="datetime-local"
                                className="form-control"
                                value={fleetForm.dispatch_time ? new Date(fleetForm.dispatch_time).toISOString().slice(0, 16) : ''}
                                onChange={e => setFleetForm({ ...fleetForm, dispatch_time: e.target.value })}
                                style={{ width: '100%', padding: '0.5rem', border: '1px solid #ced4da', borderRadius: '4px' }}
                            />
                        </div>
                        <div>
                            <label style={{ display: 'block', marginBottom: '0.5rem', fontSize: '0.9rem', fontWeight: '600' }}>Return Time</label>
                            <input
                                type="datetime-local"
                                className="form-control"
                                value={fleetForm.return_time ? new Date(fleetForm.return_time).toISOString().slice(0, 16) : ''}
                                onChange={e => setFleetForm({ ...fleetForm, return_time: e.target.value })}
                                style={{ width: '100%', padding: '0.5rem', border: '1px solid #ced4da', borderRadius: '4px' }}
                            />
                        </div>

                        {/* Metrics */}
                        <div>
                            <label style={{ display: 'block', marginBottom: '0.5rem', fontSize: '0.9rem', fontWeight: '600' }}>Fuel Used (Liters)</label>
                            <input
                                type="number"
                                className="form-control"
                                value={fleetForm.fuel_used || ''}
                                onChange={e => setFleetForm({ ...fleetForm, fuel_used: parseFloat(e.target.value) })}
                                style={{ width: '100%', padding: '0.5rem', border: '1px solid #ced4da', borderRadius: '4px' }}
                            />
                        </div>
                        <div>
                            <label style={{ display: 'block', marginBottom: '0.5rem', fontSize: '0.9rem', fontWeight: '600' }}>KM Traveled</label>
                            <input
                                type="number"
                                className="form-control"
                                value={fleetForm.km_traveled || ''}
                                onChange={e => setFleetForm({ ...fleetForm, km_traveled: parseFloat(e.target.value) })}
                                style={{ width: '100%', padding: '0.5rem', border: '1px solid #ced4da', borderRadius: '4px' }}
                            />
                        </div>

                        {/* Status Flags */}
                        <div style={{ display: 'flex', gap: '2rem', alignItems: 'center', marginTop: '1rem' }}>
                            <label style={{ display: 'flex', alignItems: 'center', gap: '0.5rem', cursor: 'pointer' }}>
                                <input
                                    type="checkbox"
                                    checked={fleetForm.trip_completed || false}
                                    onChange={e => setFleetForm({ ...fleetForm, trip_completed: e.target.checked })}
                                    style={{ width: '18px', height: '18px' }}
                                />
                                <span style={{ fontWeight: '600' }}>Trip Completed</span>
                            </label>

                            <label style={{ display: 'flex', alignItems: 'center', gap: '0.5rem', cursor: 'pointer' }}>
                                <input
                                    type="checkbox"
                                    checked={fleetForm.breakdown_occurred || false}
                                    onChange={e => setFleetForm({ ...fleetForm, breakdown_occurred: e.target.checked })}
                                    style={{ width: '18px', height: '18px' }}
                                />
                                <span style={{ fontWeight: '600', color: '#e74c3c' }}>Breakdown Occurred</span>
                            </label>
                        </div>

                        <div style={{ gridColumn: '1 / -1', marginTop: '1rem' }}>
                            <button
                                className="btn btn-primary"
                                onClick={handleSaveFleetDetails}
                                style={{ width: '100%', padding: '0.75rem' }}
                            >
                                💾 Save Fleet Details
                            </button>
                        </div>
                    </div>
                </div>
            )}

            {/* HR DEPLOYMENT SECTION */}
            {request.resource_type === 'HR' && (
                <div style={{
                    marginTop: '2rem',
                    padding: '2rem',
                    background: '#F8F9FA',
                    borderTop: '1px solid #DEE2E6'
                }}>
                    <h3 style={{
                        fontSize: '1.1rem',
                        fontWeight: '700',
                        color: '#1B1717',
                        marginBottom: '1.5rem',
                        display: 'flex',
                        alignItems: 'center',
                        gap: '0.5rem'
                    }}>
                        HR DEPLOYMENT
                    </h3>

                    <div style={{
                        display: 'grid',
                        gridTemplateColumns: '1fr 1fr',
                        gap: '1.5rem'
                    }}>
                        {/* Staff & Competency */}
                        <div>
                            <label style={{ display: 'block', marginBottom: '0.5rem', fontSize: '0.9rem', fontWeight: '600' }}>Staff Assigned</label>
                            <input
                                type="text"
                                className="form-control"
                                value={hrForm.staff_assigned || ''}
                                onChange={e => setHrForm({ ...hrForm, staff_assigned: e.target.value })}
                                placeholder="e.g. Nurse Joy"
                                style={{ width: '100%', padding: '0.5rem', border: '1px solid #ced4da', borderRadius: '4px' }}
                            />
                        </div>
                        <div>
                            <label style={{ display: 'block', marginBottom: '0.5rem', fontSize: '0.9rem', fontWeight: '600' }}>Competency Required</label>
                            <input
                                type="text"
                                className="form-control"
                                value={hrForm.competency_required || ''}
                                onChange={e => setHrForm({ ...hrForm, competency_required: e.target.value })}
                                placeholder="e.g. ICU Certified"
                                style={{ width: '100%', padding: '0.5rem', border: '1px solid #ced4da', borderRadius: '4px' }}
                            />
                        </div>

                        {/* Dates */}
                        <div>
                            <label style={{ display: 'block', marginBottom: '0.5rem', fontSize: '0.9rem', fontWeight: '600' }}>Actual Start Date</label>
                            <input
                                type="datetime-local"
                                className="form-control"
                                value={hrForm.actual_start_date ? new Date(hrForm.actual_start_date).toISOString().slice(0, 16) : ''}
                                onChange={e => setHrForm({ ...hrForm, actual_start_date: e.target.value })}
                                style={{ width: '100%', padding: '0.5rem', border: '1px solid #ced4da', borderRadius: '4px' }}
                            />
                        </div>
                        <div>
                            <label style={{ display: 'block', marginBottom: '0.5rem', fontSize: '0.9rem', fontWeight: '600' }}>Actual End Date</label>
                            <input
                                type="datetime-local"
                                className="form-control"
                                value={hrForm.actual_end_date ? new Date(hrForm.actual_end_date).toISOString().slice(0, 16) : ''}
                                onChange={e => setHrForm({ ...hrForm, actual_end_date: e.target.value })}
                                style={{ width: '100%', padding: '0.5rem', border: '1px solid #ced4da', borderRadius: '4px' }}
                            />
                        </div>

                        {/* Metrics */}
                        <div>
                            <label style={{ display: 'block', marginBottom: '0.5rem', fontSize: '0.9rem', fontWeight: '600' }}>Deployment Duration (Days)</label>
                            <input
                                type="number"
                                className="form-control"
                                value={hrForm.deployment_duration_days || ''}
                                onChange={e => setHrForm({ ...hrForm, deployment_duration_days: parseInt(e.target.value) })}
                                style={{ width: '100%', padding: '0.5rem', border: '1px solid #ced4da', borderRadius: '4px' }}
                            />
                        </div>
                        <div>
                            <label style={{ display: 'block', marginBottom: '0.5rem', fontSize: '0.9rem', fontWeight: '600' }}>Overtime Hours</label>
                            <input
                                type="number"
                                className="form-control"
                                value={hrForm.overtime_hours || ''}
                                onChange={e => setHrForm({ ...hrForm, overtime_hours: parseFloat(e.target.value) })}
                                style={{ width: '100%', padding: '0.5rem', border: '1px solid #ced4da', borderRadius: '4px' }}
                            />
                        </div>

                        {/* Status Flags */}
                        <div style={{ display: 'flex', gap: '2rem', alignItems: 'center', marginTop: '1rem' }}>
                            <label style={{ display: 'flex', alignItems: 'center', gap: '0.5rem', cursor: 'pointer' }}>
                                <input
                                    type="checkbox"
                                    checked={hrForm.deployment_filled || false}
                                    onChange={e => setHrForm({ ...hrForm, deployment_filled: e.target.checked })}
                                    style={{ width: '18px', height: '18px' }}
                                />
                                <span style={{ fontWeight: '600', color: '#10B981' }}>Deployment Filled</span>
                            </label>
                        </div>

                        <div style={{ gridColumn: '1 / -1', marginTop: '1rem' }}>
                            <button
                                className="btn btn-primary"
                                onClick={handleSaveHRDetails}
                                style={{ width: '100%', padding: '0.75rem' }}
                            >
                                💾 Save HR Details
                            </button>
                        </div>
                    </div>
                </div>
            )}

            {/* FINANCE TRANSACTION SECTION */}
            {request.resource_type === 'FINANCE' && (
                <div style={{
                    marginTop: '2rem',
                    padding: '2rem',
                    background: '#F8F9FA',
                    borderTop: '1px solid #DEE2E6'
                }}>
                    <h3 style={{
                        fontSize: '1.1rem',
                        fontWeight: '700',
                        color: '#1B1717',
                        marginBottom: '1.5rem',
                        display: 'flex',
                        alignItems: 'center',
                        gap: '0.5rem'
                    }}>
                        FINANCE TRANSACTION
                    </h3>

                    <div style={{
                        display: 'grid',
                        gridTemplateColumns: '1fr 1fr',
                        gap: '1.5rem'
                    }}>
                        {/* Transaction Info */}
                        <div>
                            <label style={{ display: 'block', marginBottom: '0.5rem', fontSize: '0.9rem', fontWeight: '600' }}>Transaction Type</label>
                            <select
                                className="form-control"
                                value={financeForm.transaction_type || ''}
                                onChange={e => setFinanceForm({ ...financeForm, transaction_type: e.target.value })}
                                style={{ width: '100%', padding: '0.5rem', border: '1px solid #ced4da', borderRadius: '4px' }}
                            >
                                <option value="">Select Type</option>
                                <option value="VENDOR_PAYMENT">Vendor Payment</option>
                                <option value="PAYROLL">Payroll</option>
                                <option value="TAX_PAYMENT">Tax Payment</option>
                                <option value="REIMBURSEMENT">Reimbursement</option>
                                <option value="OTHER">Other</option>
                            </select>
                        </div>
                        <div>
                            <label style={{ display: 'block', marginBottom: '0.5rem', fontSize: '0.9rem', fontWeight: '600' }}>Amount</label>
                            <input
                                type="number"
                                className="form-control"
                                value={financeForm.amount || ''}
                                onChange={e => setFinanceForm({ ...financeForm, amount: parseFloat(e.target.value) })}
                                style={{ width: '100%', padding: '0.5rem', border: '1px solid #ced4da', borderRadius: '4px' }}
                            />
                        </div>

                        {/* Processing Info */}
                        <div>
                            <label style={{ display: 'block', marginBottom: '0.5rem', fontSize: '0.9rem', fontWeight: '600' }}>Processing Officer</label>
                            <input
                                type="text"
                                className="form-control"
                                value={financeForm.processing_officer || ''}
                                onChange={e => setFinanceForm({ ...financeForm, processing_officer: e.target.value })}
                                style={{ width: '100%', padding: '0.5rem', border: '1px solid #ced4da', borderRadius: '4px' }}
                            />
                        </div>
                        <div>
                            <label style={{ display: 'block', marginBottom: '0.5rem', fontSize: '0.9rem', fontWeight: '600' }}>Completeness Score (0-100)</label>
                            <input
                                type="number"
                                className="form-control"
                                value={financeForm.document_completeness_score || ''}
                                onChange={e => setFinanceForm({ ...financeForm, document_completeness_score: parseInt(e.target.value) })}
                                min="0"
                                max="100"
                                style={{ width: '100%', padding: '0.5rem', border: '1px solid #ced4da', borderRadius: '4px' }}
                            />
                        </div>

                        {/* Dates */}
                        <div>
                            <label style={{ display: 'block', marginBottom: '0.5rem', fontSize: '0.9rem', fontWeight: '600' }}>Date Received</label>
                            <input
                                type="datetime-local"
                                className="form-control"
                                value={financeForm.date_received ? new Date(financeForm.date_received).toISOString().slice(0, 16) : ''}
                                onChange={e => setFinanceForm({ ...financeForm, date_received: e.target.value })}
                                style={{ width: '100%', padding: '0.5rem', border: '1px solid #ced4da', borderRadius: '4px' }}
                            />
                        </div>
                        <div>
                            <label style={{ display: 'block', marginBottom: '0.5rem', fontSize: '0.9rem', fontWeight: '600' }}>Date Processed</label>
                            <input
                                type="datetime-local"
                                className="form-control"
                                value={financeForm.date_processed ? new Date(financeForm.date_processed).toISOString().slice(0, 16) : ''}
                                onChange={e => setFinanceForm({ ...financeForm, date_processed: e.target.value })}
                                style={{ width: '100%', padding: '0.5rem', border: '1px solid #ced4da', borderRadius: '4px' }}
                            />
                        </div>

                        {/* Checkboxes */}
                        <div style={{ gridColumn: '1 / -1', display: 'flex', gap: '2rem', flexWrap: 'wrap', marginTop: '1rem' }}>
                            <label style={{ display: 'flex', alignItems: 'center', gap: '0.5rem', cursor: 'pointer' }}>
                                <input
                                    type="checkbox"
                                    checked={financeForm.supporting_docs_complete || false}
                                    onChange={e => setFinanceForm({ ...financeForm, supporting_docs_complete: e.target.checked })}
                                    style={{ width: '18px', height: '18px' }}
                                />
                                <span style={{ fontWeight: '600' }}>Docs Complete</span>
                            </label>

                            <label style={{ display: 'flex', alignItems: 'center', gap: '0.5rem', cursor: 'pointer' }}>
                                <input
                                    type="checkbox"
                                    checked={financeForm.complies_with_finance_sop || false}
                                    onChange={e => setFinanceForm({ ...financeForm, complies_with_finance_sop: e.target.checked })}
                                    style={{ width: '18px', height: '18px' }}
                                />
                                <span style={{ fontWeight: '600' }}>SOP Compliant</span>
                            </label>

                            <label style={{ display: 'flex', alignItems: 'center', gap: '0.5rem', cursor: 'pointer' }}>
                                <input
                                    type="checkbox"
                                    checked={financeForm.payment_accuracy || false}
                                    onChange={e => setFinanceForm({ ...financeForm, payment_accuracy: e.target.checked })}
                                    style={{ width: '18px', height: '18px' }}
                                />
                                <span style={{ fontWeight: '600' }}>Payment Accurate</span>
                            </label>
                        </div>

                        <div style={{ gridColumn: '1 / -1', marginTop: '1rem' }}>
                            <button
                                className="btn btn-primary"
                                onClick={handleSaveFinanceDetails}
                                style={{ width: '100%', padding: '0.75rem' }}
                            >
                                💾 Save Finance Details
                            </button>
                        </div>
                    </div>
                </div>
            )}

            {/* ICT SUPPORT TICKET SECTION */}
            {request.resource_type === 'ICT' && (
                <div style={{
                    marginTop: '2rem',
                    padding: '2rem',
                    background: '#F8F9FA',
                    borderTop: '1px solid #DEE2E6'
                }}>
                    <h3 style={{
                        fontSize: '1.1rem',
                        fontWeight: '700',
                        color: '#1B1717',
                        marginBottom: '1.5rem',
                        display: 'flex',
                        alignItems: 'center',
                        gap: '0.5rem'
                    }}>
                        ICT SUPPORT TICKET
                    </h3>

                    <div style={{
                        display: 'grid',
                        gridTemplateColumns: '1fr 1fr',
                        gap: '1.5rem'
                    }}>
                        {/* Ticket Info */}
                        <div>
                            <label style={{ display: 'block', marginBottom: '0.5rem', fontSize: '0.9rem', fontWeight: '600' }}>Ticket Number</label>
                            <input
                                type="text"
                                className="form-control"
                                value={ictForm.ticket_number || ''}
                                onChange={e => setIctForm({ ...ictForm, ticket_number: e.target.value })}
                                placeholder="e.g. ICT-2024-001"
                                style={{ width: '100%', padding: '0.5rem', border: '1px solid #ced4da', borderRadius: '4px' }}
                            />
                        </div>
                        <div>
                            <label style={{ display: 'block', marginBottom: '0.5rem', fontSize: '0.9rem', fontWeight: '600' }}>Problem Type</label>
                            <select
                                className="form-control"
                                value={ictForm.problem_type || ''}
                                onChange={e => setIctForm({ ...ictForm, problem_type: e.target.value })}
                                style={{ width: '100%', padding: '0.5rem', border: '1px solid #ced4da', borderRadius: '4px' }}
                            >
                                <option value="">Select Type</option>
                                <option value="HARDWARE">Hardware Issue</option>
                                <option value="SOFTWARE">Software Issue</option>
                                <option value="NETWORK">Network/Internet</option>
                                <option value="ACCESS">Access/Login</option>
                                <option value="OTHER">Other</option>
                            </select>
                        </div>

                        {/* Severity & Technician */}
                        <div>
                            <label style={{ display: 'block', marginBottom: '0.5rem', fontSize: '0.9rem', fontWeight: '600' }}>Severity</label>
                            <select
                                className="form-control"
                                value={ictForm.severity || ''}
                                onChange={e => setIctForm({ ...ictForm, severity: e.target.value })}
                                style={{ width: '100%', padding: '0.5rem', border: '1px solid #ced4da', borderRadius: '4px' }}
                            >
                                <option value="">Select Severity</option>
                                <option value="LOW">Low</option>
                                <option value="MEDIUM">Medium</option>
                                <option value="HIGH">High</option>
                                <option value="CRITICAL">Critical</option>
                            </select>
                        </div>
                        <div>
                            <label style={{ display: 'block', marginBottom: '0.5rem', fontSize: '0.9rem', fontWeight: '600' }}>Technician Assigned</label>
                            <input
                                type="text"
                                className="form-control"
                                value={ictForm.technician_assigned || ''}
                                onChange={e => setIctForm({ ...ictForm, technician_assigned: e.target.value })}
                                style={{ width: '100%', padding: '0.5rem', border: '1px solid #ced4da', borderRadius: '4px' }}
                            />
                        </div>

                        {/* Metrics */}
                        <div>
                            <label style={{ display: 'block', marginBottom: '0.5rem', fontSize: '0.9rem', fontWeight: '600' }}>Resolution Time (Minutes)</label>
                            <input
                                type="number"
                                className="form-control"
                                value={ictForm.resolution_time_minutes || ''}
                                onChange={e => setIctForm({ ...ictForm, resolution_time_minutes: parseInt(e.target.value) })}
                                style={{ width: '100%', padding: '0.5rem', border: '1px solid #ced4da', borderRadius: '4px' }}
                            />
                        </div>
                        <div>
                            <label style={{ display: 'block', marginBottom: '0.5rem', fontSize: '0.9rem', fontWeight: '600' }}>System Downtime (Minutes)</label>
                            <input
                                type="number"
                                className="form-control"
                                value={ictForm.system_downtime_minutes || ''}
                                onChange={e => setIctForm({ ...ictForm, system_downtime_minutes: parseInt(e.target.value) })}
                                style={{ width: '100%', padding: '0.5rem', border: '1px solid #ced4da', borderRadius: '4px' }}
                            />
                        </div>

                        {/* Checkboxes */}
                        <div style={{ gridColumn: '1 / -1', display: 'flex', gap: '2rem', flexWrap: 'wrap', marginTop: '1rem' }}>
                            <label style={{ display: 'flex', alignItems: 'center', gap: '0.5rem', cursor: 'pointer' }}>
                                <input
                                    type="checkbox"
                                    checked={ictForm.escalated || false}
                                    onChange={e => setIctForm({ ...ictForm, escalated: e.target.checked })}
                                    style={{ width: '18px', height: '18px' }}
                                />
                                <span style={{ fontWeight: '600', color: '#e74c3c' }}>Escalated</span>
                            </label>

                            <label style={{ display: 'flex', alignItems: 'center', gap: '0.5rem', cursor: 'pointer' }}>
                                <input
                                    type="checkbox"
                                    checked={ictForm.reopened || false}
                                    onChange={e => setIctForm({ ...ictForm, reopened: e.target.checked })}
                                    style={{ width: '18px', height: '18px' }}
                                />
                                <span style={{ fontWeight: '600', color: '#f39c12' }}>Reopened</span>
                            </label>
                        </div>

                        <div style={{ gridColumn: '1 / -1', marginTop: '1rem' }}>
                            <button
                                className="btn btn-primary"
                                onClick={handleSaveICTDetails}
                                style={{ width: '100%', padding: '0.75rem' }}
                            >
                                💾 Save ICT Details
                            </button>
                        </div>
                    </div>
                </div>
            )}

            {/* LOGISTICS & SUPPLY CHAIN SECTION */}
            {request.resource_type === 'LOGISTICS' && (
                <div style={{
                    marginTop: '2rem',
                    padding: '2rem',
                    background: '#F8F9FA',
                    borderTop: '1px solid #DEE2E6'
                }}>
                    <h3 style={{
                        fontSize: '1.1rem',
                        fontWeight: '700',
                        color: '#1B1717',
                        marginBottom: '1.5rem',
                        display: 'flex',
                        alignItems: 'center',
                        gap: '0.5rem'
                    }}>
                        LOGISTICS & SUPPLY CHAIN
                    </h3>

                    <div style={{
                        display: 'grid',
                        gridTemplateColumns: '1fr 1fr',
                        gap: '1.5rem'
                    }}>
                        {/* Item Info */}
                        <div>
                            <label style={{ display: 'block', marginBottom: '0.5rem', fontSize: '0.9rem', fontWeight: '600' }}>Item Requested</label>
                            <input
                                type="text"
                                className="form-control"
                                value={logisticsForm.item_requested || ''}
                                onChange={e => setLogisticsForm({ ...logisticsForm, item_requested: e.target.value })}
                                placeholder="e.g. Surgical Gloves"
                                style={{ width: '100%', padding: '0.5rem', border: '1px solid #ced4da', borderRadius: '4px' }}
                            />
                        </div>
                        <div>
                            <label style={{ display: 'block', marginBottom: '0.5rem', fontSize: '0.9rem', fontWeight: '600' }}>Cost Per Item</label>
                            <input
                                type="number"
                                className="form-control"
                                value={logisticsForm.cost_per_item || ''}
                                onChange={e => setLogisticsForm({ ...logisticsForm, cost_per_item: parseFloat(e.target.value) })}
                                style={{ width: '100%', padding: '0.5rem', border: '1px solid #ced4da', borderRadius: '4px' }}
                            />
                        </div>

                        {/* Quantities */}
                        <div>
                            <label style={{ display: 'block', marginBottom: '0.5rem', fontSize: '0.9rem', fontWeight: '600' }}>Quantity Requested</label>
                            <input
                                type="number"
                                className="form-control"
                                value={logisticsForm.quantity_requested || ''}
                                onChange={e => setLogisticsForm({ ...logisticsForm, quantity_requested: parseInt(e.target.value) })}
                                style={{ width: '100%', padding: '0.5rem', border: '1px solid #ced4da', borderRadius: '4px' }}
                            />
                        </div>
                        <div>
                            <label style={{ display: 'block', marginBottom: '0.5rem', fontSize: '0.9rem', fontWeight: '600' }}>Quantity Delivered</label>
                            <input
                                type="number"
                                className="form-control"
                                value={logisticsForm.quantity_delivered || ''}
                                onChange={e => setLogisticsForm({ ...logisticsForm, quantity_delivered: parseInt(e.target.value) })}
                                style={{ width: '100%', padding: '0.5rem', border: '1px solid #ced4da', borderRadius: '4px' }}
                            />
                        </div>

                        {/* Times */}
                        <div>
                            <label style={{ display: 'block', marginBottom: '0.5rem', fontSize: '0.9rem', fontWeight: '600' }}>Delivery Time (Days)</label>
                            <input
                                type="number"
                                className="form-control"
                                value={logisticsForm.delivery_time_days || ''}
                                onChange={e => setLogisticsForm({ ...logisticsForm, delivery_time_days: parseInt(e.target.value) })}
                                style={{ width: '100%', padding: '0.5rem', border: '1px solid #ced4da', borderRadius: '4px' }}
                            />
                        </div>
                        <div>
                            <label style={{ display: 'block', marginBottom: '0.5rem', fontSize: '0.9rem', fontWeight: '600' }}>Lead Time (Days)</label>
                            <input
                                type="number"
                                className="form-control"
                                value={logisticsForm.lead_time_days || ''}
                                onChange={e => setLogisticsForm({ ...logisticsForm, lead_time_days: parseInt(e.target.value) })}
                                style={{ width: '100%', padding: '0.5rem', border: '1px solid #ced4da', borderRadius: '4px' }}
                            />
                        </div>

                        {/* Checkboxes */}
                        <div style={{ gridColumn: '1 / -1', display: 'flex', gap: '2rem', flexWrap: 'wrap', marginTop: '1rem' }}>
                            <label style={{ display: 'flex', alignItems: 'center', gap: '0.5rem', cursor: 'pointer' }}>
                                <input
                                    type="checkbox"
                                    checked={logisticsForm.stock_available || false}
                                    onChange={e => setLogisticsForm({ ...logisticsForm, stock_available: e.target.checked })}
                                    style={{ width: '18px', height: '18px' }}
                                />
                                <span style={{ fontWeight: '600', color: '#10B981' }}>Stock Available</span>
                            </label>

                            <label style={{ display: 'flex', alignItems: 'center', gap: '0.5rem', cursor: 'pointer' }}>
                                <input
                                    type="checkbox"
                                    checked={logisticsForm.requisition_accurate || false}
                                    onChange={e => setLogisticsForm({ ...logisticsForm, requisition_accurate: e.target.checked })}
                                    style={{ width: '18px', height: '18px' }}
                                />
                                <span style={{ fontWeight: '600' }}>Requisition Accurate</span>
                            </label>

                            <label style={{ display: 'flex', alignItems: 'center', gap: '0.5rem', cursor: 'pointer' }}>
                                <input
                                    type="checkbox"
                                    checked={logisticsForm.documentation_complete || false}
                                    onChange={e => setLogisticsForm({ ...logisticsForm, documentation_complete: e.target.checked })}
                                    style={{ width: '18px', height: '18px' }}
                                />
                                <span style={{ fontWeight: '600' }}>Docs Complete</span>
                            </label>
                        </div>

                        <div style={{ gridColumn: '1 / -1', marginTop: '1rem' }}>
                            <button
                                className="btn btn-primary"
                                onClick={handleSaveLogisticsDetails}
                                style={{ width: '100%', padding: '0.75rem' }}
                            >
                                💾 Save Logistics Details
                            </button>
                        </div>
                    </div>
                </div>
            )}

            {/* Footer with Contact Info */}
            <div style={{
                position: 'relative',
                marginTop: '3rem',
                paddingTop: '2rem',
                paddingBottom: '1.5rem',
                background: 'white',
                borderTop: '3px solid #E63946'
            }}>

                <div style={{
                    position: 'relative',
                    zIndex: 1,
                    display: 'flex',
                    justifyContent: 'center',
                    gap: '3rem',
                    padding: '0 2rem',
                    fontSize: '0.75rem',
                    color: '#6C757D',
                    marginTop: '1rem'
                }}>
                    <div style={{ display: 'flex', alignItems: 'center', gap: '0.5rem' }}>
                        <span style={{ fontSize: '1rem' }}>📞</span>
                        <div>
                            <div>8035</div>
                            <div>+251 911 225464</div>
                        </div>
                    </div>

                    <div style={{ display: 'flex', alignItems: 'center', gap: '0.5rem' }}>
                        <span style={{ fontSize: '1rem' }}></span>
                        <div>
                            <div>{request.requester?.email || 'info@tebitambulance.com'}</div>
                            <div>www.tebitambulance.com</div>
                        </div>
                    </div>

                    <div style={{ display: 'flex', alignItems: 'center', gap: '0.5rem' }}>
                        <span style={{ fontSize: '1rem' }}>📍</span>
                        <div>
                            <div>Addis Ababa,</div>
                            <div>Ethiopia</div>
                        </div>
                    </div>
                </div>
            </div>

            {/* Action Buttons */}
            <div style={{
                display: 'flex',
                gap: '1rem',
                padding: '2rem',
                borderTop: '1px solid #DEE2E6',
                flexWrap: 'wrap'
            }}>
                <button
                    className="btn btn-secondary"
                    onClick={() => navigate('/requests')}
                >
                    ← Back to Requests
                </button>

                <button
                    className="btn btn-outline"
                    onClick={() => window.print()}
                >
                    Print
                </button>

                {/* Acknowledge Button - Only show if not acknowledged */}
                {!request.acknowledged_at && token && (
                    <button
                        className="btn btn-primary"
                        onClick={async () => {
                            if (!window.confirm('Are you sure you want to acknowledge this request?')) return;

                            try {
                                await api.acknowledgeRequest(token, request.id);
                                alert('Request acknowledged successfully!');
                                // Refresh request data
                                const updated = await api.getRequest(token, request.id);
                                setRequest(updated);
                            } catch (error: any) {
                                const message = error.response?.data?.detail || 'Failed to acknowledge request';
                                alert(`Error: ${message}`);
                                console.error('Error acknowledging request:', error);
                            }
                        }}
                    >
                        Acknowledge Request
                    </button>
                )}

                {/* Validate Completion Button - Only show if completed but not validated */}
                {request.status === 'COMPLETED' && !request.completion_validated_at && token && (
                    <button
                        className="btn btn-primary"
                        style={{ background: '#10B981' }}
                        onClick={async () => {
                            if (!window.confirm('Are you sure you want to validate the completion of this request?')) return;

                            try {
                                await api.validateRequestCompletion(token, request.id);
                                alert('Request completion validated successfully!');
                                // Refresh request data
                                const updated = await api.getRequest(token, request.id);
                                setRequest(updated);
                            } catch (error: any) {
                                const message = error.response?.data?.detail || 'Failed to validate completion';
                                alert(`Error: ${message}`);
                                console.error('Error validating completion:', error);
                            }
                        }}
                    >
                        Validate Completion
                    </button>
                )}

                {/* Customer Satisfaction Rating Section */}
                {request.status === 'COMPLETED' && (
                    <div className="card" style={{ marginTop: '2rem' }}>
                        <div className="card-header">
                            <h2 className="card-title">Customer Satisfaction</h2>
                        </div>

                        {existingRating ? (
                            /* Display existing rating */
                            <div style={{ padding: '2rem' }}>
                                <div className="rating-display">
                                    <div className="rating-overall">
                                        <div style={{ fontSize: '3rem', fontWeight: '800', color: 'var(--primary)' }}>
                                            {existingRating.overall_score} / 5
                                        </div>
                                        <div style={{ fontSize: '1rem', color: 'var(--text-muted)', marginTop: '0.5rem' }}>
                                            Overall Rating
                                        </div>
                                    </div>

                                    <div className="rating-dimensions" style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(200px, 1fr))', gap: '1.5rem', marginTop: '2rem' }}>
                                        <div>
                                            <div style={{ fontWeight: '600', marginBottom: '0.5rem' }}>Timeliness</div>
                                            <div style={{ fontSize: '1.5rem', color: 'var(--primary)' }}>
                                                {(existingRating.timeliness_score) + '/5'}
                                                {''}
                                            </div>
                                        </div>
                                        <div>
                                            <div style={{ fontWeight: '600', marginBottom: '0.5rem' }}>Quality</div>
                                            <div style={{ fontSize: '1.5rem', color: 'var(--primary)' }}>
                                                {(existingRating.quality_score) + '/5'}
                                                {''}
                                            </div>
                                        </div>
                                        <div>
                                            <div style={{ fontWeight: '600', marginBottom: '0.5rem' }}>Communication</div>
                                            <div style={{ fontSize: '1.5rem', color: 'var(--primary)' }}>
                                                {(existingRating.communication_score) + '/5'}
                                                {''}
                                            </div>
                                        </div>
                                        <div>
                                            <div style={{ fontWeight: '600', marginBottom: '0.5rem' }}>Professionalism</div>
                                            <div style={{ fontSize: '1.5rem', color: 'var(--primary)' }}>
                                                {(existingRating.professionalism_score) + '/5'}
                                                {''}
                                            </div>
                                        </div>
                                    </div>

                                    {existingRating.comments && (
                                        <div style={{ marginTop: '2rem', padding: '1rem', background: 'rgba(255,255,255,0.05)', borderRadius: '8px' }}>
                                            <div style={{ fontWeight: '600', marginBottom: '0.5rem' }}>Comments</div>
                                            <div style={{ color: 'var(--text-muted)' }}>{existingRating.comments}</div>
                                        </div>
                                    )}

                                    <div style={{ marginTop: '1rem', fontSize: '0.875rem', color: 'var(--text-muted)' }}>
                                        Submitted by {existingRating.submitted_by?.full_name} on {new Date(existingRating.submitted_at).toLocaleDateString()}
                                    </div>
                                </div>
                            </div>
                        ) : (
                            /* Show "Rate This Request" button */
                            <div style={{ padding: '2rem', textAlign: 'center' }}>
                                <p style={{ marginBottom: '1.5rem', color: 'var(--text-muted)' }}>
                                    This request has been completed. Please share your feedback!
                                </p>
                                <button
                                    className="btn btn-primary"
                                    onClick={() => setShowRatingModal(true)}
                                    style={{
                                        fontSize: '1.1rem',
                                        padding: '1rem 2rem',
                                        background: 'linear-gradient(135deg, #667eea 0%, #764ba2 100%)'
                                    }}
                                >
                                    Rate This Request
                                </button>
                            </div>
                        )}
                    </div>
                )}

                {/* Rating Modal */}
                {request && (
                    <RatingModal
                        requestId={request.id}
                        requestNumber={request.request_id}
                        isOpen={showRatingModal}
                        onClose={() => setShowRatingModal(false)}
                        onSubmit={handleSubmitRating}
                    />
                )}
            </div>
        </div>
    );
};
