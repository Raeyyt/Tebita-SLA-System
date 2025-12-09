import { useState, useEffect } from 'react';
import { useAuth } from '../contexts/AuthContext';
import { api } from '../services/api';

export const SystemSettingsPage = () => {
    const { token, user } = useAuth();
    const [emailEnabled, setEmailEnabled] = useState(false);
    const [loading, setLoading] = useState(true);
    const [saving, setSaving] = useState(false);

    // SMTP State
    const [smtpConfig, setSmtpConfig] = useState({
        smtp_email: '',
        smtp_password: '',
        smtp_host: 'smtp.gmail.com',
        smtp_port: '587'
    });
    const [showSmtpForm, setShowSmtpForm] = useState(false);

    // Health Check State
    const [healthStatus, setHealthStatus] = useState<any>(null);
    const [testingSystem, setTestingSystem] = useState(false);

    useEffect(() => {
        const loadSettings = async () => {
            if (!token) return;

            try {
                const status = await api.getEmailNotificationStatus(token);
                setEmailEnabled(status.enabled);

                // Note: We don't load existing SMTP password for security, 
                // but we could load other fields if the API supported it.
                // For now, we start blank or with defaults.
            } catch (err) {
                console.error('Failed to load settings:', err);
            } finally {
                setLoading(false);
            }
        };

        loadSettings();
    }, [token]);

    const handleToggleEmail = async () => {
        if (!token || saving) return;

        setSaving(true);
        try {
            const newValue = !emailEnabled;
            await api.updateEmailNotifications(token, newValue);
            setEmailEnabled(newValue);
            alert(`Email notifications ${newValue ? 'enabled' : 'disabled'} successfully!`);
        } catch (err) {
            console.error('Failed to update settings:', err);
            alert('Failed to update settings');
        } finally {
            setSaving(false);
        }
    };

    const handleSmtpChange = (e: React.ChangeEvent<HTMLInputElement>) => {
        setSmtpConfig({
            ...smtpConfig,
            [e.target.name]: e.target.value
        });
    };

    const handleSaveSmtp = async (e: React.FormEvent) => {
        e.preventDefault();
        if (!token) return;

        setSaving(true);
        try {
            await api.updateSmtpSettings(token, smtpConfig);
            alert('SMTP settings saved successfully!');
            setShowSmtpForm(false);
        } catch (err) {
            console.error('Failed to save SMTP settings:', err);
            alert('Failed to save SMTP settings');
        } finally {
            setSaving(false);
        }
    };

    const handleTestSystem = async () => {
        if (!token) return;

        setTestingSystem(true);
        setHealthStatus(null);
        try {
            const result = await api.testSystemHealth(token);
            setHealthStatus(result);
        } catch (err) {
            console.error('System health check failed:', err);
            alert('System health check failed');
        } finally {
            setTestingSystem(false);
        }
    };

    const downloadHealthReport = () => {
        if (!healthStatus) return;

        const report = JSON.stringify(healthStatus, null, 2);
        const blob = new Blob([report], { type: 'application/json' });
        const url = URL.createObjectURL(blob);
        const link = document.createElement('a');
        link.href = url;
        link.download = `system_health_${new Date().toISOString().split('T')[0]}.json`;
        document.body.appendChild(link);
        link.click();
        document.body.removeChild(link);
    };

    if (user?.role !== 'ADMIN') {
        return (
            <div style={{ padding: '2rem' }}>
                <div className="card">
                    <div style={{ padding: '3rem', textAlign: 'center' }}>
                        <p style={{ fontSize: '1.2rem', color: 'var(--error)' }}>
                            Access Denied: Admin privileges required
                        </p>
                    </div>
                </div>
            </div>
        );
    }

    if (loading) {
        return <div className="spinner"></div>;
    }

    return (
        <div style={{ padding: '2rem' }}>
            <div className="card-header" style={{ marginBottom: '2rem' }}>
                <div>
                    <h1 className="card-title">System Settings</h1>
                    <p className="text-muted">Configure system-wide features and preferences</p>
                </div>
                <button
                    onClick={handleTestSystem}
                    disabled={testingSystem}
                    className="btn btn-primary"
                    style={{ display: 'flex', alignItems: 'center', gap: '0.5rem' }}
                >
                    {testingSystem ? 'Testing...' : 'Test System Health'}
                </button>
            </div>

            {/* Health Check Results */}
            {healthStatus && (
                <div className="card" style={{ marginBottom: '2rem', borderLeft: `4px solid ${healthStatus.status === 'healthy' ? '#10b981' : '#ef4444'}` }}>
                    <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '1rem' }}>
                        <h3 style={{ margin: 0 }}>System Health Report</h3>
                        <button onClick={downloadHealthReport} className="btn btn-outline">
                            Download Report
                        </button>
                    </div>
                    <div style={{ marginBottom: '1rem' }}>
                        <strong>Status: </strong>
                        <span style={{
                            color: healthStatus.status === 'healthy' ? '#10b981' : '#ef4444',
                            fontWeight: 'bold',
                            textTransform: 'uppercase'
                        }}>
                            {healthStatus.status}
                        </span>
                        <span style={{ marginLeft: '1rem', color: '#666', fontSize: '0.9rem' }}>
                            {new Date(healthStatus.timestamp).toLocaleString()}
                        </span>
                    </div>
                    <div style={{ display: 'grid', gap: '0.5rem' }}>
                        {healthStatus.checks.map((check: any, index: number) => (
                            <div key={index} style={{
                                padding: '0.75rem',
                                background: '#f8f9fa',
                                borderRadius: '6px',
                                display: 'flex',
                                justifyContent: 'space-between',
                                alignItems: 'center'
                            }}>
                                <span>{check.name}</span>
                                <div style={{ display: 'flex', alignItems: 'center', gap: '1rem' }}>
                                    <span style={{ fontSize: '0.9rem', color: '#666' }}>{check.details}</span>
                                    <span style={{
                                        fontWeight: 'bold',
                                        color: check.status === 'PASS' ? '#10b981' : check.status === 'WARNING' ? '#f59e0b' : '#ef4444'
                                    }}>
                                        {check.status}
                                    </span>
                                </div>
                            </div>
                        ))}
                    </div>
                </div>
            )}

            <div className="card">
                <div className="card-header">
                    <h2 className="card-title">Email Notifications</h2>
                </div>

                <div style={{ padding: '2rem' }}>
                    <div style={{
                        display: 'flex',
                        justifyContent: 'space-between',
                        alignItems: 'center',
                        padding: '1.5rem',
                        background: 'rgba(0, 0, 0, 0.02)',
                        borderRadius: '8px',
                        border: '1px solid rgba(0, 0, 0, 0.1)'
                    }}>
                        <div>
                            <div style={{ fontSize: '1.1rem', fontWeight: '600', marginBottom: '0.5rem' }}>
                                All Requests Alert
                            </div>
                            <div style={{ fontSize: '0.875rem', color: 'var(--text-muted)' }}>
                                Send email notifications for ALL new requests (High, Medium, Low).
                                Emails are sent to assigned department users.
                            </div>
                        </div>

                        <label className="toggle-switch" style={{ marginLeft: '2rem' }}>
                            <input
                                type="checkbox"
                                checked={emailEnabled}
                                onChange={handleToggleEmail}
                                disabled={saving}
                            />
                            <span className="toggle-slider"></span>
                        </label>
                    </div>

                    <div style={{
                        marginTop: '1.5rem',
                        padding: '1rem',
                        background: emailEnabled ? '#d4edda' : '#f8d7da',
                        border: `1px solid ${emailEnabled ? '#c3e6cb' : '#f5c6cb'}`,
                        borderRadius: '8px',
                        color: emailEnabled ? '#155724' : '#721c24'
                    }}>
                        <strong>Status:</strong> Email notifications are currently{' '}
                        <strong>{emailEnabled ? 'ENABLED' : 'DISABLED'}</strong>
                    </div>

                    {emailEnabled && (
                        <div style={{ marginTop: '2rem' }}>
                            <button
                                onClick={() => setShowSmtpForm(!showSmtpForm)}
                                className="btn btn-outline"
                                style={{ marginBottom: '1rem' }}
                            >
                                {showSmtpForm ? 'Hide Configuration' : 'Configure SMTP Settings'}
                            </button>

                            {showSmtpForm && (
                                <form onSubmit={handleSaveSmtp} style={{
                                    padding: '1.5rem',
                                    background: '#f8f9fa',
                                    borderRadius: '8px',
                                    border: '1px solid #e9ecef'
                                }}>
                                    <h3 style={{ marginTop: 0, marginBottom: '1rem', fontSize: '1.1rem' }}>SMTP Configuration</h3>

                                    <div className="form-group">
                                        <label>Sender Email</label>
                                        <input
                                            type="email"
                                            name="smtp_email"
                                            value={smtpConfig.smtp_email}
                                            onChange={handleSmtpChange}
                                            className="form-control"
                                            placeholder="e.g., notifications@tebita.com"
                                            required
                                        />
                                    </div>

                                    <div className="form-group">
                                        <label>App Password</label>
                                        <input
                                            type="password"
                                            name="smtp_password"
                                            value={smtpConfig.smtp_password}
                                            onChange={handleSmtpChange}
                                            className="form-control"
                                            placeholder="Enter app password"
                                            required
                                        />
                                        <small className="text-muted">
                                            For Gmail, use an App Password, not your login password.
                                        </small>
                                    </div>

                                    <div style={{ display: 'grid', gridTemplateColumns: '2fr 1fr', gap: '1rem' }}>
                                        <div className="form-group">
                                            <label>SMTP Host</label>
                                            <input
                                                type="text"
                                                name="smtp_host"
                                                value={smtpConfig.smtp_host}
                                                onChange={handleSmtpChange}
                                                className="form-control"
                                                placeholder="smtp.gmail.com"
                                                required
                                            />
                                        </div>
                                        <div className="form-group">
                                            <label>Port</label>
                                            <input
                                                type="text"
                                                name="smtp_port"
                                                value={smtpConfig.smtp_port}
                                                onChange={handleSmtpChange}
                                                className="form-control"
                                                placeholder="587"
                                                required
                                            />
                                        </div>
                                    </div>

                                    <div style={{ marginTop: '1rem', display: 'flex', justifyContent: 'flex-end' }}>
                                        <button type="submit" className="btn btn-primary" disabled={saving}>
                                            {saving ? 'Saving...' : 'Save Configuration'}
                                        </button>
                                    </div>
                                </form>
                            )}
                        </div>
                    )}
                </div>
            </div>

            {/* Toggle Switch Styles */}
            <style>{`
                .toggle-switch {
                    position: relative;
                    display: inline-block;
                    width: 60px;
                    height: 34px;
                }

                .toggle-switch input {
                    opacity: 0;
                    width: 0;
                    height: 0;
                }

                .toggle-slider {
                    position: absolute;
                    cursor: pointer;
                    top: 0;
                    left: 0;
                    right: 0;
                    bottom: 0;
                    background-color: #ccc;
                    transition: 0.4s;
                    border-radius: 34px;
                }

                .toggle-slider:before {
                    position: absolute;
                    content: "";
                    height: 26px;
                    width: 26px;
                    left: 4px;
                    bottom: 4px;
                    background-color: white;
                    transition: 0.4s;
                    border-radius: 50%;
                }

                input:checked + .toggle-slider {
                    background-color: #10b981;
                }

                input:checked + .toggle-slider:before {
                    transform: translateX(26px);
                }

                input:disabled + .toggle-slider {
                    opacity: 0.5;
                    cursor: not-allowed;
                }
            `}</style>
        </div>
    );
};
