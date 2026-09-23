import os
import psycopg2

db_url = "postgresql://postgres.soxcyhefpsltzpudonkx:%25K-3PpjKnptctRZ@aws-1-eu-west-1.pooler.supabase.com:6543/postgres"

def clear_data():
    conn = psycopg2.connect(db_url)
    cur = conn.cursor()
    
    tables = [
        'inventory_activitylog',
        'inventory_inventorytransaction',
        'inventory_stock',
        'inventory_product',
        'inventory_category',
        'inventory_color',
        'inventory_size',
        'inventory_partner',
    ]
    
    for table in tables:
        try:
            print(f"Clearing {table}...")
            cur.execute(f"TRUNCATE TABLE {table} CASCADE;")
        except Exception as e:
            print(f"Error on {table}: {e}")
            conn.rollback()
        else:
            conn.commit()
            
    cur.close()
    conn.close()
    print("All operational data cleared successfully on the remote database!")

if __name__ == "__main__":
    clear_data()
