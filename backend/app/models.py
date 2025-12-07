from sqlalchemy import Column, Integer, String, Boolean, ForeignKey, DateTime, Enum as SQLEnum, Text, Numeric, JSON, Float
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from datetime import datetime
import enum

from .database import Base


# Enums
class UserRole(str, enum.Enum):
    ADMIN = "ADMIN"  # Level 1: Full access
    DIVISION_MANAGER = "DIVISION_MANAGER"  # Level 2: Division oversight
    DEPARTMENT_HEAD = "DEPARTMENT_HEAD"  # Level 3: Department management
    SUB_DEPARTMENT_STAFF = "SUB_DEPARTMENT_STAFF"  # Level 4: Request handling only


class DivisionType(str, enum.Enum):
    INCOME_GENERATING = "INCOME_GENERATING"
    SUPPORT = "SUPPORT"


class RequestStatus(str, enum.Enum):
    PENDING = "PENDING"
    APPROVAL_PENDING = "APPROVAL_PENDING"
    APPROVED = "APPROVED"
    IN_PROGRESS = "IN_PROGRESS"
    COMPLETED = "COMPLETED"
    REJECTED = "REJECTED"
    CANCELLED = "CANCELLED"


class Priority(str, enum.Enum):
    HIGH = "HIGH"
    MEDIUM = "MEDIUM"
    LOW = "LOW"


class ResourceType(str, enum.Enum):
    """Type of shared resource being requested"""
    FLEET = "FLEET"  # Vehicle/transport requests
    HR = "HR"  # Staff deployment, recruitment
    FINANCE = "FINANCE"  # Payments, reimbursements, budget
    ICT = "ICT"  # IT support, systems, infrastructure
    LOGISTICS = "LOGISTICS"  # Supplies, equipment, procurement
    FACILITIES = "FACILITIES"  # Building, maintenance, utilities
    GENERAL = "GENERAL"  # Other/uncategorized requests


class WorkflowStep(str, enum.Enum):
    SUBMITTED = "SUBMITTED"
    APPROVAL_PENDING = "APPROVAL_PENDING"
    APPROVED = "APPROVED"
    REJECTED = "REJECTED"
    DEPLOYED = "DEPLOYED"
    COMPLETED = "COMPLETED"
    RECEIVED = "RECEIVED"
    VALIDATED = "VALIDATED"


class RequestActivityAction(str, enum.Enum):
    SENT = "SENT"
    RECEIVED = "RECEIVED"


class AlertType(str, enum.Enum):
    PERCENT_50 = "50_PERCENT"
    PERCENT_80 = "80_PERCENT"
    OVERDUE = "OVERDUE"


class ScoreRating(str, enum.Enum):
    OUTSTANDING = "OUTSTANDING"
    VERY_GOOD = "VERY_GOOD"
    GOOD = "GOOD"
    NEEDS_IMPROVEMENT = "NEEDS_IMPROVEMENT"
    UNSATISFACTORY = "UNSATISFACTORY"


# Models
class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    username = Column(String(100), unique=True, nullable=False, index=True)
    full_name = Column(String(200), nullable=False)
    email = Column(String(255), nullable=True, index=True)
    phone = Column(String(20))
    hashed_password = Column(String(255), nullable=False)
    role = Column(SQLEnum(UserRole), nullable=False)
    division_id = Column(Integer, ForeignKey("divisions.id"))
    department_id = Column(Integer, ForeignKey("departments.id"))
    subdepartment_id = Column(Integer, ForeignKey("subdepartments.id"))
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    # Relationships
    division = relationship("Division", back_populates="users")
    department = relationship("Department", back_populates="users")
    subdepartment = relationship("SubDepartment", back_populates="users")
    requests_created = relationship("Request", foreign_keys="Request.requester_id", back_populates="requester")
    requests_assigned = relationship("Request", foreign_keys="Request.assigned_to_user_id", back_populates="assigned_to")


class Division(Base):
    __tablename__ = "divisions"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(200), unique=True, nullable=False)
    type = Column(SQLEnum(DivisionType), nullable=False)
    description = Column(Text)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    # Relationships
    users = relationship("User", back_populates="division")
    departments = relationship("Department", back_populates="division")
    requests_from = relationship("Request", foreign_keys="Request.requester_division_id", back_populates="requester_division")
    requests_to = relationship("Request", foreign_keys="Request.assigned_division_id", back_populates="assigned_division")


class Department(Base):
    __tablename__ = "departments"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(200), nullable=False)
    division_id = Column(Integer, ForeignKey("divisions.id"), nullable=False)
    description = Column(Text)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    # Relationships
    division = relationship("Division", back_populates="departments")
    subdepartments = relationship("SubDepartment", back_populates="department", cascade="all, delete-orphan")
    users = relationship("User", back_populates="department")
    requests_from = relationship("Request", foreign_keys="Request.requester_department_id", back_populates="requester_department")
    requests_to = relationship("Request", foreign_keys="Request.assigned_department_id", back_populates="assigned_department")


class SubDepartment(Base):
    __tablename__ = "subdepartments"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(200), nullable=False)
    department_id = Column(Integer, ForeignKey("departments.id"), nullable=False)
    description = Column(Text)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    # Relationships
    department = relationship("Department", back_populates="subdepartments")
    users = relationship("User", back_populates="subdepartment")
    requests_from = relationship("Request", foreign_keys="Request.requester_subdepartment_id", back_populates="requester_subdepartment")
    requests_to = relationship("Request", foreign_keys="Request.assigned_subdepartment_id", back_populates="assigned_subdepartment")


class RequestActivityLog(Base):
    __tablename__ = "request_activity_logs"

    id = Column(Integer, primary_key=True, index=True)
    request_id = Column(Integer, ForeignKey("requests.id"), nullable=False)
    action = Column(SQLEnum(RequestActivityAction), nullable=False)
    performed_by_user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    performed_by_department_id = Column(Integer, ForeignKey("departments.id"))
    performed_by_division_id = Column(Integer, ForeignKey("divisions.id"))
    target_department_id = Column(Integer, ForeignKey("departments.id"))
    target_division_id = Column(Integer, ForeignKey("divisions.id"))
    details = Column(Text)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    request = relationship("Request", back_populates="activity_logs")
    performed_by = relationship("User", foreign_keys=[performed_by_user_id])
    performed_department = relationship("Department", foreign_keys=[performed_by_department_id])
    performed_division = relationship("Division", foreign_keys=[performed_by_division_id])
    target_department = relationship("Department", foreign_keys=[target_department_id])
    target_division = relationship("Division", foreign_keys=[target_division_id])


class Request(Base):
    __tablename__ = "requests"

    id = Column(Integer, primary_key=True, index=True)
    request_id = Column(String(100), unique=True, nullable=False, index=True)  # REQ-DEPT-DATE-XXX
    request_type = Column(String(100), nullable=False)  # HR, FINANCE, ICT, etc.
    resource_type = Column(SQLEnum(ResourceType), default=ResourceType.GENERAL)  # Type of shared resource
    
    # Requester info
    requester_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    requester_division_id = Column(Integer, ForeignKey("divisions.id"), nullable=False)
    requester_department_id = Column(Integer, ForeignKey("departments.id"))
    requester_subdepartment_id = Column(Integer, ForeignKey("subdepartments.id"))
    
    # Assigned to
    assigned_division_id = Column(Integer, ForeignKey("divisions.id"))
    assigned_department_id = Column(Integer, ForeignKey("departments.id"))
    assigned_subdepartment_id = Column(Integer, ForeignKey("subdepartments.id"))
    assigned_to_user_id = Column(Integer, ForeignKey("users.id"))
    
    # Priority and status
    priority = Column(SQLEnum(Priority), default=Priority.MEDIUM, nullable=False)
    status = Column(SQLEnum(RequestStatus), default=RequestStatus.PENDING, nullable=False)
    
    # SLA tracking (Enhanced for M&E)
    sla_response_time_hours = Column(Integer)  # Expected response time in hours
    sla_completion_time_hours = Column(Integer)  # Expected completion time in hours
    sla_response_deadline = Column(DateTime(timezone=True))  # Calculated deadline for first response
    sla_completion_deadline = Column(DateTime(timezone=True))  # Calculated deadline for completion
    actual_response_time = Column(DateTime(timezone=True))  # When first action was taken
    actual_completion_time = Column(DateTime(timezone=True))  # When request was completed
    reason_for_delay = Column(Text)  # Explanation if SLA was missed
    
    # Cost tracking (for M&E cost optimization KPIs)
    cost_estimate = Column(Numeric(10, 2))  # Estimated cost in Birr
    actual_cost = Column(Numeric(10, 2))  # Actual cost incurred in Birr
    
    # Customer satisfaction (for M&E satisfaction scorecards)
    satisfaction_rating = Column(Integer)  # 1-5 scale
    satisfaction_comment = Column(Text)  # Optional feedback from requester
    
    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    submitted_at = Column(DateTime(timezone=True))
    approved_at = Column(DateTime(timezone=True))
    started_at = Column(DateTime(timezone=True))
    completed_at = Column(DateTime(timezone=True))
    acknowledged_at = Column(DateTime(timezone=True))
    acknowledged_by_user_id = Column(Integer, ForeignKey("users.id"))
    completion_validated_at = Column(DateTime(timezone=True))
    completion_validated_by_user_id = Column(Integer, ForeignKey("users.id"))
    
    # Content
    description = Column(Text, nullable=False)
    notes = Column(Text)
    attachments = Column(JSON)  # Store file paths/URLs as JSON array
    
    # Approval
    approval_required = Column(Boolean, default=True)
    approved_by_user_id = Column(Integer, ForeignKey("users.id"))

    # Relationships
    requester = relationship("User", foreign_keys=[requester_id], back_populates="requests_created")
    requester_division = relationship("Division", foreign_keys=[requester_division_id], back_populates="requests_from")
    requester_department = relationship("Department", foreign_keys=[requester_department_id], back_populates="requests_from")
    requester_subdepartment = relationship("SubDepartment", foreign_keys=[requester_subdepartment_id], back_populates="requests_from")
    assigned_division = relationship("Division", foreign_keys=[assigned_division_id], back_populates="requests_to")
    assigned_department = relationship("Department", foreign_keys=[assigned_department_id], back_populates="requests_to")
    assigned_subdepartment = relationship("SubDepartment", foreign_keys=[assigned_subdepartment_id], back_populates="requests_to")
    assigned_to = relationship("User", foreign_keys=[assigned_to_user_id], back_populates="requests_assigned")
    
    items =relationship("RequestItem", back_populates="request", cascade="all, delete-orphan")
    workflow = relationship("RequestWorkflow", back_populates="request", cascade="all, delete-orphan")
    activity_logs = relationship("RequestActivityLog", back_populates="request", cascade="all, delete-orphan")
    alerts = relationship("SLAAlert", back_populates="request", cascade="all, delete-orphan")
    satisfaction = relationship("CustomerSatisfaction", back_populates="request", uselist=False, cascade="all, delete-orphan")
    acknowledged_by = relationship("User", foreign_keys=[acknowledged_by_user_id])
    completion_validated_by = relationship("User", foreign_keys=[completion_validated_by_user_id])


class RequestItem(Base):
    __tablename__ = "request_items"
    
    id = Column(Integer, primary_key=True, index=True)
    request_id = Column(Integer, ForeignKey("requests.id"), nullable=False)
    item_description = Column(Text, nullable=False)
    quantity = Column(Float)
    unit_price = Column(Float)
    expected_delivery_date = Column(DateTime(timezone=True))
    notes = Column(Text)
    custom_fields = Column(JSON)  # Store type-specific fields as JSON
    
    # File attachment fields for item documentation (PHASE 1 ADDITION)
    attachment_filename = Column(String(255))
    attachment_path = Column(String(500))
    attachment_type = Column(String(50))  # 'word', 'excel', 'pdf', 'image'
    
    # Relationships
    request = relationship("Request", back_populates="items")


class RequestWorkflow(Base):
    __tablename__ = "request_workflow"
    
    id = Column(Integer, primary_key=True, index=True)
    request_id = Column(Integer, ForeignKey("requests.id"), nullable=False)
    step = Column(SQLEnum(WorkflowStep), nullable=False)
    performed_by_user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    performed_at = Column(DateTime(timezone=True), server_default=func.now())
    notes = Column(Text)
    attachments = Column(JSON)
    
    # Relationships
    request = relationship("Request", back_populates="workflow")
    performed_by = relationship("User")


class SLAAlert(Base):
    __tablename__ = "sla_alerts"
    
    id = Column(Integer, primary_key=True, index=True)
    request_id = Column(Integer, ForeignKey("requests.id"), nullable=False)
    alert_type = Column(SQLEnum(AlertType), nullable=False)
    sent_at = Column(DateTime(timezone=True), server_default=func.now())
    acknowledged_at = Column(DateTime(timezone=True))
    acknowledged_by_user_id = Column(Integer, ForeignKey("users.id"))
    
    # Relationships
    request = relationship("Request", back_populates="alerts")
    acknowledged_by = relationship("User")


class CustomerSatisfaction(Base):
    __tablename__ = "customer_satisfaction"
    
    id = Column(Integer, primary_key=True, index=True)
    request_id = Column(Integer, ForeignKey("requests.id"), nullable=False, unique=True)
    timeliness_score = Column(Integer)  # 1-5
    quality_score = Column(Integer)  # 1-5
    communication_score = Column(Integer)  # 1-5
    professionalism_score = Column(Integer)  # 1-5
    overall_score = Column(Integer)  # 1-5
    comments = Column(Text)
    submitted_at = Column(DateTime(timezone=True), server_default=func.now())
    submitted_by_user_id = Column(Integer, ForeignKey("users.id"))
    
    # Relationships
    request = relationship("Request", back_populates="satisfaction")
    submitted_by = relationship("User")


class KPIMetric(Base):
    __tablename__ = "kpi_metrics"
    
    id = Column(Integer, primary_key=True, index=True)
    metric_name = Column(String(200), nullable=False)
    metric_type = Column(String(100), nullable=False)
    department_id = Column(Integer, ForeignKey("departments.id"))
    division_id = Column(Integer, ForeignKey("divisions.id"))
    target_value = Column(Numeric(10, 2))
    actual_value = Column(Numeric(10, 2))
    period = Column(String(20))  # DAILY, WEEKLY, MONTHLY, QUARTERLY
    recorded_at = Column(DateTime(timezone=True), server_default=func.now())
    calculated_at = Column(DateTime(timezone=True))
    
    # Relationships
    department = relationship("Department")
    division = relationship("Division")


class Scorecard(Base):
    __tablename__ = "scorecards"
    
    id = Column(Integer, primary_key=True, index=True)
    period_start = Column(DateTime(timezone=True), nullable=False)
    period_end = Column(DateTime(timezone=True), nullable=False)
    division_id = Column(Integer, ForeignKey("divisions.id"))
    department_id = Column(Integer, ForeignKey("departments.id"))
    
    # 4 Dimensions (total = 100%)
    service_efficiency_score = Column(Numeric(5, 2))  # 25%
    compliance_score = Column(Numeric(5, 2))  # 30%
    cost_optimization_score = Column(Numeric(5, 2))  # 20%
    satisfaction_score = Column(Numeric(5, 2))  # 25%
    
    total_score = Column(Numeric(5, 2))  # Sum of above
    rating = Column(SQLEnum(ScoreRating))
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    created_by_user_id = Column(Integer, ForeignKey("users.id"))
    
    # Relationships
    division = relationship("Division")
    department = relationship("Department")
    created_by = relationship("User")


# ============================================================================
# RESOURCE-SPECIFIC MODELS (Phase 1 - For M&E KPI Tracking)
# ============================================================================

class FleetRequest(Base):
    """Track fleet/vehicle-specific request details for KPI calculation"""
    __tablename__ = "fleet_requests"
    
    id = Column(Integer, primary_key=True, index=True)
    request_id = Column(Integer, ForeignKey("requests.id"), nullable=False, unique=True)
    
    # Vehicle assignment
    vehicle_assigned = Column(String(100))  # Vehicle ID/plate number
    driver_assigned = Column(String(200))  # Driver name
    
    # Trip details
    dispatch_time = Column(DateTime(timezone=True))
    return_time = Column(DateTime(timezone=True))
    fuel_used = Column(Float)  # Liters
    km_traveled = Column(Float)  # Kilometers
    
    # KPI tracking
    trip_completed = Column(Boolean, default=False)
    breakdown_occurred = Column(Boolean, default=False)
    
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    
    # Relationship
    request = relationship("Request", backref="fleet_details")


class HRDeployment(Base):
    """Track HR deployment request details for staff allocation KPIs"""
    __tablename__ = "hr_deployments"
    
    id = Column(Integer, primary_key=True, index=True)
    request_id = Column(Integer, ForeignKey("requests.id"), nullable=False, unique=True)
    
    # Staff details
    staff_assigned = Column(String(200))  # Staff member name/ID
    competency_required = Column(String(200))  # Required skills/qualifications
    deployment_duration_days = Column(Integer)  # Expected duration in days
    
    # Tracking
    actual_start_date = Column(DateTime(timezone=True))
    actual_end_date = Column(DateTime(timezone=True))
    overtime_hours = Column(Float)  # Overtime hours logged
    deployment_filled = Column(Boolean, default=False)  # Was position filled?
    
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    
    # Relationship
    request = relationship("Request", backref="hr_details")


class FinanceTransaction(Base):
    """Track finance request details for payment processing KPIs"""
    __tablename__ = "finance_transactions"
    
    id = Column(Integer, primary_key=True, index=True)
    request_id = Column(Integer, ForeignKey("requests.id"), nullable=False, unique=True)
    
    # Transaction details
    transaction_type = Column(String(100))  # vendor, payroll, tax, reimbursement, pension
    amount = Column(Numeric(12, 2))  # Amount in Birr
    processing_officer = Column(String(200))  # Finance staff who processed
    
    # Document verification
    supporting_docs_complete = Column(Boolean, default=False)
    document_completeness_score = Column(Integer)  # % of required docs submitted
    
    # Compliance
    complies_with_finance_sop = Column(Boolean, default=True)
    payment_accuracy = Column(Boolean, default=True)  # Was payment amount correct?
    
    # Timing
    date_received = Column(DateTime(timezone=True))
    date_processed = Column(DateTime(timezone=True))
    
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    
    # Relationship
    request = relationship("Request", backref="finance_details")


class ICTTicket(Base):
    """Track ICT support tickets for IT KPIs"""
    __tablename__ = "ict_tickets"
    
    id = Column(Integer, primary_key=True, index=True)
    request_id = Column(Integer, ForeignKey("requests.id"), nullable=False, unique=True)
    
    # Ticket details
    ticket_number = Column(String(100), unique=True)
    problem_type = Column(String(200))  # Hardware, Software, Network, etc.
    severity = Column(String(50))  # Critical, High, Medium, Low
    
    # Resolution tracking
    technician_assigned = Column(String(200))
    resolution_time_minutes = Column(Integer)  # Minutes to resolve
    escalated = Column(Boolean, default=False)
    reopened = Column(Boolean, default=False)  # Was ticket reopened?
    
    # Uptime impact
    system_downtime_minutes = Column(Integer)  # Minutes of downtime caused
    
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    
    # Relationship
    request = relationship("Request", backref="ict_details")


class LogisticsRequest(Base):
    """Track logistics/supply chain requests for fulfillment KPIs"""
    __tablename__ = "logistics_requests"
    
    id = Column(Integer, primary_key=True, index=True)
    request_id = Column(Integer, ForeignKey("requests.id"), nullable=False, unique=True)
    
    # Item details
    item_requested = Column(String(300))
    quantity_requested = Column(Float)
    quantity_delivered = Column(Float)
    
    # Stock and delivery
    stock_available = Column(Boolean, default=True)
    delivery_time_days = Column(Integer)  # Actual delivery time
    lead_time_days = Column(Integer)  # Time from request to delivery
    
    # Quality
    requisition_accurate = Column(Boolean, default=True)  # Was request form complete?
    documentation_complete = Column(Boolean, default=True)
    cost_per_item = Column(Numeric(10, 2))  # Cost per unit delivered
    
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    
    # Relationship
    request = relationship("Request", backref="logistics_details")


class SystemSettings(Base):
    """System-wide configuration settings for features and preferences"""
    __tablename__ = "system_settings"

    id = Column(Integer, primary_key=True, index=True)
    setting_key = Column(String, unique=True, nullable=False, index=True)
    setting_value = Column(Text, nullable=False)
    description = Column(Text)
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())

    def __repr__(self):
        return f"<SystemSettings {self.setting_key}={self.setting_value}>"
