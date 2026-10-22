import sys, os
import psycopg2
from dotenv import load_dotenv

load_dotenv()
cld = os.getenv("CLOUD_DB_URL")
print("=== CLOUD NEON DB COLUMNS ===")
conn = psycopg2.connect(cld)
with conn.cursor() as cur:
    cur.execute("""
        SELECT column_name, data_type, character_maximum_length 
        FROM information_schema.columns 
        WHERE table_name = 'extracted_skills';
    """)
    for r in cur.fetchall():
        print(f"Cloud: {r[0]}: {r[1]} ({r[2]})")
conn.close()
