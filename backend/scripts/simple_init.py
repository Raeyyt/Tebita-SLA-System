"""
Enhanced database initialization with demo data - no env dependencies
"""
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from passlib.context import CryptContext
from datetime import datetime, timedelta
import random

# Direct imports
import sys
sys.path.insert(0, '.')

from app.models import (
    Base, User, Division, Department, Request, RequestItem,
    UserRole, DivisionType, Priority, RequestStatus, ResourceType
)

# Create engine directly
engine = create_engine("sqlite:///./tebita.db", connect_args={"check_same_thread": False})
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Password hashing using pbkdf2_sha256 (no binary dependencies)
pwd_context = CryptContext(schemes=["pbkdf2_sha256"], deprecated="auto")

def get_password_hash(password: str) -> str:
    return pwd_context.hash(password)

# Create all tables
Base.metadata.create_all(bind=engine)

db = SessionLocal()

try:
    # Check if data already exists
    existing_user = db.query(User).first()
    if existing_user:
        print("Database already initialized!")
        print("\nTo reset, delete tebita.db and run this script again.")
        exit(0)

    # ============================================================================
    # CREATE DIVISIONS
    # ============================================================================
    print("Creating divisions...")
    
    ems_division = Division(
        name="EMS Division",
        type=DivisionType.INCOME_GENERATING,
        description="Emergency Medical Services"
    )
    db.add(ems_division)
    
    medcom_division = Division(
        name="MEDCOM Division",
        type=DivisionType.INCOME_GENERATING,
        description="Medical Commerce and Supplies"
    )
    db.add(medcom_division)
    
    finance = Division(
        name="Finance",
        type=DivisionType.SUPPORT,
        description="Financial management"
    )
    db.add(finance)
    
    hr = Division(
        name="HR",
        type=DivisionType.SUPPORT,
        description="Human Resources"
    )
    db.add(hr)
    
    ict = Division(
        name="ICT",
        type=DivisionType.SUPPORT,
        description="Information Technology"
    )
    db.add(ict)
    
    logistics = Division(
        name="Logistics",
        type=DivisionType.SUPPORT,
        description="Supply Chain and Logistics"
    )
    db.add(logistics)
    
    db.flush()
    
    # ============================================================================
    # CREATE DEPARTMENTS
    # ============================================================================
    print("Creating departments...")
    
    # EMS Departments
    ems_operations = Department(
        name="EMS Operations",
        division_id=ems_division.id,
        description="Emergency response operations"
    )
    db.add(ems_operations)
    
    ems_dispatch = Department(
        name="Dispatch Center",
        division_id=ems_division.id,
        description="Emergency dispatch and coordination"
    )
    db.add(ems_dispatch)
    
    # MEDCOM Departments
    pharmacy = Department(
        name="Pharmacy",
        division_id=medcom_division.id,
        description="Pharmaceutical services"
    )
    db.add(pharmacy)
    
    medical_supplies = Department(
        name="Medical Supplies",
        division_id=medcom_division.id,
        description="Medical equipment and supplies"
    )
    db.add(medical_supplies)
    
    # Support Departments
    hr_dept = Department(
        name="HR Department",
        division_id=hr.id,
        description="Human resources management"
    )
    db.add(hr_dept)
    
    finance_dept = Department(
        name="Finance Department",
        division_id=finance.id,
        description="Financial operations"
    )
    db.add(finance_dept)
    
    ict_dept = Department(
        name="ICT Department",
        division_id=ict.id,
        description="IT support and infrastructure"
    )
    db.add(ict_dept)
    
    logistics_dept = Department(
        name="Logistics Department",
        division_id=logistics.id,
        description="Supply chain management"
    )
    db.add(logistics_dept)
    
    db.flush()
    
    # ============================================================================
    # CREATE USERS
    # ============================================================================
    print("Creating users...")
    
    # Admin Users
    admin = User(
        username="admin",
        full_name="System Administrator",
        email="admin@tebita.com",
        hashed_password=get_password_hash("password123"),
        role=UserRole.ADMIN,
        is_active=True
    )
    db.add(admin)
    
    # M&E Staff
    me_staff = User(
        username="me_staff",
        full_name="M&E Officer",
        email="me@tebita.com",
        hashed_password=get_password_hash("password123"),
        role=UserRole.ME_STAFF,
        is_active=True
    )
    db.add(me_staff)
    
    # Leadership
    ceo = User(
        username="ceo",
        full_name="Chief Executive Officer",
        email="ceo@tebita.com",
        hashed_password=get_password_hash("password123"),
        role=UserRole.LEADERSHIP,
        is_active=True
    )
    db.add(ceo)
    
    # EMS Staff
    ems_manager = User(
        username="ems_manager",
        full_name="EMS Manager",
        email="ems_manager@tebita.com",
        hashed_password=get_password_hash("password123"),
        role=UserRole.DIVISION_STAFF,
        division_id=ems_division.id,
        department_id=ems_operations.id,
        is_active=True
    )
    db.add(ems_manager)
    
    dispatcher = User(
        username="dispatcher",
        full_name="Dispatch Supervisor",
        email="dispatcher@tebita.com",
        hashed_password=get_password_hash("password123"),
        role=UserRole.DIVISION_STAFF,
        division_id=ems_division.id,
        department_id=ems_dispatch.id,
        is_active=True
    )
    db.add(dispatcher)
    
    # MEDCOM Staff
    pharmacy_head = User(
        username="pharmacy_head",
        full_name="Pharmacy Manager",
        email="pharmacy@tebita.com",
        hashed_password=get_password_hash("password123"),
        role=UserRole.DIVISION_STAFF,
        division_id=medcom_division.id,
        department_id=pharmacy.id,
        is_active=True
    )
    db.add(pharmacy_head)
    
    supplies_officer = User(
        username="supplies_officer",
        full_name="Medical Supplies Officer",
        email="supplies@tebita.com",
        hashed_password=get_password_hash("password123"),
        role=UserRole.DIVISION_STAFF,
        division_id=medcom_division.id,
        department_id=medical_supplies.id,
        is_active=True
    )
    db.add(supplies_officer)
    
    # Support Staff
    hr_manager = User(
        username="hr_manager",
        full_name="HR Manager",
        email="hr@tebita.com",
        hashed_password=get_password_hash("password123"),
        role=UserRole.SUPPORT_STAFF,
        division_id=hr.id,
        department_id=hr_dept.id,
        is_active=True
    )
    db.add(hr_manager)
    
    finance_officer = User(
        username="finance_officer",
        full_name="Finance Officer",
        email="finance@tebita.com",
        hashed_password=get_password_hash("password123"),
        role=UserRole.SUPPORT_STAFF,
        division_id=finance.id,
        department_id=finance_dept.id,
        is_active=True
    )
    db.add(finance_officer)
    
    ict_support = User(
        username="ict_support",
        full_name="ICT Support Specialist",
        email="ict@tebita.com",
        hashed_password=get_password_hash("password123"),
        role=UserRole.SUPPORT_STAFF,
        division_id=ict.id,
        department_id=ict_dept.id,
        is_active=True
    )
    db.add(ict_support)
    
    logistics_manager = User(
        username="logistics_manager",
        full_name="Logistics Manager",
        email="logistics@tebita.com",
        hashed_password=get_password_hash("password123"),
        role=UserRole.SUPPORT_STAFF,
        division_id=logistics.id,
        department_id=logistics_dept.id,
        is_active=True
    )
    db.add(logistics_manager)
    
    db.flush()
    
    # ============================================================================
    # CREATE DEMO REQUESTS
    # ============================================================================
    print("Creating demo requests...")
    
    request_templates = [
        {
            "requester": ems_manager,
            "assigned_div": finance,
            "assigned_dept": finance_dept,
            "resource_type": ResourceType.FINANCE,
            "description": "Budget approval for new ambulance purchase",
            "priority": Priority.HIGH,
            "status": RequestStatus.PENDING
        },
        {
            "requester": dispatcher,
            "assigned_div": ict,
            "assigned_dept": ict_dept,
            "resource_type": ResourceType.ICT,
            "description": "Dispatch system software upgrade needed urgently",
            "priority": Priority.HIGH,
            "status": RequestStatus.IN_PROGRESS
        },
        {
            "requester": pharmacy_head,
            "assigned_div": logistics,
            "assigned_dept": logistics_dept,
            "resource_type": ResourceType.LOGISTICS,
            "description": "Medical supplies restocking - Emergency medications",
            "priority": Priority.HIGH,
            "status": RequestStatus.APPROVED
        },
        {
            "requester": ems_manager,
            "assigned_div": hr,
            "assigned_dept": hr_dept,
            "resource_type": ResourceType.HR,
            "description": "Recruitment request for 5 new paramedics",
            "priority": Priority.MEDIUM,
            "status": RequestStatus.IN_PROGRESS
        },
        {
            "requester": supplies_officer,
            "assigned_div": finance,
            "assigned_dept": finance_dept,
            "resource_type": ResourceType.FINANCE,
            "description": "Payment processing for medical equipment supplier",
            "priority": Priority.MEDIUM,
            "status": RequestStatus.COMPLETED
        },
        {
            "requester": finance_officer,
            "assigned_div": ict,
            "assigned_dept": ict_dept,
            "resource_type": ResourceType.ICT,
            "description": "Accounting software license renewal",
            "priority": Priority.LOW,
            "status": RequestStatus.PENDING
        },
        {
            "requester": hr_manager,
            "assigned_div": finance,
            "assigned_dept": finance_dept,
            "resource_type": ResourceType.FINANCE,
            "description": "Salary payment for new employees",
            "priority": Priority.HIGH,
            "status": RequestStatus.APPROVED
        },
        {
            "requester": dispatcher,
            "assigned_div": logistics,
            "assigned_dept": logistics_dept,
            "resource_type": ResourceType.LOGISTICS,
            "description": "Office supplies for dispatch center",
            "priority": Priority.LOW,
            "status": RequestStatus.COMPLETED
        },
        {
            "requester": ems_manager,
            "assigned_div": logistics,
            "assigned_dept": logistics_dept,
            "resource_type": ResourceType.FLEET,
            "description": "Ambulance maintenance and fuel supply",
            "priority": Priority.HIGH,
            "status": RequestStatus.IN_PROGRESS
        },
        {
            "requester": pharmacy_head,
            "assigned_div": hr,
            "assigned_dept": hr_dept,
            "resource_type": ResourceType.HR,
            "description": "Training request for pharmacy staff on new systems",
            "priority": Priority.MEDIUM,
            "status": RequestStatus.PENDING
        },
        {
            "requester": ict_support,
            "assigned_div": logistics,
            "assigned_dept": logistics_dept,
            "resource_type": ResourceType.LOGISTICS,
            "description": "Computer hardware and networking equipment",
            "priority": Priority.MEDIUM,
            "status": RequestStatus.APPROVED
        },
        {
            "requester": logistics_manager,
            "assigned_div": finance,
            "assigned_dept": finance_dept,
            "resource_type": ResourceType.FINANCE,
            "description": "Vendor payment for warehouse supplies",
            "priority": Priority.MEDIUM,
            "status": RequestStatus.COMPLETED
        },
        {
            "requester": ems_manager,
            "assigned_div": ict,
            "assigned_dept": ict_dept,
            "resource_type": ResourceType.ICT,
            "description": "GPS tracking system for ambulances",
            "priority": Priority.HIGH,
            "status": RequestStatus.IN_PROGRESS
        },
        {
            "requester": supplies_officer,
            "assigned_div": logistics,
            "assigned_dept": logistics_dept,
            "resource_type": ResourceType.LOGISTICS,
            "description": "Urgent oxygen cylinder refills needed",
            "priority": Priority.HIGH,
            "status": RequestStatus.APPROVED
        },
        {
            "requester": finance_officer,
            "assigned_div": hr,
            "assigned_dept": hr_dept,
            "resource_type": ResourceType.HR,
            "description": "Staff benefit deduction verification",
            "priority": Priority.LOW,
            "status": RequestStatus.PENDING
        },
    ]
    
    for i, template in enumerate(request_templates, 1):
        # Create request with days offset to show variety
        days_ago = (i - 1) * 2  # Spread requests over time
        created_date = datetime.now() - timedelta(days=days_ago)
        
        req = Request(
            request_id=f"REQ-{template['assigned_dept'].name[:3].upper()}-{created_date.strftime('%Y%m%d')}-{i:03d}",
            request_type=template['resource_type'].value,
            resource_type=template['resource_type'],
            requester_id=template['requester'].id,
            requester_division_id=template['requester'].division_id,
            requester_department_id=template['requester'].department_id,
            assigned_division_id=template['assigned_div'].id,
            assigned_department_id=template['assigned_dept'].id,
            priority=template['priority'],
            status=template['status'],
            description=template['description'],
            created_at=created_date,
            submitted_at=created_date
        )
        db.add(req)
        db.flush()
        
        # Add a sample item
        item = RequestItem(
            request_id=req.id,
            item_description=f"Item for {template['description'][:30]}...",
            quantity=1,
            notes="Sample request item"
        )
        db.add(item)
    
    db.commit()
    
    print("\n✅ Database initialized successfully!")
    print("\n" + "="*70)
    print("👤 LOGIN CREDENTIALS (All passwords: password123)")
    print("="*70)
    print(f"{'Role':<20} | {'Username':<20} | {'Division':<20}")
    print("-"*70)
    print(f"{'Admin':<20} | {'admin':<20} | {'-':<20}")
    print(f"{'M&E Staff':<20} | {'me_staff':<20} | {'-':<20}")
    print(f"{'Leadership':<20} | {'ceo':<20} | {'-':<20}")
    print(f"{'EMS Manager':<20} | {'ems_manager':<20} | {'EMS Division':<20}")
    print(f"{'Dispatcher':<20} | {'dispatcher':<20} | {'EMS Division':<20}")
    print(f"{'Pharmacy Manager':<20} | {'pharmacy_head':<20} | {'MEDCOM Division':<20}")
    print(f"{'Supplies Officer':<20} | {'supplies_officer':<20} | {'MEDCOM Division':<20}")
    print(f"{'HR Manager':<20} | {'hr_manager':<20} | {'HR':<20}")
    print(f"{'Finance Officer':<20} | {'finance_officer':<20} | {'Finance':<20}")
    print(f"{'ICT Support':<20} | {'ict_support':<20} | {'ICT':<20}")
    print(f"{'Logistics Manager':<20} | {'logistics_manager':<20} | {'Logistics':<20}")
    print("="*70)
    print(f"\n📊 Created {len(request_templates)} demo requests with proper sender/recipient data")
    print("="*70)
    
except Exception as e:
    print(f"❌ Error: {e}")
    import traceback
    traceback.print_exc()
    db.rollback()
finally:
    db.close()
