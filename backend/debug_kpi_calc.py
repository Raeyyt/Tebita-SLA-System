import sys
import os
from datetime import datetime, timedelta
sys.path.append(os.getcwd())

from app.database import SessionLocal
from app.services.kpi_calculator import calculate_customer_satisfaction_score

db = SessionLocal()

print("--- Debugging KPI Calculator ---")

# Test 1: No date filter
score_all = calculate_customer_satisfaction_score(db)
print(f"Score (All Time): {score_all}")

# Test 2: Monthly (Last 30 days)
end_date = datetime.utcnow()
start_date = end_date - timedelta(days=30)
score_monthly = calculate_customer_satisfaction_score(db, start_date=start_date, end_date=end_date)
print(f"Score (Last 30 Days): {score_monthly}")

# Test 3: Daily (Today)
start_today = datetime.utcnow().replace(hour=0, minute=0, second=0, microsecond=0)
score_today = calculate_customer_satisfaction_score(db, start_date=start_today, end_date=end_date)
print(f"Score (Today): {score_today}")
