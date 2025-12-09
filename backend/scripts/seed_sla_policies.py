"""
SLA Policy Seeder
Populates sla_policies table with comprehensive activity-specific SLA rules
Based on organizational requirements document
"""

import sqlite3
from pathlib import Path

def seed_sla_policies():
    db_path = Path(__file__).parent.parent / "tebita.db"
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    try:
        print("Seeding SLA Policies...")
        
        # Clear existing policies (for fresh seed)
        cursor.execute("DELETE FROM sla_policies")
        print("  - Cleared existing policies")
        
        policies = []
        
        # ===== FINANCE POLICIES =====
        print("\n📊 Finance Policies")
        policies.extend([
            # Payment Inquiries
            ("FINANCE", "Payment Inquiry - Urgent", "HIGH", 2, 24, "Supplier threatens service interruption, medical consumables shortage, or operational risk"),
            ("FINANCE", "Payment Inquiry - Routine", "MEDIUM", 4, 48, "Vendor status check, routine settlement, staff reimbursement follow-up"),
            ("FINANCE", "Payment Inquiry - Non-urgent", "LOW", 24, 120, "Historical reconfirmation, audit clarification, old payment check"),
            
            # Reports (Note: These are calendar-based, storing as hours for approximation)
            ("FINANCE", "Monthly Financial Report", "HIGH", 4, 120, "Monthly division financial report - due by 5th of following month"),
            ("FINANCE", "Quarterly Financial Report", "HIGH", 4, 288, "Quarterly report - due within 12 days after quarter end"),
            ("FINANCE", "Annual Financial Report", "HIGH", 4, 600, "Annual report - due within 25 days after fiscal year end"),
        ])
        
        # ===== STORE POLICIES =====
        print("📦 Store Policies")
        policies.extend([
            # Medical Consumables
            ("LOGISTICS", "Medical Consumables - Critical", "HIGH", 0.5, 1, "IV cannulas, gloves, O2 masks, syringes, wound dressings - 15-30 min response, 1 hr completion"),
            ("LOGISTICS", "Medical Consumables - Routine", "MEDIUM", 2, 24, "Daily/weekly consumables restock"),
            ("LOGISTICS", "Emergency Drugs", "HIGH", 0, 0.5, "Adrenaline, IV fluids, salbutamol, glucose, pain medicines - Immediate response, 30 min completion"),
            ("LOGISTICS", "Medical Equipment", "MEDIUM", 2, 24, "BP cuff, glucometer, suction machine parts, stethoscope"),
            
            # Spare Parts
            ("LOGISTICS", "Spare Parts - Critical", "HIGH", 0.5, 24, "Urgent spare parts for ambulance out of service - battery, alternator, tire, brake pads"),
            ("LOGISTICS", "Spare Parts - Scheduled", "MEDIUM", 4, 48, "Scheduled maintenance spare parts - filters, engine oil, belts"),
            ("LOGISTICS", "Spare Parts - Non-urgent", "LOW", 24, 72, "Non-urgent spare parts - interior fittings, non-essential accessories"),
            
            # Stationery
            ("LOGISTICS", "Stationery - Operational", "MEDIUM", 4, 24, "Patient care forms, PCR sheets, dispatch logs"),
            ("LOGISTICS", "Stationery - Administrative", "LOW", 24, 72, "Office A4 paper, pens, folders"),
        ])
        
        # ===== FLEET/MAINTENANCE POLICIES =====
        print("🚑 Fleet/Maintenance Policies")
        policies.extend([
            # Emergency & Critical
            ("FLEET", "Emergency Breakdown", "HIGH", 0.5, 4, "Mechanical breakdown during dispatch or patient transport - 30 min response, 2-4 hrs completion"),
            ("FLEET", "Critical Mechanical Failure", "HIGH", 1, 24, "Engine failure, brake failure, steering issues, transmission malfunction"),
            ("FLEET", "Light & Siren System Failure", "HIGH", 1, 12, "Beacon light, siren amplifier, speaker malfunction - safety critical"),
            ("FLEET", "Interior Sanitation & Deep Cleaning", "HIGH", 0.5, 2, "Biohazard contamination, spill cleanup - infection prevention protocol"),
            
            # Medical Equipment
            ("FLEET", "Medical Equipment Failure - Critical", "HIGH", 1, 12, "Defibrillator, suction machine, ventilator, oxygen system failure"),
            ("FLEET", "Medical Equipment Calibration", "MEDIUM", 72, 168, "Annual/periodic calibration for monitors, defibrillators, oxygen regulators"),
            
            # Preventive & Routine Maintenance
            ("FLEET", "Preventive Maintenance", "MEDIUM", 24, 48, "Scheduled servicing - oil change, filters, inspection"),
            ("FLEET", "Tire Replacement/Damage", "MEDIUM", 2, 24, "Tire puncture, worn-out tires, alignment issues"),
            ("FLEET", "Battery Issues", "MEDIUM", 2, 6, "Replacement of dead/weak battery"),
            ("FLEET", "Inverter/Power System Failure", "MEDIUM", 4, 24, "Power outlets, inverter, charging systems for medical devices"),
            ("FLEET", "AC/Ventilation Issues", "MEDIUM", 4, 48, "AC malfunction affecting patient comfort or safety"),
            ("FLEET", "Fuel System Maintenance", "MEDIUM", 2, 24, "Fuel pump issues, filter replacement"),
            
            # Minor Repairs
            ("FLEET", "Bodywork & Minor Damage", "LOW", 48, 168, "Bumper scratches, light repairs, repainting - only when ambulance off-call"),
        ])
        
        # ===== REFITTING POLICIES =====
        print("🔧 Refitting Policies")
        policies.extend([
            # Critical Safety
            ("FLEET", "Critical Safety Refitting", "HIGH", 2, 72, "Brake system, steering, suspension, structural welds - 1-3 days"),
            ("FLEET", "Oxygen System Refitting", "HIGH", 4, 48, "Piping, regulator installation, manifold, cylinder brackets"),
            ("FLEET", "Electrical & Power System Refitting", "HIGH", 4, 48, "Inverter, sockets, interior lighting, battery isolators"),
            ("FLEET", "Stretcher & Mounting System", "HIGH", 4, 24, "Stretcher base plate, locking mechanism"),
            ("FLEET", "Siren & Light Bar Refitting", "HIGH", 4, 24, "Emergency lights, siren unit, speaker alignment"),
            ("FLEET", "Medical Equipment Reinstallation", "HIGH", 4, 24, "Defibrillator brackets, suction, monitoring"),
            
            # Medium Priority Refitting
            ("FLEET", "Medical Cabinet & Interior Layout", "MEDIUM", 24, 168, "Cabinet repair, stretcher mounts, flooring, wall panels - 3-7 days"),
            ("FLEET", "HVAC/AC Ventilation Refitting", "MEDIUM", 24, 72, "AC repair, vents repositioning, cabin airflow"),
            ("FLEET", "Communication System Setup", "MEDIUM", 24, 48, "Radio, GPS, dispatch device mounting"),
            ("FLEET", "Fire Safety & IPC Installation", "MEDIUM", 24, 24, "Fire extinguisher mount, sanitation hardware"),
            
            # Low Priority Refitting
            ("FLEET", "Exterior Branding & Sticker Refitting", "LOW", 24, 96, "Logo, reflective markings, numbering"),
            ("FLEET", "Full Ambulance Refurbishment", "LOW", 48, 504, "Bodywork, repainting, rewiring, interior redesign - 10-21 days"),
        ])
        
        # ===== HR POLICIES =====
        print("👥 HR Policies")
        policies.extend([
            # Recruitment
            ("HR", "Recruitment - Critical Staffing Gap", "HIGH", 0, 168, "Urgent manpower gap affecting ambulance readiness - 3-7 days"),
            ("HR", "Recruitment - Key Roles", "HIGH", 24, 504, "Hiring for critical roles (EMT, Paramedic, Driver) - 14-21 days"),
            ("HR", "Recruitment - Routine", "MEDIUM", 48, 720, "Routine recruitment for admin/support roles - 21-30 days"),
            
            # Payroll
            ("HR", "Payroll Issue", "HIGH", 4, 24, "Payroll issue affecting staff payment"),
            ("HR", "Monthly Payroll", "HIGH", 0, 0, "Monthly payroll processing - due 25th monthly (calendar-based)"),
            
            # Other HR
            ("HR", "Contract Issuance", "HIGH", 24, 72, "Employment contract issuance - 3 days"),
            ("HR", "Disciplinary Case - Critical", "HIGH", 0, 48, "Critical disciplinary case requiring immediate attention - 24-48 hours"),
            ("HR", "Exit Clearance", "MEDIUM", 24, 168, "Exit clearance processing - 5-7 days"),
            ("HR", "HR Routine Request", "LOW", 48, 120, "Routine HR requests - 3-5 days"),
        ])
        
        # ===== PROCUREMENT POLICIES =====
        print("🛒 Procurement Policies")
        policies.extend([
            # Medical
            ("LOGISTICS", "Procurement - Medical Emergency", "HIGH", 0, 48, "Emergency medical items due to stock-out - 24-48 hours local purchase"),
            ("LOGISTICS", "Procurement - Medical Scheduled", "MEDIUM", 24, 120, "Scheduled monthly medical supplies - 3-5 days"),
            
            # Fleet Spares
            ("LOGISTICS", "Procurement - Spare Parts Critical", "HIGH", 1, 48, "Critical spare part for ambulance down - same day to 48 hours"),
            ("LOGISTICS", "Procurement - Spare Parts Scheduled", "MEDIUM", 24, 72, "Scheduled maintenance parts - 3 days"),
            
            # Equipment
            ("LOGISTICS", "Procurement - Equipment Critical", "HIGH", 0, 72, "Life-saving equipment malfunction - 24-72 hours"),
            ("LOGISTICS", "Procurement - Equipment Routine", "MEDIUM", 24, 240, "Regular replacement or upgrade - 5-10 days"),
            
            # Training
            ("LOGISTICS", "Procurement - Training Materials Urgent", "HIGH", 0, 48, "Items required for active training - 24-48 hours"),
            ("LOGISTICS", "Procurement - Training Scheduled", "MEDIUM", 24, 120, "Scheduled training materials - 3-5 days"),
        ])
        
        # ===== TRAINING POLICIES =====
        print("🎓 Training Policies")
        policies.extend([
            ("GENERAL", "Emergency Skills Refresher", "HIGH", 24, 72, "CPR, BLS, Trauma refresh based on incident - 24-48 hours response, 48-72 hours completion"),
            ("GENERAL", "New Staff Onboarding", "HIGH", 24, 120, "First aid, SOPs, ambulance protocols - 24 hours response, 3-5 days completion"),
            ("GENERAL", "Certification Issuance", "LOW", 48, 168, "Certification issuance after training - 2 days response, 7 days completion"),
            ("GENERAL", "Training Report Submission", "LOW", 120, 720, "Monthly training summary - 5 days response, monthly completion"),
            ("GENERAL", "Training Materials Development", "MEDIUM", 72, 240, "Guides, checklists, SOPs - 3 days response, 10 days completion"),
            ("GENERAL", "Simulation/Drills Planning", "MEDIUM", 72, 336, "Mass casualty, emergency drills - 3 days response, 7-14 days completion"),
        ])
        
        # ===== ADMIN POLICIES =====
        print("📋 Admin Policies")
        policies.extend([
            ("FACILITIES", "Office Supply Issuance", "MEDIUM", 0, 24, "Stationery, printer ink, PPE - same day response, 24 hours completion"),
            ("FACILITIES", "Office Repairs & Facility Issues", "HIGH", 1, 12, "Electricity, water, plumbing - 1 hour response, 2-12 hours completion"),
            ("FACILITIES", "Transport Arrangement", "MEDIUM", 3, 24, "Staff vehicle assignment - 3 hours response, same day completion"),
            ("GENERAL", "Visitor Management", "LOW", 1, 0, "Meeting arrangement, guest reception - 1 hour response, as scheduled"),
            ("GENERAL", "Document Handling", "LOW", 24, 72, "Filing, scanning, letters - 1 day response, 1-3 days completion"),
            ("GENERAL", "Uniform Issuance", "MEDIUM", 24, 72, "For ambulance crew and staff - 1 day response, 3 days completion"),
            ("GENERAL", "Staff Welfare Support", "HIGH", 2, 12, "Accommodation, incident support - 2 hours response, 12 hours completion"),
        ])
        
        # ===== GENERAL/OTHER =====
        print("📝 General Policies (Catch-all)")
        policies.extend([
            ("GENERAL", "General - Other", "HIGH", 2, 24, "Other high priority requests not categorized"),
            ("GENERAL", "General - Other", "MEDIUM", 8, 72, "Other medium priority requests not categorized"),
            ("GENERAL", "General - Other", "LOW", 24, 168, "Other low priority requests not categorized"),
        ])
        
        # Insert all policies
        print(f"\n💾 Inserting {len(policies)} SLA policies...")
        for resource_type, activity_type, priority, response_hrs, completion_hrs, description in policies:
            cursor.execute("""
                INSERT INTO sla_policies 
                (division_id, department_id, resource_type, activity_type, priority, 
                 response_time_hours, completion_time_hours, description, is_active)
                VALUES (NULL, NULL, ?, ?, ?, ?, ?, ?, 1)
            """, (resource_type, activity_type, priority, response_hrs, completion_hrs, description))
        
        conn.commit()
        print(f"\n✅ Successfully seeded {len(policies)} SLA policies!")
        
        # Show summary by category
        print("\n📊 Summary by Resource Type:")
        cursor.execute("""
            SELECT resource_type, COUNT(*) as count
            FROM sla_policies
            GROUP BY resource_type
            ORDER BY count DESC
        """)
        for row in cursor.fetchall():
            print(f"  • {row[0]}: {row[1]} policies")
        
    except Exception as e:
        conn.rollback()
        print(f"\n❌ Seeding failed: {e}")
        raise
    finally:
        conn.close()

if __name__ == "__main__":
    seed_sla_policies()
