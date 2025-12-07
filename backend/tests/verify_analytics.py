import sys
import os
from datetime import datetime, timedelta

# Add backend directory to path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from app.database import SessionLocal
from app.services.scorecard_calculator import calculate_overall_scorecard
from app.services.reporting_service import generate_scorecard_pdf, generate_request_export_csv

def verify_analytics():
    db = SessionLocal()
    try:
        print("🚀 Starting Analytics Verification...")
        
        # 1. Test Scorecard Calculation
        print("\n1. Testing Scorecard Calculation...")
        end_date = datetime.utcnow()
        start_date = end_date - timedelta(days=30)
        
        scorecard = calculate_overall_scorecard(db, start_date=start_date, end_date=end_date)
        print(f"   Scorecard: {scorecard}")
        
        assert "total_score" in scorecard
        assert "rating" in scorecard
        print("   ✅ Scorecard calculation successful")

        # 2. Test PDF Generation
        print("\n2. Testing PDF Generation...")
        pdf_buffer = generate_scorecard_pdf(scorecard, "Test Division", "Last 30 Days")
        pdf_bytes = pdf_buffer.getvalue()
        print(f"   PDF Size: {len(pdf_bytes)} bytes")
        
        assert len(pdf_bytes) > 0
        assert pdf_bytes.startswith(b'%PDF')
        print("   ✅ PDF generation successful")

        # 3. Test CSV Export
        print("\n3. Testing CSV Export...")
        csv_buffer = generate_request_export_csv(db, start_date, end_date)
        csv_content = csv_buffer.getvalue()
        print(f"   CSV Length: {len(csv_content)} chars")
        print(f"   CSV Preview: {csv_content[:100]}...")
        
        assert "Request ID" in csv_content
        print("   ✅ CSV export successful")
        
        print("\n✅ Verification Complete!")
        
    except Exception as e:
        print(f"\n❌ Verification Failed: {e}")
        import traceback
        with open("verification_error.txt", "w") as f:
            traceback.print_exc(file=f)
    finally:
        db.close()

if __name__ == "__main__":
    verify_analytics()
