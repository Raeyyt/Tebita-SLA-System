import { useState, useEffect } from 'react';
import { useAuth } from '../contexts/AuthContext';
import { api } from '../services/api';

export const SystemSettingsPage = () => {
    const { token, user } = useAuth();
    const [emailEnabled, setEmailEnabled] = useState(false);
    const [loading, setLoading] = useState(true);
    const [saving, setSaving] = useState(false);

    useEffect(() => {
        const loadSettings = async () => {
            if (!token) return;

            try {
                const status = await api.getEmailNotificationStatus(token);
                setEmailEnabled(status.enabled);
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
        return (
            <div style={{ padding: '2rem' }}>
                <div className="card">
                    <div style={{ padding: '3rem', textAlign: 'center' }}>
                        Loading settings...
                    </div>
                </div>
            </div>
        );
    }

    return (
        <div style={{ padding: '2rem' }}>
            <div className="card-header" style={{ marginBottom: '2rem' }}>
                <div>
                    <h1 className="card-title">System Settings</h1>
                    <p className="text-muted">Configure system-wide features and preferences</p>
                </div>
            </div>

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
                                HIGH Priority Email Alerts
                            </div>
                            <div style={{ fontSize: '0.875rem', color: 'var(--text-muted)' }}>
                                Send email notifications when HIGH priority requests are created.
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
                        <div style={{
                            marginTop: '1.5rem',
                            padding: '1rem',
                            background: '#fff3cd',
                            border: '1px solid #ffc107',
                            borderRadius: '8px'
                        }}>
                            <div style={{ fontWeight: '600', marginBottom: '0.5rem', color: '#856404' }}>
                                Configuration Required
                            </div>
                            <div style={{ fontSize: '0.875rem', color: '#856404' }}>
                                Make sure SMTP settings are configured in the backend .env file:
                                <ul style={{ marginTop: '0.5rem', marginLeft: '1.5rem' }}>
                                    <li>SMTP_USERNAME</li>
                                    <li>SMTP_PASSWORD</li>
                                    <li>SMTP_HOST (default: smtp.gmail.com)</li>
                                </ul>
                            </div>
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
