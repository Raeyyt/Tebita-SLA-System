"""
Database initialization script for Tebita SLA System
Creates initial divisions, departments, and admin user
"""

from app.database import SessionLocal, engine
from app.models import Base, User, Division, Department, UserRole, DivisionType
from app.auth import get_password_hash

# Create all tables
Base.metadata.create_all(bind=engine)

db = SessionLocal()

try:
    # Check if data already exists
    existing_user = db.query(User).first()
    if existing_user:
        print("Database already initialized!")
        exit(0)

    # Create Divisions
    print("Creating divisions...")
    
    # Income Generating Divisions
    ems_division = Division(
        name="EMS Division",
        type=DivisionType.INCOME_GENERATING,
        description="Emergency Medical Services - Training and Ambulance Operations"
    )
    db.add(ems_division)
    
    medical_equipment = Division(
        name="Medical Equipment Production and Imports",
        type=DivisionType.INCOME_GENERATING,
        description="Production and import of medical equipment"
    )
    db.add(medical_equipment)
    
    # Support Divisions
    finance = Division(
        name="Finance",
        type=DivisionType.SUPPORT,
        description="Financial management and accounting"
    )
    db.add(finance)
    
    hr = Division(
        name="HR",
        type=DivisionType.SUPPORT,
        description="Human Resources and Procurement"
    )
    db.add(hr)
    
    ict = Division(
        name="ICT",
        type=DivisionType.SUPPORT,
        description="Information and Communication Technology"
    )
    db.add(ict)
    
    sales_marketing = Division(
        name="Sales & Marketing",
        type=DivisionType.SUPPORT,
        description="Sales and marketing operations"
    )
    db.add(sales_marketing)
    
    maintenance = Division(
        name="Maintenance",
        type=DivisionType.SUPPORT,
        description="Facility and equipment maintenance"
    )
    db.add(maintenance)
    
    communication = Division(
        name="Communication & Public Relations",
        type=DivisionType.SUPPORT,
        description="Communications and public relations"
    )
    db.add(communication)
    
    db.flush()  # Get division IDs
    
    # Create Departments
    print("Creating departments...")
    
    # EMS Division Departments
    cpd_training = Department(
        name="Short-term CPD Training",
        division_id=ems_division.id,
        description="Continuing Professional Development training programs"
    )
    db.add(cpd_training)
    
    longterm_training = Department(
        name="Long-term Training",
        division_id=ems_division.id,
        description="Extended training programs"
    )
    db.add(longterm_training)
    
    ambulance_ops = Department(
        name="Ambulance Operations (Fleet)",
        division_id=ems_division.id,
        description="Ambulance fleet management and operations"
    )
    db.add(ambulance_ops)
    
    # Finance Departments
    cost_unit = Department(
        name="Cost Unit",
        division_id=finance.id,
        description="Cost analysis and management"
    )
    db.add(cost_unit)
    
    payment = Department(
        name="Payment",
        division_id=finance.id,
        description="Payment processing"
    )
    db.add(payment)
    
    collection = Department(
        name="Collection",
        division_id=finance.id,
        description="Revenue collection"
    )
    db.add(collection)
    
    junior_accountant = Department(
        name="Junior Accountant",
        division_id=finance.id,
        description="Junior accounting staff"
    )
    db.add(junior_accountant)
    
    cashier = Department(
        name="Cashier",
        division_id=finance.id,
        description="Cash handling and management"
    )
    db.add(cashier)
    
    db.flush()
    
    # Create Admin User
    print("Creating admin user...")
    admin = User(
        username="admin",
        full_name="System Administrator",
        email="admin@tebita.com",
        hashed_password=get_password_hash("admin123"),
        role=UserRole.ADMIN,
        is_active=True
    )
    db.add(admin)
    
    # Create Second Admin User
    admin2 = User(
        username="rtxyz",
        full_name="System Administrator 2",
        email="rtxyz@tebita.com",
        hashed_password=get_password_hash("rtxyz123"),
        role=UserRole.ADMIN,
        is_active=True
    )
    db.add(admin2)
    
    # Create M&E Staff User
    me_staff = User(
        username="me_staff",
        full_name="M&E Officer",
        email="me@tebita.com",
        hashed_password=get_password_hash("me123"),
        role=UserRole.ME_STAFF,
        is_active=True
    )
    db.add(me_staff)
    
    # Create Division Staff User (EMS)
    division_staff = User(
        username="ems_staff",
        full_name="EMS Division Manager",
        email="ems@tebita.com",
        hashed_password=get_password_hash("ems123"),
        role=UserRole.DIVISION_STAFF,
        division_id=ems_division.id,
        is_active=True
    )
    db.add(division_staff)
    
    # Create Support Staff User (HR)
    support_staff = User(
        username="hr_staff",
        full_name="HR Manager",
        email="hr@tebita.com",
        hashed_password=get_password_hash("hr123"),
        role=UserRole.SUPPORT_STAFF,
        division_id=hr.id,
        is_active=True
    )
    db.add(support_staff)
    
    db.commit()
    
    print("\n✅ Database initialized successfully!")
    print("\n👤 Default user accounts:")
    print("=" * 50)
    print("1. Admin #1:")
    print("   Username: admin")
    print("   Password: admin123")
    print("\n2. Admin #2:")
    print("   Username: rtxyz")
    print("   Password: rtxyz123")
    print("\n3. M&E Staff:")
    print("   Username: me_staff")
    print("   Password: me123")
    print("\n4. EMS Division Staff:")
    print("   Username: ems_staff")
    print("   Password: ems123")
    print("\n5. HR Support Staff:")
    print("   Username: hr_staff")
    print("   Password: hr123")
    print("=" * 50)
    
except Exception as e:
    print(f"❌ Error: {e}")
    db.rollback()
    raise
finally:
    db.close()
