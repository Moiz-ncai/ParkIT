#!/usr/bin/env python3
"""
Basic test script for ParkIT Platform backend concept
Uses Python's built-in HTTP server to demonstrate core functionality
"""

import json
import sqlite3
from http.server import BaseHTTPRequestHandler, HTTPServer
from urllib.parse import urlparse, parse_qs
from datetime import datetime
import threading

class ParkITHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        parsed_path = urlparse(self.path)
        path = parsed_path.path
        
        if path == "/":
            self.send_response(200)
            self.send_header('Content-type', 'application/json')
            self.send_header('Access-Control-Allow-Origin', '*')
            self.end_headers()
            response = {
                "message": "ParkIT Platform Backend Test",
                "status": "running",
                "timestamp": datetime.now().isoformat()
            }
            self.wfile.write(json.dumps(response).encode())
            
        elif path == "/health":
            self.send_response(200)
            self.send_header('Content-type', 'application/json')
            self.send_header('Access-Control-Allow-Origin', '*')
            self.end_headers()
            response = {"status": "healthy", "timestamp": datetime.now().isoformat()}
            self.wfile.write(json.dumps(response).encode())
            
        elif path == "/plazas":
            self.send_response(200)
            self.send_header('Content-type', 'application/json')
            self.send_header('Access-Control-Allow-Origin', '*')
            self.end_headers()
            
            conn = sqlite3.connect('test_parkit.db')
            cursor = conn.cursor()
            cursor.execute("SELECT id, name, address, total_spots, available_spots FROM plazas")
            plazas = []
            for row in cursor.fetchall():
                plazas.append({
                    "id": row[0],
                    "name": row[1], 
                    "address": row[2],
                    "total_spots": row[3],
                    "available_spots": row[4]
                })
            conn.close()
            
            response = {"plazas": plazas, "count": len(plazas)}
            self.wfile.write(json.dumps(response).encode())
            
        elif path.startswith("/plazas/") and path.endswith("/availability"):
            plaza_id = path.split("/")[2]
            
            self.send_response(200)
            self.send_header('Content-type', 'application/json') 
            self.send_header('Access-Control-Allow-Origin', '*')
            self.end_headers()
            
            conn = sqlite3.connect('test_parkit.db')
            cursor = conn.cursor()
            cursor.execute("SELECT name, total_spots, available_spots FROM plazas WHERE id = ?", (plaza_id,))
            plaza = cursor.fetchone()
            
            if plaza:
                response = {
                    "plaza_id": int(plaza_id),
                    "plaza_name": plaza[0],
                    "total_spots": plaza[1],
                    "available_spots": plaza[2],
                    "occupied_spots": plaza[1] - plaza[2],
                    "occupancy_rate": round(((plaza[1] - plaza[2]) / plaza[1] * 100) if plaza[1] > 0 else 0, 2)
                }
            else:
                response = {"error": "Plaza not found"}
            
            conn.close()
            self.wfile.write(json.dumps(response).encode())
        
        else:
            self.send_response(404)
            self.send_header('Content-type', 'application/json')
            self.send_header('Access-Control-Allow-Origin', '*')
            self.end_headers()
            response = {"error": "Not found"}
            self.wfile.write(json.dumps(response).encode())

    def do_POST(self):
        if self.path == "/plazas":
            content_length = int(self.headers['Content-Length'])
            post_data = self.rfile.read(content_length)
            
            try:
                data = json.loads(post_data.decode('utf-8'))
                name = data.get('name', 'Test Plaza')
                address = data.get('address', 'Test Address')
                
                conn = sqlite3.connect('test_parkit.db')
                cursor = conn.cursor()
                cursor.execute("INSERT INTO plazas (name, address) VALUES (?, ?)", (name, address))
                plaza_id = cursor.lastrowid
                conn.commit()
                conn.close()
                
                self.send_response(201)
                self.send_header('Content-type', 'application/json')
                self.send_header('Access-Control-Allow-Origin', '*')
                self.end_headers()
                
                response = {
                    "id": plaza_id,
                    "name": name,
                    "address": address,
                    "message": "Plaza created successfully"
                }
                self.wfile.write(json.dumps(response).encode())
                
            except Exception as e:
                self.send_response(400)
                self.send_header('Content-type', 'application/json')
                self.send_header('Access-Control-Allow-Origin', '*')
                self.end_headers()
                response = {"error": str(e)}
                self.wfile.write(json.dumps(response).encode())
        
        else:
            self.send_response(404)
            self.send_header('Content-type', 'application/json')
            self.send_header('Access-Control-Allow-Origin', '*')
            self.end_headers()
            response = {"error": "Not found"}
            self.wfile.write(json.dumps(response).encode())

    def do_OPTIONS(self):
        # Handle preflight requests
        self.send_response(200)
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Access-Control-Allow-Methods', 'GET, POST, PUT, DELETE, OPTIONS')
        self.send_header('Access-Control-Allow-Headers', 'Content-Type, Authorization')
        self.end_headers()

def init_database():
    """Initialize the test database with sample data"""
    conn = sqlite3.connect('test_parkit.db')
    cursor = conn.cursor()
    
    # Create tables
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS plazas (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            address TEXT NOT NULL,
            total_spots INTEGER DEFAULT 0,
            available_spots INTEGER DEFAULT 0,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """)
    
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS parking_spots (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            plaza_id INTEGER,
            spot_number TEXT NOT NULL,
            status TEXT DEFAULT 'available',
            last_updated TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (plaza_id) REFERENCES plazas (id)
        )
    """)
    
    # Add sample data if tables are empty
    cursor.execute("SELECT COUNT(*) FROM plazas")
    if cursor.fetchone()[0] == 0:
        print("Adding sample data...")
        
        # Add sample plazas
        cursor.execute("INSERT INTO plazas (name, address, total_spots, available_spots) VALUES (?, ?, ?, ?)",
                      ("Downtown Plaza", "123 Main St, City Center", 150, 23))
        plaza1_id = cursor.lastrowid
        
        cursor.execute("INSERT INTO plazas (name, address, total_spots, available_spots) VALUES (?, ?, ?, ?)",
                      ("Mall Parking", "456 Shopping Ave, Mall District", 300, 87))
        plaza2_id = cursor.lastrowid
        
        cursor.execute("INSERT INTO plazas (name, address, total_spots, available_spots) VALUES (?, ?, ?, ?)",
                      ("Airport Parking", "789 Airport Rd, Terminal Area", 500, 234))
        plaza3_id = cursor.lastrowid
        
        # Add sample parking spots
        for i in range(1, 151):
            status = "available" if i <= 23 else "occupied"
            cursor.execute("INSERT INTO parking_spots (plaza_id, spot_number, status) VALUES (?, ?, ?)",
                          (plaza1_id, f"A{i:03d}", status))
        
        for i in range(1, 301):
            status = "available" if i <= 87 else "occupied"
            cursor.execute("INSERT INTO parking_spots (plaza_id, spot_number, status) VALUES (?, ?, ?)",
                          (plaza2_id, f"B{i:03d}", status))
        
        for i in range(1, 501):
            status = "available" if i <= 234 else "occupied"
            cursor.execute("INSERT INTO parking_spots (plaza_id, spot_number, status) VALUES (?, ?, ?)",
                          (plaza3_id, f"C{i:03d}", status))
    
    conn.commit()
    conn.close()
    print("✅ Database initialized successfully!")

def start_server(port=8000):
    """Start the HTTP server"""
    print(f"🚀 Starting ParkIT Test Server on port {port}...")
    init_database()
    
    server = HTTPServer(('localhost', port), ParkITHandler)
    print(f"✅ Server running at http://localhost:{port}")
    print("\nAvailable endpoints:")
    print(f"  GET  http://localhost:{port}/                    - API status")
    print(f"  GET  http://localhost:{port}/health             - Health check")
    print(f"  GET  http://localhost:{port}/plazas             - List plazas")
    print(f"  POST http://localhost:{port}/plazas             - Create plaza")
    print(f"  GET  http://localhost:{port}/plazas/1/availability - Plaza availability")
    print("\nPress Ctrl+C to stop the server")
    
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        print("\n🛑 Server stopped")
        server.server_close()

if __name__ == "__main__":
    start_server() 