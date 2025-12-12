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
    const [showPassword, setShowPassword] = useState(false);

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

    const handleResetData = async () => {
        if (!token) return;

        setSaving(true);
        try {
            const result = await api.resetSystemData(token);
            alert(result.message || 'System data reset successfully.');
            // Reload page to reflect changes (optional, but good practice)
            window.location.reload();
        } catch (err) {
            console.error('Failed to reset system data:', err);
            alert('Failed to reset system data. Check console for details.');
        } finally {
            setSaving(false);
        }
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
                                    marginTop: '1.5rem',
                                    padding: '2rem',
                                    background: '#ffffff',
                                    borderRadius: '12px',
                                    border: '1px solid #e2e8f0',
                                    boxShadow: '0 4px 6px -1px rgba(0, 0, 0, 0.1), 0 2px 4px -1px rgba(0, 0, 0, 0.06)'
                                }}>
                                    <div style={{ display: 'flex', alignItems: 'center', marginBottom: '1.5rem', borderBottom: '1px solid #f1f5f9', paddingBottom: '1rem' }}>
                                        <div style={{
                                            width: '32px',
                                            height: '32px',
                                            borderRadius: '8px',
                                            background: '#eff6ff',
                                            color: '#3b82f6',
                                            display: 'flex',
                                            alignItems: 'center',
                                            justifyContent: 'center',
                                            marginRight: '0.75rem'
                                        }}>
                                            <svg width="20" height="20" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                                                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M10.325 4.317c.426-1.756 2.924-1.756 3.35 0a1.724 1.724 0 002.573 1.066c1.543-.94 3.31.826 2.37 2.37a1.724 1.724 0 001.065 2.572c1.756.426 1.756 2.924 0 3.35a1.724 1.724 0 00-1.066 2.573c.94 1.543-.826 3.31-2.37 2.37a1.724 1.724 0 00-2.572 1.065c-.426 1.756-2.924 1.756-3.35 0a1.724 1.724 0 00-2.573-1.066c-1.543.94-3.31-.826-2.37-2.37a1.724 1.724 0 00-1.065-2.572c-1.756-.426-1.756-2.924 0-3.35a1.724 1.724 0 001.066-2.573c-.94-1.543.826-3.31 2.37-2.37.996.608 2.296.07 2.572-1.065z"></path>
                                                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M15 12a3 3 0 11-6 0 3 3 0 016 0z"></path>
                                            </svg>
                                        </div>
                                        <h3 style={{ margin: 0, fontSize: '1.25rem', color: '#1e293b' }}>SMTP Configuration</h3>
                                    </div>

                                    <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '1.5rem' }}>
                                        <div className="form-group" style={{ gridColumn: '1 / -1' }}>
                                            <label style={{ display: 'block', marginBottom: '0.5rem', fontWeight: '500', color: '#475569' }}>Sender Email</label>
                                            <input
                                                type="email"
                                                name="smtp_email"
                                                value={smtpConfig.smtp_email}
                                                onChange={handleSmtpChange}
                                                className="form-control"
                                                placeholder="notifications@tebita.com"
                                                required
                                                style={{ width: '100%', padding: '0.75rem', borderRadius: '6px', border: '1px solid #cbd5e1' }}
                                            />
                                        </div>

                                        <div className="form-group" style={{ gridColumn: '1 / -1' }}>
                                            <label style={{ display: 'block', marginBottom: '0.5rem', fontWeight: '500', color: '#475569' }}>
                                                App Password
                                                <span style={{ marginLeft: '0.5rem', fontSize: '0.8rem', color: '#64748b', fontWeight: 'normal' }}>
                                                    (Use an App Password for Gmail, not your login password)
                                                </span>
                                            </label>
                                            <div style={{ position: 'relative' }}>
                                                <input
                                                    type={showPassword ? "text" : "password"}
                                                    name="smtp_password"
                                                    value={smtpConfig.smtp_password}
                                                    onChange={handleSmtpChange}
                                                    className="form-control"
                                                    placeholder="Enter app password"
                                                    required
                                                    style={{ width: '100%', padding: '0.75rem', borderRadius: '6px', border: '1px solid #cbd5e1', paddingRight: '3rem' }}
                                                />
                                                <button
                                                    type="button"
                                                    onClick={() => setShowPassword(!showPassword)}
                                                    style={{
                                                        position: 'absolute',
                                                        right: '0.75rem',
                                                        top: '50%',
                                                        transform: 'translateY(-50%)',
                                                        background: 'none',
                                                        border: 'none',
                                                        cursor: 'pointer',
                                                        color: '#94a3b8'
                                                    }}
                                                >
                                                    {showPassword ? (
                                                        <svg width="20" height="20" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M13.875 18.825A10.05 10.05 0 0112 19c-4.478 0-8.268-2.943-9.543-7a9.97 9.97 0 011.563-3.029m5.858.908a3 3 0 114.243 4.243M9.878 9.878l4.242 4.242M9.88 9.88l-3.29-3.29m7.532 7.532l3.29 3.29M3 3l3.59 3.59m0 0A9.953 9.953 0 0112 5c4.478 0 8.268 2.943 9.543 7a10.025 10.025 0 01-4.132 5.411m0 0L21 21"></path></svg>
                                                    ) : (
                                                        <svg width="20" height="20" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M15 12a3 3 0 11-6 0 3 3 0 016 0z"></path><path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M2.458 12C3.732 7.943 7.523 5 12 5c4.478 0 8.268 2.943 9.542 7-1.274 4.057-5.064 7-9.542 7-4.477 0-8.268-2.943-9.542-7z"></path></svg>
                                                    )}
                                                </button>
                                            </div>
                                        </div>

                                        <div className="form-group">
                                            <label style={{ display: 'block', marginBottom: '0.5rem', fontWeight: '500', color: '#475569' }}>SMTP Host</label>
                                            <input
                                                type="text"
                                                name="smtp_host"
                                                value={smtpConfig.smtp_host}
                                                onChange={handleSmtpChange}
                                                className="form-control"
                                                placeholder="smtp.gmail.com"
                                                required
                                                style={{ width: '100%', padding: '0.75rem', borderRadius: '6px', border: '1px solid #cbd5e1' }}
                                            />
                                        </div>

                                        <div className="form-group">
                                            <label style={{ display: 'block', marginBottom: '0.5rem', fontWeight: '500', color: '#475569' }}>Port</label>
                                            <input
                                                type="text"
                                                name="smtp_port"
                                                value={smtpConfig.smtp_port}
                                                onChange={handleSmtpChange}
                                                className="form-control"
                                                placeholder="587"
                                                required
                                                style={{ width: '100%', padding: '0.75rem', borderRadius: '6px', border: '1px solid #cbd5e1' }}
                                            />
                                        </div>
                                    </div>

                                    <div style={{ marginTop: '2rem', display: 'flex', justifyContent: 'flex-end', gap: '1rem' }}>
                                        <button
                                            type="button"
                                            className="btn btn-outline"
                                            onClick={() => setShowSmtpForm(false)}
                                            style={{ padding: '0.75rem 1.5rem' }}
                                        >
                                            Cancel
                                        </button>
                                        <button
                                            type="submit"
                                            className="btn btn-primary"
                                            disabled={saving}
                                            style={{ padding: '0.75rem 1.5rem', display: 'flex', alignItems: 'center', gap: '0.5rem' }}
                                        >
                                            {saving ? 'Saving...' : (
                                                <>
                                                    <svg width="18" height="18" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M5 13l4 4L19 7"></path></svg>
                                                    Save Configuration
                                                </>
                                            )}
                                        </button>
                                    </div>
                                </form>
                            )}
                        </div>
                    )}
                </div>
            </div>

            {/* Danger Zone */}
            <div className="card" style={{ marginTop: '2rem', borderColor: 'var(--error)' }}>
                <div className="card-header" style={{ borderBottom: '1px solid var(--gray-200)' }}>
                    <h2 className="card-title" style={{ color: 'var(--error)' }}>Danger Zone</h2>
                </div>
                <div style={{ padding: '2rem' }}>
                    <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
                        <div>
                            <h3 style={{ fontSize: '1.1rem', fontWeight: '600', marginBottom: '0.5rem' }}>Reset System Data</h3>
                            <p className="text-muted" style={{ maxWidth: '600px' }}>
                                This action will permanently delete all requests, workflows, logs, alerts, and feedback data.
                                Users, departments, and system settings will be preserved.
                                <strong>This action cannot be undone.</strong>
                            </p>
                        </div>
                        <button
                            className="btn"
                            style={{
                                background: 'var(--error)',
                                color: 'white',
                                border: 'none',
                                padding: '0.75rem 1.5rem'
                            }}
                            onClick={() => {
                                if (window.confirm('ARE YOU SURE? This will delete ALL requests and related data permanently. This action cannot be undone.')) {
                                    handleResetData();
                                }
                            }}
                        >
                            Reset Data
                        </button>
                    </div>
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
