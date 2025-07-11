from sqlalchemy import Column, String, DateTime, ForeignKey, DECIMAL
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
import uuid
from ..core.database import Base


class SpotOccupancyHistory(Base):
    __tablename__ = "spot_occupancy_history"

    history_id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    spot_id = Column(UUID(as_uuid=True), ForeignKey("parking_spots.spot_id"), nullable=False)
    status = Column(String(20), nullable=False)  # available, occupied, reserved, maintenance
    detected_at = Column(DateTime(timezone=True), server_default=func.now())
    vehicle_type = Column(String(50), nullable=True)  # car, motorcycle, bus, train, truck
    confidence_score = Column(DECIMAL(3, 2), nullable=True)  # Detection confidence 0.00-1.00

    # Relationships
    spot = relationship("ParkingSpot", back_populates="occupancy_history")

    def __repr__(self):
        return f"<SpotOccupancyHistory(spot_id='{self.spot_id}', status='{self.status}', detected_at='{self.detected_at}')>" 