"""Add KPI metrics and Scorecards for 3-month period"""
from datetime import datetime, timedelta
from decimal import Decimal
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
import random
import sys
sys.path.insert(0, '.')

from app.models import *

engine = create_engine("sqlite:///./tebita.db", connect_args={"check_same_thread": False})
Session = sessionmaker(bind=engine)
db = Session()

print("Adding KPIs and Scorecards...")

try:
    divs = db.query(Division).all()
    ems = [d for d in divs if "EMS" in d.name][0]
    fin = [d for d in divs if "Finance" in d.name][0]
    hr = [d for d in divs if "HR" in d.name][0]
    
    # Add KPIs for September, October, November
    periods = ["2024-09", "2024-10", "2024-11"]
    kpis = [
        {"name": "Response Time (hrs)", "type": "response_time", "target": 24},
        {"name": "Completion Rate (%)", "type": "completion_rate", "target": 95},
        {"name": "SLA Compliance (%)", "type": "sla_compliance", "target": 90},
        {"name": "Customer Satisfaction", "type": "satisfaction", "target": 4.5},
    ]
    
    kpi_count = 0
    for period in periods:
        for div in [ems, fin, hr]:
            for kpi in kpis:
                variance = kpi["target"] * 0.12
                actual = kpi["target"] + random.uniform(-variance, variance)
                
                m = KPIMetric(
                    metric_name=kpi["name"],
                    metric_type=kpi["type"],
                    division_id=div.id,
                    target_value=Decimal(str(kpi["target"])),
                    actual_value=Decimal(str(round(actual, 2))),
                    period=period,
                    recorded_at=datetime.strptime(f"{period}-15", "%Y-%m-%d"),
                    calculated_at=datetime.strptime(f"{period}-28", "%Y-%m-%d")
                )
                db.add(m)
                kpi_count += 1
    
    # Add Scorecards for 3 months
    scorecard_count = 0
    sc_periods = [
        (datetime(2024, 9, 1), datetime(2024, 9, 30)),
        (datetime(2024, 10, 1), datetime(2024, 10, 31)),
        (datetime(2024, 11, 1), datetime(2024, 11, 30)),
    ]
    
    for start, end in sc_periods:
        for div in [ems, fin, hr]:
            eff = Decimal(str(random.uniform(82, 94)))
            comp = Decimal(str(random.uniform(85, 96)))
            cost = Decimal(str(random.uniform(80, 92)))
            sat = Decimal(str(random.uniform(88, 96)))
            total = (eff + comp + cost + sat) / 4
            
            rating = ScoreRating.OUTSTANDING if total >= 90 else (ScoreRating.VERY_GOOD if total >= 85 else ScoreRating.GOOD)
            
            sc = Scorecard(
                period_start=start,
                period_end=end,
                division_id=div.id,
                service_efficiency_score=eff,
                compliance_score=comp,
                cost_optimization_score=cost,
                satisfaction_score=sat,
                total_score=total,
                rating=rating,
                created_at=end + timedelta(days=2)
            )
            db.add(sc)
            scorecard_count += 1
    
    db.commit()
    print(f"✓ Created {kpi_count} KPI metrics")
    print(f"✓ Created {scorecard_count} scorecards")
    print(f"✓ Total KPIs: {db.query(KPIMetric).count()}")
    print(f"✓ Total Scorecards: {db.query(Scorecard).count()}")
    
except Exception as e:
    print(f"Error: {e}")
    import traceback
    traceback.print_exc()
    db.rollback()
finally:
    db.close()
