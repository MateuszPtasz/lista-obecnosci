# csv_export.py - CSV export functionality

import csv
import io
from datetime import datetime
from typing import List, Dict, Any
from fastapi import HTTPException

def generate_csv_report(data: List[Dict[str, Any]], report_type: str = "attendance") -> str:
    """Generate CSV report from data"""
    output = io.StringIO()
    
    if not data:
        return ""
    
    if report_type == "attendance_summary":
        fieldnames = [
            'ID Pracownika', 'Imię i Nazwisko', 'Stawka/h', 'Dni obecności', 
            'Łączny czas', 'Łączne godziny', 'Soboty', 'Niedziele', 'Święta'
        ]
        
        writer = csv.DictWriter(output, fieldnames=fieldnames, delimiter=';')
        writer.writeheader()
        
        for row in data:
            writer.writerow({
                'ID Pracownika': row.get('id', ''),
                'Imię i Nazwisko': row.get('name', ''),
                'Stawka/h': row.get('rate', ''),
                'Dni obecności': row.get('days_present', ''),
                'Łączny czas': row.get('total_time', ''),
                'Łączne godziny': row.get('total_hours', ''),
                'Soboty': row.get('saturdays', ''),
                'Niedziele': row.get('sundays', ''),
                'Święta': row.get('holidays', '')
            })
    
    elif report_type == "attendance_details":
        fieldnames = [
            'Data', 'Imię i Nazwisko', 'Godzina rozpoczęcia', 'Godzina zakończenia',
            'Czas trwania', 'Typ dnia', 'Kwota', 'Urlop', 'Chorobowe'
        ]
        
        writer = csv.DictWriter(output, fieldnames=fieldnames, delimiter=';')
        writer.writeheader()
        
        logs = data.get('logs', [])
        for row in logs:
            writer.writerow({
                'Data': row.get('date', ''),
                'Imię i Nazwisko': row.get('name', ''),
                'Godzina rozpoczęcia': row.get('start', ''),
                'Godzina zakończenia': row.get('stop', ''),
                'Czas trwania': row.get('duration', ''),
                'Typ dnia': row.get('typ', ''),
                'Kwota': row.get('kwota', ''),
                'Urlop': 'Tak' if row.get('is_holiday') == 'tak' else 'Nie',
                'Chorobowe': row.get('is_sick', 'Nie')
            })
    
    elif report_type == "daily_attendance":
        fieldnames = [
            'Imię i Nazwisko', 'Godzina rozpoczęcia', 'Godzina zakończenia',
            'Czas trwania', 'Lokalizacja start', 'Lokalizacja stop'
        ]
        
        writer = csv.DictWriter(output, fieldnames=fieldnames, delimiter=';')
        writer.writeheader()
        
        for row in data:
            start_location = f"{row.get('start_lat', '')},{row.get('start_lon', '')}" if row.get('start_lat') else ""
            stop_location = f"{row.get('stop_lat', '')},{row.get('stop_lon', '')}" if row.get('stop_lat') else ""
            
            writer.writerow({
                'Imię i Nazwisko': row.get('name', ''),
                'Godzina rozpoczęcia': row.get('start', ''),
                'Godzina zakończenia': row.get('stop', ''),
                'Czas trwania': row.get('duration', ''),
                'Lokalizacja start': start_location,
                'Lokalizacja stop': stop_location
            })
    
    else:
        # Generic CSV export
        if data:
            fieldnames = list(data[0].keys())
            writer = csv.DictWriter(output, fieldnames=fieldnames, delimiter=';')
            writer.writeheader()
            for row in data:
                writer.writerow(row)
    
    return output.getvalue()

def create_excel_content(csv_content: str) -> str:
    """Convert CSV to Excel-compatible format (still CSV but with proper encoding)"""
    # Add BOM for Excel to recognize UTF-8
    return '\ufeff' + csv_content

def generate_report_filename(report_type: str, employee_name: str = None, format: str = "csv") -> str:
    """Generate appropriate filename for report"""
    timestamp = datetime.now().strftime("%Y-%m-%d_%H-%M")
    
    if employee_name:
        base_name = f"Raport_{employee_name}_{timestamp}"
    else:
        type_names = {
            "attendance_summary": "Podsumowanie_obecnosci",
            "attendance_details": "Szczegoly_obecnosci", 
            "daily_attendance": "Obecnosc_dzienna"
        }
        base_name = f"{type_names.get(report_type, 'Raport')}_{timestamp}"
    
    return f"{base_name}.{format}"