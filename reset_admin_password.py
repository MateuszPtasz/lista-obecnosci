from database import SessionLocal, engine
import models
from auth import get_password_hash

def reset_admin_password():
    db = SessionLocal()
    try:
        # Znajdź użytkownika admin
        admin = db.query(models.Employee).filter(models.Employee.id == "admin").first()
        
        if not admin:
            print("Nie znaleziono konta administratora")
            return
            
        # Ustaw nowe hasło
        admin.password_hash = get_password_hash("admin123")
        db.commit()
        print("Hasło administratora zostało zresetowane")
        
    except Exception as e:
        print(f"Błąd podczas resetowania hasła: {e}")
    finally:
        db.close()

if __name__ == "__main__":
    reset_admin_password()
