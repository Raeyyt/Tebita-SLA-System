"""
Database Migration Script: Add SLA and M&E Fields
Robust version using SQLAlchemy Inspector and raw SQL
"""
import sqlalchemy as sa
from sqlalchemy import inspect, text
from app.database import engine, Base
from app.models import (
    FleetRequest, HRDeployment, FinanceTransaction, 
    ICTTicket, LogisticsRequest, Request
)

def upgrade():
    """Add SLA and M&E enhancements to database"""
    print("🔄 Starting migration...")
    
    inspector = inspect(engine)
    columns = [c['name'] for c in inspector.get_columns('requests')]
    
    with engine.connect() as conn:
        # Add columns to requests table if they don't exist
        if 'resource_type' not in columns:
            print("  Adding resource_type column...")
            conn.execute(text("ALTER TABLE requests ADD COLUMN resource_type VARCHAR(50) DEFAULT 'GENERAL'"))
            
        if 'sla_response_deadline' not in columns:
            print("  Adding SLA columns...")
            conn.execute(text("ALTER TABLE requests ADD COLUMN sla_response_deadline DATETIME"))
            conn.execute(text("ALTER TABLE requests ADD COLUMN sla_completion_deadline DATETIME"))
            conn.execute(text("ALTER TABLE requests ADD COLUMN reason_for_delay TEXT"))
            
        if 'cost_estimate' not in columns:
            print("  Adding cost columns...")
            conn.execute(text("ALTER TABLE requests ADD COLUMN cost_estimate NUMERIC(10, 2)"))
            conn.execute(text("ALTER TABLE requests ADD COLUMN actual_cost NUMERIC(10, 2)"))
            
        if 'satisfaction_rating' not in columns:
            print("  Adding satisfaction columns...")
            conn.execute(text("ALTER TABLE requests ADD COLUMN satisfaction_rating INTEGER"))
            conn.execute(text("ALTER TABLE requests ADD COLUMN satisfaction_comment TEXT"))
            
        conn.commit()
    
    # Create new tables
    print("  Creating resource-specific tables...")
    Base.metadata.create_all(bind=engine)
    
    print("✅ Migration complete: SLA and M&E enhancements added successfully!")

if __name__ == "__main__":
    upgrade()
