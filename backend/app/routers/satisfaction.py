from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from sqlalchemy import func
from typing import List

from ..database import get_db
from ..auth import get_current_active_user
from ..models import User, Request, CustomerSatisfaction, RequestStatus, Department
from ..schemas import SatisfactionRatingCreate, SatisfactionRatingResponse, DepartmentRatingStats, UserBasic
from ..services.access_control import apply_role_based_filtering

router = APIRouter(prefix="/satisfaction", tags=["satisfaction"])


@router.post("/requests/{request_id}/rate", response_model=SatisfactionRatingResponse, status_code=status.HTTP_201_CREATED)
async def submit_rating(
    request_id: int,
    rating: SatisfactionRatingCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """
    Submit a satisfaction rating for a completed request.
    
    Business Rules:
    - Only the original requester can submit a rating
    - Request must be in COMPLETED status
    - One rating per request (unique constraint)
    """
    # 1. Fetch the request
    request = db.query(Request).filter(Request.id == request_id).first()
    if not request:
        raise HTTPException(status_code=404, detail="Request not found")
    
    # 2. Verify requester is the one rating
    if request.requester_id != current_user.id:
        raise HTTPException(
            status_code=403,
            detail="Only the original requester can rate this request"
        )
    
    # 3. Verify request is completed
    if request.status != RequestStatus.COMPLETED:
        raise HTTPException(
            status_code=400,
            detail="Can only rate completed requests"
        )
    
    # 4. Check if rating already exists
    existing_rating = db.query(CustomerSatisfaction).filter(
        CustomerSatisfaction.request_id == request_id
    ).first()
    
    if existing_rating:
        raise HTTPException(
            status_code=400,
            detail="This request has already been rated"
        )
    
    # 5. Create the rating
    new_rating = CustomerSatisfaction(
        request_id=request_id,
        timeliness_score=rating.timeliness_score,
        quality_score=rating.quality_score,
        communication_score=rating.communication_score,
        professionalism_score=rating.professionalism_score,
        overall_score=rating.overall_score,
        comments=rating.comments,
        submitted_by_user_id=current_user.id
    )
    
    db.add(new_rating)
    db.commit()
    db.refresh(new_rating)
    
    # 6. Return response
    return SatisfactionRatingResponse(
        id=new_rating.id,
        request_id=new_rating.request_id,
        timeliness_score=new_rating.timeliness_score,
        quality_score=new_rating.quality_score,
        communication_score=new_rating.communication_score,
        professionalism_score=new_rating.professionalism_score,
        overall_score=new_rating.overall_score,
        comments=new_rating.comments,
        submitted_at=new_rating.submitted_at,
        submitted_by=UserBasic(
            id=new_rating.submitted_by.id,
            username=new_rating.submitted_by.username,
            full_name=new_rating.submitted_by.full_name,
            email=new_rating.submitted_by.email
        )
    )


@router.get("/requests/{request_id}", response_model=SatisfactionRatingResponse)
async def get_rating(
    request_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """Get the satisfaction rating for a specific request"""
    rating = db.query(CustomerSatisfaction).filter(
        CustomerSatisfaction.request_id == request_id
    ).first()
    
    if not rating:
        raise HTTPException(status_code=404, detail="No rating found for this request")
    
    return SatisfactionRatingResponse(
        id=rating.id,
        request_id=rating.request_id,
        timeliness_score=rating.timeliness_score,
        quality_score=rating.quality_score,
        communication_score=rating.communication_score,
        professionalism_score=rating.professionalism_score,
        overall_score=rating.overall_score,
        comments=rating.comments,
        submitted_at=rating.submitted_at,
        submitted_by=UserBasic(
            id=rating.submitted_by.id,
            username=rating.submitted_by.username,
            full_name=rating.submitted_by.full_name,
            email=rating.submitted_by.email
        )
    )


@router.get("/department/{department_id}/stats", response_model=DepartmentRatingStats)
async def get_department_stats(
    department_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """Get aggregate rating statistics for a department"""
    # Get department info
    department = db.query(Department).filter(Department.id == department_id).first()
    if not department:
        raise HTTPException(status_code=404, detail="Department not found")
    
    # Get all ratings for requests assigned to this department
    ratings_query = db.query(CustomerSatisfaction).join(Request).filter(
        Request.assigned_department_id == department_id
    )
    
    ratings = ratings_query.all()
    total_ratings = len(ratings)
    
    if total_ratings == 0:
        return DepartmentRatingStats(
            department_id=department_id,
            department_name=department.name,
            total_ratings=0,
            average_overall=0.0,
            average_timeliness=0.0,
            average_quality=0.0,
            average_communication=0.0,
            average_professionalism=0.0,
            rating_distribution={"5": 0, "4": 0, "3": 0, "2": 0, "1": 0}
        )
    
    # Calculate averages
    avg_overall = sum(r.overall_score for r in ratings) / total_ratings
    avg_timeliness = sum(r.timeliness_score for r in ratings) / total_ratings
    avg_quality = sum(r.quality_score for r in ratings) / total_ratings
    avg_communication = sum(r.communication_score for r in ratings) / total_ratings
    avg_professionalism = sum(r.professionalism_score for r in ratings) / total_ratings
    
    # Calculate rating distribution
    distribution = {"5": 0, "4": 0, "3": 0, "2": 0, "1": 0}
    for rating in ratings:
        distribution[str(rating.overall_score)] += 1
    
    return DepartmentRatingStats(
        department_id=department_id,
        department_name=department.name,
        total_ratings=total_ratings,
        average_overall=round(avg_overall, 2),
        average_timeliness=round(avg_timeliness, 2),
        average_quality=round(avg_quality, 2),
        average_communication=round(avg_communication, 2),
        average_professionalism=round(avg_professionalism, 2),
        rating_distribution=distribution
    )


@router.get("/my-ratings", response_model=List[SatisfactionRatingResponse])
async def get_my_ratings(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """Get all ratings submitted by the current user"""
    ratings = db.query(CustomerSatisfaction).filter(
        CustomerSatisfaction.submitted_by_user_id == current_user.id
    ).all()
    
    return [
        SatisfactionRatingResponse(
            id=r.id,
            request_id=r.request_id,
            timeliness_score=r.timeliness_score,
            quality_score=r.quality_score,
            communication_score=r.communication_score,
            professionalism_score=r.professionalism_score,
            overall_score=r.overall_score,
            comments=r.comments,
            submitted_at=r.submitted_at,
            submitted_by=UserBasic(
                id=r.submitted_by.id,
                username=r.submitted_by.username,
                full_name=r.submitted_by.full_name,
                email=r.submitted_by.email
            )
        )
        for r in ratings
    ]


@router.get("/analytics/all-departments")
async def get_all_departments_analytics(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """Get comprehensive rating analytics for all departments with rankings"""
    from datetime import datetime, timedelta
    
    # Get all departments
    query = db.query(Department)
    query = apply_role_based_filtering(query, current_user, model=Department)
    departments = query.all()
    
    department_stats = []
    
    for dept in departments:
        # Get ratings for this department
        ratings = db.query(CustomerSatisfaction).join(Request).filter(
            Request.assigned_department_id == dept.id
        ).all()
        
        if not ratings:
            continue  # Skip departments with no ratings
        
        total_ratings = len(ratings)
        
        # Calculate averages
        avg_overall = sum(r.overall_score for r in ratings) / total_ratings
        avg_timeliness = sum(r.timeliness_score for r in ratings) / total_ratings
        avg_quality = sum(r.quality_score for r in ratings) / total_ratings
        avg_communication = sum(r.communication_score for r in ratings) / total_ratings
        avg_professionalism = sum(r.professionalism_score for r in ratings) / total_ratings
        
        # Get recent ratings (last 30 days)
        thirty_days_ago = datetime.utcnow() - timedelta(days=30)
        recent_ratings = [r for r in ratings if r.submitted_at >= thirty_days_ago]
        
        # Get ratings with comments
        ratings_with_comments = [r for r in ratings if r.comments]
        recent_comments = sorted(
            [(r.comments, r.submitted_at, r.request_id) for r in ratings_with_comments[-5:]],
            key=lambda x: x[1],
            reverse=True
        )
        
        department_stats.append({
            "department_id": dept.id,
            "department_name": dept.name,
            "total_ratings": total_ratings,
            "average_overall": round(avg_overall, 2),
            "average_timeliness": round(avg_timeliness, 2),
            "average_quality": round(avg_quality, 2),
            "average_communication": round(avg_communication, 2),
            "average_professionalism": round(avg_professionalism, 2),
            "recent_ratings_count": len(recent_ratings),
            "recent_comments": [
                {
                    "comment": c[0],
                    "submitted_at": c[1].isoformat(),
                    "request_id": c[2]
                } for c in recent_comments
            ]
        })
    
    # Sort by average overall rating
    department_stats.sort(key=lambda x: x["average_overall"], reverse=True)
    
    return {
        "departments": department_stats,
        "total_departments_rated": len(department_stats),
        "top_performer": department_stats[0] if department_stats else None,
        "needs_improvement": department_stats[-1] if department_stats else None
    }

