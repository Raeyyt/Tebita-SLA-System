import { BrowserRouter, Routes, Route, Navigate } from 'react-router-dom';
import { AuthProvider } from './contexts/AuthContext';
import { ProtectedRoute } from './components/ProtectedRoute';
import { AppLayout } from './layout/AppLayout';
import { LoginPage } from './pages/LoginPage';
import { DashboardPage } from './pages/DashboardPage';
import { RequestsPage } from './pages/RequestsPage';
import { RequestViewPage } from './pages/RequestViewPage';
import { NewRequestPage } from './pages/NewRequestPage';
import { RequestInboxPage } from './pages/RequestInboxPage';
import { SentRequestsPage } from './pages/SentRequestsPage';
import { MEDashboardPage } from './pages/MEDashboardPage';
import { SLAMonitorPage } from './pages/SLAMonitorPage';
import { KPIsPage } from './pages/KPIsPage';
import { ScorecardsPage } from './pages/ScorecardsPage';
import { AnalyticsDashboardPage } from './pages/AnalyticsDashboardPage';
import { AdminDashboardPage } from './pages/AdminDashboardPage';
import UserManagement from './pages/admin/UserManagement';
import { DivisionDashboardPage } from './pages/DivisionDashboardPage';
import { DepartmentDashboardPage } from './pages/DepartmentDashboardPage';
import { StaffDashboardPage } from './pages/StaffDashboardPage';
import { DepartmentRatingsPage } from './pages/DepartmentRatingsPage';
import { SystemSettingsPage } from './pages/SystemSettingsPage';
import './index.css';

function App() {
  return (
    <BrowserRouter>
      <AuthProvider>
        <Routes>
          <Route path="/login" element={<LoginPage />} />

          <Route element={
            <ProtectedRoute>
              <AppLayout />
            </ProtectedRoute>
          }>
            <Route index element={<DashboardPage />} />

            {/* Role-Based Dashboards */}
            <Route path="dashboard/admin" element={<AdminDashboardPage />} />
            <Route path="dashboard/division" element={<DivisionDashboardPage />} />
            <Route path="dashboard/department" element={<DepartmentDashboardPage />} />
            <Route path="dashboard/staff" element={<StaffDashboardPage />} />

            <Route path="requests" element={<RequestsPage />} />
            <Route path="requests/inbox" element={<RequestInboxPage />} />
            <Route path="requests/sent" element={<SentRequestsPage />} />
            <Route path="requests/new" element={<NewRequestPage />} />
            <Route path="requests/:id" element={<RequestViewPage />} />
            <Route path="me-dashboard" element={<MEDashboardPage />} />
            <Route path="sla-monitor" element={<SLAMonitorPage />} />
            <Route path="kpis" element={<KPIsPage />} />
            <Route path="scorecards" element={<ScorecardsPage />} />
            <Route path="analytics" element={<AnalyticsDashboardPage />} />  {/* Phase 4: Comprehensive Analytics */}
            <Route path="ratings" element={<DepartmentRatingsPage />} />  {/* Department Ratings Analytics */}
            <Route path="settings" element={<SystemSettingsPage />} />  {/* System Settings */}
            <Route path="admin/users" element={<UserManagement />} />
            <Route path="reports" element={<div className="card"><h2>Reports - Coming Soon</h2></div>} />
          </Route>

          <Route path="*" element={<Navigate to="/" replace />} />
        </Routes>
      </AuthProvider>
    </BrowserRouter>
  );
}

export default App;
