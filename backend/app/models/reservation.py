from sqlalchemy import Column, String, DateTime, ForeignKey, Enum as SQLEnum
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
import uuid
import enum
from ..core.database import Base


class ReservationStatus(str, enum.Enum):
    ACTIVE = "active"
    COMPLETED = "completed"
    CANCELLED = "cancelled"
    EXPIRED = "expired"


class Reservation(Base):
    __tablename__ = "reservations"

    reservation_id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.user_id"), nullable=False)
    spot_id = Column(UUID(as_uuid=True), ForeignKey("parking_spots.spot_id"), nullable=False)
    reserved_from = Column(DateTime(timezone=True), nullable=False)
    reserved_until = Column(DateTime(timezone=True), nullable=False)
    status = Column(SQLEnum(ReservationStatus), default=ReservationStatus.ACTIVE)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())

    # Relationships
    user = relationship("User", back_populates="reservations")
    spot = relationship("ParkingSpot", back_populates="reservations")

    def __repr__(self):
        return f"<Reservation(user_id='{self.user_id}', spot_id='{self.spot_id}', status='{self.status}')>" 