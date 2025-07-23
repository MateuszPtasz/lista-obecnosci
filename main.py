from fastapi import FastAPI, Depends, HTTPException, Body, Query
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from sqlalchemy.orm import Session
from datetime import datetime, timedelta, date
from pydantic import BaseModel
from fastapi.responses import JSONResponse
from sqlalchemy import func
import calendar
from typing import List
import os
import ast
import holidays

import models, schemas, database
from config import MOBILE_APP_CONFIG, CONFIG_VERSION, APP_VERSION_INFO, EMAIL_CONFIG

app = FastAPI()

PL_HOLIDAYS = holidays.Poland()

# Middleware CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # możesz tu podać konkretną domenę np. ["http://localhost:3000"]
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Serwowanie plików statycznych z folderu frontend
app.mount("/frontend", StaticFiles(directory="frontend"), name="frontend")

models.Base.metadata.create_all(bind=database.engine)

# Dependency
def get_db():
    db = database.SessionLocal()
    try:
        yield db
    finally:
        db.close()

@app.post("/send-report-email")
async def send_report_email(email_data: schemas.EmailReport):
    """Endpoint do wysyłania raportów przez email"""
    try:
        # Dekodowanie danych raportu z Base64
        report_bytes = base64.b64decode(email_data.report_data)
        
        # Określenie nazwy pliku i typu
        if email_data.report_type.lower() == "pdf":
            file_extension = "pdf"
            content_type = "application/pdf"
        else:
            file_extension = "csv"
            content_type = "text/csv"
        
        # Generowanie nazwy pliku
        timestamp = datetime.now().strftime("%Y-%m-%d_%H-%M")
        if email_data.employee_name:
            filename = f"Raport_{email_data.employee_name}_{timestamp}.{file_extension}"
        else:
            filename = f"Raport_obecnosci_{timestamp}.{file_extension}"
        
        # Generowanie treści emaila
        html_body = f"""
        <html>
        <body>
            <h2>📊 Raport Lista Obecności</h2>
            <p>Witaj!</p>
            <p>W załączeniu przesyłamy raport wygenerowany z systemu Lista Obecności.</p>
            
            <h3>📋 Szczegóły raportu:</h3>
            <ul>
                <li><strong>Typ raportu:</strong> {email_data.report_type.upper()}</li>
                {"<li><strong>Pracownik:</strong> " + email_data.employee_name + "</li>" if email_data.employee_name else ""}
                {"<li><strong>Okres:</strong> " + email_data.date_range + "</li>" if email_data.date_range else ""}
                <li><strong>Data wygenerowania:</strong> {datetime.now().strftime("%d.%m.%Y %H:%M")}</li>
            </ul>
            
            <p>📎 <strong>Załącznik:</strong> {filename}</p>
            
            <hr>
            <p style="color: #666; font-size: 12px;">
                Wiadomość została wygenerowana automatycznie przez system Lista Obecności.<br>
                Nie odpowiadaj na ten email.
            </p>
        </body>
        </html>
        """
        
        # Wysłanie emaila
        send_email(
            to_email=email_data.to_email,
            subject=email_data.subject,
            body=html_body,
            attachment_data=report_bytes,
            attachment_name=filename
        )
        
        return {
            "success": True,
            "message": f"Raport został wysłany na adres {email_data.to_email}",
            "filename": filename,
            "timestamp": datetime.now().isoformat()
        }
        
    except Exception as e:
        return {
            "success": False,
            "message": f"Błąd wysyłania raportu: {str(e)}"
        }

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


# Endpoint do wysyłania raportów przez email
@app.post("/send-report-email")
async def send_report_email_endpoint(email_data: schemas.EmailReport):
    """Endpoint do wysyłania raportów przez email"""
    try:
        from email_service import send_report_email as send_report_service
        return send_report_service(
            to_email=email_data.to_email,
            subject=email_data.subject,
            report_type=email_data.report_type,
            report_data=email_data.report_data,
            employee_name=email_data.employee_name,
            date_range=email_data.date_range
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Błąd wysyłania raportu: {str(e)}")


# Dependency
def get_db():
    db = database.SessionLocal()
    try:
        yield db
    finally:
        db.close()

@app.post("/start")
def start_shift(data: schemas.StartShift, db: Session = Depends(get_db)):
    new_log = models.AttendanceLog(
        worker_id=data.employee_id,
        start_time=data.czas_start,
        start_lat=data.lokalizacja_start.lat,
        start_lon=data.lokalizacja_start.lon
    )
    db.add(new_log)
    db.commit()
    db.refresh(new_log)
    return {"msg": "Shift started", "id": new_log.id}

@app.post("/stop")
def stop_shift(data: schemas.StopShift, db: Session = Depends(get_db)):
    log = db.query(models.AttendanceLog).filter(
        models.AttendanceLog.worker_id == data.employee_id,
        models.AttendanceLog.stop_time == None
    ).order_by(models.AttendanceLog.start_time.desc()).first()
    if not log:
        raise HTTPException(status_code=404, detail="No active shift found")
    log.stop_time = data.czas_stop
    log.stop_lat = data.lokalizacja_stop.lat
    log.stop_lon = data.lokalizacja_stop.lon
    db.commit()
    return {"msg": "Shift stopped", "duration_min": round((log.stop_time - log.start_time).total_seconds() / 60)}

@app.get("/shifts/{employee_id}")
def get_shifts(employee_id: int, db: Session = Depends(get_db)):
    shifts = db.query(models.Shift).filter(models.Shift.employee_id == employee_id).all()
    return shifts

@app.get("/logs/{worker_id}")
def get_logs(worker_id: str, db: Session = Depends(get_db)):
    logs = db.query(models.AttendanceLog).filter(models.AttendanceLog.worker_id == worker_id).all()
    return [
        {
            "id": log.id,
            "worker_id": log.worker_id,
            "start_time": log.start_time,
            "start_location": log.start_location,
            "stop_time": log.stop_time,
            "stop_location": log.stop_location,
        }
        for log in logs
    ]

@app.get("/logs")
def get_all_logs(db: Session = Depends(get_db)):
    logs = db.query(models.AttendanceLog).all()
    return [
        {
            "id": log.id,
            "worker_id": log.worker_id,
            "start_time": log.start_time,
            "start_lat": log.start_lat,
            "start_lon": log.start_lon,
            "stop_time": log.stop_time,
            "stop_lat": log.stop_lat,
            "stop_lon": log.stop_lon,
        }
        for log in logs
    ]

pracownicy_db = {}  # klucz: numer pracownika

@app.post("/dodaj_pracownika")
def dodaj_pracownika(p: schemas.Pracownik):
    if p.numer in pracownicy_db:
        raise HTTPException(status_code=400, detail="Pracownik już istnieje.")
    pracownicy_db[p.numer] = p
    return {"msg": "Dodano pracownika", "numer": p.numer}

@app.get("/lista_pracownikow")
def lista_pracownikow():
    return list(pracownicy_db.values())

class EmployeeCreate(BaseModel):
    id: str
    name: str
    hourly_rate: float

@app.post("/employees")
def create_employee(employee: EmployeeCreate, db: Session = Depends(get_db)):
    db_employee = models.Employee(id=employee.id, name=employee.name, hourly_rate=employee.hourly_rate)
    db.add(db_employee)
    db.commit()
    db.refresh(db_employee)
    return db_employee

@app.get("/employees")
def get_employees(db: Session = Depends(get_db)):
    return db.query(models.Employee).all()

@app.post("/start_shift")
def start_shift_api(shift: schemas.StartShift, db: Session = Depends(get_db)):
    log = models.AttendanceLog(
        worker_id=shift.employee_id,
        start_time=shift.czas_start,
        start_location=f"{shift.lokalizacja_start.lat},{shift.lokalizacja_start.lon}",
        stop_time=None,
        stop_location=None
    )
    db.add(log)
    db.commit()
    db.refresh(log)
    return {"msg": "Rozpoczęto zmianę", "id": log.id}

@app.post("/stop_shift")
def stop_shift_api(shift: schemas.StopShift, db: Session = Depends(get_db)):
    log = db.query(models.AttendanceLog).filter(
        models.AttendanceLog.worker_id == shift.employee_id,
        models.AttendanceLog.stop_time == None
    ).order_by(models.AttendanceLog.start_time.desc()).first()
    if not log:
        raise HTTPException(status_code=404, detail="Nie znaleziono aktywnej zmiany")
    log.stop_time = shift.czas_stop
    log.stop_location = f"{shift.lokalizacja_stop.lat},{shift.lokalizacja_stop.lon}"
    db.commit()
    db.refresh(log)
    return {"msg": "Zakończono zmianę", "id": log.id}

@app.get("/employees/{employee_id}")
def get_employee(employee_id: str, db: Session = Depends(get_db)):
    emp = db.query(models.Employee).filter(models.Employee.id == employee_id).first()
    if not emp:
        raise HTTPException(status_code=404, detail="Employee not found")
    return emp

@app.put("/employees/{employee_id}")
def update_employee(employee_id: str, data: schemas.EmployeeUpdate, db: Session = Depends(get_db)):
    emp = db.query(models.Employee).filter(models.Employee.id == employee_id).first()
    if not emp:
        raise HTTPException(status_code=404, detail="Employee not found")
    emp.name = f"{data.first_name} {data.last_name}"
    emp.hourly_rate = data.rate
    db.commit()
    return {"msg": "Employee updated"}

@app.get("/worker/{worker_id}")
def get_worker(worker_id: str, db: Session = Depends(get_db)):
    emp = db.query(models.Employee).filter(models.Employee.id == worker_id).first()
    if not emp:
        raise HTTPException(status_code=404, detail="Worker not found")
    # Rozbij name na first_name, last_name jeśli to możliwe
    first_name, last_name = (emp.name.split(" ", 1) + [""])[:2]
    return {
        "id": emp.id,
        "first_name": first_name,
        "last_name": last_name,
        "hourly_rate": emp.hourly_rate,
        "rate_saturday": emp.rate_saturday,
        "rate_sunday": emp.rate_sunday,
        "rate_night": emp.rate_night,
        "rate_overtime": emp.rate_overtime
    }

@app.put("/worker/{worker_id}")
def update_worker(worker_id: str, data: schemas.EmployeeUpdate, db: Session = Depends(get_db)):
    emp = db.query(models.Employee).filter(models.Employee.id == worker_id).first()
    if not emp:
        raise HTTPException(status_code=404, detail="Worker not found")
    # Obsługa zmiany ID
    new_id = getattr(data, 'new_id', None)
    if new_id and new_id != worker_id:
        # Sprawdź czy nowy ID nie jest już zajęty
        if db.query(models.Employee).filter(models.Employee.id == new_id).first():
            raise HTTPException(status_code=400, detail="Pracownik o tym ID już istnieje")
        emp.id = new_id
    emp.name = f"{data.first_name} {data.last_name}"
    emp.hourly_rate = data.rate
    emp.rate_saturday = data.rate_saturday
    emp.rate_sunday = data.rate_sunday
    emp.rate_night = data.rate_night
    emp.rate_overtime = data.rate_overtime
    db.commit()
    return {"msg": "Worker updated"}

@app.post("/workers")
def create_worker(worker: dict = Body(...), db: Session = Depends(get_db)):
    # Oczekujemy: id, first_name, last_name, hourly_rate, rate_saturday, rate_sunday, rate_night, rate_overtime
    if db.query(models.Employee).filter(models.Employee.id == worker["id"]).first():
        raise HTTPException(status_code=400, detail="Pracownik o tym ID już istnieje")
    name = f"{worker['first_name']} {worker['last_name']}"
    db_employee = models.Employee(
        id=worker["id"],
        name=name,
        hourly_rate=worker["hourly_rate"],
        rate_saturday=worker.get("rate_saturday", 0.0),
        rate_sunday=worker.get("rate_sunday", 0.0),
        rate_night=worker.get("rate_night", 0.0),
        rate_overtime=worker.get("rate_overtime", 0.0)
    )
    db.add(db_employee)
    db.commit()
    db.refresh(db_employee)
    return db_employee

@app.delete("/workers/{worker_id}")
def delete_worker(worker_id: str, db: Session = Depends(get_db)):
    worker = db.query(models.Employee).filter(models.Employee.id == worker_id).first()
    if not worker:
        raise HTTPException(status_code=404, detail="Pracownik nie istnieje")
    db.delete(worker)
    db.commit()
    return {"msg": "Usunięto pracownika"}

@app.get("/workers")
def get_workers(db: Session = Depends(get_db)):
    return db.query(models.Employee).all()

@app.get("/active_workers")
def get_active_workers():
    from database import SessionLocal
    db = SessionLocal()
    logs = db.query(models.AttendanceLog).all()
    employees = db.query(models.Employee).all()
    today = date.today()
    # Mapowanie: worker_id -> najnowszy log z dzisiaj
    logs_today = {}
    for log in logs:
        if log.start_time and log.start_time.date() == today:
            if log.worker_id not in logs_today or log.start_time > logs_today[log.worker_id].start_time:
                logs_today[log.worker_id] = log
    result = []
    for worker_id, log in logs_today.items():
        emp = next((w for w in employees if w.id == worker_id), None)
        if emp:
            # Rozbij name na first_name, last_name jeśli trzeba
            if hasattr(emp, 'first_name') and hasattr(emp, 'last_name'):
                name = f"{emp.first_name} {emp.last_name}"
            else:
                parts = emp.name.split(' ')
                first_name = parts[0] if len(parts) > 0 else ''
                last_name = ' '.join(parts[1:]) if len(parts) > 1 else ''
                name = f"{first_name} {last_name}".strip()
            time_now = datetime.now()
            stop_time = log.stop_time
            if stop_time:
                time_diff = stop_time - log.start_time
            else:
                time_diff = time_now - log.start_time
            hours, remainder = divmod(time_diff.total_seconds(), 3600)
            minutes = remainder // 60
            result.append({
                "name": name,
                "start_time": log.start_time.strftime("%H:%M"),
                "duration": f"{int(hours)}h {int(minutes)}min",
                "online": stop_time is None,
                "start_lat": log.start_lat,
                "start_lon": log.start_lon
            })
    return JSONResponse(content=result)

@app.get("/attendance_by_date")
def attendance_by_date(date: str = Query(...)):
    from database import SessionLocal
    db = SessionLocal()
    try:
        selected_date = datetime.strptime(date, "%Y-%m-%d")
        start_of_day = selected_date
        end_of_day = selected_date + timedelta(days=1)
        logs = db.query(models.AttendanceLog).filter(
            models.AttendanceLog.start_time >= start_of_day,
            models.AttendanceLog.start_time < end_of_day
        ).all()
        employees = db.query(models.Employee).all()
        result = []
        for log in logs:
            emp = next((w for w in employees if w.id == log.worker_id), None)
            if emp:
                parts = emp.name.split(' ')
                first_name = parts[0] if len(parts) > 0 else ''
                last_name = ' '.join(parts[1:]) if len(parts) > 1 else ''
                name = f"{first_name} {last_name}".strip()
                start = log.start_time.strftime("%H:%M")
                stop = log.stop_time.strftime("%H:%M") if log.stop_time else "Trwa"
                if log.stop_time:
                    duration = log.stop_time - log.start_time
                    hours, remainder = divmod(duration.total_seconds(), 3600)
                    minutes = remainder // 60
                    duration_str = f"{int(hours)}h {int(minutes)}min"
                else:
                    duration_str = "W trakcie"
                result.append({
                    "name": name,
                    "start": start,
                    "stop": stop,
                    "duration": duration_str,
                    "start_lat": log.start_lat,
                    "start_lon": log.start_lon,
                    "stop_lat": log.stop_lat,
                    "stop_lon": log.stop_lon
                })
        return result
    except Exception as e:
        return {"error": str(e)}

@app.get("/attendance_summary")
def attendance_summary(date_from: str = Query(...), date_to: str = Query(...)):
    from database import SessionLocal
    db = SessionLocal()
    try:
        date_from_dt = datetime.strptime(date_from, "%Y-%m-%d")
        date_to_dt = datetime.strptime(date_to, "%Y-%m-%d") + timedelta(days=1)
        logs = db.query(models.AttendanceLog).filter(
            models.AttendanceLog.start_time >= date_from_dt,
            models.AttendanceLog.start_time < date_to_dt,
            models.AttendanceLog.stop_time != None
        ).all()
        employees = db.query(models.Employee).all()
        summary = {}
        for log in logs:
            emp = next((w for w in employees if w.id == log.worker_id), None)
            if not emp:
                continue
            parts = emp.name.split(' ')
            first_name = parts[0] if len(parts) > 0 else ''
            last_name = ' '.join(parts[1:]) if len(parts) > 1 else ''
            name = f"{first_name} {last_name}".strip()
            day = log.start_time.date()
            key = emp.id
            if key not in summary:
                summary[key] = {
                    "id": emp.id,
                    "name": name,
                    "rate": emp.hourly_rate,
                    "days": set(),
                    "total_seconds": 0,
                    "saturdays": 0,
                    "sundays": 0,
                    "holidays": 0
                }
            summary[key]["days"].add(day)
            if log.stop_time:
                summary[key]["total_seconds"] += int((log.stop_time - log.start_time).total_seconds())
            weekday = log.start_time.weekday()
            if weekday == 5:
                summary[key]["saturdays"] += 1
            elif weekday == 6:
                summary[key]["sundays"] += 1
            # Święta (na razie 0, można dodać logikę później)
        result = []
        for val in summary.values():
            hours, remainder = divmod(val["total_seconds"], 3600)
            minutes = remainder // 60
            total_hours = val["total_seconds"] / 3600
            result.append({
                "id": val["id"],
                "name": val["name"],
                "rate": val["rate"],
                "days_present": len(val["days"]),
                "total_time": f"{int(hours)}h {int(minutes)}min",
                "total_hours": round(total_hours, 2),
                "saturdays": val["saturdays"],
                "sundays": val["sundays"],
                "holidays": val["holidays"]
            })
        return result
    except Exception as e:
        import traceback
        print("attendance_summary error:", traceback.format_exc())
        # Zwracaj pustą listę zamiast error
        return []

@app.get("/attendance_details")
def attendance_details(worker_id: str = Query(...), date_from: str = Query(...), date_to: str = Query(...)):
    from database import SessionLocal
    db = SessionLocal()
    try:
        date_from_dt = datetime.strptime(date_from, "%Y-%m-%d")
        date_to_dt = datetime.strptime(date_to, "%Y-%m-%d") + timedelta(days=1)
        logs = db.query(models.AttendanceLog).filter(
            models.AttendanceLog.worker_id == worker_id,
            models.AttendanceLog.start_time >= date_from_dt,
            models.AttendanceLog.start_time < date_to_dt,
            models.AttendanceLog.stop_time != None
        ).order_by(models.AttendanceLog.start_time).all()
        emp = db.query(models.Employee).filter(models.Employee.id == worker_id).first()
        print(f"[attendance_details] worker_id={worker_id}, date_from={date_from}, date_to={date_to}")
        print(f"[attendance_details] employee found: {emp is not None}")
        print(f"[attendance_details] logs found: {len(logs)}")
        if emp:
            print(f"[attendance_details] employee: id={emp.id}, name={emp.name}, hourly_rate={emp.hourly_rate}")
        # Domyślne zerowe podsumowanie
        empty_summary = {
            "dni": 0,
            "godziny": 0.0,
            "soboty": 0,
            "niedziele": 0,
            "swieta": 0,
            "kwota": 0.0,
            "kwota_soboty": 0.0,
            "kwota_niedziele": 0.0,
            "kwota_swieta": 0.0,
            "kwota_zwykle": 0.0,
            "urlop_dni": 0,
            "urlop_kwota": 0.0,
            "chorobowe_dni": 0,
            "chorobowe_kwota": 0.0
        }
        if not emp:
            print("[attendance_details] employee not found, returning empty data.")
            return {"logs": [], "summary": empty_summary}
        parts = emp.name.split(' ')
        first_name = parts[0] if len(parts) > 0 else ''
        last_name = ' '.join(parts[1:]) if len(parts) > 1 else ''
        name = f"{first_name} {last_name}".strip()
        all_logs = db.query(models.AttendanceLog).filter(models.AttendanceLog.worker_id == worker_id, models.AttendanceLog.stop_time != None).order_by(models.AttendanceLog.start_time).all()
        result = []
        summary = empty_summary.copy()
        for log in logs:
            duration = log.stop_time - log.start_time if log.stop_time else None
            hours, remainder = divmod(duration.total_seconds(), 3600) if duration else (0, 0)
            minutes = remainder // 60 if duration else 0
            duration_hours = duration.total_seconds() / 3600 if duration else 0
            kwota = 0.0
            typ = 'zwykly'
            # --- KWOTA I PODSUMOWANIE ---
            if str(getattr(log, 'is_holiday', '')) in ['tak', 'true', 'urlop']:
                date_3m_ago = log.start_time - timedelta(days=90)
                logs_3m = [l for l in all_logs if l.start_time >= date_3m_ago and l.start_time <= log.start_time and str(getattr(l, 'is_holiday', '')) not in ['tak', 'true', 'urlop'] and str(getattr(l, 'is_sick', '')) not in ['tak', 'true', 'chorobowe', 'zus']]
                suma = sum((l.stop_time - l.start_time).total_seconds() / 3600 * emp.hourly_rate for l in logs_3m if l.stop_time)
                godziny = sum((l.stop_time - l.start_time).total_seconds() / 3600 for l in logs_3m if l.stop_time)
                stawka_urlop = (suma / godziny) if godziny > 0 else emp.hourly_rate
                kwota = round(stawka_urlop * 8, 2)
                typ = 'urlop'
                summary["urlop_dni"] += 1
                summary["urlop_kwota"] += kwota
                # NIE sumuj godzin/dni urlopowych do zwykłych
            elif str(getattr(log, 'is_sick', '')) in ['tak', 'true', 'chorobowe']:
                date_6m_ago = log.start_time - timedelta(days=180)
                logs_6m = [l for l in all_logs if l.start_time >= date_6m_ago and l.start_time <= log.start_time and str(getattr(l, 'is_holiday', '')) not in ['tak', 'true', 'urlop'] and str(getattr(l, 'is_sick', '')) not in ['tak', 'true', 'chorobowe', 'zus']]
                suma = sum((l.stop_time - l.start_time).total_seconds() / 3600 * emp.hourly_rate for l in logs_6m if l.stop_time)
                godziny = sum((l.stop_time - l.start_time).total_seconds() / 3600 for l in logs_6m if l.stop_time)
                stawka_chorobowe = (suma / godziny) * 0.8 if godziny > 0 else emp.hourly_rate * 0.8
                kwota = round(stawka_chorobowe * 8, 2)
                typ = 'chorobowe'
                summary["chorobowe_dni"] += 1
                summary["chorobowe_kwota"] += kwota
                # NIE sumuj godzin/dni chorobowych do zwykłych
            elif str(getattr(log, 'is_sick', '')) == 'zus':
                kwota = 0.0
                typ = 'chorobowe_zus'
                summary["chorobowe_dni"] += 1
            else:
                day = log.start_time.date()
                if day in PL_HOLIDAYS:
                    typ = 'swieto'
                    stawka = emp.rate_sunday if getattr(emp, 'rate_sunday', 0) else emp.hourly_rate
                    kwota = round(stawka * duration_hours, 2)
                    summary["swieta"] += 1
                    summary["kwota_swieta"] += kwota
                elif log.start_time.weekday() == 6:
                    typ = 'niedziela'
                    stawka = emp.rate_sunday if getattr(emp, 'rate_sunday', 0) else emp.hourly_rate
                    kwota = round(stawka * duration_hours, 2)
                    summary["niedziele"] += 1
                    summary["kwota_niedziele"] += kwota
                elif log.start_time.weekday() == 5:
                    typ = 'sobota'
                    stawka = emp.rate_saturday if getattr(emp, 'rate_saturday', 0) else emp.hourly_rate
                    kwota = round(stawka * duration_hours, 2)
                    summary["soboty"] += 1
                    summary["kwota_soboty"] += kwota
                else:
                    typ = 'zwykly'
                    stawka = emp.hourly_rate
                    kwota = round(stawka * duration_hours, 2)
                    summary["kwota_zwykle"] += kwota
                summary["dni"] += 1
                summary["godziny"] += duration_hours
                summary["kwota"] += kwota
            result.append({
                "log_id": log.id,
                "name": name,
                "date": log.start_time.strftime("%Y-%m-%d"),
                "start": log.start_time.strftime("%H:%M"),
                "stop": log.stop_time.strftime("%H:%M") if log.stop_time else '-',
                "duration": f"{int(hours)}h {int(minutes)}min",
                "is_holiday": log.is_holiday,
                "is_sick": log.is_sick,
                "kwota": kwota,
                "typ": typ
            })
        for k in ["kwota", "kwota_soboty", "kwota_niedziele", "kwota_swieta", "kwota_zwykle", "urlop_kwota", "chorobowe_kwota"]:
            summary[k] = round(summary[k], 2)
        summary["godziny"] = round(summary["godziny"], 2)
        print(f"[attendance_details] summary: {summary}")
        return {"logs": result, "summary": summary}
    except Exception as e:
        print(f"[attendance_details] ERROR: {e}")
        return {"logs": [], "summary": empty_summary, "error": str(e)}

@app.post("/logs")
def create_log(log: schemas.AttendanceLogCreate, db: Session = Depends(get_db)):
    new_log = models.AttendanceLog(**log.dict())
    db.add(new_log)
    db.commit()
    db.refresh(new_log)
    return new_log

@app.patch("/logs/{log_id}")
def update_log(log_id: int, log_data: schemas.AttendanceLogUpdate, db: Session = Depends(get_db)):
    log = db.query(models.AttendanceLog).filter(models.AttendanceLog.id == log_id).first()
    if not log:
        raise HTTPException(status_code=404, detail="Nie znaleziono rekordu")
    data = log_data.dict(exclude_unset=True)
    # Parsowanie stringów na datetime, jeśli przyszły z frontendu
    from datetime import datetime
    def parse_dt(val):
        if isinstance(val, str):
            for fmt in ("%Y-%m-%dT%H:%M:%S", "%Y-%m-%d %H:%M:%S", "%Y-%m-%dT%H:%M", "%Y-%m-%d %H:%M"):
                try:
                    return datetime.strptime(val, fmt)
                except Exception:
                    continue
            return None
        return val
    if "start_time" in data and data["start_time"]:
        log.start_time = parse_dt(data["start_time"])
    if "stop_time" in data and data["stop_time"]:
        log.stop_time = parse_dt(data["stop_time"])
    # Ujednolicenie obsługi is_holiday/is_sick z frontendu
    if "is_holiday" in data or "is_sick" in data:
        if "is_holiday" in data and data["is_holiday"] is not None:
            if data["is_holiday"] in [True, "true", "tak", "urlop"]:
                log.is_holiday = "tak"
            else:
                log.is_holiday = "nie"
        if "is_sick" in data and data["is_sick"] is not None:
            if data["is_sick"] in [True, "true", "tak", "chorobowe"]:
                log.is_sick = "tak"
            elif data["is_sick"] == "zus":
                log.is_sick = "zus"
            else:
                log.is_sick = "nie"
    db.commit()
    db.refresh(log)
    return log

@app.delete("/logs/{log_id}")
def delete_log(log_id: int, db: Session = Depends(get_db)):
    log = db.query(models.AttendanceLog).filter(models.AttendanceLog.id == log_id).first()
    if not log:
        raise HTTPException(status_code=404, detail="Nie znaleziono logu")
    db.delete(log)
    db.commit()
    return {"msg": "Usunięto log"}

@app.post("/logs/batch")
def create_logs(logs: List[dict], db: Session = Depends(get_db)):
    # Obsługa batchowego dodawania logów (lista słowników z co najmniej: employee_id, date)
    created = []
    for log in logs:
        # Ustaw domyślne godziny pracy (np. 08:00-16:00)
        start_time = datetime.strptime(log["date"] + " 08:00", "%Y-%m-%d %H:%M")
        stop_time = datetime.strptime(log["date"] + " 16:00", "%Y-%m-%d %H:%M")
        new_log = models.AttendanceLog(
            worker_id=log["employee_id"],
            start_time=start_time,
            stop_time=stop_time,
            start_lat=None,
            start_lon=None,
            stop_lat=None,
            stop_lon=None
        )
        db.add(new_log)
        db.commit()
        db.refresh(new_log)
        created.append({"id": new_log.id, "date": log["date"]})
    return created

@app.get("/employees_without_logs")
def employees_without_logs(date_from: str = Query(...), date_to: str = Query(...), db: Session = Depends(get_db)):
    date_from_dt = datetime.strptime(date_from, "%Y-%m-%d")
    date_to_dt = datetime.strptime(date_to, "%Y-%m-%d") + timedelta(days=1)
    employees = db.query(models.Employee).all()
    logs = db.query(models.AttendanceLog).filter(
        models.AttendanceLog.start_time >= date_from_dt,
        models.AttendanceLog.start_time < date_to_dt
    ).all()
    logged_ids = set(log.worker_id for log in logs)
    result = []
    for emp in employees:
        if str(emp.id) not in logged_ids:
            result.append({"id": emp.id, "name": emp.name})
    return result

@app.get("/work_summary")
def get_work_summary(start_date: date = Query(...), end_date: date = Query(...), db: Session = Depends(get_db)):
    logs = db.query(models.AttendanceLog).filter(
        models.AttendanceLog.start_time >= start_date,
        models.AttendanceLog.stop_time <= end_date
    ).all()

    employees = db.query(models.Employee).all()
    result = {}
    for emp in employees:
        result[emp.id] = {
            "id": emp.id,
            "imie": emp.name.split(' ')[0] if emp.name else '',
            "nazwisko": ' '.join(emp.name.split(' ')[1:]) if emp.name else '',
            "dni": 0,
            "godziny": 0.0,
            "soboty": 0,
            "niedziele": 0,
            "swieta": 0,
            "kwota": 0.0,
            "kwota_soboty": 0.0,
            "kwota_niedziele": 0.0,
            "kwota_swieta": 0.0,
            "kwota_zwykle": 0.0,
            "urlop_dni": 0,
            "urlop_kwota": 0.0,
            "chorobowe_dni": 0,
            "chorobowe_kwota": 0.0
        }

    for log in logs:
        emp = result.get(log.worker_id)
        if not emp:
            continue
        day = log.start_time.date()
        duration = log.stop_time - log.start_time
        duration_hours = duration.total_seconds() / 3600

        # Urlop
        if getattr(log, 'is_holiday', False):
            emp["urlop_dni"] += 1
            # Średnia stawka z 3 miesięcy
            date_3m_ago = log.start_time - timedelta(days=90)
            logs_3m = [l for l in logs if l.worker_id == log.worker_id and l.start_time >= date_3m_ago and l.start_time <= log.start_time and not getattr(l, 'is_holiday', False) and not getattr(l, 'is_sick', False)]
            suma = sum((l.stop_time - l.start_time).total_seconds() / 3600 * emp["kwota_zwykle"] for l in logs_3m if l.stop_time)
            godziny = sum((l.stop_time - l.start_time).total_seconds() / 3600 for l in logs_3m if l.stop_time)
            stawka_urlop = (suma / godziny) if godziny > 0 else 0.0
            kwota_urlop = round(stawka_urlop * 8, 2)
            emp["urlop_kwota"] += kwota_urlop
            continue
        # Chorobowe
        if getattr(log, 'is_sick', None) and log.is_sick not in [None, '', 'zus']:
            emp["chorobowe_dni"] += 1
            # Średnia stawka z 6 miesięcy
            date_6m_ago = log.start_time - timedelta(days=180)
            logs_6m = [l for l in logs if l.worker_id == log.worker_id and l.start_time >= date_6m_ago and l.start_time <= log.start_time and not getattr(l, 'is_holiday', False) and not getattr(l, 'is_sick', False)]
            suma = sum((l.stop_time - l.start_time).total_seconds() / 3600 * emp["kwota_zwykle"] for l in logs_6m if l.stop_time)
            godziny = sum((l.stop_time - l.start_time).total_seconds() / 3600 for l in logs_6m if l.stop_time)
            stawka_chorobowe = (suma / godziny) * 0.8 if godziny > 0 else 0.0
            kwota_chorobowe = round(stawka_chorobowe * 8, 2)
            emp["chorobowe_kwota"] += kwota_chorobowe
            continue

        # ...dotychczasowa logika...
        if day in PL_HOLIDAYS:
            typ = 'swieto'
            stawka = emp.rate_sunday if getattr(emp, 'rate_sunday', 0) else emp["kwota_zwykle"]
        elif log.start_time.weekday() == 6:
            typ = 'niedziela'
            stawka = emp.rate_sunday if getattr(emp, 'rate_sunday', 0) else emp["kwota_zwykle"]
        elif log.start_time.weekday() == 5:
            typ = 'sobota'
            stawka = emp.rate_saturday if getattr(emp, 'rate_saturday', 0) else emp["kwota_zwykle"]
        else:
            typ = 'zwykly'
            stawka = emp["kwota_zwykle"]

        kwota = round(stawka * duration_hours, 2)
        emp["dni"] += 1
        emp["godziny"] += duration_hours
        emp["kwota"] += kwota
        if typ == 'sobota':
            emp["soboty"] += 1
            emp["kwota_soboty"] += kwota
        elif typ == 'niedziela':
            emp["niedziele"] += 1
            emp["kwota_niedziele"] += kwota
        elif typ == 'swieto':
            emp["swieta"] += 1
            emp["kwota_swieta"] += kwota
        else:
            emp["kwota_zwykle"] += kwota

    return list(result.values())

@app.get("/mobile-config")
async def get_mobile_config():
    """Endpoint do pobierania konfiguracji dla aplikacji mobilnej"""
    return {
        "config": MOBILE_APP_CONFIG,
        "version": CONFIG_VERSION,
        "timestamp": datetime.now().isoformat()
    }

@app.get("/config-version")
async def get_config_version():
    """Sprawdzenie wersji konfiguracji"""
    return {
        "version": CONFIG_VERSION,
        "timestamp": datetime.now().isoformat()
    }

@app.get("/app-version")
async def check_app_version():
    """Endpoint do sprawdzania wersji aplikacji mobilnej"""
    return {
        "version_info": APP_VERSION_INFO,
        "server_time": datetime.now().isoformat(),
        "config_version": CONFIG_VERSION
    }

@app.post("/app-version/check")
async def check_app_version_post(version_data: dict = Body(...)):
    """Endpoint do sprawdzania czy aplikacja wymaga aktualizacji"""
    try:
        client_version = version_data.get("current_version", "0.0.0")
        
        # Porównaj wersje
        def version_tuple(v):
            return tuple(map(int, (v.split("."))))
        
        current_tuple = version_tuple(APP_VERSION_INFO["current_version"])
        client_tuple = version_tuple(client_version)
        minimum_tuple = version_tuple(APP_VERSION_INFO["minimum_version"])
        
        update_available = current_tuple > client_tuple
        update_required = client_tuple < minimum_tuple
        
        return {
            "client_version": client_version,
            "latest_version": APP_VERSION_INFO["current_version"],
            "update_available": update_available,
            "update_required": update_required,
            "update_message": APP_VERSION_INFO["update_message"] if update_available else None,
            "play_store_url": APP_VERSION_INFO["play_store_url"] if update_available else None,
            "features": APP_VERSION_INFO["update_features"] if update_available else None,
            "timestamp": datetime.now().isoformat()
        }
        
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Błąd sprawdzania wersji: {str(e)}")

@app.post("/mobile-config")
async def update_mobile_config(config_data: dict = Body(...)):
    """Endpoint do aktualizacji konfiguracji aplikacji mobilnej"""
    try:
        # Walidacja danych
        if not isinstance(config_data, dict):
            raise HTTPException(status_code=400, detail="Nieprawidłowy format danych")
        
        # Ścieżka do pliku konfiguracji
        config_file_path = os.path.join(os.path.dirname(__file__), "config.py")
        
        # Wczytaj aktualny plik
        with open(config_file_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Znajdź i zamień konfigurację
        # Prosta implementacja - zastąp całą konfigurację
        new_config_str = "MOBILE_APP_CONFIG = {\n"
        for key, value in config_data.items():
            if isinstance(value, bool):
                new_config_str += f'    "{key}": {str(value)},\n'
            else:
                new_config_str += f'    "{key}": {repr(value)},\n'
        new_config_str += "}"
        
        # Zastąp w pliku
        import re
        pattern = r'MOBILE_APP_CONFIG\s*=\s*{[^}]*}'
        new_content = re.sub(pattern, new_config_str, content, flags=re.DOTALL)
        
        # Zapisz plik
        with open(config_file_path, 'w', encoding='utf-8') as f:
            f.write(new_content)
        
        # Aktualizuj zmienną globalną (wymaga restaru serwera dla pełnego efektu)
        global MOBILE_APP_CONFIG
        MOBILE_APP_CONFIG.update(config_data)
        
        return {
            "success": True,
            "message": "Konfiguracja została zaktualizowana",
            "config": MOBILE_APP_CONFIG,
            "version": CONFIG_VERSION,
            "timestamp": datetime.now().isoformat()
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Błąd podczas zapisywania konfiguracji: {str(e)}")

# Import funkcji email
from email_service import send_report_email as send_report_service

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
    print("Hello, world!")
