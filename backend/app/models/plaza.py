from sqlalchemy import Column, String, DateTime, JSON, ForeignKey, Integer, Text, Enum as SQLEnum, DECIMAL
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
import uuid
import enum
from ..core.database import Base


class AreaType(str, enum.Enum):
    OUTDOOR = "outdoor"
    COVERED = "covered"
    UNDERGROUND = "underground"


class SpotType(str, enum.Enum):
    REGULAR = "regular"
    HANDICAP = "handicap"
    ELECTRIC = "electric"
    COMPACT = "compact"


class SpotStatus(str, enum.Enum):
    AVAILABLE = "available"
    OCCUPIED = "occupied"
    RESERVED = "reserved"
    MAINTENANCE = "maintenance"


class CameraStatus(str, enum.Enum):
    ACTIVE = "active"
    INACTIVE = "inactive"
    MAINTENANCE = "maintenance"


class Plaza(Base):
    __tablename__ = "plazas"

    plaza_id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    name = Column(String(255), nullable=False)
    address = Column(Text, nullable=False)
    coordinates = Column(JSON)  # Store as {"lat": float, "lng": float}
    owner_id = Column(UUID(as_uuid=True), ForeignKey("users.user_id"), nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())

    # Relationships
    owner = relationship("User", back_populates="owned_plazas")
    parking_areas = relationship("ParkingArea", back_populates="plaza", cascade="all, delete-orphan")
    cameras = relationship("Camera", back_populates="plaza", cascade="all, delete-orphan")

    def __repr__(self):
        return f"<Plaza(name='{self.name}')>"


class ParkingArea(Base):
    __tablename__ = "parking_areas"

    area_id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    plaza_id = Column(UUID(as_uuid=True), ForeignKey("plazas.plaza_id"), nullable=False)
    name = Column(String(255), nullable=False)
    floor_level = Column(Integer, default=0)
    area_type = Column(SQLEnum(AreaType), default=AreaType.OUTDOOR)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    # Relationships
    plaza = relationship("Plaza", back_populates="parking_areas")
    parking_spots = relationship("ParkingSpot", back_populates="area", cascade="all, delete-orphan")

    def __repr__(self):
        return f"<ParkingArea(name='{self.name}')>"


class ParkingSpot(Base):
    __tablename__ = "parking_spots"

    spot_id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    area_id = Column(UUID(as_uuid=True), ForeignKey("parking_areas.area_id"), nullable=False)
    spot_number = Column(String(50), nullable=False)
    spot_type = Column(SQLEnum(SpotType), default=SpotType.REGULAR)
    polygon_coordinates = Column(JSON)  # Store polygon points for spot boundary
    camera_id = Column(UUID(as_uuid=True), ForeignKey("cameras.camera_id"), nullable=True)
    status = Column(SQLEnum(SpotStatus), default=SpotStatus.AVAILABLE)
    last_updated = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())

    # Relationships
    area = relationship("ParkingArea", back_populates="parking_spots")
    camera = relationship("Camera", back_populates="assigned_spots")
    occupancy_history = relationship("SpotOccupancyHistory", back_populates="spot", cascade="all, delete-orphan")
    reservations = relationship("Reservation", back_populates="spot", cascade="all, delete-orphan")

    def __repr__(self):
        return f"<ParkingSpot(number='{self.spot_number}', status='{self.status}')>"


class Camera(Base):
    __tablename__ = "cameras"

    camera_id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    plaza_id = Column(UUID(as_uuid=True), ForeignKey("plazas.plaza_id"), nullable=False)
    name = Column(String(255), nullable=False)
    rtsp_url = Column(Text, nullable=True)
    position_coordinates = Column(JSON)  # Store as {"lat": float, "lng": float}
    coverage_area = Column(JSON)  # Store polygon for camera coverage
    status = Column(SQLEnum(CameraStatus), default=CameraStatus.ACTIVE)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())

    # Relationships
    plaza = relationship("Plaza", back_populates="cameras")
    assigned_spots = relationship("ParkingSpot", back_populates="camera")

    def __repr__(self):
        return f"<Camera(name='{self.name}', status='{self.status}')>" 