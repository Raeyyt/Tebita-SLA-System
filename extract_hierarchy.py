import re

def extract_hierarchy(filename, output_file):
    with open(filename, 'r', encoding='utf-16') as f:
        content = f.read()
    
    # Extract Divisions
    div_matches = re.findall(r'ID: (\d+) \| Name: (.*?) \| Type: (.*)', content)
    divisions = {m[0]: {"name": m[1], "departments": {}} for m in div_matches}
    
    # Extract Departments
    dept_matches = re.findall(r'ID: (\d+) \| Name: (.*?) \| Division ID: (\d+)', content)
    departments = {}
    for d_id, d_name, div_id in dept_matches:
        departments[d_id] = {"name": d_name, "subdepartments": []}
        if div_id in divisions:
            divisions[div_id]["departments"][d_id] = departments[d_id]
    
    # Extract Sub-Departments
    sub_matches = re.findall(r'ID: (\d+) \| Name: (.*?) \| Department ID: (\d+)', content)
    for s_id, s_name, dept_id in sub_matches:
        if dept_id in departments:
            departments[dept_id]["subdepartments"].append(s_name)
            
    # Write to file
    with open(output_file, 'w', encoding='utf-8') as f:
        for div_id, div in divisions.items():
            f.write(f"Division: {div['name']}\n")
            for dept_id, dept in div["departments"].items():
                f.write(f"  Department: {dept['name']}\n")
                for sub in dept["subdepartments"]:
                    f.write(f"    Sub-Department: {sub}\n")
            f.write("-" * 30 + "\n")

if __name__ == "__main__":
    extract_hierarchy('db_local_correct.txt', 'local_hierarchy_full.txt')
