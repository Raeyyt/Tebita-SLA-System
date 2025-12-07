

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
