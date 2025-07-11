#!/usr/bin/env python3
"""
Simple test API to verify FastAPI is working
"""

try:
    from fastapi import FastAPI
    from fastapi.middleware.cors import CORSMiddleware
    import uvicorn
    import json
    from datetime import datetime
    import sqlite3
    import os
    
    app = FastAPI(title="ParkIT Test API", version="1.0.0")
    
    # Add CORS middleware
    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )
    
    # Simple database setup
    DB_FILE = "test_parkit.db"
    
    def init_db():
        conn = sqlite3.connect(DB_FILE)
        cursor = conn.cursor()
        
        # Create a simple plazas table
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
        
        # Create a simple spots table
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
        
        conn.commit()
        conn.close()
    
    @app.on_event("startup")
    async def startup_event():
        print("🚀 Starting ParkIT Test API...")
        init_db()
        print("✅ Database initialized!")
    
    @app.get("/")
    async def root():
        return {
            "message": "ParkIT Platform Test API",
            "status": "running",
            "timestamp": datetime.now().isoformat()
        }
    
    @app.get("/health")
    async def health_check():
        return {"status": "healthy", "timestamp": datetime.now().isoformat()}
    
    @app.post("/plazas")
    async def create_plaza(name: str, address: str):
        conn = sqlite3.connect(DB_FILE)
        cursor = conn.cursor()
        
        cursor.execute(
            "INSERT INTO plazas (name, address) VALUES (?, ?)",
            (name, address)
        )
        plaza_id = cursor.lastrowid
        conn.commit()
        conn.close()
        
        return {
            "id": plaza_id,
            "name": name,
            "address": address,
            "message": "Plaza created successfully"
        }
    
    @app.get("/plazas")
    async def list_plazas():
        conn = sqlite3.connect(DB_FILE)
        cursor = conn.cursor()
        
        cursor.execute("SELECT id, name, address, total_spots, available_spots, created_at FROM plazas")
        plazas = []
        for row in cursor.fetchall():
            plazas.append({
                "id": row[0],
                "name": row[1],
                "address": row[2],
                "total_spots": row[3],
                "available_spots": row[4],
                "created_at": row[5]
            })
        
        conn.close()
        return {"plazas": plazas, "count": len(plazas)}
    
    @app.post("/plazas/{plaza_id}/spots")
    async def create_parking_spot(plaza_id: int, spot_number: str):
        conn = sqlite3.connect(DB_FILE)
        cursor = conn.cursor()
        
        # Check if plaza exists
        cursor.execute("SELECT id FROM plazas WHERE id = ?", (plaza_id,))
        if not cursor.fetchone():
            conn.close()
            return {"error": "Plaza not found"}, 404
        
        cursor.execute(
            "INSERT INTO parking_spots (plaza_id, spot_number) VALUES (?, ?)",
            (plaza_id, spot_number)
        )
        spot_id = cursor.lastrowid
        
        # Update plaza total spots
        cursor.execute(
            "UPDATE plazas SET total_spots = total_spots + 1, available_spots = available_spots + 1 WHERE id = ?",
            (plaza_id,)
        )
        
        conn.commit()
        conn.close()
        
        return {
            "id": spot_id,
            "plaza_id": plaza_id,
            "spot_number": spot_number,
            "status": "available",
            "message": "Parking spot created successfully"
        }
    
    @app.get("/plazas/{plaza_id}/availability")
    async def get_plaza_availability(plaza_id: int):
        conn = sqlite3.connect(DB_FILE)
        cursor = conn.cursor()
        
        # Get plaza info
        cursor.execute("SELECT name, total_spots, available_spots FROM plazas WHERE id = ?", (plaza_id,))
        plaza = cursor.fetchone()
        
        if not plaza:
            conn.close()
            return {"error": "Plaza not found"}, 404
        
        # Get spot details
        cursor.execute(
            "SELECT spot_number, status FROM parking_spots WHERE plaza_id = ?",
            (plaza_id,)
        )
        spots = [{"spot_number": row[0], "status": row[1]} for row in cursor.fetchall()]
        
        conn.close()
        
        return {
            "plaza_id": plaza_id,
            "plaza_name": plaza[0],
            "total_spots": plaza[1],
            "available_spots": plaza[2],
            "occupied_spots": plaza[1] - plaza[2],
            "spots": spots
        }
    
    @app.put("/spots/{spot_id}/status")
    async def update_spot_status(spot_id: int, status: str):
        if status not in ["available", "occupied", "reserved", "maintenance"]:
            return {"error": "Invalid status"}, 400
        
        conn = sqlite3.connect(DB_FILE)
        cursor = conn.cursor()
        
        # Get current status and plaza_id
        cursor.execute("SELECT status, plaza_id FROM parking_spots WHERE id = ?", (spot_id,))
        result = cursor.fetchone()
        
        if not result:
            conn.close()
            return {"error": "Parking spot not found"}, 404
        
        old_status, plaza_id = result
        
        # Update spot status
        cursor.execute(
            "UPDATE parking_spots SET status = ?, last_updated = CURRENT_TIMESTAMP WHERE id = ?",
            (status, spot_id)
        )
        
        # Update plaza availability counts
        if old_status == "available" and status != "available":
            cursor.execute("UPDATE plazas SET available_spots = available_spots - 1 WHERE id = ?", (plaza_id,))
        elif old_status != "available" and status == "available":
            cursor.execute("UPDATE plazas SET available_spots = available_spots + 1 WHERE id = ?", (plaza_id,))
        
        conn.commit()
        conn.close()
        
        return {
            "spot_id": spot_id,
            "old_status": old_status,
            "new_status": status,
            "message": "Spot status updated successfully"
        }
    
    if __name__ == "__main__":
        print("🚀 Starting ParkIT Test Server...")
        uvicorn.run(app, host="0.0.0.0", port=8000, reload=True)

except ImportError as e:
    print(f"❌ Import error: {e}")
    print("Some packages may not be installed correctly.")
    print("Try: pip install fastapi uvicorn")
except Exception as e:
    print(f"❌ Error: {e}") 