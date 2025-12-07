import sqlite3

def add_subdepartment_column():
    """Add subdepartment_id column to users table if it doesn't exist"""
    conn = sqlite3.connect('tebita.db')
    cursor = conn.cursor()
    
    try:
        # Check if column exists
        cursor.execute("PRAGMA table_info(users)")
        columns = cursor.fetchall()
        column_names = [col[1] for col in columns]
        
        if 'subdepartment_id' not in column_names:
            print("Adding subdepartment_id column to users table...")
            cursor.execute("""
                ALTER TABLE users 
                ADD COLUMN subdepartment_id INTEGER 
                REFERENCES subdepartments(id)
            """)
            conn.commit()
            print("✓ Successfully added subdepartment_id column")
        else:
            print("✓ subdepartment_id column already exists")
            
    except Exception as e:
        print(f"Error: {e}")
        conn.rollback()
    finally:
        conn.close()

if __name__ == "__main__":
    add_subdepartment_column()
