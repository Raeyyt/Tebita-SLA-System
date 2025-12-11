#!/usr/bin/env python3
"""
Backfill SLA Data for Existing Requests

This script calculates and populates SLA fields for all existing requests
that are missing SLA data (sla_completion_time_hours is NULL).

Usage:
    cd backend
    python backfill_sla_data.py
"""
import sys
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent))

from app.database import SessionLocal
from app.models import Request
from app.sla_utils import calculate_sla_deadlines, SLA_RESPONSE_HOURS, SLA_COMPLETION_HOURS
from datetime import datetime, timezone


def backfill_sla_data():
    """Backfill SLA data for all requests missing it."""
    db = SessionLocal()
    
    try:
        # Get all requests with missing SLA completion time
        requests = db.query(Request).filter(
            Request.sla_completion_time_hours.is_(None)
        ).all()
        
        total_count = len(requests)
        print(f"\n{'='*60}")
        print(f"SLA Data Backfill Script")
        print(f"{'='*60}")
        print(f"Found {total_count} requests missing SLA data\n")
        
        if total_count == 0:
            print("✅ All requests already have SLA data!")
            return
        
        updated_count = 0
        skipped_count = 0
        
        for req in requests:
            # Validate required fields
            if not req.created_at:
                print(f"  ⚠️  Skipping {req.request_id} - missing created_at")
                skipped_count += 1
                continue
            
            if not req.priority:
                print(f"  ⚠️  Skipping {req.request_id} - missing priority")
                skipped_count += 1
                continue
            
            if not req.resource_type:
                print(f"  ⚠️  Skipping {req.request_id} - missing resource_type")
                skipped_count += 1
                continue
            
            # Calculate SLA deadlines using the existing utility function
            try:
                response_deadline, completion_deadline = calculate_sla_deadlines(
                    request_created_at=req.created_at,
                    priority=req.priority,
                    resource_type=req.resource_type
                )
                
                # Set SLA time hours
                req.sla_response_time_hours = SLA_RESPONSE_HOURS.get(req.priority, 24)
                req.sla_completion_time_hours = SLA_COMPLETION_HOURS.get(req.resource_type, 96)
                
                # Set deadline timestamps
                req.sla_response_deadline = response_deadline
                req.sla_completion_deadline = completion_deadline
                
                updated_count += 1
                
                # Show progress every 10 requests
                if updated_count % 10 == 0:
                    print(f"  📝 Progress: {updated_count}/{total_count}")
                    
            except Exception as e:
                print(f"  ❌ Error processing {req.request_id}: {e}")
                skipped_count += 1
                continue
        
        # Commit all changes
        db.commit()
        
        # Print summary
        print(f"\n{'='*60}")
        print(f"BACKFILL COMPLETE")
        print(f"{'='*60}")
        print(f"✅ Successfully updated: {updated_count} requests")
        if skipped_count > 0:
            print(f"⚠️  Skipped: {skipped_count} requests")
        print(f"{'='*60}\n")
        
        # Verify the backfill
        print("Verifying...")
        with_sla = db.query(Request).filter(
            Request.sla_completion_time_hours.isnot(None)
        ).count()
        total = db.query(Request).count()
        print(f"Requests with SLA data: {with_sla}/{total}")
        
        if with_sla == total:
            print("✅ 100% of requests now have SLA data!\n")
        else:
            missing = total - with_sla
            print(f"⚠️  {missing} requests still missing SLA data\n")
        
    except Exception as e:
        db.rollback()
        print(f"\n❌ FATAL ERROR: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
        
    finally:
        db.close()


if __name__ == "__main__":
    print("\n⚙️  Starting SLA backfill process...")
    backfill_sla_data()
    print("✨ Done!\n")
