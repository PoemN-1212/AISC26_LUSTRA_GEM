import os
import sys
import psycopg2
from psycopg2.extras import execute_values
from dotenv import load_dotenv

sys.stdout.reconfigure(encoding='utf-8')
env_path = os.path.join(os.getcwd(), ".env")
load_dotenv(env_path)

cld = os.getenv("CLOUD_DB_URL")
if not cld:
    print(f"CLOUD_DB_URL is not set in {env_path}!")
    exit(1)

conn_c = psycopg2.connect(cld, connect_timeout=30)
conn_l = psycopg2.connect(
    host=os.getenv("POSTGRES_HOST", "localhost"),
    port=int(os.getenv("POSTGRES_PORT", "5432")),
    user=os.getenv("POSTGRES_USER", "gem_admin"),
    password=os.getenv("POSTGRES_PASSWORD", "gem_secret_password"),
    dbname=os.getenv("POSTGRES_DB", "gem_database")
)

with conn_l.cursor() as cur_l:
    cur_l.execute("SELECT COUNT(*) FROM extracted_skills;")
    total_local = cur_l.fetchone()[0]
    print(f"Local extracted_skills count: {total_local:,}")

    cur_l.execute("""
        SELECT id, source_type, source_id, doc_id, title, evidence, skill, 
               type, context, start_char, end_char, verifier_status, rejection_reason, model_name, created_at
        FROM extracted_skills ORDER BY id;
    """)
    rows = cur_l.fetchall()

print(f"Syncing {len(rows):,} skills to Neon Cloud DB...")
with conn_c.cursor() as cur_c:
    cur_c.execute("TRUNCATE TABLE extracted_skills RESTART IDENTITY;")
    
    insert_sql = """
        INSERT INTO extracted_skills 
        (id, source_type, source_id, doc_id, title, evidence, skill, type, context, start_char, end_char, verifier_status, rejection_reason, model_name, created_at)
        VALUES %s;
    """
    batch_size = 3000
    for i in range(0, len(rows), batch_size):
        batch = rows[i:i + batch_size]
        execute_values(cur_c, insert_sql, batch)
        print(f"  -> Synced {min(i + batch_size, len(rows)):,}/{len(rows):,}...")
    
    cur_c.execute("SELECT setval(pg_get_serial_sequence('extracted_skills', 'id'), COALESCE(MAX(id), 1)) FROM extracted_skills;")
    conn_c.commit()

# Verify on Cloud
with conn_c.cursor() as cur_c:
    cur_c.execute("SELECT COUNT(*) FROM extracted_skills;")
    total_cloud = cur_c.fetchone()[0]
    cur_c.execute("SELECT verifier_status, COUNT(*) FROM extracted_skills GROUP BY verifier_status;")
    status_cloud = cur_c.fetchall()
    print(f"\n✅ Cloud Neon DB verification:")
    print(f"   • Total skills: {total_cloud:,}")
    print(f"   • Status breakdown: {status_cloud}")

conn_l.close()
conn_c.close()
