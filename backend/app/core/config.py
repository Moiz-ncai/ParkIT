import os
from typing import List


class Settings:
    # Application
    app_name: str = "ParkIT Platform API"
    version: str = "1.0.0"
    debug: bool = True
    
    # Database (SQLite for testing, PostgreSQL for production)
    database_url: str = os.getenv("DATABASE_URL", "sqlite:///./parkit_platform.db")
    database_echo: bool = os.getenv("DATABASE_ECHO", "false").lower() == "true"
    
    # JWT Authentication
    secret_key: str = os.getenv("SECRET_KEY", "your-secret-key-change-this-in-production")
    algorithm: str = "HS256"
    access_token_expire_minutes: int = 30
    
    # CORS
    allowed_origins: List[str] = [
        "http://localhost:3000", 
        "http://localhost:8080",
        "http://127.0.0.1:3000",
        "http://127.0.0.1:8080"
    ]
    
    # File Upload
    upload_dir: str = "uploads"
    max_file_size: int = 10 * 1024 * 1024  # 10MB


settings = Settings()

# Create upload directory if it doesn't exist
os.makedirs(settings.upload_dir, exist_ok=True) 