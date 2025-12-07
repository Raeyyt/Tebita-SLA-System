from app.models import Priority, ResourceType

# Standard Priority Definitions (Fallback)
# Response and Resolution times in hours
PRIORITY_DEFAULTS = {
    Priority.HIGH: {"response": 2, "resolution": 24},      # Critical/High
    Priority.MEDIUM: {"response": 8, "resolution": 72},    # 3 days
    Priority.LOW: {"response": 24, "resolution": 168},     # 7 days
}

# Department/Resource-Specific Rules
# Overrides the defaults based on ResourceType and Priority
RESOURCE_SLA = {
    ResourceType.FINANCE: {
        Priority.HIGH: {"response": 2, "resolution": 24},
        Priority.MEDIUM: {"response": 8, "resolution": 48},   # 2 days
        Priority.LOW: {"response": 24, "resolution": 120},    # 5 days
    },
    ResourceType.LOGISTICS: {
        # Mapping "Emergency/Critical" to HIGH
        Priority.HIGH: {"response": 0.5, "resolution": 1},    # 30 mins / 1 hour (Critical medical consumables)
        Priority.MEDIUM: {"response": 2, "resolution": 24},   # Medical equipment
        Priority.LOW: {"response": 24, "resolution": 48},     # Routine restock
    },
    ResourceType.FLEET: {
        Priority.HIGH: {"response": 0.5, "resolution": 24},   # Critical spare part
        Priority.MEDIUM: {"response": 4, "resolution": 48},   # Scheduled spares
        Priority.LOW: {"response": 24, "resolution": 72},     # Non-urgent
    },
    ResourceType.HR: {
        Priority.HIGH: {"response": 4, "resolution": 24},     # Payroll issue / Critical staffing
        Priority.MEDIUM: {"response": 24, "resolution": 120}, # Exit clearance (approx 5 days)
        Priority.LOW: {"response": 48, "resolution": 120},    # Routine HR requests
    },
    ResourceType.ICT: {
        # Using Maintenance standards as proxy for ICT/Equipment
        Priority.HIGH: {"response": 1, "resolution": 24},     # Critical failure
        Priority.MEDIUM: {"response": 24, "resolution": 48},  # Preventive maintenance
        Priority.LOW: {"response": 48, "resolution": 168},    # Minor issues
    }
}

def get_sla_standards(resource_type: ResourceType, priority: Priority):
    """
    Returns the SLA standards (response and resolution time in hours)
    for a given resource type and priority.
    """
    # Check for resource-specific override
    if resource_type in RESOURCE_SLA and priority in RESOURCE_SLA[resource_type]:
        return RESOURCE_SLA[resource_type][priority]
    
    # Fallback to priority defaults
    return PRIORITY_DEFAULTS.get(priority, PRIORITY_DEFAULTS[Priority.MEDIUM])
