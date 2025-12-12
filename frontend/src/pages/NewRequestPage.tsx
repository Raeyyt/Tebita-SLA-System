import { useState, useEffect, type FormEvent, type ChangeEvent } from 'react';
import { useNavigate } from 'react-router-dom';
import { useAuth } from '../contexts/AuthContext';
import { api } from '../services/api';
import type { Division, Department, SubDepartment } from '../types';

interface RequestItemForm {
    item_description: string;
    quantity?: number;
    unit_price?: number;
    notes?: string;
    file?: File;
}

export const NewRequestPage = () => {
    const navigate = useNavigate();
    const { token, user } = useAuth();
    const [divisions, setDivisions] = useState<Division[]>([]);
    const [departments, setDepartments] = useState<Department[]>([]);
    const [subDepartments, setSubDepartments] = useState<SubDepartment[]>([]);
    const [senderSubDeptName, setSenderSubDeptName] = useState<string>('');
    const [loading, setLoading] = useState(false);
    const [error, setError] = useState('');

    // Sender info (auto-filled from user)
    const [senderDivisionId, setSenderDivisionId] = useState('');
    const [senderDepartmentId, setSenderDepartmentId] = useState('');
    const [senderSubDepartmentId, setSenderSubDepartmentId] = useState('');

    // Recipient info (user selects)
    const [recipientDivisionId, setRecipientDivisionId] = useState('');
    const [recipientDepartmentId, setRecipientDepartmentId] = useState('');
    const [recipientSubDepartmentId, setRecipientSubDepartmentId] = useState('');

    // Request details
    const [description, setDescription] = useState('');
    const [priority, setPriority] = useState<'HIGH' | 'MEDIUM' | 'LOW'>('MEDIUM');
    const [resourceType, setResourceType] = useState<string>('GENERAL');

    const [items, setItems] = useState<RequestItemForm[]>([
        { item_description: '', quantity: undefined, unit_price: undefined, notes: '', file: undefined }
    ]);
    const [requestFiles, setRequestFiles] = useState<File[]>([]);

    useEffect(() => {
        const loadData = async () => {
            if (!token || !user) return;

            // Admin Restriction
            if (user.role === 'ADMIN') {
                alert("Administrators cannot create requests. Please use a standard user account.");
                navigate('/dashboard');
                return;
            }

            try {
                const [divisionsData, departmentsData] = await Promise.all([
                    api.getDivisions(token),
                    api.getDepartments(token),
                ]);
                setDivisions(divisionsData);
                setDepartments(departmentsData);

                // Auto-fill sender info from logged-in user
                if (user?.division_id) {
                    setSenderDivisionId(String(user.division_id));
                }
                if (user?.department_id) {
                    setSenderDepartmentId(String(user.department_id));
                }
                if (user?.subdepartment_id) {
                    setSenderSubDepartmentId(String(user.subdepartment_id));
                    // Load sender's subdepartment name
                    if (user.department_id) {
                        const loadSenderSubDept = async () => {
                            try {
                                const subDepts = await api.getSubDepartments(token, user.department_id!);
                                const userSubDept = subDepts.find(sd => sd.id === user.subdepartment_id);
                                setSenderSubDeptName(userSubDept?.name || 'Not assigned');
                            } catch (err) {
                                console.error('Failed to load sender subdepartment:', err);
                                setSenderSubDeptName('Not assigned');
                            }
                        };
                        loadSenderSubDept();
                    }
                }
            } catch (err) {
                console.error('Failed to load data:', err);
            }
        };
        loadData();
    }, [token, user, navigate]);

    // Load subdepartments when recipient department changes
    useEffect(() => {
        const loadSubDepartments = async () => {
            if (!token || !recipientDepartmentId) {
                setSubDepartments([]);
                return;
            }
            try {
                const data = await api.getSubDepartments(token, Number(recipientDepartmentId));
                setSubDepartments(data);
            } catch (err) {
                console.error('Failed to load subdepartments:', err);
                setSubDepartments([]);
            }
        };
        loadSubDepartments();
    }, [token, recipientDepartmentId]);

    const addItem = () => {
        setItems([...items, { item_description: '', quantity: undefined, unit_price: undefined, notes: '', file: undefined }]);
    };

    const removeItem = (index: number) => {
        setItems(items.filter((_, i) => i !== index));
    };

    const updateItem = (index: number, field: keyof RequestItemForm, value: any) => {
        const newItems = [...items];
        newItems[index] = { ...newItems[index], [field]: value };
        setItems(newItems);
    };

    const handleFileChange = (index: number, e: ChangeEvent<HTMLInputElement>) => {
        if (e.target.files && e.target.files[0]) {
            updateItem(index, 'file', e.target.files[0]);
        }
    };

    const handleSubmit = async (e: FormEvent) => {
        e.preventDefault();
        if (!token || !user) return;

        setLoading(true);
        setError('');

        try {
            // Prepare items with file uploads
            const itemsWithUploads = await Promise.all(items.map(async (item) => {
                // Skip empty items
                if (item.item_description.trim() === '') return null;

                let attachmentData = {};

                // If item has a file, upload it first
                if (item.file) {
                    try {
                        const formData = new FormData();
                        formData.append('file', item.file);

                        // Upload file
                        const uploadResponse = await api.uploadItemFile(token, formData);

                        attachmentData = {
                            attachment_filename: uploadResponse.filename,
                            attachment_path: uploadResponse.saved_filename,
                            attachment_type: uploadResponse.type
                        };
                    } catch (uploadErr) {
                        console.error("File upload failed for item:", item.item_description, uploadErr);
                        // We continue without the file if upload fails, or you could throw error
                        // throw new Error(`Failed to upload file for ${item.item_description}`);
                    }
                }

                return {
                    item_description: item.item_description,
                    quantity: item.quantity,
                    unit_price: item.unit_price,
                    notes: item.notes,
                    ...attachmentData
                };
            }));

            // Filter out nulls (empty items)
            const validItems = itemsWithUploads.filter(item => item !== null);

            // Basic sender validation - at minimum need division
            if (!senderDivisionId) {
                throw new Error('Your profile must be assigned to a division before submitting requests. Please contact an administrator.');
            }

            // Department and SubDepartment are now optional - allow sending to division level
            // if (!recipientSubDepartmentId) {
            //     throw new Error('Please select a Sub-Department for the recipient.');
            // }

            // Self-Request Validation
            if (senderDivisionId === recipientDivisionId && senderDepartmentId === recipientDepartmentId) {
                // If user has subdept, check if sending to same subdept
                if (user.subdepartment_id && Number(recipientSubDepartmentId) === user.subdepartment_id) {
                    throw new Error("You cannot send a request to your own Sub-Department.");
                }
                // If user is Dept Head (no subdept), check if sending to Dept-wide (no subdept selected - though UI enforces subdept selection now)
                // or if logic dictates Dept Heads can't send to their own Dept at all (usually they assign tasks within)
                // For now, we align with backend: if subdepts match, block.
            }

            // Upload request-level files if exist
            let requestAttachments: any[] = [];
            if (requestFiles.length > 0) {
                try {
                    // Upload files in parallel
                    const uploadPromises = requestFiles.map(async (file) => {
                        const formData = new FormData();
                        formData.append('file', file);
                        const uploadResponse = await api.uploadItemFile(token, formData);
                        return {
                            attachment_filename: uploadResponse.filename,
                            attachment_path: uploadResponse.saved_filename,
                            attachment_type: uploadResponse.type
                        };
                    });

                    requestAttachments = await Promise.all(uploadPromises);
                } catch (err: any) {
                    console.error("Failed to upload request files", err);
                    const errorMessage = err.response?.data?.detail || err.message || "Unknown error";
                    alert(`Failed to upload attachments: ${errorMessage}`);
                    setLoading(false);
                    return; // Stop submission if upload fails
                }
            }

            await api.createRequest(token, {
                request_type: 'GENERAL', // Default type
                resource_type: resourceType,
                requester_division_id: Number(senderDivisionId),
                requester_department_id: senderDepartmentId ? Number(senderDepartmentId) : undefined,
                requester_subdepartment_id: senderSubDepartmentId ? Number(senderSubDepartmentId) : undefined,
                assigned_division_id: Number(recipientDivisionId),
                assigned_department_id: recipientDepartmentId ? Number(recipientDepartmentId) : undefined,
                assigned_subdepartment_id: recipientSubDepartmentId ? Number(recipientSubDepartmentId) : undefined,
                priority: priority,
                description: description,
                notes: '',
                items: validItems,
                attachments: requestAttachments.length > 0 ? requestAttachments : undefined,
            });

            navigate('/requests');
        } catch (err: any) {
            console.error(err);
            setError(err.response?.data?.detail || 'Failed to create request');
        } finally {
            setLoading(false);
        }
    };

    const recipientDepartments = departments.filter(
        dept => !recipientDivisionId || dept.division_id === Number(recipientDivisionId)
    );

    const senderDivisionName = divisions.find(div => String(div.id) === senderDivisionId)?.name || 'Not assigned';

    return (
        <div>
            <div className="card-header">
                <h1 className="card-title">New Request</h1>
                <p className="text-muted">Create a new service request</p>
            </div>

            {error && <div className="alert alert-error">{error}</div>}

            <form onSubmit={handleSubmit}>
                <div className="card">
                    <div className="card-header">
                        <h2 className="card-title">Request Details</h2>
                    </div>

                    {/* Sender/Recipient Side-by-Side */}
                    <div className="grid grid-2" style={{ marginBottom: '1.5rem' }}>
                        {/* SENDER Section */}
                        <div style={{ padding: '1rem', background: 'var(--gray-50)', borderRadius: 'var(--radius)' }}>
                            <h3 style={{ fontSize: '1.1rem', fontWeight: '700', color: '#610100', marginBottom: '1rem' }}>
                                SENDER
                            </h3>

                            <div className="form-group">
                                <label className="form-label">Division *</label>
                                <input
                                    className="form-input"
                                    value={senderDivisionName}
                                    readOnly
                                    placeholder="Not assigned"
                                />
                                <small className="text-muted">Linked to your user profile</small>
                            </div>

                            <div className="form-group">
                                <label className="form-label">Department *</label>
                                <input
                                    className="form-input"
                                    value={departments.find(d => d.id === user?.department_id)?.name || 'Not assigned'}
                                    readOnly
                                    placeholder="Not assigned"
                                />
                                <small className="text-muted">Linked to your user profile</small>
                            </div>

                            {user?.subdepartment_id && (
                                <div className="form-group">
                                    <label className="form-label">Sub-Department</label>
                                    <input
                                        className="form-input"
                                        value={senderSubDeptName || 'Not assigned'}
                                        readOnly
                                        placeholder="Not assigned"
                                    />
                                    <small className="text-muted">Linked to your user profile</small>
                                </div>
                            )}
                        </div>

                        {/* RECIPIENT Section */}
                        <div style={{ padding: '1rem', background: 'var(--gray-50)', borderRadius: 'var(--radius)' }}>
                            <h3 style={{ fontSize: '1.1rem', fontWeight: '700', color: '#610100', marginBottom: '1rem' }}>
                                RECIPIENT
                            </h3>

                            <div className="form-group">
                                <label className="form-label">Division *</label>
                                <select
                                    className="form-select"
                                    value={recipientDivisionId}
                                    onChange={(e) => {
                                        setRecipientDivisionId(e.target.value);
                                        setRecipientDepartmentId('');
                                        setRecipientSubDepartmentId('');
                                    }}
                                    required
                                >
                                    <option value="">Select division</option>
                                    {divisions.map(div => (
                                        <option key={div.id} value={div.id}>{div.name}</option>
                                    ))}
                                </select>
                            </div>

                            <div className="form-group">
                                <label className="form-label">Department (Optional)</label>
                                <select
                                    className="form-select"
                                    value={recipientDepartmentId}
                                    onChange={(e) => {
                                        setRecipientDepartmentId(e.target.value);
                                        setRecipientSubDepartmentId('');
                                    }}
                                    disabled={!recipientDivisionId}
                                >
                                    <option value="">Select department</option>
                                    {recipientDepartments.map(dept => (
                                        <option key={dept.id} value={dept.id}>{dept.name}</option>
                                    ))}
                                </select>
                            </div>

                            <div className="form-group">
                                <label className="form-label">Sub-Department (Optional)</label>
                                <select
                                    className="form-select"
                                    value={recipientSubDepartmentId}
                                    onChange={(e) => setRecipientSubDepartmentId(e.target.value)}
                                    disabled={!recipientDepartmentId || subDepartments.length === 0}
                                >
                                    <option value="">
                                        {subDepartments.length === 0
                                            ? (recipientDepartmentId ? 'No sub-departments available' : 'Select department first')
                                            : 'Select sub-department'}
                                    </option>
                                    {subDepartments.map(sub => (
                                        <option key={sub.id} value={sub.id}>{sub.name}</option>
                                    ))}
                                </select>
                            </div>
                        </div>
                    </div>

                    <div className="form-group">
                        <label className="form-label">Request Description *</label>
                        <textarea
                            className="form-textarea"
                            value={description}
                            onChange={(e) => setDescription(e.target.value)}
                            required
                            rows={4}
                            placeholder="Describe your request in detail..."
                        />
                    </div>

                    <div className="form-group">
                        <label className="form-label">Attachments (Optional)</label>
                        <div className="file-input-wrapper">
                            <input
                                type="file"
                                className="file-input-hidden"
                                multiple
                                onChange={(e) => {
                                    if (e.target.files) {
                                        const files = Array.from(e.target.files);

                                        // Validation: Max 3 files
                                        if (files.length > 3) {
                                            alert("You can only upload a maximum of 3 files.");
                                            e.target.value = ''; // Clear input
                                            return;
                                        }

                                        // Validation: Max 10MB per file
                                        const MAX_SIZE = 10 * 1024 * 1024; // 10MB
                                        const validFiles = files.filter(file => {
                                            if (file.size > MAX_SIZE) {
                                                alert(`File ${file.name} is too large. Max size is 10MB.`);
                                                return false;
                                            }
                                            return true;
                                        });

                                        setRequestFiles(validFiles);
                                    }
                                }}
                                accept=".doc,.docx,.xls,.xlsx,.pdf,.jpg,.jpeg,.png,.gif"
                            />
                            <div className="file-input-glass">
                                <svg xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M7 16a4 4 0 01-.88-7.903A5 5 0 1115.9 6L16 6a5 5 0 011 9.9M15 13l-3-3m0 0l-3 3m3-3v12" />
                                </svg>
                                <span>Choose Files</span>
                            </div>
                        </div>
                        <small className="text-muted">Max 3 files, up to 10MB each (Word, Excel, PDF, Image)</small>
                        {requestFiles.length > 0 && (
                            <div style={{ marginTop: '0.5rem', fontSize: '0.85rem' }}>
                                <strong>Selected files:</strong>
                                <ul style={{ margin: '0.25rem 0 0 1.2rem', padding: 0 }}>
                                    {requestFiles.map((f, i) => (
                                        <li key={i}>{f.name} ({(f.size / 1024 / 1024).toFixed(2)} MB)</li>
                                    ))}
                                </ul>
                            </div>
                        )}
                    </div>

                    {/* Priority Type */}
                    <div className="form-group">
                        <label className="form-label">Priority Type *</label>
                        <select
                            className="form-select"
                            value={priority}
                            onChange={(e) => setPriority(e.target.value as any)}
                            required
                            style={{ maxWidth: '300px' }}
                        >
                            <option value="LOW">Low</option>
                            <option value="MEDIUM">Medium</option>
                            <option value="HIGH">High</option>
                        </select>
                    </div>

                    {/* Resource Type */}
                    <div className="form-group">
                        <label className="form-label">Resource Type *</label>
                        <select
                            className="form-select"
                            value={resourceType}
                            onChange={(e) => setResourceType(e.target.value)}
                            required
                            style={{ maxWidth: '300px' }}
                        >
                            <option value="GENERAL">General Request</option>
                            <option value="FLEET">Fleet / Transport</option>
                            <option value="HR">HR Deployment</option>
                            <option value="FINANCE">Finance Transaction</option>
                            <option value="ICT">ICT Support</option>
                            <option value="LOGISTICS">Logistics / Supply</option>
                        </select>
                        <small className="text-muted">Select the specific resource area for this request</small>
                    </div>
                </div>

                {/* Request Items */}
                <div className="card">
                    <div className="card-header">
                        <h2 className="card-title">Request Items</h2>
                        <button type="button" className="btn btn-secondary" onClick={addItem}>
                            + Add Item
                        </button>
                    </div>

                    {items.map((item, index) => (
                        <div key={index} style={{ marginBottom: '1.5rem', padding: '1rem', background: 'var(--gray-50)', borderRadius: 'var(--radius)' }}>
                            <div className="flex" style={{ justifyContent: 'space-between', marginBottom: '1rem' }}>
                                <h3 style={{ fontSize: '1rem', fontWeight: '600' }}>Item {index + 1}</h3>
                                {items.length > 1 && (
                                    <button
                                        type="button"
                                        onClick={() => removeItem(index)}
                                        className="btn btn-outline"
                                        style={{ color: 'var(--error)', borderColor: 'var(--error)', padding: '0.5rem 1rem' }}
                                    >
                                        Remove
                                    </button>
                                )}
                            </div>

                            <div className="grid grid-2">
                                <div className="form-group">
                                    <label className="form-label">Item Description</label>
                                    <input
                                        type="text"
                                        className="form-input"
                                        value={item.item_description}
                                        onChange={(e) => updateItem(index, 'item_description', e.target.value)}
                                        placeholder="Describe the item (optional)"
                                    />
                                </div>

                                <div className="form-group">
                                    <label className="form-label">Item Description File</label>
                                    <div className="file-input-wrapper">
                                        <input
                                            type="file"
                                            className="file-input-hidden"
                                            onChange={(e) => handleFileChange(index, e)}
                                            accept=".doc,.docx,.xls,.xlsx,.pdf,.jpg,.jpeg,.png,.gif"
                                        />
                                        <div className="file-input-glass">
                                            <svg xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                                                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M7 16a4 4 0 01-.88-7.903A5 5 0 1115.9 6L16 6a5 5 0 011 9.9M15 13l-3-3m0 0l-3 3m3-3v12" />
                                            </svg>
                                            <span style={{ whiteSpace: 'nowrap', overflow: 'hidden', textOverflow: 'ellipsis', maxWidth: '150px' }}>
                                                {item.file ? item.file.name : 'Choose File'}
                                            </span>
                                        </div>
                                    </div>
                                    <small style={{ color: 'var(--text-muted)', fontSize: '0.85rem' }}>
                                        Word, Excel, PDF, or Image
                                    </small>
                                </div>

                                <div className="form-group">
                                    <label className="form-label">Quantity</label>
                                    <input
                                        type="number"
                                        className="form-input"
                                        value={item.quantity || ''}
                                        onChange={(e) => updateItem(index, 'quantity', e.target.value ? Number(e.target.value) : undefined)}
                                        placeholder="1"
                                    />
                                </div>

                                <div className="form-group">
                                    <label className="form-label">Unit Price</label>
                                    <input
                                        type="number"
                                        step="0.01"
                                        className="form-input"
                                        value={item.unit_price || ''}
                                        onChange={(e) => updateItem(index, 'unit_price', e.target.value ? Number(e.target.value) : undefined)}
                                        placeholder="0.00"
                                    />
                                </div>
                            </div>

                            <div className="form-group">
                                <label className="form-label">Notes</label>
                                <input
                                    type="text"
                                    className="form-input"
                                    value={item.notes || ''}
                                    onChange={(e) => updateItem(index, 'notes', e.target.value)}
                                    placeholder="Additional notes for this item"
                                />
                            </div>
                        </div>
                    ))}
                </div>

                <div className="flex gap-md">
                    <button type="submit" className="btn btn-primary" disabled={loading}>
                        {loading ? 'Submitting...' : 'Submit Request'}
                    </button>
                    <button
                        type="button"
                        className="btn btn-outline"
                        onClick={() => navigate('/requests')}
                        disabled={loading}
                    >
                        Cancel
                    </button>
                </div>
            </form>
        </div>
    );
};
