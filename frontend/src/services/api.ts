import axios from 'axios';
import type { User, Request, RequestItem, Division, Department, SubDepartment, FleetRequest, HRDeployment, FinanceTransaction, ICTTicket, LogisticsRequest } from '../types';

// Dynamic API URL detection
const getApiUrl = () => {
    // 1. Prefer environment variable if set
    if (import.meta.env.VITE_API_URL) {
        return import.meta.env.VITE_API_URL;
    }
    // 2. Fallback to current hostname (for local network access)
    // Assumes backend is on port 8000 of the same machine
    return `http://${window.location.hostname}:8000`;
};

const API_BASE = getApiUrl();

const client = axios.create({
    baseURL: API_BASE,
});

const withAuth = (token: string | null) => ({
    headers: { Authorization: `Bearer ${token}` },
});

export const api = {
    // Authentication
    login: async (username: string, password: string) => {
        const body = new URLSearchParams();
        body.append('username', username);
        body.append('password', password);
        const response = await client.post<{ access_token: string }>(
            '/auth/login',
            body,
            { headers: { 'Content-Type': 'application/x-www-form-urlencoded' } }
        );
        return response.data;
    },

    acknowledgeRequest: async (
        token: string,
        id: number,
        notes?: string
    ): Promise<Request> => {
        const response = await client.post<Request>(
            `/requests/${id}/acknowledge`,
            { notes },
            withAuth(token)
        );
        return response.data;
    },

    completeRequest: async (
        token: string,
        id: number,
        notes?: string
    ): Promise<Request> => {
        const response = await client.post<Request>(
            `/requests/${id}/complete`,
            { notes },
            withAuth(token)
        );
        return response.data;
    },

    validateRequestCompletion: async (
        token: string,
        id: number,
        notes?: string
    ): Promise<Request> => {
        const response = await client.post<Request>(
            `/requests/${id}/validate-completion`,
            { notes },
            withAuth(token)
        );
        return response.data;
    },

    getProfile: async (token: string): Promise<User> => {
        const response = await client.get<User>('/auth/me', withAuth(token));
        return response.data;
    },

    getDashboardStats: async (token: string) => {
        const response = await client.get('/api/dashboard/stats', withAuth(token));
        return response.data;
    },

    // Divisions
    getDivisions: async (token: string): Promise<Division[]> => {
        const response = await client.get<Division[]>('/divisions', withAuth(token));
        return response.data;
    },

    // Departments
    getDepartments: async (token: string): Promise<Department[]> => {
        const response = await client.get<Department[]>('/departments', withAuth(token));
        return response.data;
    },

    getSubDepartments: async (token: string, departmentId: number): Promise<SubDepartment[]> => {
        const response = await client.get<SubDepartment[]>(`/departments/${departmentId}/subdepartments`, withAuth(token));
        return response.data;
    },

    // Requests
    getRequests: async (token: string): Promise<Request[]> => {
        const response = await client.get<Request[]>('/requests', withAuth(token));
        return response.data;
    },

    getIncomingRequests: async (token: string): Promise<Request[]> => {
        const response = await client.get<Request[]>('/requests/incoming', withAuth(token));
        return response.data;
    },

    getSentRequests: async (token: string): Promise<Request[]> => {
        const response = await client.get<Request[]>('/requests/sent', withAuth(token));
        return response.data;
    },

    getRequest: async (token: string, id: number): Promise<Request> => {
        const response = await client.get<Request>(`/requests/${id}`, withAuth(token));
        return response.data;
    },

    createRequest: async (
        token: string,
        data: {
            request_type: string;
            resource_type?: string;
            requester_division_id: number;
            requester_department_id?: number;
            requester_subdepartment_id?: number;
            assigned_division_id?: number;
            assigned_department_id?: number;
            assigned_subdepartment_id?: number;
            priority: 'HIGH' | 'MEDIUM' | 'LOW';
            description: string;
            notes?: string;
            sla_response_time_hours?: number;
            sla_completion_time_hours?: number;
            items: RequestItem[];
        }
    ): Promise<Request> => {
        const response = await client.post<Request>('/requests', data, withAuth(token));
        return response.data;
    },

    updateRequestStatus: async (
        token: string,
        id: number,
        status: string
    ): Promise<Request> => {
        const response = await client.patch<Request>(
            `/requests/${id}/status`,
            { status },
            withAuth(token)
        );
        return response.data;
    },

    // M&E Dashboard
    getMEDashboard: async (token: string) => {
        const response = await client.get('/me/dashboard', withAuth(token));
        return response.data;
    },

    // SLA Monitoring
    getSLACompliance: async (token: string) => {
        const response = await client.get('/sla/compliance', withAuth(token));
        return response.data;
    },

    // File Uploads
    uploadItemFile: async (token: string, formData: FormData) => {
        const response = await client.post<{
            filename: string;
            saved_filename: string;
            path: string;
            type: string;
            size: number;
        }>('/uploads/item-file', formData, {
            headers: {
                ...withAuth(token).headers,
                'Content-Type': 'multipart/form-data',
            },
        });
        return response.data;
    },

    downloadItemFile: async (token: string, filename: string) => {
        const response = await client.get(`/uploads/item-file/${filename}`, {
            ...withAuth(token),
            responseType: 'blob',
        });

        // Create download link
        const url = window.URL.createObjectURL(response.data);
        const link = document.createElement('a');
        link.href = url;
        link.download = filename;
        document.body.appendChild(link);
        link.click();
        document.body.removeChild(link);
        window.URL.revokeObjectURL(url);
    },

    getSLADashboard: async (token: string) => {
        const response = await client.get('/sla/dashboard', withAuth(token));
        return response.data;
    },

    getSLAAlerts: async (token: string) => {
        const response = await client.get('/sla/alerts', withAuth(token));
        return response.data;
    },

    // KPIs
    getKPIDashboard: async (token: string) => {
        const response = await client.get('/kpis/dashboard', withAuth(token));
        return response.data;
    },

    getKPIMetrics: async (token: string, period?: string) => {
        const response = await client.get(
            `/kpis/metrics${period ? `?period=${period}` : ''}`,
            withAuth(token)
        );
        return response.data;
    },

    getScorecard: async (token: string, period?: string) => {
        const response = await client.get(
            `/kpis/scorecard${period ? `?period=${period}` : ''}`,
            withAuth(token)
        );
        return response.data;
    },

    downloadRequestActivityLog: async (token: string): Promise<Blob> => {
        const response = await client.get('/requests/activity/export', {
            ...withAuth(token),
            responseType: 'blob',
        });
        return response.data;
    },

    // Role-Based Dashboards
    getAdminDashboard: async (token: string) => {
        const response = await client.get('/dashboard/admin', withAuth(token));
        return response.data;
    },

    getDivisionDashboard: async (token: string) => {
        const response = await client.get('/dashboard/division-manager', withAuth(token));
        return response.data;
    },

    getDepartmentDashboard: async (token: string) => {
        const response = await client.get('/dashboard/department-head', withAuth(token));
        return response.data;
    },

    getStaffDashboard: async (token: string) => {
        const response = await client.get('/dashboard/staff', withAuth(token));
        return response.data;
    },

    // Admin users management
    getUsers: async (token: string) => {
        const response = await client.get('/admin/users', withAuth(token));
        return response.data;
    },

    createUser: async (token: string, data: any) => {
        const response = await client.post('/admin/users', data, withAuth(token));
        return response.data;
    },

    updateUser: async (token: string, id: number, data: any) => {
        const response = await client.put(`/admin/users/${id}`, data, withAuth(token));
        return response.data;
    },

    deleteUser: async (token: string, id: number) => {
        const response = await client.delete(`/admin/users/${id}`, withAuth(token));
        return response.data;
    },

    // Request actions

    // Resource Management (Phase 2)
    // Fleet
    createFleetDetails: async (token: string, requestId: number, data: any): Promise<FleetRequest> => {
        const response = await client.post<FleetRequest>(`/requests/${requestId}/fleet-details`, data, withAuth(token));
        return response.data;
    },

    getFleetDetails: async (token: string, requestId: number): Promise<FleetRequest> => {
        const response = await client.get<FleetRequest>(`/requests/${requestId}/fleet-details`, withAuth(token));
        return response.data;
    },

    updateFleetDetails: async (token: string, requestId: number, data: any): Promise<FleetRequest> => {
        const response = await client.patch<FleetRequest>(`/requests/${requestId}/fleet-details`, data, withAuth(token));
        return response.data;
    },

    // HR
    createHRDetails: async (token: string, requestId: number, data: any): Promise<HRDeployment> => {
        const response = await client.post<HRDeployment>(`/requests/${requestId}/hr-details`, data, withAuth(token));
        return response.data;
    },

    getHRDetails: async (token: string, requestId: number): Promise<HRDeployment> => {
        const response = await client.get<HRDeployment>(`/requests/${requestId}/hr-details`, withAuth(token));
        return response.data;
    },

    updateHRDetails: async (token: string, requestId: number, data: any): Promise<HRDeployment> => {
        const response = await client.patch<HRDeployment>(`/requests/${requestId}/hr-details`, data, withAuth(token));
        return response.data;
    },

    // Finance
    createFinanceDetails: async (token: string, requestId: number, data: any): Promise<FinanceTransaction> => {
        const response = await client.post<FinanceTransaction>(`/requests/${requestId}/finance-details`, data, withAuth(token));
        return response.data;
    },

    getFinanceDetails: async (token: string, requestId: number): Promise<FinanceTransaction> => {
        const response = await client.get<FinanceTransaction>(`/requests/${requestId}/finance-details`, withAuth(token));
        return response.data;
    },

    updateFinanceDetails: async (token: string, requestId: number, data: any): Promise<FinanceTransaction> => {
        const response = await client.patch<FinanceTransaction>(`/requests/${requestId}/finance-details`, data, withAuth(token));
        return response.data;
    },

    // ICT
    createICTDetails: async (token: string, requestId: number, data: any): Promise<ICTTicket> => {
        const response = await client.post<ICTTicket>(`/requests/${requestId}/ict-details`, data, withAuth(token));
        return response.data;
    },

    getICTDetails: async (token: string, requestId: number): Promise<ICTTicket> => {
        const response = await client.get<ICTTicket>(`/requests/${requestId}/ict-details`, withAuth(token));
        return response.data;
    },

    updateICTDetails: async (token: string, requestId: number, data: any): Promise<ICTTicket> => {
        const response = await client.patch<ICTTicket>(`/requests/${requestId}/ict-details`, data, withAuth(token));
        return response.data;
    },

    // Logistics
    createLogisticsDetails: async (token: string, requestId: number, data: any): Promise<LogisticsRequest> => {
        const response = await client.post<LogisticsRequest>(`/requests/${requestId}/logistics-details`, data, withAuth(token));
        return response.data;
    },

    getLogisticsDetails: async (token: string, requestId: number): Promise<LogisticsRequest> => {
        const response = await client.get<LogisticsRequest>(`/requests/${requestId}/logistics-details`, withAuth(token));
        return response.data;
    },

    updateLogisticsDetails: async (token: string, requestId: number, data: any): Promise<LogisticsRequest> => {
        const response = await client.patch<LogisticsRequest>(`/requests/${requestId}/logistics-details`, data, withAuth(token));
        return response.data;
    },


    // Organization structure management
    createDepartment: async (token: string, data: { name: string; division_id: number; description?: string }): Promise<Department> => {
        const response = await client.post<Department>('/departments', data, withAuth(token));
        return response.data;
    },

    createSubDepartment: async (token: string, departmentId: number, data: { name: string; description?: string }): Promise<SubDepartment> => {
        const response = await client.post<SubDepartment>(`/departments/${departmentId}/subdepartments`, data, withAuth(token));
        return response.data;
    },
    getRealTimeKPIs: async (token: string, departmentId?: number) => {
        const params = departmentId ? { department_id: departmentId } : {};
        const response = await client.get('/kpis/realtime', { ...withAuth(token), params });
        return response.data;
    },

    // Analytics & Reporting
    downloadScorecard: async (token: string, days: number = 30) => {
        const response = await client.get('/analytics/scorecard/export', {
            ...withAuth(token),
            params: { days },
            responseType: 'blob'
        });
        return response.data;
    },

    exportRequestLogs: async (token: string, days: number = 30) => {
        const response = await client.get('/analytics/requests/export', {
            ...withAuth(token),
            params: { days },
            responseType: 'blob'
        });
        return response.data;
    },

    // Satisfaction Ratings
    submitRating: async (token: string, requestId: number, rating: any) => {
        const response = await client.post(`/satisfaction/requests/${requestId}/rate`, rating, withAuth(token));
        return response.data;
    },

    getRating: async (token: string, requestId: number) => {
        const response = await client.get(`/satisfaction/requests/${requestId}`, withAuth(token));
        return response.data;
    },

    getDepartmentRatingStats: async (token: string, departmentId: number) => {
        const response = await client.get(`/satisfaction/department/${departmentId}/stats`, withAuth(token));
        return response.data;
    },

    getMyRatings: async (token: string) => {
        const response = await client.get('/satisfaction/my-ratings', withAuth(token));
        return response.data;
    },

    getAllDepartmentsRatingAnalytics: async (token: string) => {
        const response = await client.get('/satisfaction/analytics/all-departments', withAuth(token));
        return response.data;
    },

    // System Settings
    getEmailNotificationStatus: async (token: string) => {
        const response = await client.get('/settings/email-notifications/status', withAuth(token));
        return response.data;
    },

    updateEmailNotifications: async (token: string, enabled: boolean) => {
        const response = await client.put(`/settings/email-notifications?enabled=${enabled}`, {}, withAuth(token));
        return response.data;
    },
};
