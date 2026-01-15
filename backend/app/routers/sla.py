from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from sqlalchemy import func, extract, case, and_, or_
from typing import List
from datetime import datetime, timedelta

from ..database import get_db
from ..auth import get_current_active_user
from ..models import Request, RequestStatus, User, SLAAlert, AlertType
from .. import schemas
from ..services.access_control import apply_role_based_filtering

router = APIRouter(prefix="/sla", tags=["sla"])


@router.get("/compliance")
async def get_sla_compliance(
    period: str = "month",  # day, week, month, quarter
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """Get SLA compliance metrics - INCLUDES active overdue requests"""
    # Calculate period start
    now = datetime.utcnow()
    if period == "day":
        start = now - timedelta(days=1)
    elif period == "week":
        start = now - timedelta(weeks=1)
    elif period == "quarter":
        start = now - timedelta(days=90)
    else:  # month
        start = now - timedelta(days=30)
    
    from sqlalchemy import case, extract
    
    # Base query with role-based filtering
    base_query = db.query(Request).filter(Request.created_at >= start)
    base_query = apply_role_based_filtering(base_query, current_user)
    
    # 1. Get stats for completed requests
    actual_resp = func.coalesce(Request.actual_response_time, Request.acknowledged_at)
    actual_comp = func.coalesce(Request.actual_completion_time, Request.completed_at)
    
    completed_stats = base_query.filter(
        Request.status == RequestStatus.COMPLETED
    ).with_entities(
        func.count(Request.id).label("total"),
        func.count(case((
            and_(
                actual_resp.isnot(None),
                actual_comp.isnot(None),
                # Response SLA met
                extract('epoch', actual_resp) <= 
                extract('epoch', Request.created_at) + (func.coalesce(Request.sla_response_time_hours, 2) * 3600),
                # Resolution SLA met
                extract('epoch', actual_comp) <= 
                extract('epoch', Request.created_at) + (func.coalesce(Request.sla_completion_time_hours, 24) * 3600)
            ), 1
        ))).label("within_sla"),
        func.avg(
            extract('epoch', actual_comp) - extract('epoch', Request.created_at)
        ).label("avg_time_seconds")
    ).one()
    
    # 2. Get active overdue requests (either response or resolution overdue)
    overdue_active = base_query.filter(
        Request.status.in_([RequestStatus.PENDING, RequestStatus.IN_PROGRESS]),
        or_(
            # Response overdue (if not yet acknowledged)
            and_(
                Request.acknowledged_at.is_(None),
                extract('epoch', func.now()) > extract('epoch', Request.created_at) + (func.coalesce(Request.sla_response_time_hours, 2) * 3600)
            ),
            # Resolution overdue
            extract('epoch', func.now()) > extract('epoch', Request.created_at) + (func.coalesce(Request.sla_completion_time_hours, 24) * 3600)
        )
    ).with_entities(func.count(Request.id)).scalar() or 0
    
    # Total calculations
    total_requests = base_query.with_entities(func.count(Request.id)).scalar() or 0
    within_sla = completed_stats.within_sla or 0
    overdue_completed = (completed_stats.total or 0) - within_sla
    
    total_evaluated = (completed_stats.total or 0) + overdue_active
    total_overdue = overdue_completed + overdue_active
    compliance_rate = (within_sla / total_evaluated * 100) if total_evaluated > 0 else 100
    avg_time_hours = (completed_stats.avg_time_seconds / 3600) if completed_stats.avg_time_seconds else 0
    
    return {
        "total_requests": total_requests,
        "within_sla": within_sla,
        "overdue": total_overdue,
        "compliance_rate": round(compliance_rate, 2),
        "average_completion_time": round(avg_time_hours, 2),
        "period": period,
    }


@router.get("/alerts")
async def get_active_alerts(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """Get active SLA alerts"""
    # Get unacknowledged alerts
    query = db.query(SLAAlert).join(Request).filter(
        SLAAlert.acknowledged_at.is_(None)
    )
    query = apply_role_based_filtering(query, current_user, model=Request)
    alerts = query.order_by(SLAAlert.sent_at.desc()).limit(50).all()
    
    return alerts


@router.get("/overdue")
async def get_overdue_requests(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """Get requests that are overdue using SQL"""
    
    
    # Base query with role-based filtering
    base_query = db.query(Request).filter(
        Request.status.in_([RequestStatus.PENDING, RequestStatus.IN_PROGRESS, RequestStatus.APPROVED])
    )
    base_query = apply_role_based_filtering(base_query, current_user)
    
    # Get overdue requests directly in SQL
    overdue_requests = base_query.filter(
        or_(
            # Response overdue (if not yet acknowledged)
            and_(
                Request.acknowledged_at.is_(None),
                extract('epoch', func.now()) > extract('epoch', Request.created_at) + (func.coalesce(Request.sla_response_time_hours, 2) * 3600)
            ),
            # Resolution overdue
            extract('epoch', func.now()) > extract('epoch', Request.created_at) + (func.coalesce(Request.sla_completion_time_hours, 24) * 3600)
        )
    ).all()
    
    # Format response
    now = datetime.utcnow()
    results = []
    for req in overdue_requests:
        deadline = req.created_at + timedelta(hours=req.sla_completion_time_hours or 24)
        time_overdue = (now - deadline).total_seconds() / 3600
        results.append({
            "request": req,
            "deadline": deadline,
            "hours_overdue": round(time_overdue, 2),
        })
    
    return results


@router.get("/dashboard")
async def get_sla_dashboard(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """Get SLA dashboard data using SQL aggregations"""
    from sqlalchemy import case, extract
    
    # Base query with role-based filtering
    base_query = db.query(Request).filter(
        Request.status.in_([RequestStatus.PENDING, RequestStatus.IN_PROGRESS, RequestStatus.APPROVED])
    )
    base_query = apply_role_based_filtering(base_query, current_user)
    
    # Categorize by SLA status in one query
    now_epoch = extract('epoch', func.now())
    created_epoch = extract('epoch', Request.created_at)
    
    # Response consumption (if not acknowledged)
    resp_target = func.coalesce(Request.sla_response_time_hours, 2) * 3600
    resp_percent = case((Request.acknowledged_at.is_(None), ((now_epoch - created_epoch) / resp_target) * 100), else_=0)
    
    # Resolution consumption
    res_target = func.coalesce(Request.sla_completion_time_hours, 24) * 3600
    res_percent = ((now_epoch - created_epoch) / res_target) * 100
    
    # Composite percent (the worse of the two)
    percent_consumed = func.greatest(resp_percent, res_percent)
    
    stats = base_query.with_entities(
        func.count(Request.id).label("total_active"),
        func.count(case((percent_consumed >= 100, 1))).label("overdue"),
        func.count(case((and_(percent_consumed >= 80, percent_consumed < 100), 1))).label("critical"),
        func.count(case((and_(percent_consumed >= 50, percent_consumed < 80), 1))).label("at_risk"),
        func.count(case((percent_consumed < 50, 1))).label("on_track")
    ).one()
    
    # Today's compliance
    today_start = datetime.utcnow().replace(hour=0, minute=0, second=0, microsecond=0)
    today_completed_query = db.query(Request).filter(
        Request.status == RequestStatus.COMPLETED,
        Request.completed_at >= today_start
    )
    today_completed_query = apply_role_based_filtering(today_completed_query, current_user)
    today_completed = today_completed_query.with_entities(func.count(Request.id)).scalar() or 0
    
    return {
        "active_requests": stats.total_active or 0,
        "on_track": stats.on_track or 0,
        "at_risk_50_percent": stats.at_risk or 0,
        "critical_80_percent": stats.critical or 0,
        "overdue": stats.overdue or 0,
        "completed_today": today_completed,
    }


@router.post("/alerts/{alert_id}/acknowledge")
async def acknowledge_alert(
    alert_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """Acknowledge an SLA alert"""
    alert = db.get(SLAAlert, alert_id)
    if not alert:
        raise HTTPException(status_code=404, detail="Alert not found")
    
    alert.acknowledged_at = datetime.utcnow()
    alert.acknowledged_by_user_id = current_user.id
    
    db.commit()
    return {"status": "acknowledged"}
