from database import engine
import sqlalchemy as sa

# Dodaj nowe kolumny do tabeli employees
with engine.connect() as conn:
    # Dodaj kolumnę password_hash
    conn.execute(sa.text("""
        ALTER TABLE employees 
        ADD COLUMN password_hash TEXT;
    """))
    
    # Dodaj kolumnę is_admin
    conn.execute(sa.text("""
        ALTER TABLE employees 
        ADD COLUMN is_admin BOOLEAN DEFAULT FALSE;
    """))
    
    conn.commit()
    
print("✅ Dodano nowe kolumny do tabeli employees!")
