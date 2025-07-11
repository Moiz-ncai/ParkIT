from pydantic_settings import BaseSettings
from typing import Optional
import os


class Settings(BaseSettings):
    # Application
    app_name: str = "ParkIT Platform API"
    version: str = "1.0.0"
    debug: bool = True
    
    # Database
    database_url: str = "postgresql://postgres:password@localhost:5432/parkit_platform"
    database_echo: bool = False
    
    # JWT Authentication
    secret_key: str = "your-secret-key-change-this-in-production"
    algorithm: str = "HS256"
    access_token_expire_minutes: int = 30
    
    # CORS
    allowed_origins: list = ["http://localhost:3000", "http://localhost:8080"]
    
    # Redis (for caching and real-time features)
    redis_url: str = "redis://localhost:6379"
    
    # File Upload
    upload_dir: str = "uploads"
    max_file_size: int = 10 * 1024 * 1024  # 10MB
    
    class Config:
        env_file = ".env"
        case_sensitive = False


settings = Settings()

# Create upload directory if it doesn't exist
os.makedirs(settings.upload_dir, exist_ok=True) 