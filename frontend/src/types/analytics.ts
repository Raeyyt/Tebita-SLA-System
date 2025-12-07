// M&E Analytics Types
export type ResourceType = 'FLEET' | 'HR' | 'FINANCE' | 'ICT' | 'LOGISTICS' | 'FACILITIES' | 'GENERAL';
export type ScoreRating = 'OUTSTANDING' | 'VERY_GOOD' | 'GOOD' | 'NEEDS_IMPROVEMENT' | 'UNSATISFACTORY';

// Analytics API Response Types
export interface GeneralKPIs {
    sla_compliance_rate: number;
    service_fulfillment_rate: number;
    customer_satisfaction_score: number;
}

export interface FleetKPIs {
    vehicle_utilization_rate: number;
    trip_completion_rate: number;
    average_turnaround_time_hours: number;
    fuel_efficiency_km_per_liter: number;
    breakdown_frequency: number;
}

export interface HRKPIs {
    deployment_filling_rate: number;
    deployment_response_time_hours: number;
    overtime_usage_rate: number;
}

export interface FinanceKPIs {
    payment_processing_turnaround_days: number;
    payment_accuracy_rate: number;
    document_completeness_rate: number;
}

export interface ICT_KPIs {
    ticket_resolution_rate: number;
    average_response_time_hours: number;
    reopened_tickets_rate: number;
}

export interface LogisticsKPIs {
    on_time_delivery_rate: number;
    stock_fulfillment_rate: number;
    requisition_accuracy: number;
}

export interface ScorecardBreakdown {
    score: number;
    weight: string;
    components: string[];
}

export interface ScorecardResponse {
    period?: string;
    division_id?: number;
    department_id?: number;
    service_efficiency_score: number;
    compliance_score: number;
    cost_optimization_score: number;
    satisfaction_score: number;
    total_score: number;
    rating: ScoreRating;
    breakdown: {
        service_efficiency: ScorecardBreakdown;
        compliance: ScorecardBreakdown;
        cost_optimization: ScorecardBreakdown;
        satisfaction: ScorecardBreakdown;
    };
}

export interface IntegrationIndexResponse {
    period?: string;
    division_id?: number;
    integration_index: number;
    components: {
        coordination_effectiveness: number;
        process_alignment: number;
        reporting_timeliness: number;
        collaboration_score: number;
    };
}

export interface ComprehensiveDashboard {
    period: {
        start_date: string;
        end_date: string;
        days: number;
    };
    general_kpis: GeneralKPIs;
    resource_kpis: {
        fleet: FleetKPIs;
        hr: HRKPIs;
        finance: FinanceKPIs;
        ict: ICT_KPIs;
        logistics: LogisticsKPIs;
    };
    scorecard: ScorecardResponse;
    integration_index: IntegrationIndexResponse;
}
