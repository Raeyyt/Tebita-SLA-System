from app.database import SessionLocal
from app.models import Request

db = SessionLocal()
r = db.query(Request).filter(Request.id == 42).first()

if r:
    print(f'Request ID: {r.request_id}')
    print(f'Status: {r.status}')
    print(f'Acknowledged at: {r.acknowledged_at}')
    print(f'Acknowledged by user ID: {r.acknowledged_by_user_id}')
    print(f'Completed at: {r.completed_at}')
else:
    print('Request 42 not found')

db.close()
