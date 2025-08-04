# email_service.py
# Funkcje do wysyłania raportów przez email

import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.base import MIMEBase
from email import encoders
import base64
from datetime import datetime
from fastapi import HTTPException
from config import EMAIL_CONFIG

def send_email(to_email: str, subject: str, body: str, attachment_data: bytes = None, attachment_name: str = None):
    """Wysyła email z opcjonalnym załącznikiem"""
    if not EMAIL_CONFIG["enabled"]:
        raise HTTPException(status_code=400, detail="Wysyłanie emaili jest wyłączone")
    
    if not EMAIL_CONFIG["smtp_username"] or not EMAIL_CONFIG["smtp_password"]:
        raise HTTPException(status_code=400, detail="Nie skonfigurowano danych SMTP")
    
    try:
        # Tworzenie wiadomości
        msg = MIMEMultipart()
        msg['From'] = f"{EMAIL_CONFIG['sender_name']} <{EMAIL_CONFIG['sender_email']}>"
        msg['To'] = to_email
        msg['Subject'] = subject
        
        # Dodanie treści
        msg.attach(MIMEText(body, 'html'))
        
        # Dodanie załącznika jeśli jest
        if attachment_data and attachment_name:
            part = MIMEBase('application', 'octet-stream')
            part.set_payload(attachment_data)
            encoders.encode_base64(part)
            part.add_header(
                'Content-Disposition',
                f'attachment; filename= {attachment_name}'
            )
            msg.attach(part)
        
        # Wysłanie emaila
        server = smtplib.SMTP(EMAIL_CONFIG["smtp_server"], EMAIL_CONFIG["smtp_port"])
        server.starttls()
        server.login(EMAIL_CONFIG["smtp_username"], EMAIL_CONFIG["smtp_password"])
        text = msg.as_string()
        server.sendmail(EMAIL_CONFIG["sender_email"], to_email, text)
        server.quit()
        
        return True
        
    except Exception as e:
        print(f"Błąd wysyłania emaila: {e}")
        raise HTTPException(status_code=500, detail=f"Błąd wysyłania emaila: {str(e)}")

def generate_email_body(report_type: str, employee_name: str = None, date_range: str = None, filename: str = None):
    """Generuje treść HTML emaila z raportem"""
    html_body = f"""
    <html>
    <body>
        <h2>📊 Raport Lista Obecności</h2>
        <p>Witaj!</p>
        <p>W załączeniu przesyłamy raport wygenerowany z systemu Lista Obecności.</p>
        
        <h3>📋 Szczegóły raportu:</h3>
        <ul>
            <li><strong>Typ raportu:</strong> {report_type.upper()}</li>
            {"<li><strong>Pracownik:</strong> " + employee_name + "</li>" if employee_name else ""}
            {"<li><strong>Okres:</strong> " + date_range + "</li>" if date_range else ""}
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
    return html_body

def send_report_email(to_email: str, subject: str, report_type: str, report_data: str, 
                     employee_name: str = None, date_range: str = None):
    """Wysyła raport przez email"""
    try:
        # Dekodowanie danych raportu z Base64
        report_bytes = base64.b64decode(report_data)
        
        # Określenie nazwy pliku i typu
        if report_type.lower() == "pdf":
            file_extension = "pdf"
        else:
            file_extension = "csv"
        
        # Generowanie nazwy pliku
        timestamp = datetime.now().strftime("%Y-%m-%d_%H-%M")
        if employee_name:
            filename = f"Raport_{employee_name}_{timestamp}.{file_extension}"
        else:
            filename = f"Raport_obecnosci_{timestamp}.{file_extension}"
        
        # Generowanie treści emaila
        html_body = generate_email_body(report_type, employee_name, date_range, filename)
        
        # Wysłanie emaila
        send_email(
            to_email=to_email,
            subject=subject,
            body=html_body,
            attachment_data=report_bytes,
            attachment_name=filename
        )
        
        return {
            "success": True,
            "message": f"Raport został wysłany na adres {to_email}",
            "filename": filename,
            "timestamp": datetime.now().isoformat()
        }
        
    except Exception as e:
        return {
            "success": False,
            "message": f"Błąd wysyłania raportu: {str(e)}"
        }
