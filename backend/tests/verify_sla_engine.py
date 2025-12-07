import sys
import os
from datetime import datetime, timedelta

# Add backend directory to path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from app.database import SessionLocal
from app.models import Request, User, Priority, ResourceType, RequestStatus
from app.services.sla_calculator import calculate_deadlines, calculate_sla_status
from app.services.kpi_calculator import calculate_kpi_metrics

def verify_sla_engine():
    db = SessionLocal()
    try:
        print("🚀 Starting SLA Engine Verification...")
        
        # 1. Test SLA Calculation Logic (Unit Test style)
        print("\n1. Testing SLA Policy & Calculation Logic...")
        
        # Mock Request: Finance, High Priority
        req = Request(
            resource_type=ResourceType.FINANCE,
            priority=Priority.HIGH,
            created_at=datetime.utcnow()
        )
        calculate_deadlines(req)
        
        print(f"   Finance HIGH Response Deadline: {req.sla_response_deadline} (Expected: +2h)")
        print(f"   Finance HIGH Resolution Deadline: {req.sla_completion_deadline} (Expected: +24h)")
        
        assert req.sla_response_time_hours == 2
        assert req.sla_completion_time_hours == 24
        print("   ✅ Finance HIGH SLA correct")

        # Mock Request: Logistics, High Priority (Critical)
        req_log = Request(
            resource_type=ResourceType.LOGISTICS,
            priority=Priority.HIGH,
            created_at=datetime.utcnow()
        )
        calculate_deadlines(req_log)
        print(f"   Logistics HIGH Response Deadline: {req_log.sla_response_deadline} (Expected: +0.5h)")
        
        # Note: 0.5 hours might be stored as 1 if int field, let's check policy
        # Policy says 0.5, calculator casts to int(max(1, x)). So it should be 1 hour in DB field but deadline is correct?
        # Let's check calculator logic: 
        # request.sla_response_time_hours = int(response_hours) if response_hours >= 1 else 1
        # request.sla_response_deadline = request.created_at + timedelta(hours=response_hours)
        # So deadline uses float, field uses int.
        
        expected_deadline = req_log.created_at + timedelta(hours=0.5)
        diff = abs((req_log.sla_response_deadline - expected_deadline).total_seconds())
        assert diff < 1 # Should be almost identical
        print("   ✅ Logistics HIGH SLA correct (0.5h)")

        # 2. Test KPI Calculation
        print("\n2. Testing KPI Calculation...")
        metrics = calculate_kpi_metrics(db)
        print(f"   Total Requests: {metrics['total_requests']}")
        print(f"   SLA Compliance: {metrics['sla_compliance_rate']}%")
        print(f"   Avg Resolution: {metrics['avg_resolution_time_hours']}h")
        print(f"   Priority Breakdown: {metrics['priority_breakdown']}")
        
        print("\n✅ Verification Complete!")
        
    except Exception as e:
        print(f"\n❌ Verification Failed: {e}")
        import traceback
        traceback.print_exc()
    finally:
        db.close()

if __name__ == "__main__":
    verify_sla_engine()
