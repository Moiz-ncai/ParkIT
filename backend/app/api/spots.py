from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List
from uuid import UUID
from ..core.database import get_db
from ..models.user import User, UserType
from ..models.plaza import ParkingSpot, ParkingArea, Plaza
from ..models.occupancy import SpotOccupancyHistory
from ..api.schemas import (
    ParkingSpotCreate, ParkingSpotResponse, ParkingSpotUpdate,
    OccupancyCreate, OccupancyResponse
)
from ..api.auth import get_current_user

router = APIRouter()


@router.post("/areas/{area_id}/spots", response_model=ParkingSpotResponse)
async def create_parking_spot(
    area_id: UUID,
    spot_data: ParkingSpotCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Create a new parking spot in an area."""
    # Get the area and verify permissions
    area = db.query(ParkingArea).filter(ParkingArea.area_id == area_id).first()
    if not area:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Parking area not found"
        )
    
    # Check if user has permission to modify this plaza
    plaza = db.query(Plaza).filter(Plaza.plaza_id == area.plaza_id).first()
    if (current_user.user_type == UserType.PLAZA_OWNER and 
        plaza.owner_id != current_user.user_id and 
        current_user.user_type != UserType.ADMIN):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not enough permissions to modify this plaza"
        )
    
    # Check if spot number already exists in this area
    existing_spot = db.query(ParkingSpot).filter(
        ParkingSpot.area_id == area_id,
        ParkingSpot.spot_number == spot_data.spot_number
    ).first()
    if existing_spot:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Spot number already exists in this area"
        )
    
    db_spot = ParkingSpot(
        area_id=area_id,
        spot_number=spot_data.spot_number,
        spot_type=spot_data.spot_type,
        polygon_coordinates=spot_data.polygon_coordinates,
        camera_id=spot_data.camera_id
    )
    
    db.add(db_spot)
    db.commit()
    db.refresh(db_spot)
    
    return db_spot


@router.get("/areas/{area_id}/spots", response_model=List[ParkingSpotResponse])
async def list_parking_spots(
    area_id: UUID,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """List all parking spots in an area."""
    # Verify area exists
    area = db.query(ParkingArea).filter(ParkingArea.area_id == area_id).first()
    if not area:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Parking area not found"
        )
    
    spots = db.query(ParkingSpot).filter(ParkingSpot.area_id == area_id).all()
    return spots


@router.get("/{spot_id}", response_model=ParkingSpotResponse)
async def get_parking_spot(
    spot_id: UUID,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get a specific parking spot."""
    spot = db.query(ParkingSpot).filter(ParkingSpot.spot_id == spot_id).first()
    if not spot:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Parking spot not found"
        )
    
    return spot


@router.put("/{spot_id}", response_model=ParkingSpotResponse)
async def update_parking_spot(
    spot_id: UUID,
    spot_update: ParkingSpotUpdate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Update a parking spot."""
    spot = db.query(ParkingSpot).filter(ParkingSpot.spot_id == spot_id).first()
    if not spot:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Parking spot not found"
        )
    
    # Check permissions
    area = db.query(ParkingArea).filter(ParkingArea.area_id == spot.area_id).first()
    plaza = db.query(Plaza).filter(Plaza.plaza_id == area.plaza_id).first()
    
    if (current_user.user_type == UserType.PLAZA_OWNER and 
        plaza.owner_id != current_user.user_id and 
        current_user.user_type != UserType.ADMIN):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not enough permissions to modify this parking spot"
        )
    
    # Update fields that are provided
    update_data = spot_update.dict(exclude_unset=True)
    for field, value in update_data.items():
        setattr(spot, field, value)
    
    db.commit()
    db.refresh(spot)
    
    return spot


@router.delete("/{spot_id}")
async def delete_parking_spot(
    spot_id: UUID,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Delete a parking spot."""
    spot = db.query(ParkingSpot).filter(ParkingSpot.spot_id == spot_id).first()
    if not spot:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Parking spot not found"
        )
    
    # Check permissions
    area = db.query(ParkingArea).filter(ParkingArea.area_id == spot.area_id).first()
    plaza = db.query(Plaza).filter(Plaza.plaza_id == area.plaza_id).first()
    
    if (current_user.user_type == UserType.PLAZA_OWNER and 
        plaza.owner_id != current_user.user_id and 
        current_user.user_type != UserType.ADMIN):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not enough permissions to delete this parking spot"
        )
    
    db.delete(spot)
    db.commit()
    
    return {"message": "Parking spot deleted successfully"}


# Occupancy endpoints
@router.post("/occupancy", response_model=OccupancyResponse)
async def record_occupancy(
    occupancy_data: OccupancyCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Record a parking spot occupancy change (for detection service)."""
    # Verify spot exists
    spot = db.query(ParkingSpot).filter(ParkingSpot.spot_id == occupancy_data.spot_id).first()
    if not spot:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Parking spot not found"
        )
    
    # Create occupancy history record
    db_occupancy = SpotOccupancyHistory(
        spot_id=occupancy_data.spot_id,
        status=occupancy_data.status.value,
        vehicle_type=occupancy_data.vehicle_type,
        confidence_score=occupancy_data.confidence_score
    )
    
    # Update spot status
    spot.status = occupancy_data.status
    
    db.add(db_occupancy)
    db.commit()
    db.refresh(db_occupancy)
    
    return db_occupancy


@router.get("/{spot_id}/occupancy", response_model=List[OccupancyResponse])
async def get_spot_occupancy_history(
    spot_id: UUID,
    limit: int = 50,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get occupancy history for a parking spot."""
    # Verify spot exists
    spot = db.query(ParkingSpot).filter(ParkingSpot.spot_id == spot_id).first()
    if not spot:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Parking spot not found"
        )
    
    history = db.query(SpotOccupancyHistory).filter(
        SpotOccupancyHistory.spot_id == spot_id
    ).order_by(SpotOccupancyHistory.detected_at.desc()).limit(limit).all()
    
    return history


@router.get("/plaza/{plaza_id}/availability")
async def get_plaza_availability(
    plaza_id: UUID,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get real-time availability for a plaza."""
    # Verify plaza exists
    plaza = db.query(Plaza).filter(Plaza.plaza_id == plaza_id).first()
    if not plaza:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Plaza not found"
        )
    
    # Get all spots in all areas of this plaza
    spots = db.query(ParkingSpot).join(ParkingArea).filter(
        ParkingArea.plaza_id == plaza_id
    ).all()
    
    total_spots = len(spots)
    available_spots = len([s for s in spots if s.status == "available"])
    occupied_spots = len([s for s in spots if s.status == "occupied"])
    reserved_spots = len([s for s in spots if s.status == "reserved"])
    maintenance_spots = len([s for s in spots if s.status == "maintenance"])
    
    return {
        "plaza_id": plaza_id,
        "plaza_name": plaza.name,
        "total_spots": total_spots,
        "available_spots": available_spots,
        "occupied_spots": occupied_spots,
        "reserved_spots": reserved_spots,
        "maintenance_spots": maintenance_spots,
        "occupancy_rate": round((occupied_spots / total_spots * 100) if total_spots > 0 else 0, 2)
    } 