"""
Add SubDepartments to existing database
Migrates existing data by adding subdepartment structure
"""
from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker
import sys
sys.path.insert(0, '.')

from app.models import Base, Division, Department, SubDepartment
from app.database import engine, SessionLocal

def add_subdepartments():
    db = SessionLocal()
    
    try:
        print("🔧 Adding SubDepartment table to database...")
        
        # Create the subdepartments table if it doesn't exist
        Base.metadata.create_all(bind=engine)
        
        print("✅ SubDepartment table created/verified")
        
        # Get divisions
        ems_division = db.query(Division).filter(Division.name.like("%EMS%")).first()
        medcom_division = db.query(Division).filter(Division.name.like("%MEDCOM%")).first()
        finance_division = db.query(Division).filter(Division.name.like("%Finance%")).first()
        hr_division = db.query(Division).filter(Division.name.like("%HR%")).first()
        
        if not ems_division or not medcom_division:
            print("⚠️  Warning: EMS or MEDCOM Division not found. Creating them...")
            if not ems_division:
                ems_division = Division(name="EMS Division", type="INCOME_GENERATING", description="Emergency Medical Services")
                db.add(ems_division)
            if not medcom_division:
                medcom_division = Division(name="MEDCOM Division", type="INCOME_GENERATING", description="Medical Commerce")
                db.add(medcom_division)
            db.flush()
        
        print(f"\n📁 Found Divisions:")
        print(f"  - EMS Division (ID: {ems_division.id if ems_division else 'N/A'})")
        print(f"  - MEDCOM Division (ID: {medcom_division.id if medcom_division else 'N/A'})")
        print(f"  - Finance Division (ID: {finance_division.id if finance_division else 'N/A'})")
        print(f"  - HR Division (ID: {hr_division.id if hr_division else 'N/A'})")
        
        # Define department structure with subdepartments
        dept_structure = {
            # Finance Department (under Finance Division)
            "Finance": {
                "division": finance_division,
                "description": "Financial Management",
                "subdepartments": [
                    "Senior Revenue and Collection Accountant",
                    "Costing Accountant",
                    "Store Officer",
                    "Senior Payment and Disbursement Accountant",
                    "Junior Accountant",
                    "Cashier"
                ]
            },
            # HR Department (under HR Division)
            "HR": {
                "division": hr_division,
                "description": "Human Resources",
                "subdepartments": [
                    "Office Assistant",
                    "Legal Advisor",
                    "Procurement",
                    "IT Department",
                    "Maintenance",
                    "Communication Officer"
                ]
            },
            # Comprehensive Ambulance Service Department (under EMS Division)
            "Comprehensive Ambulance Service": {
                "division": ems_division,
                "description": "Ambulance operations and emergency response",
                "subdepartments": [
                    "Fleet Head",
                    "Ambulance Crew Head",
                    "Dispatch Supervisor"
                ]
            },
            # CPD Short Term Training Department (under EMS Division)
            "CPD Short Term Training": {
                "division": ems_division,
                "description": "Continuing Professional Development and Short Term Training",
                "subdepartments": [
                    "CPD Coordinator",
                    "Short Term Training Lead"
                ]
            },
            # Vocational Training (under EMS Division)
            "Vocational Training": {
                "division": ems_division,
                "description": "Vocational and professional training programs",
                "subdepartments": [
                    "Dean",
                    "Vice Dean"
                ]
            },
            # Medical Equipment Production Department (under MEDCOM Division)
            "Medical Equipment Production": {
                "division": medcom_division,
                "description": "Production of medical equipment and supplies",
                "subdepartments": [
                    "Ambulance Outfitting",
                    "First Aid Kit Production"
                ]
            },
            # Pharmaceutical Import Department (under MEDCOM Division)
            "Pharmaceutical Import": {
                "division": medcom_division,
                "description": "Pharmaceutical procurement and distribution",
                "subdepartments": [
                    "Supplies Coordinator",
                    "Marketing and Sales"
                ]
            }
        }
        
        print("\n🏢 Creating/Updating Departments and SubDepartments...")
        
        for dept_name, dept_info in dept_structure.items():
            division = dept_info["division"]
            
            if not division:
                print(f"  ⚠️  Skipping {dept_name} - Division not found")
                continue
            
            # Check if department exists
            department = db.query(Department).filter(
                Department.name == dept_name,
                Department.division_id == division.id
            ).first()
            
            if not department:
                # Create new department
                department = Department(
                    name=dept_name,
                    division_id=division.id,
                    description=dept_info.get("description", "")
                )
                db.add(department)
                db.flush()
                print(f"\n  ✅ Created Department: {dept_name} (under {division.name})")
            else:
                print(f"\n  ℹ️  Department exists: {dept_name}")
            
            # Add subdepartments
            for subdept_name in dept_info["subdepartments"]:
                # Check if subdepartment exists
                existing_subdept = db.query(SubDepartment).filter(
                    SubDepartment.name == subdept_name,
                    SubDepartment.department_id == department.id
                ).first()
                
                if not existing_subdept:
                    subdept = SubDepartment(
                        name=subdept_name,
                        department_id=department.id,
                        description=f"{subdept_name} under {dept_name}"
                    )
                    db.add(subdept)
                    print(f"    ✅ Added SubDepartment: {subdept_name}")
                else:
                    print(f"    ℹ️  SubDepartment exists: {subdept_name}")
        
        db.commit()
        
        # Statistics
        total_subdepts = db.query(SubDepartment).count()
        total_depts = db.query(Department).count()
        
        print("\n" + "="*70)
        print("✅ MIGRATION COMPLETE!")
        print("="*70)
        print(f"📊 Statistics:")
        print(f"  - Total Departments: {total_depts}")
        print(f"  - Total SubDepartments: {total_subdepts}")
        print("="*70)
        
        print("\n💡 Next Steps:")
        print("  1. Restart the backend server to apply model changes")
        print("  2. Update frontend to display subdepartments")
        print("  3. Test the new request form with subdepartment selection")
        
    except Exception as e:
        print(f"\n❌ Error: {e}")
        import traceback
        traceback.print_exc()
        db.rollback()
    finally:
        db.close()

if __name__ == "__main__":
    add_subdepartments()
