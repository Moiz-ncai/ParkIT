from pydantic import BaseModel, EmailStr, validator
from typing import Optional, List, Dict, Any
from datetime import datetime
from uuid import UUID
from enum import Enum


# User Schemas
class UserType(str, Enum):
    ADMIN = "admin"
    PLAZA_OWNER = "plaza_owner"
    PLAZA_STAFF = "plaza_staff"
    CONSUMER = "consumer"


class UserCreate(BaseModel):
    email: EmailStr
    password: str
    user_type: UserType
    profile_data: Optional[Dict[str, Any]] = {}


class UserResponse(BaseModel):
    user_id: UUID
    email: str
    user_type: UserType
    profile_data: Dict[str, Any]
    is_active: str
    created_at: datetime

    class Config:
        orm_mode = True


class UserLogin(BaseModel):
    email: EmailStr
    password: str


class Token(BaseModel):
    access_token: str
    token_type: str


# Plaza Schemas
class PlazaCreate(BaseModel):
    name: str
    address: str
    coordinates: Optional[Dict[str, float]] = None  # {"lat": float, "lng": float}


class PlazaResponse(BaseModel):
    plaza_id: UUID
    name: str
    address: str
    coordinates: Optional[Dict[str, float]]
    owner_id: UUID
    created_at: datetime

    class Config:
        orm_mode = True


# Parking Area Schemas
class AreaType(str, Enum):
    OUTDOOR = "outdoor"
    COVERED = "covered"
    UNDERGROUND = "underground"


class ParkingAreaCreate(BaseModel):
    name: str
    floor_level: Optional[int] = 0
    area_type: Optional[AreaType] = AreaType.OUTDOOR


class ParkingAreaResponse(BaseModel):
    area_id: UUID
    plaza_id: UUID
    name: str
    floor_level: int
    area_type: AreaType
    created_at: datetime

    class Config:
        orm_mode = True


# Parking Spot Schemas
class SpotType(str, Enum):
    REGULAR = "regular"
    HANDICAP = "handicap"
    ELECTRIC = "electric"
    COMPACT = "compact"


class SpotStatus(str, Enum):
    AVAILABLE = "available"
    OCCUPIED = "occupied"
    RESERVED = "reserved"
    MAINTENANCE = "maintenance"


class ParkingSpotCreate(BaseModel):
    spot_number: str
    spot_type: Optional[SpotType] = SpotType.REGULAR
    polygon_coordinates: Optional[List[Dict[str, float]]] = None  # [{"x": float, "y": float}, ...]
    camera_id: Optional[UUID] = None


class ParkingSpotResponse(BaseModel):
    spot_id: UUID
    area_id: UUID
    spot_number: str
    spot_type: SpotType
    polygon_coordinates: Optional[List[Dict[str, float]]]
    camera_id: Optional[UUID]
    status: SpotStatus
    last_updated: datetime

    class Config:
        orm_mode = True


class ParkingSpotUpdate(BaseModel):
    status: Optional[SpotStatus] = None
    spot_type: Optional[SpotType] = None
    polygon_coordinates: Optional[List[Dict[str, float]]] = None
    camera_id: Optional[UUID] = None


# Camera Schemas
class CameraStatus(str, Enum):
    ACTIVE = "active"
    INACTIVE = "inactive"
    MAINTENANCE = "maintenance"


class CameraCreate(BaseModel):
    name: str
    rtsp_url: Optional[str] = None
    position_coordinates: Optional[Dict[str, float]] = None
    coverage_area: Optional[List[Dict[str, float]]] = None


class CameraResponse(BaseModel):
    camera_id: UUID
    plaza_id: UUID
    name: str
    rtsp_url: Optional[str]
    position_coordinates: Optional[Dict[str, float]]
    coverage_area: Optional[List[Dict[str, float]]]
    status: CameraStatus
    created_at: datetime

    class Config:
        orm_mode = True


# Occupancy History Schemas
class OccupancyCreate(BaseModel):
    spot_id: UUID
    status: SpotStatus
    vehicle_type: Optional[str] = None
    confidence_score: Optional[float] = None


class OccupancyResponse(BaseModel):
    history_id: UUID
    spot_id: UUID
    status: str
    detected_at: datetime
    vehicle_type: Optional[str]
    confidence_score: Optional[float]

    class Config:
        orm_mode = True


# Reservation Schemas
class ReservationStatus(str, Enum):
    ACTIVE = "active"
    COMPLETED = "completed"
    CANCELLED = "cancelled"
    EXPIRED = "expired"


class ReservationCreate(BaseModel):
    spot_id: UUID
    reserved_from: datetime
    reserved_until: datetime


class ReservationResponse(BaseModel):
    reservation_id: UUID
    user_id: UUID
    spot_id: UUID
    reserved_from: datetime
    reserved_until: datetime
    status: ReservationStatus
    created_at: datetime

    class Config:
        orm_mode = True


# Combined response schemas
class PlazaWithDetails(PlazaResponse):
    parking_areas: List[ParkingAreaResponse] = []
    cameras: List[CameraResponse] = []


class ParkingAreaWithSpots(ParkingAreaResponse):
    parking_spots: List[ParkingSpotResponse] = []


# Error response schema
class ErrorResponse(BaseModel):
    detail: str 