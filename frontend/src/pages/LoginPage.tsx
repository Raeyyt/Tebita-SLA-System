import { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { useAuth } from '../contexts/AuthContext';
import './LoginPage.css';

export const LoginPage = () => {
    const navigate = useNavigate();
    const { login } = useAuth();
    const [formData, setFormData] = useState({
        username: '',
        password: '',
    });
    const [error, setError] = useState('');
    const [loading, setLoading] = useState(false);
    const [showPassword, setShowPassword] = useState(false);

    const handleSubmit = async (e: React.FormEvent) => {
        e.preventDefault();
        setError('');
        setLoading(true);

        try {
            await login(formData.username, formData.password);
            navigate('/dashboard');
        } catch (err: any) {
            console.error('Login error details:', err);
            const errorMessage = err?.response?.data?.detail || err?.message || 'Login failed. Please check your credentials.';
            setError(errorMessage);
        } finally {
            setLoading(false);
        }
    };

    return (
        <div className="login-container">
            <div className="login-card-glass">
                <div className="login-header">
                    <div className="login-logo-container">
                        <img
                            src="/tebita-logo.png"
                            alt="Tebita Ambulance"
                            className="login-logo"
                        />
                    </div>
                    <img
                        src="/tebita-sla-logo.png"
                        alt="Tebita SLA System"
                        style={{
                            height: '60px',
                            marginBottom: '1rem',
                            objectFit: 'contain'
                        }}
                    />
                    <p className="login-subtitle">Sign in to your account</p>
                </div>

                <form onSubmit={handleSubmit} className="login-form">
                    {error && (
                        <div className="login-error">
                            <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
                                <circle cx="12" cy="12" r="10" />
                                <line x1="12" y1="8" x2="12" y2="12" />
                                <line x1="12" y1="16" x2="12.01" y2="16" />
                            </svg>
                            {error}
                        </div>
                    )}

                    <div className="form-group-glass">
                        <label className="form-label-glass">Username</label>
                        <input
                            type="text"
                            className="form-input-glass"
                            placeholder="Enter your username"
                            value={formData.username}
                            onChange={(e) => setFormData({ ...formData, username: e.target.value })}
                            required
                            disabled={loading}
                        />
                    </div>

                    <div className="form-group-glass">
                        <label className="form-label-glass">Password</label>
                        <div className="password-input-wrapper">
                            <input
                                type={showPassword ? 'text' : 'password'}
                                className="form-input-glass"
                                placeholder="Enter your password"
                                value={formData.password}
                                onChange={(e) => setFormData({ ...formData, password: e.target.value })}
                                required
                                disabled={loading}
                            />
                            <button
                                type="button"
                                className="password-toggle-glass"
                                onClick={() => setShowPassword(!showPassword)}
                                tabIndex={-1}
                            >
                                {showPassword ? (
                                    <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
                                        <path d="M17.94 17.94A10.07 10.07 0 0 1 12 20c-7 0-11-8-11-8a18.45 18.45 0 0 1 5.06-5.94M9.9 4.24A9.12 9.12 0 0 1 12 4c7 0 11 8 11 8a18.5 18.5 0 0 1-2.16 3.19m-6.72-1.07a3 3 0 1 1-4.24-4.24" />
                                        <line x1="1" y1="1" x2="23" y2="23" />
                                    </svg>
                                ) : (
                                    <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
                                        <path d="M1 12s4-8 11-8 11 8 11 8-4 8-11 8-11-8-11-8z" />
                                        <circle cx="12" cy="12" r="3" />
                                    </svg>
                                )}
                            </button>
                        </div>
                    </div>

                    <button
                        type="submit"
                        className="login-button-glass"
                        disabled={loading}
                    >
                        {loading ? (
                            <>
                                <span className="spinner-small"></span>
                                Signing in...
                            </>
                        ) : (
                            'Sign In'
                        )}
                    </button>
                </form>

                <div className="login-footer-glass">
                    <p>DEVELOPED BY</p>
                    <img
                        src="/raey-logo.png"
                        alt="RAEY"
                        style={{
                            height: '50px',
                            marginTop: '0.25rem',
                            objectFit: 'contain'
                        }}
                    />
                </div>
                <div className="beta-version-label">Beta</div>
            </div>
        </div>

    );
};
