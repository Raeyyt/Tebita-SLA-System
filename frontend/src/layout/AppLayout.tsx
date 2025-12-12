import { Outlet, Link, useNavigate } from 'react-router-dom';
import { useAuth } from '../contexts/AuthContext';
import { getApiUrl } from '../services/api';
import { useState, useEffect } from 'react';
import axios from 'axios';

export const AppLayout = () => {
    const { user, logout, token } = useAuth();
    const navigate = useNavigate();
    const [unreadCount, setUnreadCount] = useState(0);
    const [mobileMenuOpen, setMobileMenuOpen] = useState(false);

    const handleLogout = () => {
        logout();
        navigate('/login');
    };

    const toggleMobileMenu = () => {
        setMobileMenuOpen(!mobileMenuOpen);
    };

    const closeMobileMenu = () => {
        setMobileMenuOpen(false);
    };

    // Fetch unread notification count
    useEffect(() => {
        const fetchUnreadCount = async () => {
            if (!token) return;
            try {
                const API_BASE = getApiUrl();
                const response = await axios.get(`${API_BASE}/notifications/unread-count`, {
                    headers: { Authorization: `Bearer ${token}` }
                });
                setUnreadCount(response.data.count || 0);
            } catch (err) {
                console.error('Failed to fetch unread count:', err);
            }
        };
        fetchUnreadCount();
        // Poll every 30 seconds
        const interval = setInterval(fetchUnreadCount, 30000);
        return () => clearInterval(interval);
    }, [token]);

    // Auto-logout on inactivity (15 minutes)
    useEffect(() => {
        if (!token) return;

        const INACTIVITY_TIMEOUT = 15 * 60 * 1000; // 15 minutes
        let timeoutId: ReturnType<typeof setTimeout>;

        const performAutoLogout = () => {
            console.log("User inactive for 15 minutes, performing auto-logout.");
            logout();
            navigate('/login');
        };

        const resetTimer = () => {
            if (timeoutId) clearTimeout(timeoutId);
            timeoutId = setTimeout(performAutoLogout, INACTIVITY_TIMEOUT);
        };

        // Events to track user activity
        const events = ['mousedown', 'mousemove', 'keydown', 'scroll', 'touchstart'];

        // Attach event listeners
        events.forEach(event => {
            document.addEventListener(event, resetTimer);
        });

        // Initial timer start
        resetTimer();

        // Cleanup
        return () => {
            if (timeoutId) clearTimeout(timeoutId);
            events.forEach(event => {
                document.removeEventListener(event, resetTimer);
            });
        };
    }, [token, logout, navigate]);

    const navLinks = [
        { to: '/', label: 'Dashboard', roles: ['ADMIN', 'DIVISION_MANAGER', 'DEPARTMENT_HEAD', 'SUB_DEPARTMENT_STAFF'] },
        { to: '/requests', label: 'All Requests', roles: ['ADMIN', 'DIVISION_MANAGER', 'DEPARTMENT_HEAD', 'SUB_DEPARTMENT_STAFF'] },
        { to: '/requests/inbox', label: 'Incoming Requests', roles: ['DIVISION_MANAGER', 'DEPARTMENT_HEAD', 'SUB_DEPARTMENT_STAFF'] },
        { to: '/requests/sent', label: 'Sent Requests', roles: ['DIVISION_MANAGER', 'DEPARTMENT_HEAD', 'SUB_DEPARTMENT_STAFF'] },
        { to: '/requests/new', label: 'New Request', roles: ['DIVISION_MANAGER', 'DEPARTMENT_HEAD', 'SUB_DEPARTMENT_STAFF'] },
        { to: '/me-dashboard', label: 'M&E Dashboard', roles: ['ADMIN', 'DIVISION_MANAGER'] },
        { to: '/sla-monitor', label: 'SLA Monitor', roles: ['ADMIN', 'DIVISION_MANAGER'] },
        { to: '/kpis', label: 'KPIs', roles: ['ADMIN', 'DIVISION_MANAGER'] },
        { to: '/visual-analytics', label: 'Visual Analytics', roles: ['ADMIN'] },
        { to: '/ratings', label: 'Department Ratings', roles: ['ADMIN', 'DIVISION_MANAGER'] },
        { to: '/settings', label: 'System Settings', roles: ['ADMIN'] },
        { to: '/admin/users', label: 'User Management', roles: ['ADMIN'] },
    ];

    const filteredLinks = navLinks.filter(link => !link.roles || link.roles.includes(user?.role || ''));

    return (
        <div className="app-container">
            {/* Mobile Menu Button */}
            <button
                className="mobile-menu-btn"
                onClick={toggleMobileMenu}
            >
                <svg width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
                    <line x1="3" y1="12" x2="21" y2="12"></line>
                    <line x1="3" y1="6" x2="21" y2="6"></line>
                    <line x1="3" y1="18" x2="21" y2="18"></line>
                </svg>
            </button>

            {/* Mobile Overlay */}
            <div
                className={`mobile-overlay ${mobileMenuOpen ? 'active' : ''}`}
                onClick={closeMobileMenu}
            ></div>

            <div className={`sidebar ${mobileMenuOpen ? 'mobile-open' : ''}`}>
                <div className="sidebar-header">
                    <img src="/tebita-logo-sidebar.png" alt="Tebita" className="sidebar-logo" />
                    <div className="sidebar-text">
                        <div className="sidebar-title">Tebita SLA System</div>
                        <div className="sidebar-subtitle">ጠብታ አምቡላንስ</div>
                    </div>
                </div>

                <nav>
                    <ul className="nav-menu">
                        {filteredLinks.map((link) => (
                            <li key={link.to} className="nav-item">
                                <Link to={link.to} className="nav-link" onClick={closeMobileMenu}>
                                    {link.label}
                                    {link.to === '/requests/inbox' && unreadCount > 0 && (
                                        <span className="notification-badge">{unreadCount}</span>
                                    )}
                                </Link>
                            </li>
                        ))}
                    </ul>
                </nav>

                <div style={{ marginTop: 'auto', paddingTop: '2rem' }}>
                    <div style={{ padding: '1rem', background: 'rgba(255,255,255,0.1)', borderRadius: '12px', marginBottom: '1rem' }}>
                        <div style={{ fontSize: '0.875rem', opacity: 0.9 }}>{user?.full_name}</div>
                        <div style={{ fontSize: '0.75rem', opacity: 0.7 }}>{user?.role}</div>
                    </div>
                    <button onClick={handleLogout} className="btn btn-secondary" style={{ width: '100%' }}>
                        Logout
                    </button>
                </div>
            </div>

            <div className="main-content">
                <Outlet />
            </div>
        </div>
    );
};
