import sqlite3

def inspect_db():
    conn = sqlite3.connect('sql_app.db')
    cursor = conn.cursor()
    
    print("Columns in 'users' table:")
    cursor.execute("PRAGMA table_info(users)")
    columns = cursor.fetchall()
    for col in columns:
        print(col)
        
    conn.close()

if __name__ == "__main__":
    inspect_db()
