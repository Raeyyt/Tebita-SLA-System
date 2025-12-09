import sqlite3

def inspect_db():
    print("Connecting to tebita.db...")
    conn = sqlite3.connect('tebita.db')
    cursor = conn.cursor()
    
    print("Columns in 'users' table:")
    try:
        cursor.execute("PRAGMA table_info(users)")
        columns = cursor.fetchall()
        if not columns:
            print("Table 'users' not found!")
        for col in columns:
            print(col)
    except Exception as e:
        print(f"Error: {e}")
        
    conn.close()

if __name__ == "__main__":
    inspect_db()
