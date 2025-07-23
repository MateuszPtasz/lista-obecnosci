# test_main.py - uproszczony backend do testowania

from fastapi import FastAPI, Body, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from config import EMAIL_CONFIG
import schemas
from email_service import send_report_email as send_report_service

app = FastAPI()

# Middleware CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/")
def root():
    return {"message": "Test API dla emaili"}

@app.post("/send-report-email")
async def send_report_email_endpoint(email_data: schemas.EmailReport):
    """Endpoint do wysyłania raportów przez email"""
    return send_report_service(
        to_email=email_data.to_email,
        subject=email_data.subject,
        report_type=email_data.report_type,
        report_data=email_data.report_data,
        employee_name=email_data.employee_name,
        date_range=email_data.date_range
    )

@app.get("/email-config")
async def get_email_config():
    """Endpoint do pobierania konfiguracji email (bez poufnych danych)"""
    return {
        "enabled": EMAIL_CONFIG["enabled"],
        "smtp_server": EMAIL_CONFIG["smtp_server"],
        "smtp_port": EMAIL_CONFIG["smtp_port"],
        "sender_name": EMAIL_CONFIG["sender_name"],
        "sender_email": EMAIL_CONFIG["sender_email"],
        "configured": bool(EMAIL_CONFIG["smtp_username"] and EMAIL_CONFIG["smtp_password"])
    }

@app.post("/email-config")
async def update_email_config(config_data: dict = Body(...)):
    """Endpoint do aktualizacji konfiguracji email"""
    try:
        # Aktualizuj tylko bezpieczne ustawienia
        if "enabled" in config_data:
            EMAIL_CONFIG["enabled"] = bool(config_data["enabled"])
        if "sender_name" in config_data:
            EMAIL_CONFIG["sender_name"] = str(config_data["sender_name"])
        if "sender_email" in config_data:
            EMAIL_CONFIG["sender_email"] = str(config_data["sender_email"])
        if "smtp_server" in config_data:
            EMAIL_CONFIG["smtp_server"] = str(config_data["smtp_server"])
        if "smtp_port" in config_data:
            EMAIL_CONFIG["smtp_port"] = int(config_data["smtp_port"])
        
        return {
            "success": True,
            "message": "Konfiguracja email została zaktualizowana",
            "config": {
                "enabled": EMAIL_CONFIG["enabled"],
                "sender_name": EMAIL_CONFIG["sender_name"],
                "sender_email": EMAIL_CONFIG["sender_email"]
            }
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Błąd aktualizacji konfiguracji email: {str(e)}")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8001)
