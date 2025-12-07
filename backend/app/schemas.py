from pydantic import BaseModel, Field
from typing import Optional, List
from datetime import datetime
from decimal import Decimal

from .models import UserRole, DivisionType, RequestStatus, Priority, WorkflowStep, AlertType, ScoreRating, ResourceType


# Dashboard Schemas
class DashboardStats(BaseModel):
    total_requests: int
    pending_approval: int
    in_progress: int
    completed: int
    overdue: int
    sla_compliance: float
    active_alerts: int


# User Schemas
class UserBase(BaseModel):
    username: str
    full_name: str
    email: Optional[str] = None
    phone: Optional[str] = None


class UserCreate(UserBase):
    password: str
    role: UserRole
    division_id: Optional[int] = None
    department_id: Optional[int] = None
    subdepartment_id: Optional[int] = None
    is_active: bool = True


class UserUpdate(BaseModel):
    full_name: Optional[str] = None
    email: Optional[str] = None
    password: Optional[str] = None
    role: Optional[UserRole] = None
    division_id: Optional[int] = None
    department_id: Optional[int] = None
    subdepartment_id: Optional[int] = None
    is_active: Optional[bool] = None


class UserRead(UserBase):
    id: int
    role: UserRole
    division_id: Optional[int]
    department_id: Optional[int]
    subdepartment_id: Optional[int]
    is_active: bool
    created_at: datetime

    class Config:
        from_attributes = True


class UserBasic(BaseModel):
    """Minimal user info for nested responses"""
    id: int
    username: str
    full_name: str
    email: Optional[str]

    class Config:
        from_attributes = True


# Division Schemas
class DivisionBase(BaseModel):
    name: str
    type: DivisionType
    description: Optional[str] = None


class DivisionCreate(DivisionBase):
    pass


class DivisionRead(DivisionBase):
    id: int
    created_at: datetime

    class Config:
        from_attributes = True


# Department Schemas
class DepartmentBase(BaseModel):
    name: str
    division_id: int
    description: Optional[str] = None


class DepartmentCreate(DepartmentBase):
    pass


class DepartmentRead(DepartmentBase):
    id: int
    created_at: datetime

    class Config:
        from_attributes = True


# SubDepartment Schemas
class SubDepartmentBase(BaseModel):
    name: str
    department_id: int
    description: Optional[str] = None


class SubDepartmentCreate(SubDepartmentBase):
    pass


class SubDepartmentRead(SubDepartmentBase):
    id: int
    created_at: datetime

    class Config:
        from_attributes = True


# Request Item Schemas
class RequestItemBase(BaseModel):
    item_description: str
    quantity: Optional[Decimal] = None
    unit_price: Optional[Decimal] = None
    expected_delivery_date: Optional[datetime] = None
    notes: Optional[str] = None
    custom_fields: Optional[dict] = None
    
    # File attachment fields
    attachment_filename: Optional[str] = None
    attachment_path: Optional[str] = None
    attachment_type: Optional[str] = None


class RequestItemCreate(RequestItemBase):
    pass


class RequestItemRead(RequestItemBase):
    id: int

    class Config:
        from_attributes = True


# Request Schemas
class RequestBase(BaseModel):
    request_type: str
    resource_type: ResourceType = ResourceType.GENERAL
    requester_division_id: int
    requester_department_id: Optional[int] = None
    requester_subdepartment_id: Optional[int] = None
    assigned_division_id: Optional[int] = None
    assigned_department_id: Optional[int] = None
    assigned_subdepartment_id: Optional[int] = None
    priority: Priority = Priority.MEDIUM
    description: str
    notes: Optional[str] = None
    sla_response_time_hours: Optional[int] = None
    sla_completion_time_hours: Optional[int] = None
    cost_estimate: Optional[Decimal] = None
    actual_cost: Optional[Decimal] = None


class RequestCreate(RequestBase):
    items: List[RequestItemCreate] = []


class RequestRead(RequestBase):
    id: int
    request_id: str
    requester_id: int
    assigned_to_user_id: Optional[int]
    status: RequestStatus
    created_at: datetime
    submitted_at: Optional[datetime]
    approved_at: Optional[datetime]
    started_at: Optional[datetime]
    completed_at: Optional[datetime]
    
    # Acknowledgement fields
    acknowledged_at: Optional[datetime] = None
    acknowledged_by_user_id: Optional[int] = None
    
    # Validation fields
    completion_validated_at: Optional[datetime] = None
    completion_validated_by_user_id: Optional[int] = None
    
    # Enhanced SLA tracking
    sla_response_deadline: Optional[datetime] = None
    sla_completion_deadline: Optional[datetime] = None
    actual_response_time: Optional[datetime] = None
    actual_completion_time: Optional[datetime] = None
    reason_for_delay: Optional[str] = None
    
    # Customer satisfaction
    satisfaction_rating: Optional[int] = Field(None, ge=1, le=5)
    satisfaction_comment: Optional[str] = None
    
    # Nested relationship data for sender/recipient display
    requester: Optional[UserRead] = None
    requester_division: Optional[DivisionRead] = None
    requester_department: Optional[DepartmentRead] = None
    requester_subdepartment: Optional[SubDepartmentRead] = None
    assigned_division: Optional[DivisionRead] = None
    assigned_department: Optional[DepartmentRead] = None
    assigned_subdepartment: Optional[SubDepartmentRead] = None
    
    items: List[RequestItemRead] = []

    class Config:
        from_attributes = True



# Workflow Schemas
class WorkflowCreate(BaseModel):
    step: WorkflowStep
    notes: Optional[str] = None
    attachments: Optional[dict] = None


class WorkflowRead(BaseModel):
    id: int
    request_id: int
    step: WorkflowStep
    performed_by_user_id: int
    performed_at: datetime
    notes: Optional[str]

    class Config:
        from_attributes = True


# Satisfaction Schemas
class SatisfactionCreate(BaseModel):
    timeliness_score: int = Field(ge=1, le=5)
    quality_score: int = Field(ge=1, le=5)
    communication_score: int = Field(ge=1, le=5)
    professionalism_score: int = Field(ge=1, le=5)
    overall_score: int = Field(ge=1, le=5)
    comments: Optional[str] = None


class SatisfactionRead(SatisfactionCreate):
    id: int
    request_id: int
    submitted_at: datetime

    class Config:
        from_attributes = True


# KPI Schemas
class KPIMetricCreate(BaseModel):
    metric_name: str
    metric_type: str
    department_id: Optional[int] = None
    division_id: Optional[int] = None
    target_value: Optional[Decimal] = None
    actual_value: Optional[Decimal] = None
    period: str


class KPIMetricRead(KPIMetricCreate):
    id: int
    recorded_at: datetime
    calculated_at: Optional[datetime]

    class Config:
        from_attributes = True


# Scorecard Schemas
class ScorecardRead(BaseModel):
    id: int
    period_start: datetime
    period_end: datetime
    division_id: Optional[int]
    department_id: Optional[int]
    service_efficiency_score: Decimal
    compliance_score: Decimal
    cost_optimization_score: Decimal
    satisfaction_score: Decimal
    total_score: Decimal
    rating: ScoreRating
    created_at: datetime

    class Config:
        from_attributes = True


# Auth Schemas
class Token(BaseModel):
    access_token: str
    token_type: str


class TokenData(BaseModel):
    username: Optional[str] = None



class SatisfactionSubmit(BaseModel):
    rating: int = Field(..., ge=1, le=5)
    comment: Optional[str] = None


# ============================================================================
# RESOURCE-SPECIFIC SCHEMAS (Phase 2)
# ============================================================================

# Fleet Request Schemas
class FleetRequestBase(BaseModel):
    vehicle_assigned: Optional[str] = None
    driver_assigned: Optional[str] = None
    dispatch_time: Optional[datetime] = None
    return_time: Optional[datetime] = None
    fuel_used: Optional[float] = None
    km_traveled: Optional[float] = None
    trip_completed: bool = False
    breakdown_occurred: bool = False


class FleetRequestCreate(FleetRequestBase):
    pass


class FleetRequestUpdate(BaseModel):
    vehicle_assigned: Optional[str] = None
    driver_assigned: Optional[str] = None
    dispatch_time: Optional[datetime] = None
    return_time: Optional[datetime] = None
    fuel_used: Optional[float] = None
    km_traveled: Optional[float] = None
    trip_completed: Optional[bool] = None
    breakdown_occurred: Optional[bool] = None


class FleetRequestRead(FleetRequestBase):
    id: int
    request_id: int
    created_at: datetime

    class Config:
        from_attributes = True


# HR Deployment Schemas
class HRDeploymentBase(BaseModel):
    staff_assigned: Optional[str] = None
    competency_required: Optional[str] = None
    deployment_duration_days: Optional[int] = None
    actual_start_date: Optional[datetime] = None
    actual_end_date: Optional[datetime] = None
    overtime_hours: Optional[float] = None
    deployment_filled: bool = False


class HRDeploymentCreate(HRDeploymentBase):
    pass


class HRDeploymentUpdate(BaseModel):
    staff_assigned: Optional[str] = None
    competency_required: Optional[str] = None
    deployment_duration_days: Optional[int] = None
    actual_start_date: Optional[datetime] = None
    actual_end_date: Optional[datetime] = None
    overtime_hours: Optional[float] = None
    deployment_filled: Optional[bool] = None


class HRDeploymentRead(HRDeploymentBase):
    id: int
    request_id: int
    created_at: datetime

    class Config:
        from_attributes = True


# Finance Transaction Schemas
class FinanceTransactionBase(BaseModel):
    transaction_type: Optional[str] = None  # vendor, payroll, tax, etc.
    amount: Optional[Decimal] = None
    processing_officer: Optional[str] = None
    supporting_docs_complete: bool = False
    document_completeness_score: Optional[int] = Field(None, ge=0, le=100)
    complies_with_finance_sop: bool = True
    payment_accuracy: bool = True
    date_received: Optional[datetime] = None
    date_processed: Optional[datetime] = None


class FinanceTransactionCreate(FinanceTransactionBase):
    pass


class FinanceTransactionUpdate(BaseModel):
    transaction_type: Optional[str] = None
    amount: Optional[Decimal] = None
    processing_officer: Optional[str] = None
    supporting_docs_complete: Optional[bool] = None
    document_completeness_score: Optional[int] = Field(None, ge=0, le=100)
    complies_with_finance_sop: Optional[bool] = None
    payment_accuracy: Optional[bool] = None
    date_received: Optional[datetime] = None
    date_processed: Optional[datetime] = None


class FinanceTransactionRead(FinanceTransactionBase):
    id: int
    request_id: int
    created_at: datetime

    class Config:
        from_attributes = True


# ICT Ticket Schemas
class ICTTicketBase(BaseModel):
    ticket_number: Optional[str] = None
    problem_type: Optional[str] = None
    severity: Optional[str] = None
    technician_assigned: Optional[str] = None
    resolution_time_minutes: Optional[int] = None
    escalated: bool = False
    reopened: bool = False
    system_downtime_minutes: Optional[int] = None


class ICTTicketCreate(ICTTicketBase):
    pass


class ICTTicketUpdate(BaseModel):
    ticket_number: Optional[str] = None
    problem_type: Optional[str] = None
    severity: Optional[str] = None
    technician_assigned: Optional[str] = None
    resolution_time_minutes: Optional[int] = None
    escalated: Optional[bool] = None
    reopened: Optional[bool] = None
    system_downtime_minutes: Optional[int] = None


class ICTTicketRead(ICTTicketBase):
    id: int
    request_id: int
    created_at: datetime

    class Config:
        from_attributes = True


# Logistics Request Schemas
class LogisticsRequestBase(BaseModel):
    item_requested: Optional[str] = None
    quantity_requested: Optional[float] = None
    quantity_delivered: Optional[float] = None
    stock_available: bool = True
    delivery_time_days: Optional[int] = None
    lead_time_days: Optional[int] = None
    requisition_accurate: bool = True
    documentation_complete: bool = True
    cost_per_item: Optional[Decimal] = None


class LogisticsRequestCreate(LogisticsRequestBase):
    pass


class LogisticsRequestUpdate(BaseModel):
    item_requested: Optional[str] = None
    quantity_requested: Optional[float] = None
    quantity_delivered: Optional[float] = None
    stock_available: Optional[bool] = None
    delivery_time_days: Optional[int] = None
    lead_time_days: Optional[int] = None
    requisition_accurate: Optional[bool] = None
    documentation_complete: Optional[bool] = None
    cost_per_item: Optional[Decimal] = None


class LogisticsRequestRead(LogisticsRequestBase):
    id: int
    request_id: int
    created_at: datetime

    class Config:
        from_attributes = True


# ============================================================================
# Customer Satisfaction / Rating Schemas
# ============================================================================

class SatisfactionRatingCreate(BaseModel):
    """Schema for submitting a rating (requester rates fulfilling department)"""
    timeliness_score: int = Field(..., ge=1, le=5, description="How quickly was the request fulfilled?")
    quality_score: int = Field(..., ge=1, le=5, description="How well was the work done?")
    communication_score: int = Field(..., ge=1, le=5, description="How well did they communicate?")
    professionalism_score: int = Field(..., ge=1, le=5, description="How professional was the interaction?")
    overall_score: int = Field(..., ge=1, le=5, description="Overall satisfaction")
    comments: Optional[str] = Field(None, max_length=1000, description="Optional feedback")


class SatisfactionRatingResponse(BaseModel):
    """Schema for displaying a rating"""
    id: int
    request_id: int
    timeliness_score: int
    quality_score: int
    communication_score: int
    professionalism_score: int
    overall_score: int
    comments: Optional[str]
    submitted_at: datetime
    submitted_by: UserBasic

    class Config:
        from_attributes = True


class DepartmentRatingStats(BaseModel):
    """Aggregate rating statistics for a department"""
    department_id: int
    department_name: str
    total_ratings: int
    average_overall: float
    average_timeliness: float
    average_quality: float
    average_communication: float
    average_professionalism: float
    rating_distribution: dict  # e.g., {"5": 10, "4": 5, "3": 2, "2": 1, "1": 0}

