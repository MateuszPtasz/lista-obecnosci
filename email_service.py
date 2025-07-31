# email_service.py
# Enhanced email service with better error handling and SMTP improvements

import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.base import MIMEBase
from email import encoders
import base64
from datetime import datetime
from fastapi import HTTPException
from config import EMAIL_CONFIG
import ssl
import socket
from typing import Dict, Any
import logging

# Get logger
logger = logging.getLogger("email_service")

class EmailError(Exception):
    """Custom exception for email-related errors"""
    pass

class SMTPConnectionError(EmailError):
    """SMTP connection related errors"""
    pass

class SMTPAuthError(EmailError):
    """SMTP authentication related errors"""
    pass

class SMTPSendError(EmailError):
    """SMTP sending related errors"""
    pass

def validate_email_config() -> Dict[str, Any]:
    """Validate email configuration and return status"""
    issues = []
    
    if not EMAIL_CONFIG["enabled"]:
        return {"valid": False, "issues": ["Email service is disabled"]}
    
    if not EMAIL_CONFIG["smtp_username"]:
        issues.append("SMTP username not configured")
    
    if not EMAIL_CONFIG["smtp_password"]:
        issues.append("SMTP password not configured")
    
    if not EMAIL_CONFIG["sender_email"]:
        issues.append("Sender email not configured")
    
    if not EMAIL_CONFIG["smtp_server"]:
        issues.append("SMTP server not configured")
    
    return {"valid": len(issues) == 0, "issues": issues}

def test_smtp_connection() -> Dict[str, Any]:
    """Test SMTP connection without sending email"""
    config_status = validate_email_config()
    if not config_status["valid"]:
        return {"success": False, "error": "Configuration invalid", "details": config_status["issues"]}
    
    try:
        # Create SSL context
        context = ssl.create_default_context()
        
        # Test connection
        with smtplib.SMTP(EMAIL_CONFIG["smtp_server"], EMAIL_CONFIG["smtp_port"], timeout=10) as server:
            server.ehlo()
            server.starttls(context=context)
            server.ehlo()
            server.login(EMAIL_CONFIG["smtp_username"], EMAIL_CONFIG["smtp_password"])
            
        return {"success": True, "message": "SMTP connection successful"}
        
    except smtplib.SMTPAuthenticationError as e:
        logger.error(f"SMTP Authentication failed: {e}")
        return {
            "success": False, 
            "error": "Authentication failed", 
            "details": "Check username and password. For Gmail, use App Password instead of regular password.",
            "smtp_error": str(e)
        }
    except smtplib.SMTPServerDisconnected as e:
        logger.error(f"SMTP Server disconnected: {e}")
        return {
            "success": False, 
            "error": "Server connection lost", 
            "details": "SMTP server disconnected unexpectedly",
            "smtp_error": str(e)
        }
    except smtplib.SMTPConnectError as e:
        logger.error(f"SMTP Connection error: {e}")
        return {
            "success": False, 
            "error": "Connection failed", 
            "details": f"Cannot connect to SMTP server {EMAIL_CONFIG['smtp_server']}:{EMAIL_CONFIG['smtp_port']}",
            "smtp_error": str(e)
        }
    except socket.timeout:
        logger.error("SMTP Connection timeout")
        return {
            "success": False, 
            "error": "Connection timeout", 
            "details": "SMTP server did not respond within 10 seconds"
        }
    except Exception as e:
        logger.error(f"Unexpected SMTP error: {e}")
        return {
            "success": False, 
            "error": "Unexpected error", 
            "details": str(e)
        }

def send_email(to_email: str, subject: str, body: str, attachment_data: bytes = None, attachment_name: str = None) -> Dict[str, Any]:
    """Enhanced email sending with comprehensive error handling"""
    
    # Validate configuration first
    config_status = validate_email_config()
    if not config_status["valid"]:
        error_msg = f"Email configuration invalid: {', '.join(config_status['issues'])}"
        logger.error(error_msg)
        raise HTTPException(status_code=400, detail=error_msg)
    
    try:
        # Create message
        msg = MIMEMultipart()
        msg['From'] = f"{EMAIL_CONFIG['sender_name']} <{EMAIL_CONFIG['sender_email']}>"
        msg['To'] = to_email
        msg['Subject'] = subject
        
        # Add body
        msg.attach(MIMEText(body, 'html', 'utf-8'))
        
        # Add attachment if provided
        if attachment_data and attachment_name:
            part = MIMEBase('application', 'octet-stream')
            part.set_payload(attachment_data)
            encoders.encode_base64(part)
            part.add_header(
                'Content-Disposition',
                f'attachment; filename= {attachment_name}'
            )
            msg.attach(part)
        
        # Create SSL context with proper settings
        context = ssl.create_default_context()
        
        # Send email with comprehensive error handling
        with smtplib.SMTP(EMAIL_CONFIG["smtp_server"], EMAIL_CONFIG["smtp_port"], timeout=30) as server:
            server.ehlo()
            server.starttls(context=context)
            server.ehlo()
            
            # Login with detailed error handling
            try:
                server.login(EMAIL_CONFIG["smtp_username"], EMAIL_CONFIG["smtp_password"])
            except smtplib.SMTPAuthenticationError as e:
                error_msg = "SMTP Authentication failed. For Gmail, ensure you're using an App Password."
                logger.error(f"{error_msg} Details: {e}")
                raise SMTPAuthError(error_msg)
            
            # Send email
            server.send_message(msg)
            
        logger.info(f"Email sent successfully to {to_email}")
        return {
            "success": True,
            "message": f"Email sent successfully to {to_email}",
            "timestamp": datetime.now().isoformat()
        }
        
    except SMTPAuthError:
        raise  # Re-raise our custom auth error
        
    except smtplib.SMTPRecipientsRefused as e:
        error_msg = f"Recipient email address rejected: {to_email}"
        logger.error(f"{error_msg} Details: {e}")
        raise HTTPException(status_code=400, detail=error_msg)
        
    except smtplib.SMTPServerDisconnected as e:
        error_msg = "SMTP server disconnected unexpectedly"
        logger.error(f"{error_msg} Details: {e}")
        raise SMTPConnectionError(error_msg)
        
    except smtplib.SMTPConnectError as e:
        error_msg = f"Cannot connect to SMTP server {EMAIL_CONFIG['smtp_server']}:{EMAIL_CONFIG['smtp_port']}"
        logger.error(f"{error_msg} Details: {e}")
        raise SMTPConnectionError(error_msg)
        
    except socket.timeout:
        error_msg = "Email sending timed out"
        logger.error(error_msg)
        raise SMTPSendError(error_msg)
        
    except Exception as e:
        error_msg = f"Unexpected error sending email: {str(e)}"
        logger.error(error_msg)
        raise HTTPException(status_code=500, detail=error_msg)

def generate_email_body(report_type: str, employee_name: str = None, date_range: str = None, filename: str = None):
    """Generate enhanced HTML email body"""
    html_body = f"""
    <!DOCTYPE html>
    <html>
    <head>
        <meta charset="utf-8">
        <title>Raport Lista Obecności</title>
        <style>
            body {{ font-family: Arial, sans-serif; line-height: 1.6; color: #333; }}
            .container {{ max-width: 600px; margin: 0 auto; padding: 20px; }}
            .header {{ background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); color: white; padding: 20px; border-radius: 10px 10px 0 0; }}
            .content {{ background: #f9f9f9; padding: 20px; border-radius: 0 0 10px 10px; }}
            .details {{ background: white; padding: 15px; border-radius: 5px; margin: 15px 0; }}
            .footer {{ font-size: 12px; color: #666; margin-top: 20px; padding-top: 15px; border-top: 1px solid #ddd; }}
            ul {{ list-style-type: none; padding: 0; }}
            li {{ padding: 5px 0; }}
            strong {{ color: #667eea; }}
        </style>
    </head>
    <body>
        <div class="container">
            <div class="header">
                <h2>📊 Raport Lista Obecności</h2>
            </div>
            <div class="content">
                <p>Witaj!</p>
                <p>W załączeniu przesyłamy raport wygenerowany z systemu Lista Obecności.</p>
                
                <div class="details">
                    <h3>📋 Szczegóły raportu:</h3>
                    <ul>
                        <li><strong>Typ raportu:</strong> {report_type.upper()}</li>
                        {"<li><strong>Pracownik:</strong> " + employee_name + "</li>" if employee_name else ""}
                        {"<li><strong>Okres:</strong> " + date_range + "</li>" if date_range else ""}
                        <li><strong>Data wygenerowania:</strong> {datetime.now().strftime("%d.%m.%Y %H:%M")}</li>
                    </ul>
                    
                    <p>📎 <strong>Załącznik:</strong> {filename}</p>
                </div>
                
                <div class="footer">
                    <p>Wiadomość została wygenerowana automatycznie przez system Lista Obecności.<br>
                    Nie odpowiadaj na ten email.</p>
                </div>
            </div>
        </div>
    </body>
    </html>
    """
    return html_body

def send_report_email(to_email: str, subject: str, report_type: str, report_data: str, 
                     employee_name: str = None, date_range: str = None) -> Dict[str, Any]:
    """Enhanced report email sending with better error handling"""
    try:
        # Decode report data
        report_bytes = base64.b64decode(report_data)
        
        # Determine file extension
        file_extension = "pdf" if report_type.lower() == "pdf" else "csv"
        
        # Generate filename
        timestamp = datetime.now().strftime("%Y-%m-%d_%H-%M")
        if employee_name:
            filename = f"Raport_{employee_name}_{timestamp}.{file_extension}"
        else:
            filename = f"Raport_obecnosci_{timestamp}.{file_extension}"
        
        # Generate enhanced email body
        html_body = generate_email_body(report_type, employee_name, date_range, filename)
        
        # Send email with enhanced error handling
        result = send_email(
            to_email=to_email,
            subject=subject,
            body=html_body,
            attachment_data=report_bytes,
            attachment_name=filename
        )
        
        result["filename"] = filename
        return result
        
    except EmailError as e:
        return {"success": False, "message": str(e), "error_type": "email_service"}
    except HTTPException:
        raise  # Re-raise HTTP exceptions
    except Exception as e:
        logger.error(f"Unexpected error in send_report_email: {e}")
        return {"success": False, "message": f"Unexpected error: {str(e)}", "error_type": "unknown"}
