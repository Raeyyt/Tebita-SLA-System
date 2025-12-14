export type UserRole = 'ADMIN' | 'DIVISION_MANAGER' | 'DEPARTMENT_HEAD' | 'SUB_DEPARTMENT_STAFF';
export type DivisionType = 'INCOME_GENERATING' | 'SUPPORT';
export type RequestStatus = 'PENDING' | 'APPROVAL_PENDING' | 'APPROVED' | 'IN_PROGRESS' | 'COMPLETED' | 'REJECTED' | 'CANCELLED';
export type Priority = 'HIGH' | 'MEDIUM' | 'LOW';

export interface User {
    id: number;
    username: string;
    full_name: string;
    email?: string;
    phone?: string;
    role: UserRole;
    division_id?: number;
    department_id?: number;
    subdepartment_id?: number;
    is_active: boolean;
    created_at: string;
}

export interface Division {
    id: number;
    name: string;
    type: DivisionType;
    description?: string;
    created_at: string;
}

export interface Department {
    id: number;
    name: string;
    division_id: number;
    description?: string;
    created_at: string;
    subdepartments?: SubDepartment[];
}

export interface SubDepartment {
    id: number;
    name: string;
    department_id: number;
    description?: string;
    created_at: string;
}

export interface RequestItem {
    id?: number;
    item_description: string;
    quantity?: number;
    unit_price?: number;
    expected_delivery_date?: string;
    notes?: string;
    custom_fields?: Record<string, any>;
    attachment_filename?: string;
}

export interface Request {
    id: number;
    request_id: string;
    request_type: string;
    resource_type?: string;
    requester_id: number;
    requester_division_id: number;
    requester_department_id?: number;
    requester_subdepartment_id?: number;
    assigned_division_id?: number;
    assigned_department_id?: number;
    assigned_subdepartment_id?: number;
    assigned_to_user_id?: number;
    priority: Priority;
    status: RequestStatus;
    sla_response_time_hours?: number;
    sla_completion_time_hours?: number;
    actual_response_time?: string;
    actual_completion_time?: string;
    created_at: string;
    submitted_at?: string;
    approved_at?: string;
    started_at?: string;
    completed_at?: string;
    acknowledged_at?: string;
    acknowledged_by_user_id?: number;
    completion_validated_at?: string;
    completion_validated_by_user_id?: number;
    description: string;
    notes?: string;
    attachments?: any;
    items?: RequestItem[];
    rejection_reason?: string;

    // Nested relationship data for sender/recipient display
    requester?: User;
    requester_division?: Division;
    requester_department?: Department;
    requester_subdepartment?: SubDepartment;
    assigned_division?: Division;
    assigned_department?: Department;
    assigned_subdepartment?: SubDepartment;
}

export interface KPIMetric {
    id: number;
    metric_name: string;
    metric_type: string;
    target_value?: number;
    actual_value?: number;
    period: string;
    recorded_at: string;
}

export interface Scorecard {
    id: number;
    period_start: string;
    period_end: string;
    division_id?: number;
    department_id?: number;
    service_efficiency_score: number;
    compliance_score: number;
    cost_optimization_score: number;
    satisfaction_score: number;
    total_score: number;
    rating: string;
    created_at: string;
}

// Resource-Specific Interfaces
export interface FleetRequest {
    id: number;
    request_id: number;
    vehicle_assigned?: string;
    driver_assigned?: string;
    dispatch_time?: string;
    return_time?: string;
    fuel_used?: number;
    km_traveled?: number;
    trip_completed: boolean;
    breakdown_occurred: boolean;
    created_at: string;
}

export interface HRDeployment {
    id: number;
    request_id: number;
    staff_assigned?: string;
    competency_required?: string;
    deployment_duration_days?: number;
    actual_start_date?: string;
    actual_end_date?: string;
    overtime_hours?: number;
    deployment_filled: boolean;
    created_at: string;
}

export interface FinanceTransaction {
    id: number;
    request_id: number;
    transaction_type?: string;
    amount?: number;
    processing_officer?: string;
    supporting_docs_complete: boolean;
    document_completeness_score?: number;
    complies_with_finance_sop: boolean;
    payment_accuracy: boolean;
    date_received?: string;
    date_processed?: string;
    created_at: string;
}

export interface ICTTicket {
    id: number;
    request_id: number;
    ticket_number?: string;
    problem_type?: string;
    severity?: string;
    technician_assigned?: string;
    resolution_time_minutes?: number;
    escalated: boolean;
    reopened: boolean;
    system_downtime_minutes?: number;
    created_at: string;
}

export interface LogisticsRequest {
    id: number;
    request_id: number;
    item_requested?: string;
    quantity_requested?: number;
    quantity_delivered?: number;
    stock_available: boolean;
    delivery_time_days?: number;
    lead_time_days?: number;
    requisition_accurate: boolean;
    documentation_complete: boolean;
    cost_per_item?: number;
    created_at: string;
}
