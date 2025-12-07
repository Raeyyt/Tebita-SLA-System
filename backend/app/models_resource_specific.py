

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
