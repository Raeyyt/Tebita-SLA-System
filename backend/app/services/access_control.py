from sqlalchemy.orm import Query
from sqlalchemy import or_
from ..models import User, Request, UserRole, Department, Division

def apply_role_based_filtering(query: Query, user: User, model=Request) -> Query:
    """
    Apply hierarchical filtering to a SQLAlchemy query based on user role.
    
    Args:
        query: The SQLAlchemy query to filter
        user: The current user
        model: The model class being queried (default: Request)
        
    Returns:
        Filtered query
    """
    # Debug print
    # print(f"DEBUG ACCESS: User={user.username}, Role={user.role} ({type(user.role)}), Model={model}", flush=True)
    
    # Convert role to string for safer comparison
    user_role_str = str(user.role)
    
    if "ADMIN" in user_role_str:
        return query
        
    elif "DIVISION_MANAGER" in user_role_str:
        # Division Manager sees:
        # 1. Requests where their division is the requester
        # 2. Requests where their division is the assignee
        if model == Request:
            return query.filter(
                or_(
                    Request.requester_division_id == user.division_id,
                    Request.assigned_division_id == user.division_id
                )
            )
        # For other models (like KPIMetric, Scorecard), we might need different logic
        # But for now, most use cases are Request-based or have division_id fields
        elif model == Division:
            return query.filter(Division.id == user.division_id)
        elif hasattr(model, 'division_id'):
            return query.filter(model.division_id == user.division_id)
            
    elif "DEPARTMENT_HEAD" in user_role_str:
        # Department Head sees:
        # 1. Requests where their department is the requester
        # 2. Requests where their department is the assignee
        if model == Request:
            return query.filter(
                or_(
                    Request.requester_department_id == user.department_id,
                    Request.assigned_department_id == user.department_id
                )
            )
        elif model == Department:
            return query.filter(Department.id == user.department_id)
        elif hasattr(model, 'department_id'):
            return query.filter(model.department_id == user.department_id)
            
    elif "SUB_DEPARTMENT_STAFF" in user_role_str:
        # Staff sees:
        # 1. Requests they created
        # 2. Requests assigned to their sub-department
        # 3. Requests assigned to them personally
        if model == Request:
            return query.filter(
                or_(
                    Request.requester_id == user.id,
                    Request.assigned_subdepartment_id == user.subdepartment_id,
                    Request.assigned_to_user_id == user.id
                )
            )
            
    return query
