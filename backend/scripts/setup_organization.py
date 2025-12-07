"""
Populate Tebita Ambulance Organizational Structure
Run this script to set up divisions and departments according to company structure
"""
from sqlalchemy.orm import Session
from app.database import SessionLocal, engine
from app.models import Division, Department, DivisionType, Base

def clear_existing_data(db: Session):
    """Clear existing divisions and departments"""
    print("🗑️  Clearing existing divisions and departments...")
    db.query(Department).delete()
    db.query(Division).delete()
    db.commit()
    print("✅ Cleared existing data")

def create_organizational_structure(db: Session):
    """Create the complete organizational structure"""
    
    print("\n📊 Creating Divisions...")
    
    # 1. EMS Division (Income Generating)
    ems_division = Division(
        name="EMS Division",
        type=DivisionType.INCOME_GENERATING,
        description="Emergency Medical Services - Led by Deputy CEO & EMS Division Manager"
    )
    db.add(ems_division)
    db.flush()
    print(f"✅ Created: {ems_division.name}")
    
    # 2. MEDCOM Division (Income Generating)
    medcom_division = Division(
        name="MEDCOM Division",
        type=DivisionType.INCOME_GENERATING,
        description="Medical Equipment & Pharmaceutical - Led by Division Manager"
    )
    db.add(medcom_division)
    db.flush()
    print(f"✅ Created: {medcom_division.name}")
    
    # 3. Support Division
    support_division = Division(
        name="Support Division",
        type=DivisionType.SUPPORT,
        description="Administrative and Financial Support Services"
    )
    db.add(support_division)
    db.flush()
    print(f"✅ Created: {support_division.name}")
    
    db.commit()
    
    # ========================================
    # EMS DIVISION DEPARTMENTS
    # ========================================
    print("\n📁 Creating EMS Division Departments...")
    
    ems_departments = [
        {
            "name": "Comprehensive Ambulance Services",
            "description": "Led by Ambulance Operation Manager - Fleet, Crew, and Dispatch operations"
        },
        {
            "name": "CPD Short-Term Training",
            "description": "Led by Training Manager/CPD Director - Professional Development and Short-term Training"
        },
        {
            "name": "Vocational Training",
            "description": "Led by Dean & Vice Dean - Long-term vocational training programs"
        }
    ]
    
    for dept_data in ems_departments:
        dept = Department(
            name=dept_data["name"],
            division_id=ems_division.id,
            description=dept_data["description"]
        )
        db.add(dept)
        print(f"  ✅ {dept_data['name']}")
    
    # ========================================
    # MEDCOM DIVISION DEPARTMENTS
    # ========================================
    print("\n📁 Creating MEDCOM Division Departments...")
    
    medcom_departments = [
        {
            "name": "Medical Equipment Production Department",
            "description": "Led by Department Head - Production and manufacturing of medical equipment"
        },
        {
            "name": "Pharmaceutical Import Department",
            "description": "Led by Department Head - Import and distribution of pharmaceutical products"
        }
    ]
    
    for dept_data in medcom_departments:
        dept = Department(
            name=dept_data["name"],
            division_id=medcom_division.id,
            description=dept_data["description"]
        )
        db.add(dept)
        print(f"  ✅ {dept_data['name']}")
    
    # ========================================
    # SUPPORT DIVISION DEPARTMENTS
    # ========================================
    print("\n📁 Creating Support Division Departments...")
    
    support_departments = [
        {
            "name": "Human Resources (HR)",
            "description": "Led by Administrative Manager - HR, Legal, Procurement, IT, Maintenance, Communication"
        },
        {
            "name": "Finance Department",
            "description": "Led by Finance Manager - Revenue, Costing, Payment, and Disbursement"
        }
    ]
    
    for dept_data in support_departments:
        dept = Department(
            name=dept_data["name"],
            division_id=support_division.id,
            description=dept_data["description"]
        )
        db.add(dept)
        print(f"  ✅ {dept_data['name']}")
    
    db.commit()
    print("\n✅ All departments created successfully!")

def display_structure(db: Session):
    """Display the created organizational structure"""
    print("\n" + "="*60)
    print("📋 TEBITA AMBULANCE ORGANIZATIONAL STRUCTURE")
    print("="*60)
    
    divisions = db.query(Division).all()
    
    for division in divisions:
        print(f"\n🏢 {division.name} ({division.type})")
        print(f"   {division.description}")
        
        departments = db.query(Department).filter(
            Department.division_id == division.id
        ).all()
        
        for dept in departments:
            print(f"   📁 {dept.name}")
            if dept.description:
                print(f"      {dept.description}")
    
    print("\n" + "="*60)
    print(f"📊 Total: {len(divisions)} Divisions, {db.query(Department).count()} Departments")
    print("="*60 + "\n")

def main():
    """Main execution function"""
    print("🚀 Setting up Tebita Ambulance Organizational Structure\n")
    
    # Create tables if they don't exist
    Base.metadata.create_all(bind=engine)
    
    db = SessionLocal()
    
    try:
        # Clear existing data
        clear_existing_data(db)
        
        # Create new structure
        create_organizational_structure(db)
        
        # Display the structure
        display_structure(db)
        
        print("✅ Organizational structure setup complete!")
        print("👉 You can now use these divisions and departments in your requests\n")
        
    except Exception as e:
        print(f"\n❌ Error: {e}")
        db.rollback()
        raise
    finally:
        db.close()

if __name__ == "__main__":
    main()
