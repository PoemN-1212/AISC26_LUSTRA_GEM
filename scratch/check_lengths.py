import os
from sqlalchemy import create_engine, text

engine = create_engine('postgresql+psycopg2://gem_admin:gem_secret_password@localhost:5432/gem_database')
with engine.connect() as conn:
    for col in ['source_type', 'source_id', 'doc_id', 'type', 'context', 'verifier_status', 'model_name']:
        m_len = conn.execute(text(f"SELECT MAX(LENGTH(CAST({col} AS TEXT))) FROM extracted_skills;")).scalar()
        print(f"Max length of {col}: {m_len}")
        if m_len and m_len > 20:
            sample = conn.execute(text(f"SELECT DISTINCT {col} FROM extracted_skills WHERE LENGTH(CAST({col} AS TEXT)) > 20 LIMIT 5;")).fetchall()
            print(f"   -> Samples > 20: {[r[0] for r in sample]}")
