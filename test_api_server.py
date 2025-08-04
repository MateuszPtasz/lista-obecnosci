#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Prosty serwer testowy do diagnostyki
Uruchamia minimalny serwer HTTP, który zwraca odpowiedzi w oczekiwanym formacie
"""

from http.server import BaseHTTPRequestHandler, HTTPServer
import json
import datetime as dt
import socket
import os
import sys
import argparse

class TestAPIHandler(BaseHTTPRequestHandler):
    def _set_headers(self, content_type="application/json"):
        self.send_response(200)
        self.send_header('Content-type', content_type)
        self.end_headers()
    
    def _send_json_response(self, data):
        self._set_headers()
        self.wfile.write(json.dumps(data).encode('utf-8'))
    
    def do_GET(self):
        """Obsługuje żądania GET"""
        print(f"Otrzymano żądanie GET: {self.path}")
        
        if self.path == "/api/connection-test":
            # Endpoint testu połączenia
            self._send_json_response({
                "status": "success", 
                "message": "API działa poprawnie",
                "server_time": dt.datetime.now().isoformat()
            })
            
        elif self.path == "/api/mobile-config":
            # Endpoint konfiguracji mobilnej - POPRAWNY FORMAT z zagnieżdżonym 'config'
            self._send_json_response({
                "config": {
                    "enable_location": True,
                    "location_interval_seconds": 60,
                    "enable_pin_security": True, 
                    "require_device_verification": True,
                    "offline_mode_enabled": True,
                    "sync_interval_minutes": 15,
                    "battery_saving_mode": False,
                    "notify_on_success": True,
                    "debug_mode": True,
                    "timer_enabled": True,
                    "daily_stats": True,
                    "monthly_stats": True
                },
                "version": "1.0.5-test",
                "timestamp": dt.datetime.now().isoformat()
            })
            
        elif self.path == "/api/mobile-config-flat":
            # Endpoint konfiguracji mobilnej - NIEPOPRAWNY FORMAT (płaski)
            self._send_json_response({
                "enable_location": True,
                "location_interval_seconds": 60,
                "enable_pin_security": True, 
                "require_device_verification": True,
                "offline_mode_enabled": True,
                "sync_interval_minutes": 15,
                "battery_saving_mode": False,
                "notify_on_success": True,
                "debug_mode": True,
                "timer_enabled": True,
                "daily_stats": True,
                "monthly_stats": True,
                "version": "1.0.5-test",
                "timestamp": dt.datetime.now().isoformat()
            })
            
        elif self.path.startswith("/api/worker/"):
            # Endpoint statusu pracownika
            worker_id = self.path.split("/")[-1]
            self._send_json_response({
                "status": "active",
                "worker_id": worker_id,
                "last_active": dt.datetime.now().isoformat()
            })
            
        else:
            # Domyślna odpowiedź dla nieznanych ścieżek
            self._set_headers(content_type="text/html")
            self.wfile.write("""
            <html>
            <head><title>Test API Server</title></head>
            <body>
                <h1>Test API Server</h1>
                <p>Serwer testowy działa poprawnie.</p>
                <p>Dostępne endpointy:</p>
                <ul>
                    <li><a href="/api/connection-test">/api/connection-test</a> - Test połączenia</li>
                    <li><a href="/api/mobile-config">/api/mobile-config</a> - Konfiguracja mobilna (poprawny format)</li>
                    <li><a href="/api/mobile-config-flat">/api/mobile-config-flat</a> - Konfiguracja mobilna (niepoprawny format)</li>
                </ul>
            </body>
            </html>
            """.encode('utf-8'))
    
    def do_POST(self):
        """Obsługuje żądania POST"""
        content_length = int(self.headers['Content-Length'])
        post_data = self.rfile.read(content_length)
        
        print(f"Otrzymano żądanie POST: {self.path}")
        print(f"Dane: {post_data.decode('utf-8')}")
        
        try:
            data = json.loads(post_data.decode('utf-8'))
            
            if self.path == "/api/start":
                # Endpoint rozpoczęcia pracy
                employee_id = data.get("employee_id") or data.get("worker_id")
                self._send_json_response({
                    "status": "success",
                    "message": f"Rozpoczęto pracę dla pracownika {employee_id}",
                    "shift_id": 12345
                })
                
            elif self.path == "/api/stop":
                # Endpoint zakończenia pracy
                employee_id = data.get("employee_id") or data.get("worker_id")
                self._send_json_response({
                    "status": "success",
                    "message": f"Zakończono pracę dla pracownika {employee_id}",
                    "shift_id": 12345
                })
                
            else:
                # Domyślna odpowiedź dla nieznanych ścieżek
                self._send_json_response({
                    "status": "error",
                    "message": f"Nieznany endpoint: {self.path}"
                })
                
        except json.JSONDecodeError:
            # Nieprawidłowy format JSON
            self._send_json_response({
                "status": "error",
                "message": "Nieprawidłowy format JSON"
            })

def run_server(port=8000, host='0.0.0.0'):
    """Uruchamia serwer HTTP na określonym porcie"""
    server_address = (host, port)
    httpd = HTTPServer(server_address, TestAPIHandler)
    
    try:
        hostname = socket.gethostname()
        local_ip = socket.gethostbyname(hostname)
    except:
        local_ip = "nieznane"
    
    print(f"Uruchamianie serwera testowego na {host}:{port}")
    print(f"Lokalny adres IP: {local_ip}")
    print("Naciśnij CTRL+C, aby zakończyć")
    
    try:
        httpd.serve_forever()
    except KeyboardInterrupt:
        print("Zatrzymywanie serwera...")
        httpd.server_close()

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Prosty serwer API do testów')
    parser.add_argument('-p', '--port', type=int, default=8000, help='Port serwera (domyślnie: 8000)')
    parser.add_argument('--host', default='0.0.0.0', help='Adres hosta (domyślnie: 0.0.0.0)')
    
    args = parser.parse_args()
    run_server(port=args.port, host=args.host)
