from database import SessionLocal, engine
import models
from auth import get_password_hash

def create_test_admin():
    db = SessionLocal()
    try:
        # Sprawdź czy testowy admin już istnieje
        admin = db.query(models.Employee).filter(models.Employee.id == "admin").first()
        if not admin:
            # Utwórz testowego admina
            admin = models.Employee(
                id="admin",
                name="Administrator Systemu",
                password_hash=get_password_hash("admin123"),
                hourly_rate=0,
                is_admin=True
            )
            db.add(admin)
            db.commit()
            print("Utworzono testowe konto administratora:")
            print("Login: admin")
            print("Hasło: admin123")
        else:
            print("Konto administratora już istnieje")
    
    finally:
        db.close()

if __name__ == "__main__":
    create_test_admin()
