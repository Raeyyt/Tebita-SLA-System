import sqlite3
import json

db_path = r"c:\Users\raeyy\OneDrive\Desktop\Final project\Tebita-SLA-System\backend\tebita.db"

try:
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    # Get the most recent request with items
    cursor.execute("""
        SELECT r.request_id, r.attachments, r.id
        FROM requests r
        ORDER BY r.created_at DESC 
        LIMIT 5
    """)
    
    requests = cursor.fetchall()
    
    for req_id, attachments, id in requests:
        print(f"\n{'='*60}")
        print(f"Request ID: {req_id} (DB ID: {id})")
        print(f"Attachments Type: {type(attachments)}")
        print(f"Attachments Value: {repr(attachments)}")
        
        # Get items for this request
        cursor.execute("SELECT id, item_description, attachment_filename, attachment_path FROM request_items WHERE request_id = ?", (id,))
        items = cursor.fetchall()
        
        print(f"\nNumber of items: {len(items)}")
        for item_id, desc, filename, path in items:
            print(f"  Item {item_id}:")
            print(f"    Description: {desc[:50] if desc else 'None'}...")
            print(f"    Attachment Filename: {filename}")
            print(f"    Attachment Path: {path}")
        
    conn.close()
    print("\n" + "="*60)
    
except Exception as e:
    print(f"Error: {e}")
    import traceback
    traceback.print_exc()
