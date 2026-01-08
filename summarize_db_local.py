import re

def summarize_db(filename):
    with open(filename, 'r', encoding='utf-16') as f:
        content = f.read()
    
    divisions = re.findall(r'ID: \d+ \| Name: (.*?) \| Type: (.*)', content)
    departments = re.findall(r'ID: \d+ \| Name: (.*?) \| Division ID: (\d+)', content)
    subdepts = re.findall(r'ID: \d+ \| Name: (.*?) \| Department ID: (\d+)', content)
    
    print(f"Total Divisions: {len(divisions)}")
    for name, dtype in divisions:
        print(f"  - {name} ({dtype})")
        
    print(f"\nTotal Departments: {len(departments)}")
    # Print first 5 depts
    for name, div_id in departments[:5]:
        print(f"  - {name} (Div ID: {div_id})")
    if len(departments) > 5:
        print(f"  ... and {len(departments)-5} more")
        
    print(f"\nTotal Sub-Departments: {len(subdepts)}")
    # Print first 5 subdepts
    for name, dept_id in subdepts[:5]:
        print(f"  - {name} (Dept ID: {dept_id})")
    if len(subdepts) > 5:
        print(f"  ... and {len(subdepts)-5} more")

if __name__ == "__main__":
    summarize_db('db_local_correct.txt')
