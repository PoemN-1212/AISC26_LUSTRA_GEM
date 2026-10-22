from sqlalchemy import create_engine, text

engine = create_engine('postgresql+psycopg2://gem_admin:gem_secret_password@localhost:5432/gem_database')
with engine.begin() as conn:
    res = conn.execute(text("DELETE FROM extracted_skills WHERE model_name = 'gemini-3.5-flash-lite'"))
    print(f"Cleaned {res.rowcount} gemini records.")
